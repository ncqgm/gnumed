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
from Gnumed.pycommon import gmDateTime


_log = logging.getLogger('gm.import')

#============================================================
# class to handle unmatched incoming clinical data
#------------------------------------------------------------
_SQL_get_incoming_data = """SELECT * FROM clin.v_incoming_data_unmatched WHERE %s"""

class cIncomingData(gmBusinessDBObject.cBusinessDBObject):
	"""Represents items of incoming data, say, HL7 snippets."""

	_cmd_fetch_payload = _SQL_get_incoming_data % "pk_incoming_data_unmatched = %s"
	_cmds_store_payload = [
		"""UPDATE clin.incoming_data_unmatched SET
				fk_patient_candidates = %(pk_patient_candidates)s,
				fk_identity_disambiguated = %(pk_identity_disambiguated)s,
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
				pk = %(pk_incoming_data_unmatched)s
					AND
				xmin = %(xmin_incoming_data_unmatched)s
			RETURNING
				xmin as xmin_incoming_data_unmatched,
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
		'pk_identity_disambiguated',
		'pk_provider_disambiguated'		# The provider the data is relevant to.
	]
	#--------------------------------------------------------
	def format(self):
		return '%s' % self
	#--------------------------------------------------------
	def _format_patient_identification(self):
		tmp = '%s %s %s' % (
			gmTools.coalesce(self._payload[self._idx['lastnames']], '', 'last=%s'),
			gmTools.coalesce(self._payload[self._idx['firstnames']], '', 'first=%s'),
			gmTools.coalesce(self._payload[self._idx['gender']], '', 'gender=%s')
		)
		if self._payload[self._idx['dob']] is not None:
			tmp += ' dob=%s' % gmDateTime.pydt_strftime(self._payload[self._idx['dob']], '%Y %b %d')
		return tmp

	patient_identification = property(_format_patient_identification)

	#--------------------------------------------------------
	def update_data_from_file(self, fname=None):
		# sanity check
		if not (os.access(fname, os.R_OK) and os.path.isfile(fname)):
			_log.error('[%s] is not a readable file' % fname)
			return False

		_log.debug('updating [pk=%s] from [%s]', self.pk_obj, fname)
		gmPG2.file2bytea (
			query = "UPDATE clin.incoming_data_unmatched SET data = %(data)s::bytea WHERE pk = %(pk)s",
			filename = fname,
			args = {'pk': self.pk_obj}
		)

		# must update XMIN now ...
		self.refetch_payload()
		return True

	#--------------------------------------------------------
	def save_to_file(self, aChunkSize=0, filename=None):

		if self._payload[self._idx['data_size']] == 0:
			return None

		if self._payload[self._idx['data_size']] is None:
			return None

		if filename is None:
			filename = gmTools.get_unique_filename(prefix = 'gm-incoming_data_unmatched-')

		success = gmPG2.bytea2file (
			data_query = {
				'cmd': 'SELECT substring(data from %(start)s for %(size)s) FROM clin.incoming_data_unmatched WHERE pk = %(pk)s',
				'args': {'pk': self.pk_obj}
			},
			filename = filename,
			chunk_size = aChunkSize,
			data_size = self._payload[self._idx['data_size']]
		)

		if not success:
			return None

		return filename

	#--------------------------------------------------------
	def lock(self, exclusive=False):
		return gmPG2.lock_row(table = 'clin.incoming_data_unmatched', pk = self.pk_obj, exclusive = exclusive)

	#--------------------------------------------------------
	def unlock(self, exclusive=False):
		return gmPG2.unlock_row(table = 'clin.incoming_data_unmatched', pk = self.pk_obj, exclusive = exclusive)

#------------------------------------------------------------
def get_incoming_data(order_by=None, return_pks=False):
	if order_by is None:
		order_by = 'true'
	else:
		order_by = 'true ORDER BY %s' % order_by
	cmd = _SQL_get_incoming_data % order_by
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = True)
	if return_pks:
		return [ r['pk_incoming_data_unmatched'] for r in rows ]
	return [ cIncomingData(row = {'data': r, 'idx': idx, 'pk_field': 'pk_incoming_data_unmatched'}) for r in rows ]

#------------------------------------------------------------
def create_incoming_data(data_type, filename):
	args = {'typ': data_type}
	cmd = """
		INSERT INTO clin.incoming_data_unmatched (type, data)
		VALUES (%(typ)s, 'new data'::bytea)
		RETURNING pk"""
	rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True, get_col_idx = False)
	pk = rows[0]['pk']
	incoming = cIncomingData(aPK_obj = pk)
	if not incoming.update_data_from_file(fname = filename):
		_log.debug('cannot update newly created incoming_data record from file, deleting stub')
		delete_incoming_data(pk_incoming_data = pk)
		return None

	return incoming

#------------------------------------------------------------
def delete_incoming_data(pk_incoming_data=None):
	args = {'pk': pk_incoming_data}
	cmd = "DELETE FROM clin.incoming_data_unmatched WHERE pk = %(pk)s"
	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
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
	def test_incoming_data():
		for d in get_incoming_data():
			print(d)

	#-------------------------------------------------------
	test_incoming_data()
