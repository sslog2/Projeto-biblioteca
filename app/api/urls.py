from django.urls import path
from .views import (
    LivroListView,
    LivroDetailView,
    LivroCreateView,
    LivroUpdateView,
    LivroDeleteView,
    EstanteListView,
    EstanteDetailView,
    EstanteCreateView,
    EstanteUpdateView,
    EstanteDeleteView,
)

urlpatterns = [
    # Livros
    path('livros/', LivroListView.as_view(), name='livro-list'),
    path('livros/criar/', LivroCreateView.as_view(), name='livro-create'),
    path('livros/<int:pk>/', LivroDetailView.as_view(), name='livro-detail'),
    path('livros/<int:pk>/atualizar/', LivroUpdateView.as_view(), name='livro-update'),
    path('livros/<int:pk>/deletar/', LivroDeleteView.as_view(), name='livro-delete'),
    # Estantes
    path('estantes/', EstanteListView.as_view(), name='estante-list'),
    path('estantes/criar/', EstanteCreateView.as_view(), name='estante-create'),
    path('estantes/<int:pk>/', EstanteDetailView.as_view(), name='estante-detail'),
    path('estantes/<int:pk>/atualizar/', EstanteUpdateView.as_view(), name='estante-update'),
    path('estantes/<int:pk>/deletar/', EstanteDeleteView.as_view(), name='estante-delete'),
]