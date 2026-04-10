from django.db import models
from django.utils import timezone


class Editora(models.Model):
    nome = models.CharField(max_length=200)
    site = models.URLField(blank=True)
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.nome


class Livro(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, unique=True)
    paginas = models.PositiveIntegerField()
    ano_publicacao = models.PositiveIntegerField()
    editora = models.ForeignKey(
        Editora, on_delete=models.SET_NULL, null=True, blank=True, related_name='livros'
    )
    data_cadastro = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.titulo


class Estante(models.Model):
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    livros = models.ManyToManyField(Livro, related_name='estantes', blank=True)

    def __str__(self):
        return self.nome


class Membro(models.Model):
    nome = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20, blank=True)
    ativo = models.BooleanField(default=True)
    data_cadastro = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.nome

    @property
    def iniciais(self):
        partes = self.nome.split()
        if len(partes) >= 2:
            return f"{partes[0][0]}{partes[-1][0]}".upper()
        return self.nome[:2].upper()


class Emprestimo(models.Model):
    class Status(models.TextChoices):
        EM_DIA = 'em_dia', 'Em dia'
        VENCENDO = 'vencendo', 'Vencendo'
        ATRASADO = 'atrasado', 'Atrasado'

    membro = models.ForeignKey(Membro, on_delete=models.CASCADE, related_name='emprestimos')
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE, related_name='emprestimos')
    data_emprestimo = models.DateField(auto_now_add=True)
    data_devolucao = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.EM_DIA)
    devolvido = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.membro.nome} — {self.livro.titulo}"


class Multa(models.Model):
    emprestimo = models.OneToOneField(
        Emprestimo, on_delete=models.CASCADE, related_name='multa'
    )
    valor = models.DecimalField(max_digits=8, decimal_places=2)
    pago = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"R$ {self.valor} — {self.emprestimo.membro.nome}"
