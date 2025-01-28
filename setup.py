import os
import shutil
from setuptools import setup, find_packages
from setuptools.command.install import install

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        # Copy config files to ~/.config/cosmo
        config_path = os.path.expanduser('~/.config/cosmo')
        if not os.path.exists(config_path):
            os.makedirs(config_path)
        source_path = os.path.join(self.install_lib, 'cosmo', 'config_files')
        for item in os.listdir(source_path):
            s = os.path.join(source_path, item)
            d = os.path.join(config_path, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, False, None)
            else:
                shutil.copy2(s, d)

setup(
    name='cosmo',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'typer',
        'pandas',
        'rich',
        'toml',
        'selenium'
    ],
    entry_points={
        'console_scripts': [
            'cosmo=cosmo.main:app',
        ],
    },
    cmdclass={
        'install': PostInstallCommand,
    },
    package_data={
        'cosmo': ['config_files/*', 'config_files/data/*']
    }
)