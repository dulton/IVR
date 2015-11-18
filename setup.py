import os
import sys
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.md')).read()

requires = [
    'gevent=1.0'
    'ws4py=0.3.4'
]

if sys.version_info < (2,7):
    requires.append('unittest2')

setup(name='IVR',
      version='0.1.0',
      license='AGPLv3',
      url='https://github.com/OpenSight/IVR',
      description='',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Development Status :: 4 - Beta",
          "Framework :: Pyramid",
          "Intended Audience :: System Administrators",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: GNU Affero General Public License v3",
          "Operating System :: POSIX :: Linux",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
          "Topic :: System :: Monitoring",
          "Topic :: System :: Networking :: Monitoring",
          "Topic :: System :: Systems Administration",
      ],
      author='OpenSight',
      author_email='',
      keywords='',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="IVR.tests",
      #     data_files=[
      #         ('/etc/', ['storlever.ini']),
      #         ('/etc/init.d', ['initscripts/storlever']),
      #     ],
      entry_points="""
      """,
      )