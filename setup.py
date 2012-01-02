import os
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), "supstream", "__version__.py")) as version_file:
    exec version_file.read()

setup(
    name='django-static-upstream',
    version=__version_str__,
    author='Yaniv Aknin',
    author_email='yaniv@aknin.name',
    packages=find_packages(),
    url='https://github.com/yaniv-aknin/supstream',
    license='MIT',
    description='Django package to handle (serve, reference, compile) static files',
)
