# -*- coding: utf-8 -*-

"""GNUmed LaTeX definitions and helpers."""
#============================================================
# SPDX-License-Identifier: GPL-2.0-or-later
__author__ = "karsten.hilbert@gmx.net"
__license__ = "GPL v2 or later"

# standard library imports
import sys
import re as regex

# 3rd party library imports
#import ...

# setup translation
#if __name__ == '__main__':
#	sys.path.insert(0, '../../')
#	_ = lambda x:x
#else:
#	try: _		# do we already have _() ?
#	except NameError:
#		from Gnumed.pycommon import gmI18N
#		gmI18N.activate_locale()
#		gmI18N.install_domain()

# GNUmed module imports
#from Gnumed.pycommon import ...

#_log = logging.getLogger('gm.ABCD')

#============================================================
_REGEX_LaTeX__usepackage__name = regex.compile(r'{\S+?}')
LATEX__define_tnl_as_tabularnewline = r'\providecommand{\tnl}{\tabularnewline}'

#------------------------------------------------------------
_LATEX__require_pkg_code = r"""%% this document requires "\usepackage{%(pkg)s}", checking:
\makeatletter
\@ifpackageloaded{xltabular}%%
	{\typeout{GNUmed: <%(pkg)s> package is loaded}}%%
	{\typeout{GNUmed: <%(pkg)s> not loaded, aborting compilation}\batchmode\stop}
\makeatother"""

#------------------------------------------------------------
_LATEX__define_gmcheckandloadpkg_cmd = r"""
% defining new command for checked loading of packages
% aborts immediately if package does not seem available
\makeatletter
\newcommand{\gmcheckandloadpkg}[2]{%
	\makeatletter%
	\typeout{GNUmed: attempting to load <#1>}%
	\IfFileExists{#1}%
		{\typeout{GNUmed: found, loading}#2}%
		{\typeout{GNUmed: not found, aborting compilation}\batchmode\stop}%
	\makeatother%
}
\makeatother

"""
#============================================================
def require_package(package:str=None) -> str:
	return _LATEX__require_pkg_code % {'pkg': package}

#------------------------------------------------------------
def wrap_usepackage_cmd(filename:str=None) -> str:
	"""Replaces \\usepackage with \gmcheckandloadpkg in <latex_file>.

	Only one \\usepackage per line and only at start of lines.

	Args:
		filename: name of file to process

	Returns:
		Name of processed file.
	"""
	output_filename = '%s.safe-usepackage.tex' % filename
	_log.debug(' [%s] -> [%s]', filename, output_filename)
	input_file = open(filename, mode = 'rt', encoding = 'utf-8-sig')
	output_file = open(output_filename, mode = 'wt', encoding = 'utf8')
	gmcheckandloadpkg_defined = False
	for line in input_file:
		if not line.lstrip().startswith(r'\usepackage'):
			output_file.write(line)
			continue

		_log.debug(r'\usepackage found')
		if not gmcheckandloadpkg_defined:
			output_file.write(_LATEX__define_gmcheckandloadpkg_cmd)
			gmcheckandloadpkg_defined = True
		pkg_name = _REGEX_LaTeX__usepackage__name.findall(line)[0]
		pkg_name = pkg_name.strip('{}')
		parts = line.split('%', 1)
		use_cmd = parts[0].strip()
		comment = ''
		if len(parts) > 1:
			comment = '\t\t%%%s' % parts[1]
		output_file.write(r'\gmcheckandloadpkg{%s.sty}{%s}%s' % (pkg_name, use_cmd, comment))
	output_file.close()
	input_file.close()
	return output_filename

#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

#	del _			# setup a real translation
#	from Gnumed.pycommon import gmI18N
#	gmI18N.activate_locale()
#	gmI18N.install_domain(domain = 'gnumed', prefer_local_catalog = True)

	#--------------------------------------------------------
	def test_require_package():
		print(require_package(package = 'xltabular'))

	#--------------------------------------------------------
	test_require_package()
