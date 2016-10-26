from os import path

import io

import music_scraper

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup
    from pkgutil import walk_packages


    def _find_packages(path='.', prefix=''):
        yield prefix
        prefix += "."
        for _, name, is_package in walk_packages(path,
                                                 prefix,
                                                 onerror=lambda x: x):
            if is_package:
                yield name


    def find_packages():
        return list(_find_packages(music_scraper.__path__, music_scraper.__name__))

here = path.abspath(path.dirname(__file__))

with io.open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(name='music_scraper',
      version='1.1.0',
      install_requires=['scrapy >= 1.1.1'],
      description='Gets Songs from the web and allows users to download the same',
      long_description=long_description,
      url='https://github.com/srivatsan-ramesh/Music-Scraper',
      author='srivatsan-ramesh',
      author_email='sriramesh4@gmail.com',
      license='MIT',
      packages=find_packages(),
      entry_points={
          'console_scripts': ['music-scraper=music_scraper.main:main'],
      },
      zip_safe=False)
