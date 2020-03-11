import re
from os.path import join, dirname

from setuptools import setup, find_packages


# reading package version (same way the sqlalchemy does)
with open(join(dirname(__file__), 'jaguar', '__init__.py')) as v_file:
    package_version = re.\
        compile(r".*__version__ = '(.*?)'", re.S).\
        match(v_file.read()).\
        group(1)


dependencies = [
    'restfulpy >= 2.7.2',
    'sqlalchemy_media >= 0.17.1',
    'asyncpg',

    # Messaging
    'aioredis',
    'aiohttp',
    'cchardet',
    'async_generator',
]


setup(
    name="jaguar",
    version=package_version,
    author="mkhfring",
    author_email="mkhajezade@carrene.com",
    description="Back-end for cucumber project",
    url='https://github.com/Carrene/jaguar.git',
    install_requires=dependencies,
    packages=find_packages(),
    test_suite="jaguar.tests",
    entry_points={
        'console_scripts': [
            'jaguar = jaguar:jaguar.cli_main'
        ]
    },
)

