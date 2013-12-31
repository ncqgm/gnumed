"""GNUmed export area

Think shopping cart in a web shop.

This is where you want to put documents for further
processing by you or someone else, like your secretary.
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
from Gnumed.pycommon import gmBusinessDBObject
from Gnumed.pycommon import gmPG2
#from Gnumed.pycommon import gmDateTime

#from Gnumed.business import gmStaff

_log = logging.getLogger('gm.exp_area')

#============================================================
# export area item handling
#------------------------------------------------------------
_SQL_get_export_items = u"SELECT * FROM clin.v_export_items WHERE %s"

class cExportItem(gmBusinessDBObject.cBusinessDBObject):
	"""Represents an item in the export area table"""

	_cmd_fetch_payload = _SQL_get_export_items % u"pk_export_item = %s"
	_cmds_store_payload = [
		u"""UPDATE clin.export_item SET
				fk_identity = CASE
					WHEN %(pk_doc_obj)s IS NULL THEN %(pk_identity)s
					ELSE NULL
				END,
				created_by = gm.nullify_empty_string(%(created_by)s),
				created_when = %(created_when)s,
				designation = gm.nullify_empty_string(%(designation)s),
				description = gm.nullify_empty_string(%(description)s),
				fk_doc_obj = %(pk_doc_obj)s,
				data = CASE
					WHEN %(pk_doc_obj)s IS NULL THEN coalesce(data, 'to be replaced by real data')
					ELSE NULL
				END
			WHERE
				pk = %(pk_export_item)s
					AND
				xmin = %(xmin_export_item)s
			RETURNING
				xmin AS xmin_export_item,
				created_by,
				md5(coalesce (
					data,
					coalesce((select b_do.data from blobs.doc_obj b_do where b_do.pk = fk_doc_obj),'')
				)) AS md5_sum
		"""
	]
	_updatable_fields = [
		u'pk_identity',
		u'created_by',
		u'pk_doc_obj'
	]
	#--------------------------------------------------------
#	def format(self):
#		return u'%s' % self

#------------------------------------------------------------
def get_export_items(order_by=None, pk_identity=None):

	args = {'pat': pk_identity}
	where_parts = [u'TRUE']

	if order_by is None:
		order_by = u''
	else:
		order_by = u' ORDER BY %s' % order_by

	if pk_identity is not None:
		where_parts.append(u'pk_identity = %(pat)s')

	cmd = _SQL_get_export_items % u' AND '.join(where_parts) + order_by
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = True)

	return [ cExportItem(row = {'data': r, 'idx': idx, 'pk_field': 'pk_export_item'}) for r in rows ]
#------------------------------------------------------------
def create_export_item(designation=None, description=None, pk_identity=None, pk_doc_obj=None):

	args = {
		u'desig': designation,
		u'desc': description,
		u'pk_obj': pk_doc_obj,
		u'pk_pat': pk_identity
	}
	cmd = u"""
		INSERT INTO clin.export_item (
			designation,
			description,
			fk_doc_obj,
			fk_identity,
			data
		) VALUES (
			gm.nullify_empty_string(%(desig)s),
			gm.nullify_empty_string(%(desc)s),
			%(pk_obj)s,
			CASE
				WHEN %(pk_obj)s IS NULL THEN %(pk_pat)s
				ELSE NULL
			END,
			CASE
				WHEN %(pk_obj)s IS NULL THEN 'to be replaced by real data'::bytea
				ELSE NULL
			END
		)
		RETURNING pk
		--RETURNING *
	"""
	rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True, get_col_idx = False)
	#rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True, get_col_idx = True)

	return cExportItem(aPK_obj = rows[0]['pk'])
	#return cExportItem(row = {'data': r, 'idx': idx, 'pk_field': 'pk_export_item'})

#------------------------------------------------------------
def delete_export_item(pk_export_item=None):
	args = {'pk': pk_export_item}
	cmd = u"DELETE FROM clin.export_item WHERE pk = %(pk)s"
	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
	return True
#------------------------------------------------------------




#============================================================
class cExportTray(object):

	def __init__(self):
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
	def test_export_items():
#		items = get_export_items()
#		for item in items:
#			print item.format()
#		import random
#		create_export_item(designation=None, description = 'description %s' % random.random(), pk_identity = 12, pk_doc_obj=None)
		items = get_export_items()
		for item in items:
			print item.format()
		item['pk_doc_obj'] = 1
		item.save()
		print item
	#---------------------------------------
	#test_tray()
	test_export_items()
