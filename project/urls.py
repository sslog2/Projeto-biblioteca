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
    MultaTemplateView
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
    path('admin/', admin.site.urls),
    path('api/', include('app.api.urls')),
    path('api/utils/', include('app.utils.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('', DashboardTemplateView.as_view(), name='dashboard'),
    path('feed/', FeedTemplateView.as_view(), name='feed'),
    path('ranking/', RankingTemplateView.as_view(), name='ranking'),
    path('livros/', LivrosTemplateView.as_view(), name='livros'),
    path('editoras/', EditorasTemplateView.as_view(), name='editoras'),
    path('membros/', MembrosTemplateView.as_view(), name='membros'),
    path('multa/', MultaTemplateView.as_view(), name='multa'),
]