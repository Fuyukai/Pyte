import sys
from pathlib import Path

from setuptools import setup

if sys.implementation != "cpython":
    raise RuntimeError("This package only works on CPython.")

if sys.version_info[0:2] < (3, 3):
    raise RuntimeError("This package requires Python 3.3+.")

install_requires = []

if sys.version_info[0:2] < (3, 5):
    install_requires.append("typing")

setup(
    name="pytec",
    use_scm_version={
        "version_scheme": "guess-next-dev",
        "local_scheme": "dirty-tag"
    },
    packages=[
        "pyte",
        "pyte.ops"
    ],
    url="https://github.com/SunDwarf/asyncqlio",
    license="MIT",
    author="Laura Dickinson",
    author_email="l@veriny.tf",
    description="The Python bytecode utility.",
    long_description=Path(__file__).with_name("README.rst").read_text(encoding="utf-8"),
    setup_requires=[
        "setuptools_scm",
        "pytest-runner"
    ],
    install_requires=install_requires,
    tests_requires=[
        'pytest>=2.9.1',
        'coveralls',
        'pytest-cov>=2.2.1',
        'coveralls>=1.1'
    ],
    python_requires=">=3.3",
)
