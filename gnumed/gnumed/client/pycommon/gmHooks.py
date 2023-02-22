"""GNUmed hooks framework.

This module provides convenience functions and definitions
for accessing the GNUmed hooks framework.

This framework calls the script

	~/.config/gnumed/scripts/hook_script.py

at various times during client execution. The script must
contain a function

def run_script(hook=None):
	pass

which accepts a single argument <hook>. That argument will
contain the hook that is being activated.
"""
# ========================================================================
__author__  = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later (details at https://www.gnu.org)"

# stdlib
import os
import sys
import stat
import logging
import io


# GNUmed libs
if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmTools


_log = logging.getLogger('gm.hook')

# ========================================================================
known_hooks = [
	'post_patient_activation',
	'post_person_creation',

	'after_waiting_list_modified',

	'shutdown-post-GUI',
	'startup-after-GUI-init',
	'startup-before-GUI',

	'request_user_attention',
	'app_activated_startup',
	'app_activated',
	'app_deactivated',

	'after_substance_intake_modified',
	'after_test_result_modified',
	'after_soap_modified',
	'after_code_link_modified',

	'after_new_doc_created',
	'before_print_doc',
	'before_fax_doc',
	'before_mail_doc',
	'before_print_doc_part',
	'before_fax_doc_part',
	'before_mail_doc_part',
	'before_external_doc_access',

	'db_maintenance_warning'
]


README_pat_dir = """Directory for data files containing the current patient.

Whenever the patient is changed GNUmed will export
formatted demographics into files in this directory
for use by 3rd party software.

Currently exported formats:

GDT, VCF (vcard), MCF (mecard), XML (linuxmednews)"""


HOOK_SCRIPT_EXAMPLE = """#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#===========================================================================
#
# Example script to be run off GNUmed hooks.
#
# It can print a message to stdout whenever any hook is invoked.
#
# Copy this file to ~/.config/gnumed/scripts/hook_script.py and modify as needed.
#
# Known hooks:
#
#	%s
#
#===========================================================================
# SPDX-License-Identifier: GPL-2.0-or-later
__license__ = "GPL v2 or later (details at https://www.gnu.org)"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"


import os


from Gnumed.pycommon import gmWorkerThread
from Gnumed.pycommon import gmTools

from Gnumed.business import gmPerson

from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmPatSearchWidgets


PAT_DIR = os.path.join(gmTools.gmPaths().user_appdata_dir, 'current_patient')
README_pat_dir = \"\"\"%s
\"\"\"
CURR_PAT = None

#===========================================================================
def on_startup_after_GUI_init():
	# examine external patient sources
	gmPatSearchWidgets.get_person_from_external_sources(search_immediately = False, activate_immediately = True)


def request_user_attention():
	# signal user to look at GNUmed
	gmGuiHelpers.gm_show_info(_('Hey, GNUmed wants you to take a look at it !'))


#def on_app_activated_startup():
	#pass


def on_app_activated():
	# might want to look at external sources again
	gmPatSearchWidgets.get_person_from_external_sources(search_immediately = False, activate_immediately = True)


def _export_patient_demographics():
	if CURR_PAT is None:
		return

	fname = os.path.join(PAT_DIR, 'patient')
	CURR_PAT.export_as_gdt(filename = fname + '.gdt', encoding = 'cp850')
	CURR_PAT.export_as_xml_linuxmednews(filename = fname + '.xml')
	CURR_PAT.export_as_vcard(filename = fname + '.vcf')
	CURR_PAT.export_as_mecard(filename = fname + '.mcf')


#def on_app_deactivated():
def on_post_patient_activation():
	# might want to export the active patient into an xDT file
	global CURR_PAT
	curr_pat = gmPerson.gmCurrentPatient()
	if not curr_pat.connected:
		CURR_PAT = None
		return

	CURR_PAT = curr_pat
	gmWorkerThread.execute_in_worker_thread (
		payload_function = _export_patient_demographics,
		worker_name = 'current_patient_demographics_exporter'
	)


#===========================================================================
gmTools.mkdir(PAT_DIR)
gmTools.create_directory_description_file(directory = PAT_DIR, readme = README_pat_dir)

# main entry point
def run_script(hook=None):

	if hook is None:
		hook = _('no hook specified, please report bug')
		print('hook_script.py::run_script():', hook)

	#print('GNUmed invoked the hook:', hook)

	# a few examples:

	#if hook == 'startup-after-GUI-init':
	#	on_startup_after_GUI_init()

	#if hook == 'request_user_attention':
	#	on_request_user_attention()

	#if hook == 'app_activated_startup':
	#	on_app_activated_startup()

	#if hook == 'app_activated':
	#	on_app_activated()

	#if hook == 'app_deactivated':
	#	on_app_deactivated()

	if hook == 'post_patient_activation':
		on_post_patient_activation()

	return
""" % (
	'\n#\t'.join(known_hooks),
	README_pat_dir
)


# hardcoding path and script name allows us to not
# need configuration for it, the environment can
# always be detected at runtime (workplace etc)
HOOK_SCRIPT_NAME = 'hook_script.py'
HOOK_SCRIPT_DIR = os.path.join(gmTools.gmPaths().user_config_dir, 'scripts')
HOOK_SCRIPT_FULL_NAME = os.path.join(HOOK_SCRIPT_DIR, HOOK_SCRIPT_NAME)


README_hook_dir = """Directory for scripts called from hooks at client runtime.

Known hooks:

	%s

You can use <%s.example> as a script template.
""" % (
	'\n\t'.join(known_hooks),
	HOOK_SCRIPT_NAME
)


# ========================================================================
def setup_hook_dir():
	_old_path = os.path.join(gmTools.gmPaths().home_dir, '.gnumed', 'scripts')
	if os.path.isdir(_old_path):
		print('obsolete: [%s], use [%s]' %(_old_path, HOOK_SCRIPT_DIR))
		_log.debug('obsolete: %s', _old_path)
	_log.debug('known hooks:')
	for hook in known_hooks:
		_log.debug(hook)
	gmTools.mkdir(HOOK_SCRIPT_DIR)
	gmTools.create_directory_description_file(directory = HOOK_SCRIPT_DIR, readme = README_hook_dir)
	# create hook script example/template
	example_name = os.path.join(HOOK_SCRIPT_DIR, HOOK_SCRIPT_NAME + '.example')
	example = open(example_name, mode = 'wt', encoding = 'utf8')
	example.write(HOOK_SCRIPT_EXAMPLE)
	example.close()
	os.chmod(example_name, 384)

# ========================================================================
hook_module = None

def import_hook_module(reimport=False):

	global hook_module
	if not reimport:
		if hook_module is not None:
			return True

	if not os.access(HOOK_SCRIPT_FULL_NAME, os.F_OK):
		_log.warning('creating default hook script')
		f = io.open(HOOK_SCRIPT_FULL_NAME, mode = 'wt', encoding = 'utf8')
		f.write("""
# known hooks:
#  %s

def run_script(hook=None):
	pass
""" % '\n#\t'.join(known_hooks))
		f.close()
		os.chmod(HOOK_SCRIPT_FULL_NAME, 384)

	if os.path.islink(HOOK_SCRIPT_FULL_NAME):
		gmDispatcher.send (
			signal = 'statustext',
			msg = _('Script must not be a link: [%s].') % HOOK_SCRIPT_FULL_NAME
		)
		return False

	if not os.access(HOOK_SCRIPT_FULL_NAME, os.R_OK):
		gmDispatcher.send (
			signal = 'statustext',
			msg = _('Script must be readable by the calling user: [%s].') % HOOK_SCRIPT_FULL_NAME
		)
		return False

	script_stat_val = os.stat(HOOK_SCRIPT_FULL_NAME)
	_log.debug('hook script stat(): %s', script_stat_val)
	script_perms = stat.S_IMODE(script_stat_val.st_mode)
	_log.debug('hook script mode: %s (oktal: %s)', script_perms, oct(script_perms))
	if script_perms != 384:				# octal 0600
		if os.name in ['nt']:
			_log.warning('this platform does not support os.stat() file permission checking')
		else:
			gmDispatcher.send (
				signal = 'statustext',
				msg = _('Script must be readable by the calling user only (permissions "0600"): [%s].') % HOOK_SCRIPT_FULL_NAME
			)
			return False

	try:
		tmp = gmTools.import_module_from_directory(HOOK_SCRIPT_DIR, HOOK_SCRIPT_NAME)
	except Exception:
		_log.exception('cannot import hook script')
		return False

	hook_module = tmp
#	if reimport:
#		imp.reload(tmp)			# this has well-known shortcomings !

	_log.info('hook script: %s', HOOK_SCRIPT_FULL_NAME)
	return True

# ========================================================================
__current_hook_stack:list[str] = []

def run_hook_script(hook=None):
	# NOTE: this just *might* be a huge security hole

	_log.info('told to pull hook [%s]', hook)

	if hook not in known_hooks:
		raise ValueError('run_hook_script(): unknown hook [%s]' % hook)

	if not import_hook_module(reimport = False):
		_log.debug('cannot import hook module, not pulling hook')
		return False

	if hook in __current_hook_stack:
		_log.error('hook-code cycle detected, aborting')
		_log.error('current hook stack: %s', __current_hook_stack)
		return False

	__current_hook_stack.append(hook)

	try:
		hook_module.run_script(hook = hook)
	except Exception:
		_log.exception('error running hook script for [%s]', hook)
		gmDispatcher.send (
			signal = 'statustext',
			msg = _('Error running hook [%s] script.') % hook,
			beep = True
		)
		if __current_hook_stack[-1] != hook:
			_log.error('hook nesting error detected')
			_log.error('latest hook: expected [%s], found [%s]', hook, __current_hook_stack[-1])
			_log.error('current hook stack: %s', __current_hook_stack)
		else:
			__current_hook_stack.pop()
		return False

	if __current_hook_stack[-1] != hook:
		_log.error('hook nesting error detected')
		_log.error('latest hook: expected [%s], found [%s]', hook, __current_hook_stack[-1])
		_log.error('current hook stack: %s', __current_hook_stack)
	else:
		__current_hook_stack.pop()

	return True

# ========================================================================

setup_hook_dir()

if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	run_hook_script(hook = 'shutdown-post-GUI')
	run_hook_script(hook = 'post_patient_activation')
	run_hook_script(hook = 'invalid hook')

# ========================================================================
