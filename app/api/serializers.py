from rest_framework import serializers
from .models import Livro, Estante, Editora, Membro, Emprestimo, Multa


class EditoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Editora
        fields = '__all__'


class LivroSerializer(serializers.ModelSerializer):
    editora_nome = serializers.CharField(source='editora.nome', read_only=True)

    class Meta:
        model = Livro
        fields = '__all__'


class EstanteSerializer(serializers.ModelSerializer):
    livros_detalhes = LivroSerializer(source='livros', many=True, read_only=True)
    livros = serializers.PrimaryKeyRelatedField(
        queryset=Livro.objects.all(), many=True, required=False
    )

    class Meta:
        model = Estante
        fields = '__all__'


class MembroSerializer(serializers.ModelSerializer):
    iniciais = serializers.ReadOnlyField()

    class Meta:
        model = Membro
        fields = '__all__'


class EmprestimoSerializer(serializers.ModelSerializer):
    membro_nome = serializers.CharField(source='membro.nome', read_only=True)
    membro_iniciais = serializers.CharField(source='membro.iniciais', read_only=True)
    livro_titulo = serializers.CharField(source='livro.titulo', read_only=True)

    class Meta:
        model = Emprestimo
        fields = '__all__'


class MultaSerializer(serializers.ModelSerializer):
    membro_nome = serializers.CharField(source='emprestimo.membro.nome', read_only=True)
    livro_titulo = serializers.CharField(source='emprestimo.livro.titulo', read_only=True)

    class Meta:
        model = Multa
        fields = '__all__'
