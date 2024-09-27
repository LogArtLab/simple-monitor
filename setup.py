from setuptools import setup

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
    name='simplemonitor',
    version='0.1',
    description='Simple monitor for STL',
    license="GPLv3",
    long_description=long_description,
    author='Simone Silvetti',
    author_email='simone.silvetti@gmail.com',
    url="https://github.com/LogArtLab/simple-monitor",
    install_requires=['antlr4-python3-runtime', 'numpy'],  # external packages as dependencies
)
