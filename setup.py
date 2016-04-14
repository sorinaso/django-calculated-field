from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys, os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')

version = '0.1'

PACKAGES = [
    "django_calculated_field",
]

REQUIREMENTS = [
    'Django==1.9',
]

setup(
      name='django-calculated-field',
      version=version,
      description="Django package for automated calculations in fields for denormalization",
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
