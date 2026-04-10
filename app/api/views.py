from rest_framework import generics
from .models import Livro, Estante, Editora, Membro, Emprestimo, Multa
from .serializers import (
    LivroSerializer, EstanteSerializer, EditoraSerializer,
    MembroSerializer, EmprestimoSerializer, MultaSerializer,
)

class LivroListView(generics.ListAPIView):
    queryset = Livro.objects.all()
    serializer_class = LivroSerializer


class LivroDetailView(generics.RetrieveAPIView):
    queryset = Livro.objects.all()
    serializer_class = LivroSerializer


class LivroCreateView(generics.CreateAPIView):
    queryset = Livro.objects.all()
    serializer_class = LivroSerializer


class LivroUpdateView(generics.UpdateAPIView):
    queryset = Livro.objects.all()
    serializer_class = LivroSerializer


class LivroDeleteView(generics.DestroyAPIView):
    queryset = Livro.objects.all()
    serializer_class = LivroSerializer

#Estante Views

class EstanteListView(generics.ListAPIView):
    queryset = Estante.objects.all()
    serializer_class = EstanteSerializer


class EstanteDetailView(generics.RetrieveAPIView):
    queryset = Estante.objects.all()
    serializer_class = EstanteSerializer


class EstanteCreateView(generics.CreateAPIView):
    queryset = Estante.objects.all()
    serializer_class = EstanteSerializer


class EstanteUpdateView(generics.UpdateAPIView):
    queryset = Estante.objects.all()
    serializer_class = EstanteSerializer


class EstanteDeleteView(generics.DestroyAPIView):
    queryset = Estante.objects.all()
    serializer_class = EstanteSerializer


# Editora Views

class EditoraListView(generics.ListAPIView):
    queryset = Editora.objects.all()
    serializer_class = EditoraSerializer


class EditoraDetailView(generics.RetrieveAPIView):
    queryset = Editora.objects.all()
    serializer_class = EditoraSerializer


class EditoraCreateView(generics.CreateAPIView):
    queryset = Editora.objects.all()
    serializer_class = EditoraSerializer


class EditoraUpdateView(generics.UpdateAPIView):
    queryset = Editora.objects.all()
    serializer_class = EditoraSerializer


class EditoraDeleteView(generics.DestroyAPIView):
    queryset = Editora.objects.all()
    serializer_class = EditoraSerializer


# Membro Views

class MembroListView(generics.ListAPIView):
    queryset = Membro.objects.all()
    serializer_class = MembroSerializer


class MembroDetailView(generics.RetrieveAPIView):
    queryset = Membro.objects.all()
    serializer_class = MembroSerializer


class MembroCreateView(generics.CreateAPIView):
    queryset = Membro.objects.all()
    serializer_class = MembroSerializer


class MembroUpdateView(generics.UpdateAPIView):
    queryset = Membro.objects.all()
    serializer_class = MembroSerializer


class MembroDeleteView(generics.DestroyAPIView):
    queryset = Membro.objects.all()
    serializer_class = MembroSerializer


# Emprestimo Views

class EmprestimoListView(generics.ListAPIView):
    queryset = Emprestimo.objects.all()
    serializer_class = EmprestimoSerializer


class EmprestimoDetailView(generics.RetrieveAPIView):
    queryset = Emprestimo.objects.all()
    serializer_class = EmprestimoSerializer


class EmprestimoCreateView(generics.CreateAPIView):
    queryset = Emprestimo.objects.all()
    serializer_class = EmprestimoSerializer


class EmprestimoUpdateView(generics.UpdateAPIView):
    queryset = Emprestimo.objects.all()
    serializer_class = EmprestimoSerializer


class EmprestimoDeleteView(generics.DestroyAPIView):
    queryset = Emprestimo.objects.all()
    serializer_class = EmprestimoSerializer


# Multa Views

class MultaListView(generics.ListAPIView):
    queryset = Multa.objects.all()
    serializer_class = MultaSerializer


class MultaDetailView(generics.RetrieveAPIView):
    queryset = Multa.objects.all()
    serializer_class = MultaSerializer


class MultaCreateView(generics.CreateAPIView):
    queryset = Multa.objects.all()
    serializer_class = MultaSerializer


class MultaUpdateView(generics.UpdateAPIView):
    queryset = Multa.objects.all()
    serializer_class = MultaSerializer


class MultaDeleteView(generics.DestroyAPIView):
    queryset = Multa.objects.all()
    serializer_class = MultaSerializer
