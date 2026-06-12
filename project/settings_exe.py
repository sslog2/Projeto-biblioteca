"""
settings_exe.py — configurações para o modo executável (bundle PyInstaller).

Herda tudo de settings.py e sobrescreve apenas o necessário
para funcionar quando empacotado.
"""
import os
import sys
from pathlib import Path

# Importa as configurações base
from project.settings import *  # noqa: F401, F403

# ── Banco de dados ──────────────────────────────────────────────────────────
# Em modo bundle, usa o caminho injetado via variável de ambiente (AppData).
_db_path = os.environ.get('BIBLIOTECA_DB_PATH')
if _db_path:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': _db_path,
        }
    }

# ── BASE_DIR em modo bundle ─────────────────────────────────────────────────
_bundle_base = os.environ.get('BIBLIOTECA_BASE_DIR')
if _bundle_base:
    BASE_DIR = Path(_bundle_base)
    TEMPLATES[0]['DIRS'] = [BASE_DIR / 'templates']  # noqa: F405
    STATICFILES_DIRS = [BASE_DIR / 'static']  # arquivos estáticos copiados pelo PyInstaller
    STATIC_ROOT = BASE_DIR / 'staticfiles'

# ── Segurança mínima para desktop local ────────────────────────────────────
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
DEBUG = True  # necessário para servir estáticos sem collectstatic
