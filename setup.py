#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

# with open("README.md") as readme_file:
#     readme = readme_file.read()


from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md")) as f:
    long_description = f.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = ["PyYAML"]

setup_requirements = []

test_requirements = []

setup(
    author="JL Peyret",
    author_email="jpeyret@gmail.com",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    description="strip out unnecessary pip packages from requirements",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    license="MIT license",
    package_data={
        # And include any *.msg files found in the 'hello' package, too:
        "templates": ["*"]
    },
    # long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="pip_stripper",
    name="pip_stripper",
    packages=find_packages(include=["pip_stripper"]),
    entry_points={"console_scripts": ["pipstripper = pip_stripper._pip_stripper:main"]},
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/jpeyret/pip-stripper",
    version="0.2.0",
    zip_safe=False,
)
