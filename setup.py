from setuptools import setup, find_packages
import sys, os

setup(name='fp',
      version="0.2",
      description="All the good stuff from Functional Programming",
      long_description="""\ A collection of higher-order functions
that brings the the beauty of FP to Python""",
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",        
        ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Eric Moritz',
      author_email='eric@themoritzfamily.com',
      url='https://fp.readthedocs.org/en/latest/',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          "six",
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
