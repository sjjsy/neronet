from setuptools import setup, find_packages
import codecs
import os
import sys
import re

here = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    # intentionally *not* adding an encoding option to open
    return codecs.open(os.path.join(here, *parts), 'r').read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

long_description = 'TODO'

setup(
    name='neronet',
    version=1.01,
    url='http://github.com/smarisa/neronet',
    license='None',
    author='Samuel Marisa & CO.',
    install_requires=['Babel>=2.1.1',
                      'pytz>=2015.7',
                      'six>=1.10.0',
                      'snowballstemmer>=1.2.0',
                      'wheel>=0.26.0',
                      'pyyaml>=3.11',
                      ],
    author_email='teemu.blomqvist@aalto.fi',
    description='A tool for managing computational experiments.',
    long_description=long_description,
    #entry_points={},
    packages=['neronet'],
    include_package_data=True,
    platforms='any',
    zip_safe=False,
    #package_data={'sandman': ['templates/**', 'static/*/*']},
    classifiers = [
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Development Status :: 2 - Pre-Alpha',
        'Natural Language :: English',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    #extras_require={
    #'testing': ['pytest'],
    #}
)
