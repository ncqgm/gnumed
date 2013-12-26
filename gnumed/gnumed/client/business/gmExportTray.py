"""GNUmed export tray / filing cabinet.

Think shopping cart in a web shop.
"""
#============================================================
__license__ = "GPL v2 or later"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"


import sys
import logging
import shutil
import os


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmTools
#from Gnumed.pycommon import gmPG2
#from Gnumed.pycommon import gmDateTime

#from Gnumed.business import gmStaff

_log = logging.getLogger('gm.tray')
#============================================================
class cExportTray(object):

	def __init__(self, base_dir=None, directory):
		if base_dir is None:
			base_dir = gmTools.gmPaths().tmp_dir
		full_dir = os.path.join(base_dir, directory)
		if not gmTools.mkdir(directory = full_dir):
			raise ValueError('[%s.__init__()]: path [%s] is not valid' % (self.__class__.__name__, full_dir))
		self.__dir = full_dir
		_log.debug('export tray [%s]', self.__dir)
		self.__tray_items = {}
	#--------------------------------------------------------
	def add_file(self, filename=None, description=None, remove_source_file=False):

		src_filename = filename
		if description is None:
			description = src_filename

		# check for dupes
		try:
			item_fname = self.__tray_items[description]
			item_md5 = gmTools.file2md5(filename = item_fname, return_hex = False)
			src_md5 = gmTools.file2md5(filename = src_filename, return_hex = False)
			if item_md5 == src_md5:
				_log.debug('md5 match: [%s] (%s) already in tray as [%s]', description, src_filename, item_fname)
				return True
		except KeyError:
			pass
		except StandardError:
			_log.exception('cannot check [%s] for dupes in export tray [%s]', src_filename, self.__dir)
			return False

		# move into tray
		src_dir, src_name = os.path.split(src_filename)
		target_filename = os.path.join(self.__dir, src_name)
		try:
			shutil.copy2(src_filename, target_filename)
		except StandardError:
			_log.exception('cannot copy [%s] into export tray as [%s]', src_filename, target_filename)
			return False
		self.__tray_items[description] = target_filename

		# remove source
		if remove_source_file:
			try:
				os.remove(src_filename)
			except StandardError:
				_log.exception('cannot remove [%s]', src_filename)

		return True
	#--------------------------------------------------------
	def _get_tray_items(self):
		return self.__tray_items

	items = property(_get_tray_items, lambda x:x)
	#--------------------------------------------------------
	def _get_filenames(self):
		return self.__tray_items.values()

	filenames = property(_get_filenames, lambda x:x)
#============================================================
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.pycommon import gmI18N

	gmI18N.activate_locale()
	gmI18N.install_domain()

	#---------------------------------------
	def test_tray():
		tray = cExportTray(os.path.expanduser('~/tmp/'))
		print tray
		print tray.items
		print tray.filenames
	#---------------------------------------
	test_tray()
