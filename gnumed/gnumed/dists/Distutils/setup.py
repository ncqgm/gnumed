#!/usr/bin/env python
#-----------------------------------------------------------------------+
# Name:		setup.py						|
#									|
# Synopsis:	python setup.py build	# Build the module.		|
#		python setup.py install	# Install the module.		|
#									|
#		See http://www.python.org/sigs/distutils-sig/doc/ for	|
#		more information on using distutils to install Python	|
#		programs and modules.					|
#									|
# Description:	Setup script (using the distutils framework) for	|
#		GNUmed.						|
#=======================================================================|
# Copyright 2001, 2002 by Gerhard Haering.
# Copyright 2005 by Sebastian Hilbert				|
# All rights reserved.							|
#									|
# Permission to use, copy, modify, and distribute this software and its	|
# documentation for any purpose and without fee is hereby granted, pro-	|
# vided that the above copyright notice appear in all copies and that	|
# both that copyright notice and this permission notice appear in sup-	|
# porting documentation, and that the copyright owner's name not be	|
# used in advertising or publicity pertaining to distribution of the	|
# software without specific, written prior permission.			|
#									|
# THE AUTHOR(S) DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE,	|
# INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND  FITNESS.  IN	|
# NO EVENT SHALL THE AUTHOR(S) BE LIABLE FOR ANY SPECIAL, INDIRECT OR	|
# CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS	|
# OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE	|
# OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE	|
# USE OR PERFORMANCE OF THIS SOFTWARE.					|
#=======================================================================|
# People who have worked on this code.					|
#									|
# Ini Name								|
# --- ----------------------------------------------------------------- |
#  sh Sebastian Hilbert <sebastian.hilbert@gmx.net>				|
# 				|
#=======================================================================|
# Revision History:							|
#									|
# Date      Ini Description						|
# --------- --- ------------------------------------------------------- |
# 09JUN2005 sh	Initial version created by Sebastian Hilbert.		|
#-----------------------------------------------------------------------+
import os, os.path, sys

from distutils.core import setup
from distutils.extension import Extension

__version__ = "0.1"

# Define the runtime library path for this module.  It starts out as None.

def main():
	# Set this to 1 if you need to use your own settings
	USE_CUSTOM = 0	
	
	# Default settings, may be overriden for specific platforms
	#pypgsql_rt_dirs = None
	#optional_libs = ["pq"]
	modname = "GNUmed"
	
	sources = []

	if USE_CUSTOM:
		include_dirs = YOUR_LIST_HERE
		library_dirs = YOUR_LIST_HERE
	elif sys.platform == "linux2":
		include_dirs = ["/usr/include"]
		library_dirs = ["/usr/lib"]
		optional_libs = [""]
		# XXX: This is an ugly hack to make bdist_rpm find the include files.
		include_dirs.append("../" * 5)
	elif sys.platform[:8] == "unixware":
		LOCALBASE = os.environ.get('LOCALBASE', '/usr/local/pgsql')
		include_dirs = ['%s/include' % LOCALBASE]
		library_dirs = ['%s/lib' % LOCALBASE]
		pypgsql_rt_dirs = library_dirs
	elif sys.platform[:8] == "openunix":
		LOCALBASE = os.environ.get('LOCALBASE', '/usr/local/pgsql')
		include_dirs = ['%s/include' % LOCALBASE]
		library_dirs = ['%s/lib' % LOCALBASE]
		pypgsql_rt_dirs = library_dirs
	elif sys.platform == "freebsd4":
		LOCALBASE = os.environ.get('LOCALBASE', '/usr/local')
		include_dirs = ['%s/include' % LOCALBASE]
		library_dirs = ['%s/lib' % LOCALBASE]
	elif sys.platform == "openbsd3":
		LOCALBASE = os.environ.get('LOCALBASE', '/usr/local')
		include_dirs = ['%s/include/postgresql' % LOCALBASE]
		library_dirs = ['%s/lib' % LOCALBASE]
	elif sys.platform == "netbsd1":
		LOCALBASE = os.environ.get('LOCALBASE', '/usr/pkg')
		include_dirs = ['%s/include/pgsql' % LOCALBASE]
		library_dirs = ['%s/lib' % LOCALBASE]
	elif sys.platform == "cygwin":
		include_dirs  = ["/usr/include/postgresql"]
		library_dirs  = ["/usr/lib"]
	elif sys.platform == "darwin": # Mac OS X
		include_dirs = ["/usr/local/pgsql/include"]
		library_dirs = ["/usr/local/pgsql/lib"]
		optional_libs += ["ssl", "crypto"]
	elif sys.platform == "win32":
		"""# This works with the PostgreSQL source tree, so it's a bit ugly ...
		# Lines commented out are for using MSVC instead of mingw
		win_pg_build_root = os.getenv("PG_SRC", "../postgresql")

		include_dirs = [os.path.join(win_pg_build_root, p) for p in
			["src/include",
			 "src/include/libpq",
			 "src",
			 "src/interfaces/libpq"]]

		library_dirs = [win_pg_build_root + "/src/interfaces/libpq"]
		#library_dirs = [win_pg_build_root + "/src/interfaces/libpq/Release"]
		"""
		optional_libs = [""]
		#optional_libs = ["libpq", "wsock32", "advapi32"]
		modname="GNUmed"
	else:
		# Assume a Unixish system
		include_dirs = ["/usr/local/include"]
		library_dirs = ["/usr/local/lib"]

	# patch distutils if it can't cope with the "classifiers" keyword
	if sys.version < '2.2.3':
		from distutils.dist import DistributionMetadata
		DistributionMetadata.classifiers = None
		DistributionMetadata.download_url = None

	classifiers = [
		"Development Status :: 5 - Production/Stable",
		"Environment :: MacOS X :: Carbon, Win32 (MS Windows), X11 Applications",
		"Intended Audience :: Developers, End Users/Desktop, Other Audience, System Administrators",
		"License :: OSI Approved :: GNU Public License",
		"Natural Language :: English, German, Spanish",
		"Operating System :: MacOS X, Microsoft :: Windows :: Windows 95/98/ME, Microsoft :: Windows :: Windows NT/2000/XP, POSIX :: Linux, POSIX :: SunOS/Solaris",
		"Programming Language :: Python",
		"Topic :: Scientific/Engineering :: Medical Science Apps."]

	setup (
		name = "GNUmed",
		version = __version__,
		description = \
			"GNUmed - An open source practice management software",
		maintainer = "GNUmed developers",
		maintainer_email = "gnumed-devel@gnu.org",
		url = "http://www.gnumed.org",
		license = "GPL",
		packages = [
			"GNUmed", 
			"GNUmed.bitmaps",
			"GNUmed.business",
			"GNUmed.doc",
			"GNUmed.locale",
			"GNUmed.pycommon",
			"GNUmed.wxpython"
			],
		#ext_modules = [Extension(
		#	name=modname,
		#	sources = sources,
		#	include_dirs = include_dirs,
		#	library_dirs = library_dirs,
			#runtime_library_dirs = pypgsql_rt_dirs,
		#	libraries = optional_libs
		#	)],
		classifiers = classifiers
	)

if __name__ == "__main__":
    main()
