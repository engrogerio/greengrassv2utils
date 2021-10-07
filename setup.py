#!/usr/bin/env pyhthon3
import sys
sys.path.insert(0, 'ggv2utils')
from src.ggv2utils import ggmq
currentVersion = "0.0.1"

from setuptools import setup

setup(
    name = 'ggv2utils',
    packages=['ggv2utils'],
    version = currentVersion,
    description = 'Message queue services for greengrass v2 components.',
    author = 'Guardian Industries',
    author_email = 'rsilva@guardian.com',
    url = 'https://github.com/engrogerio/greengrassv2utils.git',
    download_url = 'https://github.com/engrogerio/greengrassv2utils/archive/refs/heads/main.zip',
    keywords = ['aws', 'iot', 'mqtt', 'ipc'],
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9"
    ]
)
