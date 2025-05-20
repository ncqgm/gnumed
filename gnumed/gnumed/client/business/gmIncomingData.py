# -*- coding: utf-8 -*-
"""Handling of <INCOMING> area."""
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
from Gnumed.pycommon import gmBusinessDBObject
from Gnumed.pycommon import gmPG2


_log = logging.getLogger('gm.import')

#============================================================
# class to handle unmatched incoming clinical data
#------------------------------------------------------------
_SQL_get_incoming_data = """SELECT * FROM clin.v_incoming_data WHERE %s"""

class cIncomingData(gmBusinessDBObject.cBusinessDBObject):
	"""Represents items of incoming data, say, HL7 snippets."""

	_cmd_fetch_payload = _SQL_get_incoming_data % "pk_incoming_data = %s"
	_cmds_store_payload = [
		"""UPDATE clin.incoming_data SET
				fk_patient_candidates = %(pk_patient_candidates)s,
				fk_identity = %(pk_identity)s,
				fk_provider_disambiguated = %(pk_provider_disambiguated)s,
				request_id = gm.nullify_empty_string(%(request_id)s),
				firstnames = gm.nullify_empty_string(%(firstnames)s),
				lastnames = gm.nullify_empty_string(%(lastnames)s),
				dob = %(dob)s,
				postcode = gm.nullify_empty_string(%(postcode)s),
				other_info = gm.nullify_empty_string(%(other_info)s),
				type = gm.nullify_empty_string(%(data_type)s),
				gender = gm.nullify_empty_string(%(gender)s),
				requestor = gm.nullify_empty_string(%(requestor)s),
				external_data_id = gm.nullify_empty_string(%(external_data_id)s),
				comment = gm.nullify_empty_string(%(comment)s)
			WHERE
				pk = %(pk_incoming_data)s
					AND
				xmin = %(xmin_incoming_data)s
			RETURNING
				xmin as xmin_incoming_data,
				octet_length(data) as data_size
		"""
	]
	# view columns that can be updated:
	_updatable_fields = [
		'pk_patient_candidates',
		'request_id',						# request ID as found in <data>
		'firstnames',
		'lastnames',
		'dob',
		'postcode',
		'other_info',						# other identifying info in .data
		'data_type',
		'gender',
		'requestor',						# Requestor of data (e.g. who ordered test results) if available in source data.
		'external_data_id',				# ID of content of .data in external system (e.g. importer) where appropriate
		'comment',							# a free text comment on this row, eg. why is it here, error logs etc
		'pk_identity',
		'pk_provider_disambiguated'		# The provider the data is relevant to.
	]
	#--------------------------------------------------------
	def format(self):
		return '%s' % self
	#--------------------------------------------------------
	def _format_patient_identification(self):
		tmp = '%s %s %s' % (
			gmTools.coalesce(self._payload['lastnames'], '', 'last=%s'),
			gmTools.coalesce(self._payload['firstnames'], '', 'first=%s'),
			gmTools.coalesce(self._payload['gender'], '', 'gender=%s')
		)
		if self._payload['dob']:
			tmp += ' dob=%s' % self._payload['dob'].strftime('%Y %b %d')
		return tmp

	patient_identification = property(_format_patient_identification)

	#--------------------------------------------------------
	def update_data_from_file(self, fname=None, link_obj=None, verify_import:bool=False):
		# sanity check
		if not (os.access(fname, os.R_OK) and os.path.isfile(fname)):
			_log.error('[%s] is not a readable file' % fname)
			return False

		_log.debug('updating [pk=%s] from [%s]', self.pk_obj, fname)
		gmPG2.file2bytea (
			query = "UPDATE clin.incoming_data SET data = %(data)s::bytea WHERE pk = %(pk)s",
			filename = fname,
			args = {'pk': self.pk_obj},
			conn = link_obj
		)
		# must update XMIN now ...
		self.refetch_payload(link_obj = link_obj)
		if not verify_import:
			return True

		SQL = 'SELECT (md5(data) = %(local_md5)s) AS verified FROM clin.incoming_data WHERE pk = %(pk)s'
		args = {'pk': self.pk_obj, 'local_md5': gmTools.file2md5(filename = fname)}
		rows = gmPG2.run_ro_query(sql = SQL, args = args)
		return rows[0]['verified']

	#--------------------------------------------------------
	def save_to_file(self, aChunkSize=0, filename=None):

		if self._payload['data_size'] == 0:
			return None

		if self._payload['data_size'] is None:
			return None

		if filename is None:
			filename = gmTools.get_unique_filename(prefix = 'gm-incoming_data-')

		success = gmPG2.bytea2file (
			data_query = {
				'sql': 'SELECT substring(data from %(start)s for %(size)s) FROM clin.incoming_data WHERE pk = %(pk)s',
				'args': {'pk': self.pk_obj}
			},
			filename = filename,
			chunk_size = aChunkSize,
			data_size = self._payload['data_size']
		)

		if not success:
			return None

		return filename

	#--------------------------------------------------------
	def lock(self, exclusive=False):
		return gmPG2.lock_row(table = 'clin.incoming_data', pk = self.pk_obj, exclusive = exclusive)

	#--------------------------------------------------------
	def unlock(self, exclusive=False):
		return gmPG2.unlock_row(table = 'clin.incoming_data', pk = self.pk_obj, exclusive = exclusive)

	#--------------------------------------------------------
	def set_patient(self, patient):
		if patient is None:
			pk_pat = None
		elif isinstance(patient, int):
			pk_pat = patient
		else:
			pk_pat = patient['pk_identity']
		if self['pk_identity'] == pk_pat:
			return

		self['pk_identity'] = pk_pat

	patient = property(fset = set_patient)

#------------------------------------------------------------
def get_incoming_data(order_by=None, return_pks=False):
	if order_by is None:
		order_by = 'true'
	else:
		order_by = 'true ORDER BY %s' % order_by
	SQL = _SQL_get_incoming_data % order_by
	rows = gmPG2.run_ro_query(sql = SQL)
	if return_pks:
		return [ r['pk_incoming_data'] for r in rows ]

	return [ cIncomingData(row = {'data': r, 'pk_field': 'pk_incoming_data'}) for r in rows ]

#------------------------------------------------------------
def create_incoming_data(data_type:str=None, filename:str=None, verify_import:bool=False) -> cIncomingData:
	conn = gmPG2.get_connection(readonly = False)
	args = {'typ': data_type}
	SQL = """
		INSERT INTO clin.incoming_data (type, data)
		VALUES (%(typ)s, 'new data'::bytea)
		RETURNING pk"""
	rows = gmPG2.run_rw_query (
		link_obj = conn,
		end_tx = False,
		sql = SQL,
		args = args,
		return_data = True
	)
	pk = rows[0]['pk']
	incoming = cIncomingData(aPK_obj = pk, link_obj = conn)
	if incoming.update_data_from_file(fname = filename, link_obj = conn, verify_import = verify_import):
		conn.commit()
		return incoming

	conn.rollback()
	_log.debug('cannot update incoming_data stub from file, rolled back')
	return None

#------------------------------------------------------------
def delete_incoming_data(pk_incoming_data=None):
	SQL = "DELETE FROM clin.incoming_data WHERE pk = %(pk)s"
	args = {'pk': pk_incoming_data}
	gmPG2.run_rw_query(sql = SQL, args = args)
	return True

#------------------------------------------------------------
def data_exists(filename:str) -> bool:
	"""Check by md5 hash whether data in filename already in database."""
	local_md5 = gmTools.file2md5(filename = filename)
	SQL = 'SELECT EXISTS(SELECT 1 FROM clin.incoming_data WHERE md5(data) = %(local_md5)s) AS data_exists'
	args = {'local_md5': local_md5}
	rows = gmPG2.run_ro_query(sql = SQL, args = args)
	return rows[0]['data_exists']

#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	gmTools.gmPaths()

	#-------------------------------------------------------
	def test_incoming_data():
		for d in get_incoming_data():
			print(d)

	#-------------------------------------------------------
	gmPG2.request_login_params(setup_pool = True)
	test_incoming_data()
