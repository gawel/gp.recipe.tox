# -*- coding: utf-8 -*-
"""Recipe tox"""
import subprocess
from os.path import join
import sys
import os


class Recipe(object):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options

    def install(self):
        """Installer"""
        options = self.options

        path = [p for p in sys.path if 'parts' not in p]
        del sys.modules['site']
        sys.path[:] = path
        env = os.environ.copy()
        env['PYTHONPATH'] = ':'.join(path)

        key = 'tox-install-dir'
        if key in self.buildout['buildout']:
            install_dir = self.buildout['buildout'][key]
        elif key in self.options:
            install_dir = self.options[key]
        else:
            install_dir = join(self.buildout['buildout']['parts-directory'],
                               self.name)

        bin_bir = join(install_dir, 'bin')

        tox = join(bin_bir, 'tox')
        if not os.path.isfile(tox):
            if sys.version_info[:2] >= (3,4):
                import venv
                venv.create(install_dir, with_pip=True)
                del env['PYTHONPATH']
                subprocess.call([join(bin_bir, 'pip'), 'install', 'tox'], env=env)
            else:
                import virtualenv
                subprocess.call([sys.executable, virtualenv.__file__[:-1],
                                '-q', '--distribute', install_dir], env=env)
                del env['PYTHONPATH']
                subprocess.call([join(bin_bir, 'easy_install'), 'tox'],
                                env=env)

        from zc.recipe.egg import Scripts
        options['eggs'] = 'virtualenv'
        options['scripts'] = 'tox'
        options['entry-points'] = 'tox=os:execve'
        options['arguments'] = (
                '%(tox)r, [%(tox)r] + sys.argv[1:], os.environ'
              ) % dict(tox=tox)
        options['initialization'] = '\n'.join([
                'import os',
                "os.environ['PYTHONPATH'] = ''",
            ])
        script = Scripts(self.buildout, self.name, self.options)
        script.install()
        return tuple()

    def update(self):
        """Updater"""
        pass
