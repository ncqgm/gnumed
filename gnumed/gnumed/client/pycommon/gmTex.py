# -*- coding: utf-8 -*-

"""GNUmed LaTeX definitions and helpers."""
#============================================================
# SPDX-License-Identifier: GPL-2.0-or-later
__author__ = "karsten.hilbert@gmx.net"
__license__ = "GPL v2 or later"

# standard library imports
import logging
import os
import re as regex
import shutil
import sys

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
from Gnumed.pycommon import gmShellAPI
from Gnumed.pycommon.gmTools import u_euro, u_sum, mk_sandbox_dir, fname_stem

_log = logging.getLogger('gm.tex')

#============================================================
__pdflatex_version_logged:bool = False
__pdflatex_executable:str = None
__xelatex_version_logged:bool = False
__xelatex_executable:str = None
_REGEX_LaTeX__usepackage__name = regex.compile(r'{\S+?}')
LATEX__define_tnl_as_tabularnewline = r'\providecommand{\tnl}{\tabularnewline}'

#------------------------------------------------------------
_LATEX__require_pkg_code = r"""%% this document requires "\usepackage{%(pkg)s}", checking:
\makeatletter
\@ifpackageloaded{%(pkg)s}%%
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
	r"""Replaces \usepackage with \gmcheckandloadpkg in <latex_file>.

	Only one \usepackage per line and only at start of lines.

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
		if not gmcheckandloadpkg_defined:
			output_file.write(_LATEX__define_gmcheckandloadpkg_cmd)
			gmcheckandloadpkg_defined = True
		pkg_name = _REGEX_LaTeX__usepackage__name.findall(line)[0]
		pkg_name = pkg_name.strip('{}')
		parts = line.split('%', 1)
		usepackage_cmd = parts[0].strip()
		comment = ''
		if len(parts) > 1:
			comment = '\t\t%%%s' % parts[1]
		_log.debug(r'wrapping [%s] found', usepackage_cmd)
		output_file.write(r'\gmcheckandloadpkg{%s.sty}{%s}%s' % (pkg_name, usepackage_cmd, comment))
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

#------------------------------------------------------------
def __detect_xelatex() -> bool:
	global __xelatex_version_logged
	global __xelatex_executable
	if not __xelatex_version_logged:
		__xelatex_version_logged = True
		found, __xelatex_executable = gmShellAPI.detect_external_binary(binary = 'xelatex')
		if not found:
			_log.error('xelatex not found')
			return False

		cmd_line = [__xelatex_executable, '-version']
		success, ret_code, stdout = gmShellAPI.run_process(cmd_line = cmd_line, encoding = 'utf8', verbose = True)
		if not success:
			_log.error('[%s] failed, XeLaTeX not usable', cmd_line)
			return False

		_log.debug('XeLaTeX found')
	return True

#------------------------------------------------------------
def __detect_pdflatex() -> bool:
	global __pdflatex_version_logged
	global __pdflatex_executable
	if not __pdflatex_version_logged:
		__pdflatex_version_logged = True
		found, __pdflatex_executable = gmShellAPI.detect_external_binary(binary = 'pdflatex')
		if not found:
			_log.error('pdflatex not found')
			return False

		cmd_line = [__pdflatex_executable, '-version']
		success, ret_code, stdout = gmShellAPI.run_process(cmd_line = cmd_line, encoding = 'utf8', verbose = True)
		if not success:
			_log.error('[%s] failed, PdfLaTeX not usable', cmd_line)
			return False

		_log.debug('PdfLaTeX found')
	return True

#------------------------------------------------------------
def __compile_with_pdflatex(sandbox_dir:str=None, latex_filename:str=None) -> str:
	cmd_final = [
		__pdflatex_executable,
		'-recorder',
		'-interaction=nonstopmode',
		"-output-directory=%s" % sandbox_dir
	]
	cmd_draft = cmd_final + ['-draftmode']
	# LaTeX can need up to three runs to get cross references et al right
	for cmd2run in [cmd_draft, cmd_draft, cmd_final]:
		success, ret_code, stdout = gmShellAPI.run_process (
			cmd_line = cmd2run + [latex_filename],
			acceptable_return_codes = [0],
			encoding = 'utf8',
			verbose = True	#_cfg.get(option = 'debug')
		)
		if success:
			continue
		_log.error('problem running pdflatex, cannot generate PDF, trying diagnostics')
		__check_latex_file(latex_filename = latex_filename)
		return None

	return '%s.pdf' % os.path.splitext(latex_filename)[0]

#------------------------------------------------------------
def __check_latex_file(latex_filename:str=None):
	found, binary = gmShellAPI.find_first_binary(binaries = ['lacheck', 'miktex-lacheck.exe'])
	if not found:
		_log.debug('lacheck not found')
	else:
		cmd_line = [binary, latex_filename]
		success, ret_code, stdout = gmShellAPI.run_process(cmd_line = cmd_line, encoding = 'utf8', verbose = True)
	found, binary = gmShellAPI.find_first_binary(binaries = ['chktex', 'ChkTeX.exe'])
	if not found:
		_log.debug('chcktex not found')
	else:
		cmd_line = [binary, '--verbosity=2', '--headererr', latex_filename]
		success, ret_code, stdout = gmShellAPI.run_process(cmd_line = cmd_line, encoding = 'utf8', verbose = True)

#------------------------------------------------------------
def __compile_with_xelatex(sandbox_dir:str=None, latex_filename:str=None) -> str:
	cmd_final = [
		__xelatex_executable,
		'-recorder',
		'-interaction=nonstopmode',
		"-output-directory=%s" % sandbox_dir
	]
	cmd_draft = cmd_final + ['-no-pdf']		# akin to -draftmode
	# LaTeX can need up to three runs to get cross references et al right
	for cmd2run in [cmd_draft, cmd_draft, cmd_final]:
		success, ret_code, stdout = gmShellAPI.run_process (
			cmd_line = cmd2run + [latex_filename],
			acceptable_return_codes = [0],
			encoding = 'utf8',
			verbose = True	#_cfg.get(option = 'debug')
		)
		if success:
			continue
		_log.error('problem running xelatex, cannot generate PDF')	#, trying diagnostics')
#		__check_latex_file(latex_filename = latex_filename)
		return None

	return '%s.pdf' % os.path.splitext(latex_filename)[0]

#------------------------------------------------------------
def compile_latex_to_pdf(latex_filename:str=None, verbose:bool=False, is_sandboxed:bool=False) -> str:
	"""Compile LaTeX code to PDF using xelatex or pdflatex.

	Args:
		is_sandboxed: whether or not already sandboxed (no need to create a sandbox for compiling)

	Returns:
		Name of resulting PDF, or None on failure.
	"""
	xelatex_avail = __detect_xelatex()
	__detect_pdflatex()
	if not (xelatex_avail or __pdflatex_executable):
		_log.error('neither xelatex nor pdflatex found, LaTeX not usable')
		return None

	if is_sandboxed:
		sandbox_dir = os.path.split(latex_filename)[0]
	else:
		sandbox_dir = mk_sandbox_dir(prefix = fname_stem(latex_filename) + '_')
		shutil.copy(latex_filename, sandbox_dir)
		latex_filename = os.path.join(sandbox_dir, os.path.split(latex_filename)[1])
	_log.debug('LaTeX sandbox directory: [%s]', sandbox_dir)
	if xelatex_avail:
		pdf_name = __compile_with_xelatex(sandbox_dir = sandbox_dir, latex_filename = latex_filename)
		if pdf_name is not None:
			return pdf_name

		_log.error('issue compiling with xelatex, trying with pdflatex')
	pdf_name = __compile_with_pdflatex(sandbox_dir = sandbox_dir, latex_filename = latex_filename)
	if pdf_name is not None:
		return pdf_name

	_log.error('issue compiling with pdflatex, too')
	return None

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
	#test_rst2latex_snippet()
	print(__detect_pdflatex())
	print(__pdflatex_executable)
