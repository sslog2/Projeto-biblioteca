# biblioteca.spec — configuração do PyInstaller para o servidor Django
# Gerado para o projeto Biblioteca
# Uso: pyinstaller biblioteca.spec --clean

from PyInstaller.utils.hooks import copy_metadata, collect_submodules, collect_data_files

block_cipher = None

# Coleta metadados de pacotes que usam importlib.metadata.version()
pkg_metadata = (
    copy_metadata('drf_yasg') +
    copy_metadata('djangorestframework') +
    copy_metadata('django') +
    copy_metadata('packaging')
)

# Coleta todos os submódulos automaticamente
django_hidden = collect_submodules('django')
drf_hidden = collect_submodules('rest_framework')
drf_yasg_hidden = collect_submodules('drf_yasg')

# Coleta arquivos de dados de pacotes que precisam de templates/statics
coreschema_datas = collect_data_files('coreschema')
drf_yasg_datas = collect_data_files('drf_yasg')
django_datas = collect_data_files('django')  # templates internos (403_csrf.html, technical_500.html, etc.)

a = Analysis(
    ['server.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        # Package metadata for importlib.metadata consumers
        *pkg_metadata,
        # Template/data files from third-party packages
        *coreschema_datas,
        *drf_yasg_datas,
        *django_datas,
        # Templates HTML
        ('templates', 'templates'),
        # Arquivos estáticos (CSS, JS)
        ('static', 'static'),
        # Pacote da aplicação
        ('app', 'app'),
        # Configurações do projeto
        ('project', 'project'),
        # Banco de dados inicial (copiado para AppData na primeira execução)
        ('db.sqlite3', '.'),
        # Arquivo .env se existir (ignorado silenciosamente se ausente)
    ],
    hiddenimports=[
        *django_hidden,
        *drf_hidden,
        *drf_yasg_hidden,
        # Aplicações locais
        'app',
        'app.api',
        'app.api.models',
        'app.api.views',
        'app.api.serializers',
        'app.api.admin',
        'app.api.urls',
        'app.api.apps',
        'app.api.forms',
        'app.utils',
        'app.utils.views',
        'app.utils.urls',
        'app.utils.apps',
        'app.utils.models',
        'app.utils.serializers',
        # Configurações
        'project.settings',
        'project.settings_exe',
        'project.urls',
        'project.wsgi',
        'project.asgi',
        # Dependências Python
        'decouple',
        'sqlparse',
        'pytz',
        'asgiref',
        'asgiref.sync',
        'yaml',
        'simplejson',
        'packaging',
        'inflection',
        'uritemplate',
        'coreschema',
        'coreapi',
        'openapi_codec',
        'itypes',
        # SQLite
        '_sqlite3',
    ],
    hookspath=['hooks'],
    hooksconfig={},
    runtime_hooks=[],
    # Exclui PostgreSQL — não é necessário no executável SQLite
    excludes=['psycopg2', 'psycopg2_binary'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='django_server',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,          # console=True para ver logs; mude para False em produção
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='django_server',
)
