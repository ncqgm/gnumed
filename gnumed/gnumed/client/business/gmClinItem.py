"""GnuMed clinical item related business objects.

license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/Attic/gmClinItem.py,v $
# $Id: gmClinItem.py,v 1.3 2004-04-12 22:53:19 ncq Exp $
__version__ = "$Revision: 1.3 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

from Gnumed.pycommon import gmExceptions, gmLog, gmPG
from Gnumed.pycommon.gmPyCompat import *

_log = gmLog.gmDefLog
if __name__ == '__main__':
	_log.SetAllLogLevels(gmLog.lData)
_log.Log(gmLog.lInfo, __version__)

# FIXME: auto-discover audit_fields and clin_root_item fields

#============================================================
class cClinItem:
	"""Represents clinical data items.

	Rules:
	- instances DO EXIST in the database
	- verifies its existence upon instantiation
	- does NOT verify FK targets existence
	- does NOT create new entries in the database
	- NO lazy fetching of fields
	"""
	#--------------------------------------------------------
	def __init__(self, aPKey = None, **kwargs):
		self._is_modified = False
		#<DEBUG>
		# check descendants
		self.__class__._cmd_fetch_payload
		self.__class__._cmds_store_payload
		self.__class__._updatable_fields
		#</DEBUG>
		self.pk = aPKey
		if not self._pre_init(**kwargs):
			raise gmExceptions.ConstructorError, "[%s]: cannot init" % self.__class__.__name__
		if self.pk is None:
			raise gmExceptions.ConstructorError, "[%s]: must have primary key" % self.__class__.__name__
		if not self.refetch_payload():
			raise gmExceptions.ConstructorError, "[%s:%s]: cannot load instance" % (self.__class__.__name__, self.pk)
		if not self._post_init(**kwargs):
			raise gmExceptions.ConstructorError, "[%s]: cannot init" % self.__class__.__name__
	#--------------------------------------------------------
	def __del__(self):
		if self._is_modified:
			_log.Log(gmLog.lPanic, '[%s:%s]: loosing payload changes' % (self.__class__.__name__, self.pk))
			_log.Log(gmLog.lData, self._payload)
	#--------------------------------------------------------
	def __str__(self):
		return str(self._payload)
	#--------------------------------------------------------
	def __getitem__(self, attribute):
		try:
			return self._payload[self._idx[attribute]]
		except KeyError:
			_log.Log(gmLog.lWarn, '[%s]: no attribute [%s]' % (self.__class__.__name__, attribute))
			return False
	#--------------------------------------------------------
	def __setitem__(self, attribute, value):
		if attribute not in self.__class__._updatable_fields:
			raise KeyError, '[%s]: attribute <%s> not settable' % (self.__class__.__name__, attribute)
		try:
			self._idx[attribute]
		except KeyError:
			raise KeyError, '[%s]: no attribute <%s>' % (self.__class__.__name__, attribute)
		self._payload[self._idx[attribute]] = value
		self._is_modified = True
		return True
	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def _pre_init(self, **kwargs):
		return True
	#--------------------------------------------------------
	def _post_init(self, **kwargs):
		return True
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def get_fields(self):
		return self._idx.keys()
	#--------------------------------------------------------
	def get_updatable_fields(self):
		return self.__class__._updatable_fields
	#--------------------------------------------------------
	def refetch_payload(self):
		if self._is_modified:
			_log.Log(gmLog.lPanic, '[%s:%s]: cannot reload, payload changed' % (self.__class__.__name__, self.pk))
			return False
		self._payload = None
		data, self._idx = gmPG.run_ro_query(
			'historica',
			self.__class__._cmd_fetch_payload,
			True,
			self.pk)
		if data is None:
			_log.Log(gmLog.lErr, '[%s:%s]: error retrieving instance' % (self.__class__.__name__, self.pk))
			return False
		if len(data) == 0:
			_log.Log(gmLog.lErr, '[%s:%s]: instance not found' % (self.__class__.__name__, self.pk))
			return False
		self._payload = data[0]
		return True
	#--------------------------------------------------------
	def save_payload(self):
		if not self._is_modified:
			return (True, None)
		queries = []
		for query in self.__class__._cmds_store_payload:
			queries.append((query, [self._payload]))
		status, err = gmPG.run_commit('historica', queries, True)
		if status is None:
			_log.Log(gmLog.lErr, '[%s:%s]: cannot update instance' % (self.__class__.__name__, self.pk))
			_log.Log(gmLog.lData, self._payload)
			return (None, err)
		return (True, None)
#============================================================
# $Log: gmClinItem.py,v $
# Revision 1.3  2004-04-12 22:53:19  ncq
# - __init__ now handles arbitrary keyword args
# - _pre_/_post_init()
# - streamline
# - must do _payload[self._idx[attribute]] since payload not a dict
#
# Revision 1.2  2004/04/11 11:24:00  ncq
# - handle _is_modified
# - protect against reload if modified
#
# Revision 1.1  2004/04/11 10:16:53  ncq
# - first version
#
