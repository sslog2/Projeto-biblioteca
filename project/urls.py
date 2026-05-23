"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from app.utils.views import (
    DashboardTemplateView,
    FeedTemplateView,
    RankingTemplateView,
    LivrosTemplateView,
    EditorasTemplateView,
    MembrosTemplateView,
    MembroDetalheTemplateView,
    MultaTemplateView,
    LivroCreateTemplateView,
    MembroCreateTemplateView,
    EmprestimoCreateTemplateView,
    EmprestimosTemplateView,
    PortalLoginView,
    PortalLogoutView,
    PortalCadastroView,
    PortalMembroView,
    RenovarEmprestimoView,
    ReservarLivroView,
    ExportarAtrasadosCSVView,
    DevolverLivroView,
    AlternarStatusMembroView,
    LivroDetailTemplateView,
    LivroUpdateTemplateView,
    ReservasTemplateView,
    AprovarReservaView,
    CancelarReservaAdminView,
)

schema_view = get_schema_view(
    openapi.Info(
        title="API de Livros",
        default_version='v1',
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Utilitários Admin (Deve vir antes do admin/ para evitar conflito de rotas)
    path('admin/exportar-csv/', ExportarAtrasadosCSVView.as_view(), name='exportar-csv'),
    path('admin/devolver/<int:pk>/', DevolverLivroView.as_view(), name='devolver-livro'),
    path('admin/membro/status/<int:pk>/', AlternarStatusMembroView.as_view(), name='membro-status'),

    path('admin/', admin.site.urls),
    path('api/', include('app.api.urls')),
    path('api/utils/', include('app.utils.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('', DashboardTemplateView.as_view(), name='dashboard'),
    path('feed/', FeedTemplateView.as_view(), name='feed'),
    path('ranking/', RankingTemplateView.as_view(), name='ranking'),
    path('livros/', LivrosTemplateView.as_view(), name='livros'),
    path('livros/novo/', LivroCreateTemplateView.as_view(), name='livro-create'),
    path('livros/<int:pk>/', LivroDetailTemplateView.as_view(), name='livro-detail'),
    path('livros/<int:pk>/editar/', LivroUpdateTemplateView.as_view(), name='livro-edit'),
    path('editoras/', EditorasTemplateView.as_view(), name='editoras'),
    path('membros/', MembrosTemplateView.as_view(), name='membros'),
    path('membros/<int:pk>/', MembroDetalheTemplateView.as_view(), name='membro-detail'),
    path('membros/novo/', MembroCreateTemplateView.as_view(), name='membro-create'),
    path('emprestimos/', EmprestimosTemplateView.as_view(), name='emprestimos'),
    path('emprestimos/novo/', EmprestimoCreateTemplateView.as_view(), name='emprestimo-create'),
    path('reservas/', ReservasTemplateView.as_view(), name='reservas'),
    path('reservas/aprovar/<int:pk>/', AprovarReservaView.as_view(), name='aprovar-reserva'),
    path('reservas/cancelar/<int:pk>/', CancelarReservaAdminView.as_view(), name='cancelar-reserva-admin'),
    path('multa/', MultaTemplateView.as_view(), name='multa'),
    
    # Portal do Membro (N2)
    path('portal/', PortalMembroView.as_view(), name='portal-membro'),
    path('portal/login/', PortalLoginView.as_view(), name='portal-login'),
    path('portal/logout/', PortalLogoutView.as_view(), name='portal-logout'),
    path('portal/cadastro/', PortalCadastroView.as_view(), name='portal-cadastro'),
    path('portal/renovar/<int:pk>/', RenovarEmprestimoView.as_view(), name='renovar-emprestimo'),
    path('portal/reservar/<int:pk>/', ReservarLivroView.as_view(), name='reservar-livro'),
]
