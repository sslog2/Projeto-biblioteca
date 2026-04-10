from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Count, Sum, Q, F
from rest_framework.response import Response
from rest_framework.views import APIView

from app.api.models import Livro, Membro, Emprestimo, Multa


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

        return Response({
            'total_livros': total_livros,
            'livros_novos_semana': livros_semana,
            'membros_ativos': membros_ativos,
            'membros_novos_mes': membros_mes,
            'emprestimos_ativos': emprestimos_ativos,
            'proximos_vencimento': proximos_vencimento,
            'multas_valor_total': multas_abertas['total'] or Decimal('0.00'),
            'multas_count': multas_abertas['count'],
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

    VALOR_DIARIO = Decimal('1.50')

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


