from ic import ICOpaqueData
from setuptools import setup, find_packages

try:
    long_description = open('README.md', 'rt').read()
except IOError:
    long_description = ""

setup(
    name="dcavenue",
    description="django app for integrating with ccavenue",
    long_description=long_description,

    version="0.1",
    author='Amit Upadhyay',
    author_email="upadhyay@gmail.com",

    url='https://amitu.com/dcavenue/',
    license='BSD',
    install_requires=["importd"],

    packages=find_packages(),
    zip_safe=True
)
