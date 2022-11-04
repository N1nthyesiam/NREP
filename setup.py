from setuptools import find_packages, setup

setup(
    name='NREP',
    packages=find_packages(include=['pycryptodome', 'urllib']),
    version='0.1.0',
    description='Simple python NREP/RecRoll implementation',
    author='N!nth',
    license='MIT',
)