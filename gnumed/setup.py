#!/usr/bin/env python
#
# This script should be used as follows:
#
# To build the tarball for distribution, type:
# python setup.py sdist
#
# The tarball will be created in a ./dist subdirectory
# For users and installers, to install, unpack the tarball and type:
# python setup.py install [--prefix <prefix-dir>] [--root <root-dir>]

from distutils.core import setup
from glob import glob

setup(name="Gnumed",

      version="0.1",

      description="GNU Medical Practice Management Suite",

      author="Gnumed development team",

      author_email="gnumed-devel@gnu.org",

      maintainer="David Grant",

      maintainer_email="dgrant@ieee.org",

      url="http://www.gnumed.org",

      packages=['gnumed', 'gnumed.client', 'gnumed.client.wxpython',
                'gnumed.client.python-common', 'gnumed.client.business'],

      scripts=['gnumed/client/wxpython/gnumed.py'],

      data_files=[
    #bitmap files
    ('share/gnumed/bitmaps',['gnumed/client/bitmaps/any_body2.png', 'gnumed/client/bitmaps/gnumedlogo.png']),
    #developer docs
    ('share/doc/gnumed/developer-manual',glob('gnumed/client/doc/developer-manual/*')),
    #developer docs pictures
    ('share/doc/gnumed/developer-manual/snapshots',glob('gnumed/client/doc/developer-manual/snapshots/*')),
    #user docs
    ('share/doc/gnumed/user-manual',glob('gnumed/client/doc/user-manual/*')),
    #man pages
    ('share/man/man1',['gnumed/client/doc/man-pages/gnumed.1']),
    #locale files
    ('share/gnumed/locale',['gnumed/client/locale']),
    #html docs
    ('share/gnumed/doc/html',['gnumed/html'])
    ]
)
