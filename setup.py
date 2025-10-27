# -*- coding: utf-8 -*-
"""install mythril and deploy source-dist and wheel to pypi.python.org.

deps (requires up2date version):
    *) pip install --upgrade pip wheel setuptools twine
publish to pypi w/o having to convert Readme.md to RST:
    1) #> python setup.py sdist bdist_wheel
    2) #> twine upload dist/*   #<specify bdist_wheel version to upload>; #optional --repository <testpypi> or  --repository-url <testpypi-url>
"""

import io
import os
import sys

from setuptools import find_packages, setup
from setuptools.command.install import install as _install

# Package meta-data.
NAME = "mythril"
DESCRIPTION = "Security analysis tool for Ethereum smart contracts"
URL = "https://github.com/ConsenSys/mythril"
AUTHOR = "ConsenSys Dilligence"
AUTHOR_MAIL = None
REQUIRES_PYTHON = ">=3.7.0"
here = os.path.abspath(os.path.dirname(__file__))


# What packages are required for this module to be executed?
REQUIRED = [
    "blake2b-py>=0.2.0,<1",
    "coloredlogs>=10.0",
    "coincurve>=13.0.0",
    "cytoolz>=0.12.0",
    "asn1crypto>=0.22.0",
    "configparser>=3.5.0",
    "py_ecc>=5.0.0",
    "eth-abi>=5.1.0",
    "eth-hash>=0.3.1,<0.8.0",
    "eth-utils>=2.0.0",
    "hexbytes<1.4.0",
    "jinja2>=2.9",
    "MarkupSafe<3.1.0",
    "mypy-extensions==1.0.0",
    "numpy",
    "persistent>=4.2.0",
    "py-flags",
    "py-evm==0.10.1b2",
    "py-solc-x<3.0.0",
    "py-solc",
    "pyparsing>=2.0.2,<4",
    "requests",
    "rlp>=3,<5",
    "semantic_version",
    "z3-solver>=4.8.8.0,<=4.13.4.0",
    "matplotlib",
    "certifi>=2020.06.20",
]

TESTS_REQUIRE = ["mypy==0.782", "pytest>=3.6.0", "pytest_mock", "pytest-cov"]

# What packages are optional?
EXTRAS = {}

# If version is set to None then it will be fetched from __version__.py
VERSION = None


# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
        long_description = "\n" + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION


# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, "__version__.py")) as f:
        exec(f.read(), about)
else:
    about["__version__"] = VERSION


# Package version (vX.Y.Z). It must match git tag being used for CircleCI
# deployment; otherwise the build will failed.
class VerifyVersionCommand(_install):
    """Custom command to verify that the git tag matches our version."""

    description = "verify that the git tag matches our version"

    def run(self):
        """"""
        tag = os.getenv("CIRCLE_TAG")

        if tag != about["__version__"]:
            info = "Git tag: {0} does not match the version of this app: {1}".format(
                tag, about["__version__"]
            )
            sys.exit(info)


setup(
    name=NAME,
    version=about["__version__"][1:],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",  # requires twine and recent setuptools
    url=URL,
    author=AUTHOR,
    author_email=AUTHOR_MAIL,
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Disassemblers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="hacking disassembler security ethereum",
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    install_requires=REQUIRED,
    tests_require=TESTS_REQUIRE,
    python_requires=REQUIRES_PYTHON,
    extras_require=EXTRAS,
    package_data={"mythril.analysis.templates": ["*"], "mythril.support.assets": ["*"]},
    include_package_data=True,
    entry_points={"console_scripts": ["myth=mythril.interfaces.cli:main"]},
    cmdclass={"verify": VerifyVersionCommand},
)
