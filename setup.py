#!/usr/bin/env python3
"""
Setup script for AnonCodexCli.
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="anoncodexcli",
    version="0.1.0",
    author="AnonCodexCli Team",
    description="A CLI-based AI coding assistant inspired by Cursor",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/AnonCodexCli",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "anoncodex=cli:main",
        ],
    },
) 