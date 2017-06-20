"""Spykeball Setup."""

import os

from setuptools import setup, find_packages

root = os.path.abspath(os.path.dirname(__file__))


def find(fp, fail='', strip=False, encoding='utf-8'):
    """Find file and returns contents."""
    try:
        with open(os.path.join(root, fp), encoding) as f:
            out = f.read().splitlines() if isinstance(fail, list) else f.read()
            return out.strip() if strip else out
    except Exception:
        return fail


setup(
    name='spykeball',

    version=find('VERSION', fail='0.0.0', strip=True),

    description='Spikeball Statistics Engine',
    long_description=find('README.rst'),

    keywords='statistics sports',

    license='MIT',

    classifiers=[

    ],

    author='Brandon Gomes',
    author_email='bhgomes.github@gmail.com',

    url='https://github.com/bhgomes/spykeball',
    download_url='https://github.com/bhgomes/spykeball/archive/master.zip',

    packages=find_packages(exclude=['docs', 'tests', 'tests.*']),

    install_requires=find('requirements.txt', fail=[]),

    # change to gui later
    entry_points={
        'console_scripts': [
            'spykeball=spykeball:main',
        ],
    }
)
