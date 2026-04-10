from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from app.api.models import Editora, Livro, Estante, Membro, Emprestimo, Multa


class Command(BaseCommand):
    help = 'Popula o banco com dados de demonstração'

    def handle(self, *args, **options):
        self.stdout.write('Limpando dados antigos...')
        Multa.objects.all().delete()
        Emprestimo.objects.all().delete()
        Membro.objects.all().delete()
        Livro.objects.all().delete()
        Estante.objects.all().delete()
        Editora.objects.all().delete()

        # ── Editoras ──
        self.stdout.write('Criando editoras...')
        editoras = {
            'companhia': Editora.objects.create(
                nome='Companhia das Letras',
                site='https://www.companhiadasletras.com.br',
                email='contato@companhiadasletras.com.br',
            ),
            'record': Editora.objects.create(
                nome='Editora Record',
                site='https://www.record.com.br',
                email='contato@record.com.br',
            ),
            'intrinseca': Editora.objects.create(
                nome='Intrínseca',
                site='https://www.intrinseca.com.br',
                email='contato@intrinseca.com.br',
            ),
            'rocco': Editora.objects.create(
                nome='Editora Rocco',
                site='https://www.rocco.com.br',
                email='contato@rocco.com.br',
            ),
            'cosacnaify': Editora.objects.create(
                nome='Cosac Naify',
                site='https://www.cosacnaify.com.br',
                email='contato@cosacnaify.com.br',
            ),
        }

        # ── Livros ──
        self.stdout.write('Criando livros...')
        livros_data = [
            ('Dom Casmurro', 'Machado de Assis', '9788535910681', 256, 1899, 'companhia'),
            ('Cem Anos de Solidão', 'Gabriel García Márquez', '9788501012173', 448, 1967, 'record'),
            ('1984', 'George Orwell', '9788535914849', 416, 1949, 'companhia'),
            ('A Hora da Estrela', 'Clarice Lispector', '9788532511454', 96, 1977, 'rocco'),
            ('Crime e Castigo', 'Fiódor Dostoiévski', '9788573264845', 576, 1866, 'cosacnaify'),
            ('Madame Bovary', 'Gustave Flaubert', '9788535928280', 400, 1857, 'companhia'),
            ('O Grande Gatsby', 'F. Scott Fitzgerald', '9788525056tried', 192, 1925, 'record'),
            ('O Pequeno Príncipe', 'Antoine de Saint-Exupéry', '9788595081512', 96, 1943, 'intrinseca'),
            ('Memórias Póstumas de Brás Cubas', 'Machado de Assis', '9788535911671', 208, 1881, 'companhia'),
            ('Grande Sertão: Veredas', 'Guimarães Rosa', '9788520923115', 608, 1956, 'companhia'),
            ('Vidas Secas', 'Graciliano Ramos', '9788501063230', 176, 1938, 'record'),
            ('O Cortiço', 'Aluísio Azevedo', '9788572326889', 224, 1890, 'cosacnaify'),
        ]
        livros = {}
        for titulo, autor, isbn, paginas, ano, ed_key in livros_data:
            livros[titulo] = Livro.objects.create(
                titulo=titulo,
                autor=autor,
                isbn=isbn,
                paginas=paginas,
                ano_publicacao=ano,
                editora=editoras[ed_key],
            )

        # ── Estantes ──
        self.stdout.write('Criando estantes...')
        estante_lit_br = Estante.objects.create(
            nome='Literatura Brasileira',
            descricao='Clássicos da literatura nacional',
        )
        estante_lit_br.livros.add(
            livros['Dom Casmurro'],
            livros['A Hora da Estrela'],
            livros['Memórias Póstumas de Brás Cubas'],
            livros['Grande Sertão: Veredas'],
            livros['Vidas Secas'],
            livros['O Cortiço'],
        )

        estante_lit_int = Estante.objects.create(
            nome='Literatura Internacional',
            descricao='Obras estrangeiras traduzidas',
        )
        estante_lit_int.livros.add(
            livros['Cem Anos de Solidão'],
            livros['1984'],
            livros['Crime e Castigo'],
            livros['Madame Bovary'],
            livros['O Grande Gatsby'],
            livros['O Pequeno Príncipe'],
        )

        # ── Membros ──
        self.stdout.write('Criando membros...')
        membros = {
            'ana': Membro.objects.create(
                nome='Ana Martins', email='ana.martins@email.com', telefone='(11) 98765-4321',
            ),
            'joao': Membro.objects.create(
                nome='João Ribeiro', email='joao.ribeiro@email.com', telefone='(21) 99876-5432',
            ),
            'luiza': Membro.objects.create(
                nome='Luiza Costa', email='luiza.costa@email.com', telefone='(31) 97654-3210',
            ),
            'carlos': Membro.objects.create(
                nome='Carlos Oliveira', email='carlos.oliveira@email.com', telefone='(41) 96543-2109',
            ),
            'maria': Membro.objects.create(
                nome='Maria Silva', email='maria.silva@email.com', telefone='(51) 95432-1098',
            ),
            'pedro': Membro.objects.create(
                nome='Pedro Santos', email='pedro.santos@email.com', telefone='(61) 94321-0987',
            ),
            'fernanda': Membro.objects.create(
                nome='Fernanda Lima', email='fernanda.lima@email.com', telefone='(71) 93210-9876',
            ),
            'rafael': Membro.objects.create(
                nome='Rafael Almeida', email='rafael.almeida@email.com', telefone='(81) 92109-8765',
            ),
        }

        # ── Empréstimos ──
        self.stdout.write('Criando empréstimos...')
        hoje = date.today()

        emprestimos = [
            # Em dia
            Emprestimo.objects.create(
                membro=membros['ana'],
                livro=livros['Dom Casmurro'],
                data_devolucao=hoje + timedelta(days=10),
                status=Emprestimo.Status.EM_DIA,
            ),
            Emprestimo.objects.create(
                membro=membros['carlos'],
                livro=livros['O Pequeno Príncipe'],
                data_devolucao=hoje + timedelta(days=14),
                status=Emprestimo.Status.EM_DIA,
            ),
            Emprestimo.objects.create(
                membro=membros['maria'],
                livro=livros['Vidas Secas'],
                data_devolucao=hoje + timedelta(days=7),
                status=Emprestimo.Status.EM_DIA,
            ),
            # Vencendo
            Emprestimo.objects.create(
                membro=membros['joao'],
                livro=livros['1984'],
                data_devolucao=hoje + timedelta(days=2),
                status=Emprestimo.Status.VENCENDO,
            ),
            Emprestimo.objects.create(
                membro=membros['pedro'],
                livro=livros['Grande Sertão: Veredas'],
                data_devolucao=hoje + timedelta(days=1),
                status=Emprestimo.Status.VENCENDO,
            ),
            # Atrasados
            Emprestimo.objects.create(
                membro=membros['luiza'],
                livro=livros['A Hora da Estrela'],
                data_devolucao=hoje - timedelta(days=15),
                status=Emprestimo.Status.ATRASADO,
            ),
            Emprestimo.objects.create(
                membro=membros['fernanda'],
                livro=livros['Madame Bovary'],
                data_devolucao=hoje - timedelta(days=8),
                status=Emprestimo.Status.ATRASADO,
            ),
            Emprestimo.objects.create(
                membro=membros['rafael'],
                livro=livros['Crime e Castigo'],
                data_devolucao=hoje - timedelta(days=5),
                status=Emprestimo.Status.ATRASADO,
            ),
        ]

        # ── Multas (para empréstimos atrasados) ──
        self.stdout.write('Criando multas...')
        Multa.objects.create(emprestimo=emprestimos[5], valor=Decimal('22.50'))
        Multa.objects.create(emprestimo=emprestimos[6], valor=Decimal('12.00'))
        Multa.objects.create(emprestimo=emprestimos[7], valor=Decimal('7.50'))

        self.stdout.write(self.style.SUCCESS(
            f'Banco populado com sucesso!\n'
            f'  {Editora.objects.count()} editoras\n'
            f'  {Livro.objects.count()} livros\n'
            f'  {Estante.objects.count()} estantes\n'
            f'  {Membro.objects.count()} membros\n'
            f'  {Emprestimo.objects.count()} empréstimos\n'
            f'  {Multa.objects.count()} multas'
        ))
