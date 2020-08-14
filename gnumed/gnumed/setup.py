import os
from setuptools import setup, find_packages


#def read(fname):
#	return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup (
	name = 'GNUmed',
	version = 'see.gnumed.py',
	author = 'karsten.hilbert@gmx.net',
	description = 'see appstream.xml',
	license = 'GPL-v2-or-later',
	#keywords
	url = 'https://github.com/ncqgm/gnumed',
	packages = find_packages(),
	long_description('see appstream.xml')
)
