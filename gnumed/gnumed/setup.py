#!/usr/bin/env python

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
      packages=['client.wxpython', 'client.python-common', 'client.business'],
      scripts=['client/wxpython/gnumed.py'],
      data_files=[('share/gnumed/bitmaps',['client/bitmaps/any_body2.png', 'client/bitmaps/gnumedlogo.png']),
                  ('share/doc/gnumed/developer-manual',glob('client/doc/developer-manual/*')),
                  ('share/doc/gnumed/developer-manual/snapshots',glob('client/doc/developer-manual/snapshots/*')),
                  ('share/doc/gnumed/user-manual',glob('client/doc/user-manual/*')),
                  ('share/man/man1',['client/man-pages/gnumed.1']),
                  ('share/gnumed/locale',['client/locale']),
                  ('share/gnumed/doc/html',['html'])]
)
