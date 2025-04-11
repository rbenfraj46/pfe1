import os
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

try:
    import multiprocessing
except ImportError:
    pass

VERSION = '0.0.1'

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

# with open('requirements.txt') as f:
# install_requires = f.read().splitlines()

install_requires = [
    'Django==3.2.11',
    'django-axes==5.28.0',
    'django-ipware==4.0.2',
    'Pillow==9.0.0',
    'django-ranged-response==0.2.0',
    'django-simple-captcha==0.5.14',
    'psycopg2-binary==2.9.3',
    'django-htmlmin==0.11.0',
    'requests==2.27.1',
    'django-leaflet==0.28.2',
    'django-geojson==3.2.1',
    'jsonfield==3.1.0',
    'django-extensions==3.1.5',
    'django-debug-toolbar==3.2.4',
    'django-jazzmin==2.6.0',
    'polib==1.2.0',
    'googletrans==3.1.0a0',
]

dev_requires = [
    'flake8==4.0.1',
    'django-extensions==3.1.5',
    'django-debug-toolbar==3.2.4',
    'pycodestyle==2.8.0',
    'pyflakes==2.4.0',
    'pylint==2.5.3',
    'django-debug-toolbar-template-profiler==2.0.2',
]

tests_require = [
    'pytest==6.2.5',
    'pytest_django==4.5.2',
    'Faker==11.3.0',
    'pytest_cov==3.0.0',
    'pytest-extra-durations==0.1.3',
    #'pytest-parallel==0.1.1',
    'responses==0.17.0',
    'pytest-responses==0.5.0',

    # 'pytest==3.1.0',
    # 'pytest-cov==1.4',
    # 'pytest-django==2.8.0',
    # 'pytest-xdist==1.4',
    # 'cov-core==1.3',
    # 'coverage==3.6'
]


# class PyTest(TestCommand):
#     def finalize_options(self):
#         TestCommand.finalize_options(self)
#         self.test_args = []
#         self.test_suite = True
#
#     def run_tests(self):
#         #import here, cause outside the eggs aren't loaded
#         import pytest
#
#         errno = pytest.main(self.test_args)
#         sys.exit(errno)


setup(
    name='Tun_Car',
    version=VERSION,
    packages=find_packages('.'),
    include_package_data=True,
    license='Lotus INFO License',
    description='A Django app to manage car rental.',
    long_description=open('README.md').read(),
    url='http://www.example.com/',
    author='Alaeddine Melliti',
    author_email='melliti.aladin@gmail.com',
    extras_require={
        'tests': tests_require,
        'dev': dev_requires,
    },
    install_requires=install_requires,
    tests_require=tests_require,
   # cmdclass={'test': PyTest},
    scripts=['carrent/wsgi.py', ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # Replace these appropriately if you are stuck on Python 2.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.12.1',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
