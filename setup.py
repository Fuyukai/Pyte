import os
from setuptools import setup, find_packages

rootpath = os.path.abspath(os.path.dirname(__file__))


def extract_version(module='pyte'):
    version = None
    fname = os.path.join(rootpath, module, '__init__.py')
    with open(fname) as f:
        for line in f:
            if line.startswith('__version__'):
                _, version = line.split('=')
                version = version.strip()[1:-1]  # Remove quotation characters.
                break
    return version


setup(
    name='pytec',
    version=extract_version(),
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    url='https://github.com/SunDwarf/Pyte',
    license='MIT',
    author='Isaac Dickinson',
    author_email='sun@veriny.tf',
    description='Pyte bytecode compiler',
    tests_require=['pytest>=2.9.1', 'coveralls', 'pytest-cov>=2.2.1', 'coveralls>=1.1'],
)
