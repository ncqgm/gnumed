# -*- coding: utf-8 -*-

"""GNUmed LaTeX definitions and helpers."""
#============================================================
# SPDX-License-Identifier: GPL-2.0-or-later
__author__ = "karsten.hilbert@gmx.net"
__license__ = "GPL v2 or later"

# standard library imports
import logging
import sys
import re as regex

# 3rd party library imports
# docutils
du_core = None

# setup translation
if __name__ == '__main__':
	sys.path.insert(0, '../../')
#	_ = lambda x:x
#else:
#	try: _		# do we already have _() ?
#	except NameError:
#		from Gnumed.pycommon import gmI18N
#		gmI18N.activate_locale()
#		gmI18N.install_domain()

# GNUmed module imports
#from Gnumed.pycommon import ...

_log = logging.getLogger('gm.tex')

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

#------------------------------------------------------------
def tex_escape_string(text:str=None, replace_known_unicode:bool=True, replace_eol:bool=False, keep_visual_eol:bool=False, strip_whitespace:bool=True) -> str:
	"""Check for special TeX characters and transform them.

	Args:
		text: plain (unicode) text to escape for LaTeX processing,
			note that any valid LaTeX code contained within will be
			escaped, too
		replace_eol: replaces "\n" with "\\newline{}"
		keep_visual_eol: replaces "\n" with "\\newline{}%\n" such that
			both LaTeX will know to place a line break
			at this point as well as the visual formatting
			is preserved in the LaTeX source (think multi-
			row table cells)
		strip_whitespace: whether to remove surrounding whitespace

	Returns:
		A hopefully properly escaped string palatable to LaTeX.
	"""
	# must happen first
	text = text.replace('{', '-----{{{{{-----')
	text = text.replace('}', '-----}}}}}-----')

	text = text.replace('\\', '\\textbackslash{}')			# requires \usepackage{textcomp} in LaTeX source

	text = text.replace('-----{{{{{-----', '\\{{}')
	text = text.replace('-----}}}}}-----', '\\}{}')

	text = text.replace('^', '\\textasciicircum{}')
	text = text.replace('~', '\\textasciitilde{}')

	text = text.replace('%', '\\%{}')
	text = text.replace('&', '\\&{}')
	text = text.replace('#', '\\#{}')
	text = text.replace('$', '\\${}')
	text = text.replace('_', '\\_{}')
	if replace_eol:
		if keep_visual_eol:
			text = text.replace('\n', '\\newline{}%\n')
		else:
			text = text.replace('\n', '\\newline{}')

	if replace_known_unicode:
		# this should NOT be replaced for Xe(La)Tex
		text = text.replace(u_euro, '\\euro{}')		# requires \usepackage[official]{eurosym} in LaTeX source
		text = text.replace(u_sum, '$\\Sigma$')

	if strip_whitespace:
		return text.strip()

	return text

#------------------------------------------------------------
def xetex_escape_string(text=None):
	# a web search did not reveal anything else for Xe(La)Tex
	# as opposed to LaTeX, except true unicode chars
	return tex_escape_string(text = text, replace_known_unicode = False)

#------------------------------------------------------------
def rst2latex_snippet(rst_text):
	global du_core
	if du_core is None:
		try:
			from docutils import core as du_core
		except ImportError:
			_log.warning('cannot turn ReST into LaTeX: docutils not installed')
			return tex_escape_string(text = rst_text)

	parts = du_core.publish_parts (
		source = rst_text.replace('\\', '\\\\'),
		source_path = '<internal>',
		writer_name = 'latex',
		#destination_path = '/path/to/LaTeX-template/for/calculating/relative/links/template.tex',
		settings_overrides = {
			'input_encoding': 'unicode'		# un-encoded unicode
		},
		enable_exit_status = True			# how to use ?
	)
	return parts['body']

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

	from Gnumed.pycommon.gmTools import u_euro, u_sum

	#--------------------------------------------------------
	def test_require_package():
		print(require_package(package = 'xltabular'))

	#--------------------------------------------------------
	def test_tex_escape():
		tests = ['\\', '^', '~', '{', '}', '%',  '&', '#', '$', '_', u_euro, 'abc\ndef\n\n1234']
		tests.append('  '.join(tests))
		for test in tests:
			print('%s:' % test, tex_escape_string(test))

	#--------------------------------------------------------
	def test_rst2latex_snippet():
		tests = ['\\', '^', '~', '{', '}', '%',  '&', '#', '$', '_', u_euro, 'abc\ndef\n\n1234']
		tests.append('  '.join(tests))
		tests.append(r'C:\Windows\Programme\System 32\lala.txt')
		tests.extend([
			'should be identical',
			'text *some text* text',
			"""A List
======

1. 1
2. 2

3. ist-list
1. more
2. noch was ü
#. nummer x"""
		])
		for test in tests:
			print('==================================================')
			print('raw:')
			print(test)
			print('---------')
			print('ReST 2 LaTeX:')
			latex = rst2latex_snippet(test)
			print(latex)
			if latex.strip() == test.strip():
				print('=> identical')
			print('---------')
			print('tex_escape_string:')
			print(tex_escape_string(test))
			input()

	#--------------------------------------------------------
	#test_require_package()
	#test_tex_escape()
	test_rst2latex_snippet()
