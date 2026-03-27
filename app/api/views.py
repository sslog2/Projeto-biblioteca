from rest_framework import generics
from .models import Livro, Estante
from .serializers import LivroSerializer, EstanteSerializer

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
