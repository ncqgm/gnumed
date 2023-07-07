# -*- coding: utf-8 -*-
"""Handling of automatic file import from certain directories."""
#============================================================
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"


import sys
import os
import logging


if __name__ == '__main__':
	sys.path.insert(0, '../../')

from Gnumed.pycommon import gmI18N
if __name__ == '__main__':
	gmI18N.activate_locale()
	gmI18N.install_domain()
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmDateTime
from Gnumed.business import gmIncomingData


_log = logging.getLogger('gm.autoimport')

#============================================================
def _worker__auto_import_files():
	"""Import files. Will run in a thread."""
	cAutoImportDir().import_files()

#============================================================
__default_dirs_created = False

def setup_default_import_dirs() -> bool:
	global __default_dirs_created
	if __default_dirs_created:
		return True

	_log.debug('setting up default auto-import directories')
	paths = [
		# aka "~/gnumed/"
		os.path.join(gmTools.gmPaths().user_work_dir, 'auto-import'),
		# aka ".gnumed/"
		os.path.join(gmTools.gmPaths().user_appdata_dir, 'auto-import')
	]
	README = """GNUmed Electronic Medical Record

	for user interaction:
		%s/

	for programmatic interaction:
		%s/

Files dropped into this directory and its subdirectories will
be auto-imported into the GNUmed incoming area.

Rules:

	- inaccessible files will be ignored

	- filenames ending in ".imported" will be ignored

	- filenames ending in ".new" will be ignored, unless
	  the file was last modified more than 24 hours ago

	- successfully imported files will be renamed to
	  ".FILENAME.CURRENT_TIMESTAMP.imported"

	- files already existing in the database (based on
	  MD5 of the file content) will be removed

	- only one level of subdirectories is scanned for files

	- subdirectories will not be removed, even if empty

How to safely drop files into this directory:

	Copy in the file with a filename ending in ".new". When
	done copying rename it by removing the ".new" suffix. Renaming
	in-place is expected to be a safe (atomic) operation.
""" % tuple(paths)
	for path in paths:
		_log.debug(path)
		if gmTools.mkdir(directory = path):
			gmTools.create_directory_description_file(directory = path, readme = README)
			continue
		_log.error('cannot create default auto-import dir [%s]', path)
		return False

	__default_dirs_created = True
	return True

#============================================================
class cAutoImportDir:
	"""Represents a directory from which files are auto-imported into the GNUmed database.

	Args:
		path: None -> default path, otherwise an existing directory

	Default directories:

		* ~/gnumed/auto-incoming/ (will be auto-created)
		* ~/.local/gnumed/auto-incoming/ (will be auto-created)
	"""
	def __init__(self, path:str=None):
		if path:
			path = gmTools.normalize_path(path)
			if not os.path.isdir(path):
				raise EnvironmentError('auto-import path [%s] not accessible', path)

			self.__paths = [path]
			_log.info(self.__paths)
			return

		if not setup_default_import_dirs():
			raise EnvironmentError('cannot create default auto-import path [%s]', path)

		self.__paths = [
			# aka "~/gnumed/"
			os.path.join(gmTools.gmPaths().user_work_dir, 'auto-import'),
			# aka ".gnumed/"
			os.path.join(gmTools.gmPaths().user_appdata_dir, 'auto-import')
		]
		_log.info(self.__paths)

	#--------------------------------------------------------
	def import_files(self):
		sub_dirs = []
		for basedir in self.__paths:
			for entry in gmTools.dir_list_files(directory = basedir, exclude_subdirs = False):
				path = os.path.join(basedir, entry)
				if os.path.isdir(path):
					sub_dirs.append(path)
		for import_dir in self.__paths + sub_dirs:
			self.__import_files_from_dir(import_dir)
		return

	#--------------------------------------------------------
	# internal halpers
	#--------------------------------------------------------
	def __import_files_from_dir(self, import_dir:str) -> bool:
		if not os.path.isdir(import_dir):
			_log.error('[%s] not a directory', import_dir)
			return False

		_log.debug('importing from [%s]', import_dir)
		entries = gmTools.dir_list_files(directory = import_dir, exclude_subdirs = True)
		for path in entries:
			self.__import_file(path)
		return True

	#--------------------------------------------------------
	def __import_file(self, filename:str, max_size:int=None) -> bool:
		_log.debug(filename)
		if  gmTools._GM_DIR_DESC_FILENAME_PREFIX in filename:
			_log.debug('... skipped')
			return True

		if filename.endswith('.imported'):
			_log.debug('... skipped')
			return True

		now = gmDateTime.pydt_now_here()
		if filename.endswith('.new'):
			try:
				ts_created = os.path.getmtime(filename)
			except OSError:
				_log.debug('... cannot getmtime()')
				return False

			# ignore "new" files only if younger than 24 hours
			if (now.timestamp() - ts_created) < (24 * 3600):
				_log.debug('... skipped')
				return True

		try:
			fsize = os.path.getsize(filename)
		except OSError:
			_log.debug('... cannot getsize()')
			return False

		# FIXME: make configurable
		max_size = max_size or (20 * gmTools._MB)
		if fsize > max_size:
			_log.debug('... skipped, file %s > max %s', fsize, max_size)
			return True

		if gmIncomingData.data_exists(filename):
			_log.debug('... exists')
			gmTools.remove_file(filename)
			return True

		incoming = gmIncomingData.create_incoming_data(filename = filename, verify_import = True)
		if not incoming:
			return False

		incoming['comment'] = _('%s (auto-import %s)' % (filename, now))
		incoming.save()
		new_fname = '.%s.%s.imported' % (
			gmTools.fname_from_path(filename),
			now.timestamp()
		)
		gmTools.rename_file (
			filename,
			os.path.join(gmTools.fname_dir(filename), new_fname),
			overwrite = True,
			allow_symlink = False,
			allow_hardlink = False
		)
		return True

#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	gmDateTime.init()
	gmTools.gmPaths()

	#-------------------------------------------------------
	def test():
		imp_dir = cAutoImportDir()
		gmPG2.request_login_params(setup_pool = True)
		imp_dir.import_files()

	#-------------------------------------------------------
	test()
