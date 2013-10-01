from setuptools import setup, find_packages
import sys, os
from fp import __version__

setup(name='fp',
      version=__version__,
      description="All the good stuff from Functional Programming",
      long_description="""\ A collection of higher-order functions
that brings the the beauty of FP to Python""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Eric Moritz',
      author_email='eric@themoritzfamily.com',
      url='',
      license='',
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
