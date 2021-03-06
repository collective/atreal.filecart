from setuptools import setup, find_packages
import os

version = '1.1.1.dev0'

setup(name='atreal.filecart',
      version=version,
      description="A cart for Plone to add file and download them in an archive.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='atReal',
      author_email='contact@atreal.net',
      url='http://www.atreal.net/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['atreal'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'five.intid',
          'atreal.override.albumview',
          'plone.app.kss',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
