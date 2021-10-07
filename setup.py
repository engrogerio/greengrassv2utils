#!/usr/bin/env pyhthon3
import sys
sys.path.insert(0, 'ggv2utils')
import ggv2utils
from ggv2utils import ggmq
currentVersion = "0.0.1"

from setuptools import setup

setup(
    name = 'ggv2utils',
    packages=['ggv2utils'],
    version = currentVersion,
    description = 'Message queue services for greengrass v2 components.',
    author = 'Guardian Industries',
    author_email = 'rsilva@guardian.com',
    url = 'https://kochsource.io/rsilva/greengrassv2utils.git',
    download_url = 'https://kochsource.io/rsilva/greengrassv2utils/-/archive/main/greengrassv2utils-main.zip',
    keywords = ['aws', 'iot', 'mqtt', 'ipc'],
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5"
    ]
)
