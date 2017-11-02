# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from setuptools import setup, find_packages

from boxberry import __version__


try:
    from pypandoc import convert
except ImportError:
    import io

    def convert(filename, fmt):
        with io.open(filename, encoding='utf-8') as fd:
            return fd.read()

setup(
    name='boxberry',
    version=__version__,
    packages=find_packages(),
    author='Aleksandr Alekseev',
    author_email='alekseevavx@gmail.com',
    description='Клиент для взаимодействия с API Boxberry',
    long_description=convert('README.md', 'rst'),
    url='https://github.com/AlekseevAV/boxberry',
    license='MIT',
    keywords=['boxberry'],
    install_requires=[
        'requests==2.18.4'
    ],
)
