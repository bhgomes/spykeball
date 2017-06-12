"""Spykeball Setup."""

from distutils.core import setup

setup(name='spykeball',
      version='0.0.1',
      description='Python Distribution Utilities',
      author='Brandon Gomes',
      author_email='bhgomes.github@gmail.com',
      url='https://github.com/bhgomes/spykeball',
      download_url='https://github.com/bhgomes/spykeball/archive/master.zip',
      packages=['spykeball', 'spykeball.core', 'spykeball.gui', 'spykeball'],
      )
