"""This module encapsulates document level operations.

metadata layout:

self.__metadata		{}
 |
 >- 'id'			""
 |
 >- 'type ID'		""
 |
 >- 'type'			""
 |
 >- 'comment'		""
 |
 >- 'date'			""		(time stamp)
 |
 >- 'reference'		""
 |
 >- 'description'	""
 |
 >- 'patient id'	""
 |
 `- 'objects'		{}
  |
  `- oid			{}
   |
   >- 'file name'	""		(on the local disc, fully qualified)
   |
   >- 'index'		""		(... into page sequence)
   |
   >- 'size'		""		(in bytes)
   |
   `- 'comment' 	""

@copyright: GPL
"""
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmMedDoc.py,v $
__version__ = "$Revision: 1.1 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
#=======================================================================================

import gmLog
_log = gmLog.gmDefLog

import gmPG
from gmExceptions import ConstructorError

#============================================================
class gmMedDoc:

	def __init__(self, aPKey):
		"""Fails if

		- no connection to database possible
		- document referenced by aPKey does not exist.
		"""
		self.__backend = gmPG.ConnectionPool()
		self.__defconn = self.__backend.GetConnection('blobs')

		self.ID = aPKey			# == identity.id == primary key
		if not self.__pkey_exists():
			raise gmExceptions.ConstructorError, "No document with ID [%s] in database." % aPKey
	#--------------------------------------------------------
	def __pkey_exists(self):
		"""Does this primary key exist ?

		- true/false/None
		"""
		curs = self.__defconn.cursor()
		cmd = "select exists(select id from doc_med where id = %s);"
		try:
			curs.execute(cmd, self.ID)
		except:
			curs.close
			_log.LogException('>>>%s<<< failed' % (cmd % self.ID), sys.exc_info(), fatal=0)
			return None
		res = curs.fetchone()[0]
		curs.close()
		return res
	#--------------------------------------------------------
	def __del__(self):
		self.__backend.ReleaseConnection('blobs')
	#--------------------------------------------------------
	def __getitem__(self, item):
		if item == 'metadata':
			return self.__get_metadata()
	#--------------------------------------------------------
	def __get_metadata(self):
		"""Document meta data loader for GnuMed compatible database."""
		# FIXME: error handling !

		# sanity checks
		metadata = {}
		metadata['id'] = self.ID

		# start our transaction (done implicitely by defining a cursor)
		cursor = self.__defconn.cursor()

		# get document level metadata
		cmd = "SELECT patient_id, type, comment, date, ext_ref FROM doc_med WHERE id = %s;"
		try:
			cursor.execute(cmd, self.ID)
		except:
			cursor.close()
			_log.LogException('Cannot load document [%s] metadata.' % self.ID)
			return None
		result = cursor.fetchone()
		metadata['patient id'] = result[0]
		metadata['type ID'] = result[1]
		metadata['comment'] = result[2]
		metadata['date'] = result[3]
		metadata['reference'] = result[4]
		# translate type ID to localized verbose name
		cmd = "select name from v_i18n_doc_type where id = %s;"
		try:
			cursor.execute(cmd, metadata['type ID'])
			result = cursor.fetchone()
			metadata['type'] = result[0]
		except:
			_log.LogException('Cannot load document [%s] metadata.' % self.ID)
			metadata['type'] = _('unknown doc type')

		# get object level metadata for all objects of this document
		# FIXME !!!! oid -> id
		cmd = "SELECT oid, comment, seq_idx, octet_length(data) FROM doc_obj WHERE doc_id = %s;"
		try:
			cursor.execute(cmd, metadata['id'])
		except:
			cursor.close()
			_log.LogException('Cannot load document [%s] metadata.' % self.ID)
			return None
		matching_rows = cursor.fetchall()
		metadata['objects'] = {}
		for row in matching_rows:
			oid = row[0]
			# cDocument.metadata->objects->oid->comment/index
			tmp = {'comment': row[1], 'index': row[2], 'size': int(row[3])}
			metadata['objects'][oid] = tmp

		cursor.close()
		_log.Log(gmLog.lData, 'Meta data: %s' % metadata)

		return metadata
