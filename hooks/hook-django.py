"""
Hook customizado para Django — substitui o hook interno do PyInstaller
que e incompativel com Python 3.14 (get_module_file_attribute retorna None).
"""
import os

hiddenimports = []
datas = []

try:
    import django
    django_dir = os.path.dirname(os.path.abspath(django.__file__))

    def _add(src, dest):
        if os.path.exists(src):
            datas.append((src, dest))

    _add(os.path.join(django_dir, 'conf', 'locale'),
         os.path.join('django', 'conf', 'locale'))
    _add(os.path.join(django_dir, 'contrib', 'admin', 'templates'),
         os.path.join('django', 'contrib', 'admin', 'templates'))
    _add(os.path.join(django_dir, 'contrib', 'admin', 'static'),
         os.path.join('django', 'contrib', 'admin', 'static'))
    _add(os.path.join(django_dir, 'contrib', 'auth', 'templates'),
         os.path.join('django', 'contrib', 'auth', 'templates'))
except ImportError:
    pass
