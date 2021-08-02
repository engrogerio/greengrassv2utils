#!/usr/bin/env pyhthon3
from distutils.core import setup

setup(name='greengrassv2utils',
      version='1.0',
      description='AWS Greengrass v2 Utilities',
      author='Rogerio Silva',
      author_email='rogerio@inventsis.com.br',
      url='https://www.python.org',
      packages=['ggv2utils'],
      package_dir={'ggv2utils': 'src/ggv2utils'}
     )
