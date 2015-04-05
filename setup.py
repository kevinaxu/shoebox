#!/usr/bin/env python
from distutils.core import setup

setup(name='Shoebox',
      version='1.0',
      description='Encrypted cloud file storage',
      author='Kevin Xu',
      author_email='kevin.xu@yale.edu',
      url='https://github.com/kevinaxu/shoebox'
	  long_description=open('README.md').read(),
	  install_requires=[
		  "google-api-python-client >= 1.2",
		  ],
     )
