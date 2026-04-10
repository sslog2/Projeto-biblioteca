from django.urls import path
from .views import (
    DashboardView,
    NovosLivrosView,
    RankingView,
    CalculoMultaView,
    EmprestimosAtrasadosView,
    EstatisticasMembroView,
)

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='utils-dashboard'),
    path('novos-livros/', NovosLivrosView.as_view(), name='utils-novos-livros'),
    path('ranking/', RankingView.as_view(), name='utils-ranking'),
    path('calculo-multa/', CalculoMultaView.as_view(), name='utils-calculo-multa'),
    path('atrasados/', EmprestimosAtrasadosView.as_view(), name='utils-atrasados'),
    path('membro/<int:pk>/stats/', EstatisticasMembroView.as_view(), name='utils-membro-stats'),
]