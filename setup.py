import os
import io
from setuptools import find_packages, setup, Command

# Meta
NAME = 'TrelloClone'
DESCRIPTION = 'Trello Clone API\'s using DRF'
URL = 'https://github.com/jayvasantjv/trelloclone'
REQUIRES_PYTHON = '>=3.6.0'


REQUIRED = [
    'Django',
    'djangorestframework',
    'docutils',
    'gunicorn',
    'django-heroku',
    'whitenoise',
    'dj-database-url',
    'django-cors-headers',
    'coreapi'
]


here = os.path.abspath(os.path.dirname(__file__))

try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION


setup(
    name=NAME,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires=REQUIRES_PYTHON,
    url=URL,
    # packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    install_requires=REQUIRED,
    include_package_data=True,
    license='MIT',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    # $ setup.py publish support.
)
