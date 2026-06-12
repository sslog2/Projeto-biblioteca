"""
server.py — ponto de entrada para o PyInstaller.

Quando empacotado, define os caminhos corretos e inicia o servidor Django
na porta 8000 sem reloader (necessário para modo bundle).
"""
import multiprocessing
import os
import shutil
import sys


def get_app_data_dir():
    """Retorna diretório gravável para dados do app (AppData no Windows)."""
    if sys.platform == 'win32':
        base = os.environ.get('APPDATA', os.path.expanduser('~'))
    else:
        base = os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))
    app_dir = os.path.join(base, 'Biblioteca')
    os.makedirs(app_dir, exist_ok=True)
    return app_dir


def setup_database(base_dir, app_dir):
    """Copia o banco inicial para o diretório de dados se ainda não existir."""
    db_target = os.path.join(app_dir, 'db.sqlite3')
    if not os.path.exists(db_target):
        db_source = os.path.join(base_dir, 'db.sqlite3')
        if os.path.exists(db_source):
            shutil.copy2(db_source, db_target)
    return db_target


def main():
    # Define base_dir: diretório do bundle (PyInstaller) ou do script
    if hasattr(sys, '_MEIPASS'):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    os.chdir(base_dir)
    sys.path.insert(0, base_dir)

    app_dir = get_app_data_dir()
    db_path = setup_database(base_dir, app_dir)

    # Passa o caminho do banco via variável de ambiente para o settings_exe.py
    os.environ['BIBLIOTECA_DB_PATH'] = db_path
    os.environ['BIBLIOTECA_BASE_DIR'] = base_dir
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings_exe')

    # Executa migrações silenciosamente na primeira execução
    import django
    django.setup()

    from django.core.management import call_command
    try:
        call_command('migrate', '--run-syncdb', verbosity=0)
    except Exception as exc:
        print(f'[server] Aviso ao executar migrate: {exc}')

    # Inicia o servidor
    from django.core.management import execute_from_command_line
    execute_from_command_line(['server.py', 'runserver', '127.0.0.1:8000', '--noreload'])


if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
