from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys, os

PACKAGES = [
    "calculated_field",
]

REQUIREMENTS = []

version = __import__('calculated_field').__version__

setup(
      name='django-calculated-field',
      version=version,
      description="Django package for automated calculations in fields for denormalizated fields",
      classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Framework :: Django',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules'],
      author='Alejandro Souto',
      author_email='sorinaso@gmail.com',
      url='https://github.com/sorinaso/django-calculated-field',
      license='MIT',
      packages=PACKAGES,
      include_package_data=True,
      zip_safe=False,
      install_requires=REQUIREMENTS,
)
