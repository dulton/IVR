import os
import sys
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.md')).read()

requires = [
    'gevent>=1.1rc2',
    #'ws4py==0.3.4',
    'ws4py==0.3.5',
    'PyYAML==3.11',
    'pyramid==1.5.7',
    'pyramid_debugtoolbar>=2.2.2',
    'pyramid_chameleon>=0.3',
    'SQLAlchemy>=1.0.9',
    'PyMySQL>=0.6.7',
    'alembic>=0.8.0',
    'requests==2.9.1',
]

if sys.version_info < (2, 7):
    requires.append('ordereddict')
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
      dependency_links=['https://github.com/hyt-hz/WebSocket-for-Python/archive/master.zip#egg=ws4py-0.3.5'],
      test_suite="ivr.tests",
      entry_points="""
      [console_scripts]
      ivc = ivr.ivc.main:main
      ivt = ivr.ivt.main:main
      ivc_deploy = ivr.scripts.ivc_deploy:main
      """,
      )
