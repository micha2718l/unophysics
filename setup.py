#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.md') as history_file:
    history = history_file.read()

requirements = ['Click>=6.0', 'requests', 'sshtunnel', 'pymongo', 'sympy', 'jupyter', 'numpy', 'matplotlib', 'scipy', 'PyWavelets', 'pandas']

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="Michael Haas",
    author_email='mjhaas@uno.edu',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Tools for physics from UNO.",
    entry_points={
        'console_scripts': [
            'unophysics=unophysics.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description_content_type='text/markdown',
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='unophysics',
    name='unophysics',
    packages=find_packages(include=['unophysics']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/micha2718l/unophysics',
    version='0.4.7',
    zip_safe=False,
)
