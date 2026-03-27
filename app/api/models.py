from django.db import models

class Livro(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, unique=True)
    paginas = models.PositiveIntegerField()
    ano_publicacao = models.PositiveIntegerField()

    def __str__(self):
        return self.titulo

class Estante(models.Model):
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    livros = models.ManyToManyField(Livro, related_name='estantes', blank=True)

    def __str__(self):
        return self.nome
