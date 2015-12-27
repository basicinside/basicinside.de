#!/usr/bin/env python
from setuptools import setup, find_packages
setup(
    name='evernote-sync',
    author='Robin Kuck',
    author_email='robin@basicinside.de',
    version='0.0.2',
    url='https://github.com/basicinside/basicinside.de/tree/master/evernote-sync',
    description='Sync evernote notes to jekyll posts',
    long_description=open('README.md').read(),
    packages=find_packages('.'),
    install_requires=[
        'BeautifulSoup >= 3.2.1',
        'evernote >= 1.25.1',
    ],
    entry_points={
        'console_scripts': [
            'evernote-sync = sync:main',
        ],
    }
)
