from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='functools2',
      version=version,
      description="All the good stuff from FP",
      long_description="""\
A collection of higher-order functions that brings the the beauty of FP to Python""",
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
      ],
      test_suite="functools2.tests",
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
