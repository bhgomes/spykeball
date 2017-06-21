"""Spykeball Setup."""

from setuptools import setup, find_packages

from spykeball.core.io import findfile

setup(
    name='spykeball',

    version=findfile('VERSION', fail='0.0.0', strip=True),

    description='Spikeball Statistics Engine',
    long_description=findfile('README.rst'),

    keywords='statistics sports',

    license='MIT',

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Topic :: Games/Entertainment :: Simulation',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    author='Brandon Gomes',
    author_email='bhgomes.github@gmail.com',

    url='https://github.com/bhgomes/spykeball',
    download_url='https://github.com/bhgomes/spykeball/archive/master.zip',

    packages=find_packages(exclude=['docs', 'tests', 'tests.*']),

    install_requires=findfile('requirements.txt', fail=[]),
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],

    entry_points={
        'console_scripts': [
            'spykeball=spykeball.cli:main',
        ],
    }
)
