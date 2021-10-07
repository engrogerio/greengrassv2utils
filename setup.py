currentVersion = "0.0.1"
from setuptools import setup, find_packages

setup(
    name = 'ggv2utils',
    packages=find_packages(),
    version = currentVersion,
    description = 'Message queue services for greengrass v2 components.',
    author = 'Guardian Industries',
    author_email = 'rsilva@guardian.com',
    url = 'https://github.com/engrogerio/greengrassv2utils.git',
    download_url = 'https://github.com/engrogerio/greengrassv2utils/archive/refs/heads/main.zip',
    keywords = ['aws', 'iot', 'mqtt', 'ipc'],
    classifiers = [],
    install_requires=[
        'awsiotsdk==1.7.1',
    ]
)
