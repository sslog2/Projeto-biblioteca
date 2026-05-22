import csv
from datetime import date, timedelta
from decimal import Decimal

from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.db.models import Count, Sum, Q, F
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from rest_framework.response import Response
from rest_framework.views import APIView

from app.api.models import Livro, Membro, Emprestimo, Multa, Editora, Reserva, Configuracao
from app.api.forms import LivroForm, MembroForm, EditoraForm, EmprestimoForm

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

class ExportarAtrasadosCSVView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff

    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="inadimplentes.csv"'

        writer = csv.writer(response)
        writer.writerow(['Membro', 'Livro', 'Data Devolução', 'Dias de Atraso', 'Valor da Multa'])

        atrasados = Emprestimo.objects.filter(
            devolvido=False, 
            data_devolucao__lt=date.today()
        ).select_related('membro', 'livro')

        for emp in atrasados:
            multa_valor = Decimal('0.00')
            if hasattr(emp, 'multa'):
                multa_valor = emp.multa.valor
            else:
                # Simula valor se não tiver multa criada ainda
                dias = (date.today() - emp.data_devolucao).days
                multa_valor = Configuracao.get_instance().valor_multa_dia * dias

            writer.writerow([
                emp.membro.nome,
                emp.livro.titulo,
                emp.data_devolucao,
                (date.today() - emp.data_devolucao).days,
                f'R$ {multa_valor}'
            ])

        return response

class RenovarEmprestimoView(LoginRequiredMixin, View):
    def post(self, request, pk):
        emprestimo = get_object_or_404(Emprestimo, pk=pk)
        
        # Tenta pegar o membro do usuário logado
        try:
            membro_logado = Membro.objects.get(user=request.user)
        except Membro.DoesNotExist:
            membro_logado = None

        # Validação: só o próprio membro ou admin pode renovar
        if not request.user.is_staff and (not membro_logado or emprestimo.membro != membro_logado):
            messages.error(request, "Você não tem permissão para renovar este empréstimo.")
            return redirect('portal-membro')

        if emprestimo.esta_atrasado:
            messages.error(request, f"O livro '{emprestimo.livro.titulo}' está atrasado (venceu em {emprestimo.data_devolucao}). Por favor, devolva-o na biblioteca.")
        else:
            emprestimo.data_devolucao += timedelta(days=7)
            emprestimo.save()
            messages.success(request, f"Sucesso! A nova data de devolução para '{emprestimo.livro.titulo}' é {emprestimo.data_devolucao}.")
        
        return redirect('portal-membro')

class ReservarLivroView(LoginRequiredMixin, View):
    def post(self, request, pk):
        livro = get_object_or_404(Livro, pk=pk)
        membro = get_object_or_404(Membro, user=request.user)

        # Verifica se já tem uma reserva ativa para esse livro
        reserva_existente = Reserva.objects.filter(membro=membro, livro=livro, status=Reserva.Status.ATIVA).exists()
        if reserva_existente:
            messages.warning(request, f"Você já possui uma reserva ativa para o livro '{livro.titulo}'.")
        else:
            Reserva.objects.create(membro=membro, livro=livro)
            messages.success(request, f"Reserva realizada com sucesso para o livro '{livro.titulo}'!")
        
        return redirect('portal-membro')

class PortalLoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            if request.user.is_staff:
                return redirect('dashboard')
            return redirect('portal-membro')
        return render(request, 'portal_login.html')

    def post(self, request):
        username_or_email = request.POST.get('email')
        password = request.POST.get('cpf')

        # Tenta autenticar diretamente (Django auth para o admin)
        user = authenticate(request, username=username_or_email, password=password)
        
        # Se falhou, tenta buscar pelo email do membro
        if user is None:
            try:
                membro = Membro.objects.get(email=username_or_email)
                if membro.user:
                    user = authenticate(request, username=membro.user.username, password=password)
            except Membro.DoesNotExist:
                pass

        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('dashboard')
            return redirect('portal-membro')
        else:
            messages.error(request, "E-mail ou CPF incorretos.")
        
        return render(request, 'portal_login.html')

class PortalLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('portal-login')


class PortalCadastroView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('portal-membro')
        return render(request, 'portal_cadastro.html')

    def post(self, request):
        nome     = request.POST.get('nome', '').strip()
        email    = request.POST.get('email', '').strip()
        cpf      = request.POST.get('cpf', '').strip()
        telefone = request.POST.get('telefone', '').strip()

        erros = []
        if not nome:
            erros.append("O nome é obrigatório.")
        if not email:
            erros.append("O e-mail é obrigatório.")
        if not cpf:
            erros.append("O CPF é obrigatório (será usado como senha).")

        if not erros:
            from django.contrib.auth.models import User
            if User.objects.filter(username=email).exists() or Membro.objects.filter(email=email).exists():
                erros.append("Já existe uma conta com este e-mail.")

        if erros:
            return render(request, 'portal_cadastro.html', {'erros': erros, 'dados': request.POST})

        # Cria o User e o Membro vinculados
        user = User.objects.create_user(username=email, email=email, password=cpf,
                                        first_name=nome.split()[0])
        Membro.objects.create(user=user, nome=nome, email=email, cpf=cpf, telefone=telefone)

        login(request, user)
        messages.success(request, f"Conta criada com sucesso! Bem-vindo(a), {nome.split()[0]}.")
        return redirect('portal-membro')

class PortalMembroView(LoginRequiredMixin, View):
    def get(self, request):
        # Se for admin tentando acessar o portal, redireciona pro dashboard ou deixa ver?
        # Geralmente admin não tem objeto Membro vinculado.
        try:
            membro = Membro.objects.get(user=request.user)
        except Membro.DoesNotExist:
            if request.user.is_staff:
                return redirect('dashboard')
            messages.error(request, "Seu usuário não possui um perfil de membro vinculado.")
            logout(request)
            return redirect('portal-login')
        
        # Empréstimos atuais (não devolvidos)
        emprestimos_ativos = Emprestimo.objects.filter(membro=membro, devolvido=False).select_related('livro')
        
        # Histórico completo (devolvidos)
        historico = Emprestimo.objects.filter(membro=membro, devolvido=True).select_related('livro').order_by('-data_devolucao')
        
        # Reservas Ativas
        reservas = Reserva.objects.filter(membro=membro, status=Reserva.Status.ATIVA).select_related('livro')
        reservas_livros = [r.livro for r in reservas]
        
        multas = Multa.objects.filter(emprestimo__membro=membro, pago=False)
        
        # Empréstimos atrasados que ainda não possuem registro formal de Multa
        hoje = date.today()
        valor_multa_dia = Configuracao.get_instance().valor_multa_dia
        emprestimos_atrasados_sem_multa = Emprestimo.objects.filter(
            membro=membro, devolvido=False, data_devolucao__lt=hoje
        ).exclude(multa__isnull=False).select_related('livro')
        pendencias_dinamicas = [
            {
                'valor': valor_multa_dia * (hoje - e.data_devolucao).days,
                'livro_titulo': e.livro.titulo,
                'dias': (hoje - e.data_devolucao).days,
            }
            for e in emprestimos_atrasados_sem_multa
        ]

        todos_livros = Livro.objects.all().order_by('titulo')

        # Lógica de Recomendação: "Quem leu este, também leu..."
        # 1. Pega os IDs dos livros que o membro já leu ou está lendo
        livros_lidos_ids = Emprestimo.objects.filter(membro=membro).values_list('livro_id', flat=True)
        
        # 2. Encontra outros membros que leram esses mesmos livros
        outros_membros_ids = Emprestimo.objects.filter(
            livro_id__in=livros_lidos_ids
        ).exclude(membro=membro).values_list('membro_id', flat=True).distinct()
        
        # 3. Encontra livros que esses outros membros leram, mas que o membro atual ainda não leu
        recomendacoes = Livro.objects.filter(
            emprestimos__membro_id__in=outros_membros_ids
        ).exclude(
            id__in=livros_lidos_ids
        ).annotate(
            contagem=Count('id')
        ).order_by('-contagem')[:4]

        # Fallback: Se não houver recomendações baseadas em outros usuários, sugere livros aleatórios
        if not recomendacoes:
            recomendacoes = Livro.objects.exclude(id__in=livros_lidos_ids).order_by('?')[:4]
        
        context = {
            'membro': membro,
            'emprestimos': emprestimos_ativos,
            'historico': historico,
            'reservas': reservas,
            'reservas_livros': reservas_livros,
            'multas': multas,
            'pendencias_dinamicas': pendencias_dinamicas,
            'todos_livros': todos_livros,
            'recomendacoes': recomendacoes,
        }
        return render(request, 'portal_membro.html', context)

class EmprestimosTemplateView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def get(self, request):
        qs = (
            Emprestimo.objects
            .select_related('membro', 'livro')
            .order_by('-data_emprestimo', '-id')
        )
        # Filtro por status
        filtro = request.GET.get('filtro', 'todos')
        if filtro == 'ativos':
            qs = qs.filter(devolvido=False)
        elif filtro == 'devolvidos':
            qs = qs.filter(devolvido=True)
        elif filtro == 'atrasados':
            qs = qs.filter(devolvido=False, data_devolucao__lt=date.today())

        paginator = Paginator(qs, 15)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        return render(request, 'emprestimos.html', {
            'page_obj': page_obj,
            'filtro': filtro,
            'total': qs.count(),
        })


class LivroUpdateTemplateView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def get(self, request, pk):
        livro = get_object_or_404(Livro, pk=pk)
        form = LivroForm(instance=livro)
        return render(request, 'livro_form.html', {'form': form, 'titulo': f'Editar: {livro.titulo}'})

    def post(self, request, pk):
        livro = get_object_or_404(Livro, pk=pk)
        form = LivroForm(request.POST, instance=livro)
        if form.is_valid():
            form.save()
            messages.success(request, f"Livro '{livro.titulo}' atualizado com sucesso!")
            return redirect('livros')
        return render(request, 'livro_form.html', {'form': form, 'titulo': f'Editar: {livro.titulo}'})

class LivroDetailTemplateView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def get(self, request, pk):
        livro = get_object_or_404(Livro, pk=pk)
        emprestimos_ativos = Emprestimo.objects.filter(livro=livro, devolvido=False).select_related('membro')
        reservas_ativas = Reserva.objects.filter(livro=livro, status=Reserva.Status.ATIVA).select_related('membro').order_by('data_reserva')
        disponiveis = max(livro.exemplares - emprestimos_ativos.count(), 0)
        return render(request, 'livro_detalhe.html', {
            'livro': livro, 
            'emprestimos': emprestimos_ativos,
            'reservas': reservas_ativas,
            'disponiveis': disponiveis
        })

class DevolverLivroView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def post(self, request, pk):
        emprestimo = get_object_or_404(Emprestimo, pk=pk)
        emprestimo.devolvido = True
        emprestimo.save()
        messages.success(request, f"O livro '{emprestimo.livro.titulo}' foi marcado como devolvido com sucesso!")
        referer = request.META.get('HTTP_REFERER', '')
        if 'emprestimos' in referer:
            return redirect('emprestimos')
        return redirect('dashboard')

class AlternarStatusMembroView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def post(self, request, pk):
        membro = get_object_or_404(Membro, pk=pk)
        membro.ativo = not membro.ativo
        membro.save()
        status = "ativado" if membro.ativo else "desativado"
        messages.success(request, f"O membro {membro.nome} foi {status} com sucesso!")
        return redirect('membros')

class DashboardTemplateView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return redirect('portal-membro')
        return redirect('portal-login')

    def get(self, request):
        hoje = date.today()
        semana_atras = hoje - timedelta(days=7)

        total_livros = Livro.objects.count()
        livros_semana = Livro.objects.filter(data_cadastro__date__gte=semana_atras).count()

        membros_ativos = Membro.objects.filter(ativo=True).count()
        membros_mes = Membro.objects.filter(
            data_cadastro__month=hoje.month, data_cadastro__year=hoje.year
        ).count()

        emprestimos_ativos = Emprestimo.objects.filter(devolvido=False).count()
        proximos_vencimento = Emprestimo.objects.filter(
            devolvido=False,
            data_devolucao__lte=hoje + timedelta(days=3),
            data_devolucao__gte=hoje,
        ).count()

        multas_abertas = Multa.objects.filter(pago=False).aggregate(
            total=Sum('valor'), count=Count('id')
        )
        atrasados_sem_multa = Emprestimo.objects.filter(
            devolvido=False, data_devolucao__lt=hoje
        ).exclude(multa__isnull=False)
        _vmd = Configuracao.get_instance().valor_multa_dia
        valor_dinamico = sum(
            _vmd * (hoje - e.data_devolucao).days
            for e in atrasados_sem_multa
        )
        total_multas = (multas_abertas['total'] or Decimal('0.00')) + valor_dinamico
        count_multas = (multas_abertas['count'] or 0) + atrasados_sem_multa.count()

        ultimos_livros = Livro.objects.all().order_by('-data_cadastro')[:3]
        emprestimos_recentes = (
            Emprestimo.objects
            .select_related('membro', 'livro')
            .filter(devolvido=False)
            .order_by('data_devolucao')[:5]
        )
        reservas_ativas = Reserva.objects.filter(status=Reserva.Status.ATIVA).select_related('membro', 'livro').order_by('-data_reserva')[:5]
        reservas_count = Reserva.objects.filter(status=Reserva.Status.ATIVA).count()

        context = {
            'total_livros': total_livros,
            'livros_novos_semana': livros_semana,
            'membros_ativos': membros_ativos,
            'membros_novos_mes': membros_mes,
            'emprestimos_ativos': emprestimos_ativos,
            'proximos_vencimento': proximos_vencimento,
            'multas_valor_total': total_multas,
            'multas_count': count_multas,
            'ultimos_livros': ultimos_livros,
            'emprestimos_recentes': emprestimos_recentes,
            'reservas_ativas': reservas_ativas,
            'reservas_count': reservas_count,
        }
        return render(request, 'dashboard.html', context)

class FeedTemplateView(View):
    def get(self, request):
        livros = Livro.objects.select_related('editora').all().order_by('-data_cadastro')
        return render(request, 'feed.html', {'livros': livros})

class RankingTemplateView(View):
    def get(self, request):
        hoje = date.today()
        desde = hoje - timedelta(days=7)
        ranking = (
            Livro.objects
            .filter(emprestimos__data_emprestimo__gte=desde)
            .annotate(total_emprestimos=Count('emprestimos'))
            .order_by('-total_emprestimos')[:10]
        )
        ranking_reservas = (
            Livro.objects
            .filter(reservas__status=Reserva.Status.ATIVA)
            .annotate(total_reservas=Count('reservas'))
            .order_by('-total_reservas')[:10]
        )
        return render(request, 'ranking.html', {'ranking': ranking, 'ranking_reservas': ranking_reservas})

class LivrosTemplateView(View):
    def get(self, request):
        livros = Livro.objects.select_related('editora').annotate(
            emprestimos_ativos_count=Count('emprestimos', filter=Q(emprestimos__devolvido=False))
        ).all()
        return render(request, 'livros.html', {'livros': livros})

class EditorasTemplateView(View):
    def get(self, request):
        editoras = Editora.objects.all()
        form = EditoraForm()
        return render(request, 'editoras.html', {'editoras': editoras, 'form': form})

    def post(self, request):
        form = EditoraForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('editoras')
        editoras = Editora.objects.all()
        return render(request, 'editoras.html', {'editoras': editoras, 'form': form})

class MembrosTemplateView(View):
    def get(self, request):
        membros = Membro.objects.all()
        return render(request, 'membros.html', {'membros': membros})

class MembroDetalheTemplateView(View):
    def get(self, request, pk):
        membro = get_object_or_404(Membro, pk=pk)
        emprestimos = Emprestimo.objects.filter(membro=membro).select_related('livro').order_by('-data_emprestimo')
        reservas = Reserva.objects.filter(membro=membro).select_related('livro').order_by('-data_reserva')
        return render(request, 'membro_detalhe.html', {'membro': membro, 'emprestimos': emprestimos, 'reservas': reservas})

class ReservasTemplateView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def get(self, request):
        reservas = (
            Reserva.objects
            .filter(status=Reserva.Status.ATIVA)
            .select_related('membro', 'livro')
            .order_by('data_reserva')
        )
        # Para cada reserva, calcula exemplares disponíveis
        reservas_info = []
        for r in reservas:
            emprestimos_ativos = Emprestimo.objects.filter(livro=r.livro, devolvido=False).count()
            disponivel = max(r.livro.exemplares - emprestimos_ativos, 0) > 0
            reservas_info.append({'reserva': r, 'disponivel': disponivel})
        return render(request, 'reservas.html', {'reservas_info': reservas_info, 'hoje': date.today().isoformat()})


class AprovarReservaView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def post(self, request, pk):
        reserva = get_object_or_404(Reserva, pk=pk, status=Reserva.Status.ATIVA)
        data_devolucao_str = request.POST.get('data_devolucao')
        if not data_devolucao_str:
            messages.error(request, 'Informe a data de devolução.')
            return redirect('reservas')

        from datetime import datetime
        try:
            data_devolucao = datetime.strptime(data_devolucao_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Data inválida.')
            return redirect('reservas')

        if data_devolucao <= date.today():
            messages.error(request, 'A data de devolução deve ser futura.')
            return redirect('reservas')

        emprestimos_ativos = Emprestimo.objects.filter(livro=reserva.livro, devolvido=False).count()
        if emprestimos_ativos >= reserva.livro.exemplares:
            messages.error(request, f'Não há exemplares disponíveis de "{reserva.livro.titulo}" no momento.')
            return redirect('reservas')

        Emprestimo.objects.create(
            membro=reserva.membro,
            livro=reserva.livro,
            data_devolucao=data_devolucao,
        )
        reserva.status = Reserva.Status.ATENDIDA
        reserva.save()
        messages.success(request, f'Reserva de "{reserva.livro.titulo}" para {reserva.membro.nome} aprovada! Empréstimo registrado.')
        return redirect('reservas')


class CancelarReservaAdminView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def post(self, request, pk):
        reserva = get_object_or_404(Reserva, pk=pk, status=Reserva.Status.ATIVA)
        reserva.status = Reserva.Status.CANCELADA
        reserva.save()
        messages.success(request, f'Reserva de "{reserva.livro.titulo}" cancelada.')
        return redirect('reservas')


class EmprestimoCreateTemplateView(View):
    def get(self, request):
        form = EmprestimoForm()
        return render(request, 'emprestimo_form.html', {'form': form, 'titulo': 'Novo Empréstimo'})

    def post(self, request):
        form = EmprestimoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
        return render(request, 'emprestimo_form.html', {'form': form, 'titulo': 'Novo Empréstimo'})

class MultaTemplateView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def get(self, request):
        config = Configuracao.get_instance()
        emprestimos_atrasados = Emprestimo.objects.filter(devolvido=False, data_devolucao__lt=date.today()).select_related('membro', 'livro')
        return render(request, 'multa.html', {'atrasados': emprestimos_atrasados, 'valor_dia': config.valor_multa_dia})

    def post(self, request):
        config = Configuracao.get_instance()
        try:
            novo_valor = Decimal(request.POST.get('valor_dia', '1.50'))
            if novo_valor <= 0:
                raise ValueError
            config.valor_multa_dia = novo_valor
            config.save()
            messages.success(request, f'Valor da multa atualizado para R$ {config.valor_multa_dia}/dia.')
        except (ValueError, Exception):
            messages.error(request, 'Valor inválido. Insira um número positivo.')
        return redirect('multa')

class LivroCreateTemplateView(View):
    def get(self, request):
        form = LivroForm()
        return render(request, 'livro_form.html', {'form': form, 'titulo': 'Cadastrar Livro'})

    def post(self, request):
        form = LivroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('livros')
        return render(request, 'livro_form.html', {'form': form, 'titulo': 'Cadastrar Livro'})

class MembroCreateTemplateView(View):
    def get(self, request):
        form = MembroForm()
        return render(request, 'membro_form.html', {'form': form, 'titulo': 'Cadastrar Membro'})

    def post(self, request):
        form = MembroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('membros')
        return render(request, 'membro_form.html', {'form': form, 'titulo': 'Cadastrar Membro'})

class DashboardView(APIView):

    def get(self, request):
        hoje = date.today()
        semana_atras = hoje - timedelta(days=7)

        total_livros = Livro.objects.count()
        livros_semana = Livro.objects.filter(data_cadastro__date__gte=semana_atras).count()

        membros_ativos = Membro.objects.filter(ativo=True).count()
        membros_mes = Membro.objects.filter(
            data_cadastro__month=hoje.month, data_cadastro__year=hoje.year
        ).count()

        emprestimos_ativos = Emprestimo.objects.filter(devolvido=False).count()
        proximos_vencimento = Emprestimo.objects.filter(
            devolvido=False,
            data_devolucao__lte=hoje + timedelta(days=3),
            data_devolucao__gte=hoje,
        ).count()

        multas_abertas = Multa.objects.filter(pago=False).aggregate(
            total=Sum('valor'), count=Count('id')
        )
        atrasados_sem_multa = Emprestimo.objects.filter(
            devolvido=False, data_devolucao__lt=hoje
        ).exclude(multa__isnull=False)
        _vmd = Configuracao.get_instance().valor_multa_dia
        valor_dinamico = sum(
            _vmd * (hoje - e.data_devolucao).days
            for e in atrasados_sem_multa
        )
        total_multas = (multas_abertas['total'] or Decimal('0.00')) + valor_dinamico
        count_multas = (multas_abertas['count'] or 0) + atrasados_sem_multa.count()

        return Response({
            'total_livros': total_livros,
            'livros_novos_semana': livros_semana,
            'membros_ativos': membros_ativos,
            'membros_novos_mes': membros_mes,
            'emprestimos_ativos': emprestimos_ativos,
            'proximos_vencimento': proximos_vencimento,
            'multas_valor_total': total_multas,
            'multas_count': count_multas,
        })


class NovosLivrosView(APIView):

    def get(self, request):
        limit = int(request.query_params.get('limit', 10))
        livros = Livro.objects.select_related('editora').order_by('-data_cadastro')[:limit]
        data = [
            {
                'id': l.id,
                'titulo': l.titulo,
                'autor': l.autor,
                'editora': l.editora.nome if l.editora else None,
                'ano_publicacao': l.ano_publicacao,
                'data_cadastro': l.data_cadastro,
            }
            for l in livros
        ]
        return Response(data)


class RankingView(APIView):

    def get(self, request):
        periodo = request.query_params.get('periodo', 'semana')
        hoje = date.today()

        if periodo == 'mes':
            desde = hoje - timedelta(days=30)
        else:
            desde = hoje - timedelta(days=7)

        ranking = (
            Livro.objects
            .filter(emprestimos__data_emprestimo__gte=desde)
            .annotate(total_emprestimos=Count('emprestimos'))
            .order_by('-total_emprestimos')[:10]
        )

        data = [
            {
                'posicao': i + 1,
                'id': livro.id,
                'titulo': livro.titulo,
                'autor': livro.autor,
                'total_emprestimos': livro.total_emprestimos,
            }
            for i, livro in enumerate(ranking)
        ]
        return Response({'periodo': periodo, 'ranking': data})


class CalculoMultaView(APIView):

    @property
    def VALOR_DIARIO(self):
        return Configuracao.get_instance().valor_multa_dia

    def get(self, request):
        emprestimo_id = request.query_params.get('emprestimo_id')
        if not emprestimo_id:
            return Response({'erro': 'Informe emprestimo_id'}, status=400)

        try:
            emp = Emprestimo.objects.select_related('membro', 'livro').get(pk=emprestimo_id)
        except Emprestimo.DoesNotExist:
            return Response({'erro': 'Empréstimo não encontrado'}, status=404)

        dias_atraso = max((date.today() - emp.data_devolucao).days, 0)
        valor = self.VALOR_DIARIO * dias_atraso

        return Response({
            'emprestimo_id': emp.id,
            'membro': emp.membro.nome,
            'livro': emp.livro.titulo,
            'data_devolucao': emp.data_devolucao,
            'dias_atraso': dias_atraso,
            'valor_diario': self.VALOR_DIARIO,
            'valor_total': valor,
        })

    def post(self, request):
        emprestimo_id = request.data.get('emprestimo_id')
        if not emprestimo_id:
            return Response({'erro': 'Informe emprestimo_id'}, status=400)

        try:
            emp = Emprestimo.objects.get(pk=emprestimo_id)
        except Emprestimo.DoesNotExist:
            return Response({'erro': 'Empréstimo não encontrado'}, status=404)

        if hasattr(emp, 'multa'):
            return Response({'erro': 'Multa já existe para este empréstimo'}, status=400)

        dias_atraso = max((date.today() - emp.data_devolucao).days, 0)
        if dias_atraso == 0:
            return Response({'erro': 'Empréstimo não está atrasado'}, status=400)

        valor = self.VALOR_DIARIO * dias_atraso
        multa = Multa.objects.create(emprestimo=emp, valor=valor)
        emp.status = Emprestimo.Status.ATRASADO
        emp.save()

        return Response({
            'id': multa.id,
            'valor': multa.valor,
            'dias_atraso': dias_atraso,
            'membro': emp.membro.nome,
        }, status=201)


class EmprestimosAtrasadosView(APIView):

    def get(self, request):
        hoje = date.today()
        atrasados = (
            Emprestimo.objects
            .filter(devolvido=False, data_devolucao__lt=hoje)
            .select_related('membro', 'livro')
            .order_by('data_devolucao')
        )

        data = [
            {
                'id': e.id,
                'membro': e.membro.nome,
                'membro_iniciais': e.membro.iniciais,
                'livro': e.livro.titulo,
                'data_devolucao': e.data_devolucao,
                'dias_atraso': (hoje - e.data_devolucao).days,
                'tem_multa': hasattr(e, 'multa'),
            }
            for e in atrasados
        ]
        return Response(data)


class EstatisticasMembroView(APIView):

    def get(self, request, pk):
        try:
            membro = Membro.objects.get(pk=pk)
        except Membro.DoesNotExist:
            return Response({'erro': 'Membro não encontrado'}, status=404)

        emprestimos = Emprestimo.objects.filter(membro=membro)
        multas = Multa.objects.filter(emprestimo__membro=membro)

        return Response({
            'id': membro.id,
            'nome': membro.nome,
            'iniciais': membro.iniciais,
            'ativo': membro.ativo,
            'total_emprestimos': emprestimos.count(),
            'emprestimos_ativos': emprestimos.filter(devolvido=False).count(),
            'emprestimos_atrasados': emprestimos.filter(
                devolvido=False, data_devolucao__lt=date.today()
            ).count(),
            'multas_pendentes': multas.filter(pago=False).aggregate(
                total=Sum('valor'), count=Count('id')
            ),
        }) 


