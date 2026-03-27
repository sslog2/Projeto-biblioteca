from rest_framework import serializers
from .models import Livro, Estante


class LivroSerializer(serializers.ModelSerializer):
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
