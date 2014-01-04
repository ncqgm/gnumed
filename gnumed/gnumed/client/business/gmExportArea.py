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
import codecs


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmBusinessDBObject
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmMimeLib
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmCfg2

from Gnumed.business import gmDocuments

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
		""",
		_SQL_get_export_items % u'pk_export_item = %(pk_export_item)s'
	]
	_updatable_fields = [
		u'pk_identity',
		u'created_when',
		u'designation',
		u'description',
		u'pk_doc_obj'
	]
	#--------------------------------------------------------
#	def format(self):
#		return u'%s' % self
	#--------------------------------------------------------
	def update_data_from_file(self, fname=None):
		# sanity check
		if not (os.access(fname, os.R_OK) and os.path.isfile(fname)):
			_log.error('[%s] is not a readable file' % fname)
			return False

		cmd = u"UPDATE clin.export_item SET data = %(data)s::bytea, fk_doc_obj = NULL WHERE pk = %(pk)s"
		args = {'pk': self.pk_obj}
		if not gmPG2.file2bytea(query = cmd, filename = fname, args = args):
			return False

		# must update XMIN now ...
		self.refetch_payload()
		return True
	#--------------------------------------------------------
	def export_to_file(self, aChunkSize=0, filename=None, directory=None):

		if self._payload[self._idx['pk_doc_obj']] is not None:
			return self.document_part.export_to_file (
				aChunkSize = aChunkSize,
				filename = filename,
				ignore_conversion_problems = True,
				directory = directory
			)

		if filename is None:
			filename = self.get_useful_filename(directory = directory)

		success = gmPG2.bytea2file (
			data_query = {
				'cmd': u'SELECT substring(data from %(start)s for %(size)s) FROM clin.export_item WHERE pk = %(pk)s',
				'args': {'pk': self.pk_obj}
			},
			filename = filename,
			chunk_size = aChunkSize,
			data_size = self._payload[self._idx['size']]
		)

		if not success:
			return None

		return filename
	#--------------------------------------------------------
	def display_via_mime(self, chunksize=0, block=None):

		if self._payload[self._idx['pk_doc_obj']] is not None:
			return self.document_part.display_via_mime(chunksize = chunksize, block = block)

		fname = self.export_to_file(aChunkSize = chunksize)
		if fname is None:
			return False, ''

		success, msg = gmMimeLib.call_viewer_on_file(fname, block = block)
		if not success:
			return False, msg

		return True, ''
	#--------------------------------------------------------
	def get_useful_filename(self, patient=None, directory=None):
		patient_part = ''
		if patient is not None:
			patient_part = '-%s' % patient['dirname']

		fname = gmTools.get_unique_filename (
			prefix = 'gm-export_item%s-' % patient_part,
			suffix = '.dat',
			tmp_dir = directory
		)

		return os.path.join(directory, fname)
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_doc_part(self):
		if self._payload[self._idx['pk_doc_obj']] is None:
			return None
		return gmDocuments.cDocumentPart(aPK_obj = self._payload[self._idx['pk_doc_obj']])

	document_part = property(_get_doc_part, lambda x:x)
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

	cmd = (_SQL_get_export_items % u' AND '.join(where_parts)) + order_by
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)

	return [ cExportItem(row = {'data': r, 'idx': idx, 'pk_field': 'pk_export_item'}) for r in rows ]
#------------------------------------------------------------
def create_export_item(description=None, pk_identity=None, pk_doc_obj=None):

	args = {
		u'desc': description,
		u'pk_obj': pk_doc_obj,
		u'pk_pat': pk_identity
	}
	cmd = u"""
		INSERT INTO clin.export_item (
			description,
			fk_doc_obj,
			fk_identity,
			data
		) VALUES (
			gm.nullify_empty_string(%(desc)s),
			%(pk_obj)s,
			(CASE
				WHEN %(pk_obj)s IS NULL THEN %(pk_pat)s
				ELSE NULL::integer
			END),
			(CASE
				WHEN %(pk_obj)s IS NULL THEN 'to be replaced by real data'::bytea
				ELSE NULL::bytea
			END)
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

#============================================================
_html_start = u"""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
       "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=UTF-8">
<title>Patient data for %s</title>
</head>
<body>

<h1>Patient data export</h1>

<h2>Demographics</h2>

<p>
	%s<br>
	%s
</p>

<h2>Documents</h2>

<ul>
"""

# <li><a href="documents/filename-1.ext">document 1 description</a></li>
_html_list_item = u"""	<li><a href="documents/%s">%s</a></li>
"""

_html_end = u"""
</ul>

%s, GNUmed version %s

</body>
</html>
"""

_autorun_inf = (
u'[AutoRun]\r\n'						# needs \r\n for Windows
u'label=%s\r\n'							# patient name/DOB
u'shellexecute=index.html\r\n'
u'action=%s\r\n'						# % _('Browse patient data')
u'\r\n'
u'[Content]\r\n'
u'PictureFiles=yes\r\n'
u'VideoFiles=yes\r\n'
u'MusicFiles=no\r\n'
u'\r\n'
u'[IgnoreContentPaths]\r\n'
u'\documents\r\n'
u'\r\n'
u'[unused]\r\n'
u'open=requires explicit executable\r\n'
u'icon=use standard icon for storage unit\r\n'
)

_README = u"""This is a patient data bundle created by the GNUmed Electronic Medical Record.

Patient: %s

Please display <index.html> to browse patient data.

Individual documents are stored under

	./documents/
"""

#------------------------------------------------------------
class cExportArea(object):

	def __init__(self, pk_identity):
		self.__pk_identity = pk_identity

	#--------------------------------------------------------
	def add_files(self, filenames=None):
		for fname in filenames:
			try:
				open(fname).close()
			except StandardError:
				_log.exception('cannot open file <%s>', fname)
				return False

		all_ok = True
		for fname in filenames:
			path, basename = os.path.split(fname)
			item = create_export_item (
				description = _(u'file: %s (%s/)') % (basename, path),
				pk_identity = self.__pk_identity
			)
			all_ok = all_ok and item.update_data_from_file(fname = fname)

		return all_ok
	#--------------------------------------------------------
	def add_documents(self, documents=None):
		for doc in documents:
			for obj in doc.parts:
				if self.document_part_item_exists(pk_part = obj['pk_obj']):
					continue
				create_export_item (
					description = _('doc: %s') % obj.format_single_line(),
					pk_doc_obj = obj['pk_obj']
				)
	#--------------------------------------------------------
	def document_part_item_exists(self, pk_part=None):
		cmd = u"SELECT EXISTS (SELECT 1 FROM clin.export_item WHERE fk_doc_obj = %(pk_obj)s)"
		args = {'pk_obj': pk_part}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		return rows[0][0]
	#--------------------------------------------------------
	def export_with_meta_data(self, base_dir=None, items=None):

		if items is None:
			items_found = self.items

		if len(items) == 0:
			return None

		if base_dir is None:
			base_dir = gmTools.get_unique_filename(prefix = u'gm-patient_export-', suffix = '.dir')

		_log.debug('base dir: %s', base_dir)

		doc_dir = os.path.join(base_dir, r'documents')
		gmTools.mkdir(doc_dir)

		from Gnumed.business.gmPerson import cIdentity
		pat = cIdentity(aPK_obj = self.__pk_identity)

		# index.html
		idx_fname = os.path.join(base_dir, u'index.html')
		idx_file = codecs.open(idx_fname, u'wb', u'utf8')
		# header
		idx_file.write(_html_start % (
			gmTools.html_escape_string(pat['description_gender'] + u', ' + _(u'born') + u' ' + pat.get_formatted_dob('%Y %B %d')),
			gmTools.html_escape_string(pat['description_gender']),
			gmTools.html_escape_string(_(u'born') + u' ' + pat.get_formatted_dob('%Y %B %d'))
		))
		# middle
		for item in items:
			item_path = item.export_to_file(directory = doc_dir)
			item_fname = os.path.split(item_path)[1]
			idx_file.write(_html_list_item % (
				item_fname,
				gmTools.html_escape_string(item['description'])
			))
		# footer
		_cfg = gmCfg2.gmCfgData()
		idx_file.write(_html_end % (
			gmTools.html_escape_string(gmDateTime.pydt_strftime(gmDateTime.pydt_now_here(), u'%Y %B %d')),
			gmTools.html_escape_string(_cfg.get(option = u'client_version'))
		))
		idx_file.close()

		# autorun.inf
		autorun_fname = os.path.join(base_dir, u'autorun.inf')
		autorun_file = codecs.open(autorun_fname, u'wb', u'utf8')
		autorun_file.write(_autorun_inf % (
			(pat['description_gender'] + u', ' + _(u'born') + u' ' + pat.get_formatted_dob('%Y %B %d')).strip(),
			_('Browse patient data')
		))
		autorun_file.close()

		# README
		readme_fname = os.path.join(base_dir, u'README')
		readme_file = codecs.open(readme_fname, u'wb', u'utf8')
		readme_file.write(_README % (
			pat['description_gender'] + u', ' + _(u'born') + u' ' + pat.get_formatted_dob('%Y %B %d')
		))
		readme_file.close()

		return base_dir
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_items(self):
		return get_export_items(order_by = u'designation, description', pk_identity = self.__pk_identity)

	items = property(_get_items, lambda x:x)

#============================================================
class cExportTray(object):

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
		import random
		create_export_item(description = 'description %s' % random.random(), pk_identity = 12, pk_doc_obj = None)
		items = get_export_items()
		for item in items:
			print item.format()
		item['pk_doc_obj'] = 1
		item.save()
		print item
	#---------------------------------------
	def test_export_area():
		exp = cExportArea(12)
		print exp.export_with_meta_data()
	#---------------------------------------
	#test_tray()
	#test_export_items()
	test_export_area()
