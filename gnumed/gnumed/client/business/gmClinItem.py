"""GnuMed clinical item related business objects.

license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/Attic/gmClinItem.py,v $
# $Id: gmClinItem.py,v 1.16 2004-06-02 21:50:32 ncq Exp $
__version__ = "$Revision: 1.16 $"
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
	- instances ARE ASSUMED TO EXIST in the database
	- DOES verify its existence on instantiation (fetching data fails)
	- does NOT verify FK targets existence
	- does NOT create new entries in the database
	- does NOT lazy-fetch fields
	"""
	_service = "historica"
	#--------------------------------------------------------
	def __init__(self, aPK_obj = None):
		self._is_modified = False
		# check descendants
		#<DEBUG>
		self.__class__._cmd_fetch_payload
		self.__class__._cmds_store_payload
		self.__class__._updatable_fields
		#</DEBUG>
		self.pk_obj = aPK_obj
		result = self.refetch_payload()
		if result is True:
			return
		if result is None:
			raise gmExceptions.NoSuchClinItemError, "[%s:%s]: cannot find instance" % (self.__class__.__name__, self.pk_obj)
		if result is False:
			raise gmExceptions.ConstructorError, "[%s:%s]: error loading instance" % (self.__class__.__name__, self.pk_obj)
	#--------------------------------------------------------
	def __del__(self):
		if self.__dict__.has_key('_is_modified'):
			if self._is_modified:
				_log.Log(gmLog.lPanic, '[%s:%s]: loosing payload changes' % (self.__class__.__name__, self.pk_obj))
				_log.Log(gmLog.lData, self._payload)
	#--------------------------------------------------------
	def __str__(self):
		tmp = []
		[tmp.append('%s: %s' % (attr, self._payload[self._idx[attr]])) for attr in self._idx.keys()]
		return str(tmp)
	#--------------------------------------------------------
	def __getitem__(self, attribute):
		try:
			return self._payload[self._idx[attribute]]
		except KeyError:
			_log.Log(gmLog.lWarn, '[%s]: no attribute [%s]' % (self.__class__.__name__, attribute))
			_log.Log(gmLog.lWarn, '[%s]: valid attributes: %s' % (self.__class__.__name__, str(self._idx.keys())))
			raise gmExceptions.NoSuchClinItemAttributeError, '[%s]: no attribute [%s]' % (self.__class__.__name__, attribute)
	#--------------------------------------------------------
	def __setitem__(self, attribute, value):
		if attribute not in self.__class__._updatable_fields:
			_log.Log(gmLog.lWarn, '[%s]: settable attributes: %s' % (self.__class__.__name__, str(self.__class__._updatable_fields)))
			raise gmExceptions.ClinItemAttributeNotSettableError, '[%s]: attribute <%s> not settable' % (self.__class__.__name__, attribute)
		try:
			self._idx[attribute]
		except KeyError:
			_log.Log(gmLog.lWarn, '[%s]: valid attributes: %s' % (self.__class__.__name__, str(self.__class__._updatable_fields)))
			raise gmExceptions.NoSuchClinItemAttributeError, '[%s]: no attribute <%s>' % (self.__class__.__name__, attribute)
		self._payload[self._idx[attribute]] = value
		self._is_modified = True
		return True
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def is_modified(self):
		return self._is_modified
	#--------------------------------------------------------
	def get_fields(self):
		return self._idx.keys()
	#--------------------------------------------------------
	def get_updatable_fields(self):
		return self.__class__._updatable_fields
	#--------------------------------------------------------
	def refetch_payload(self):
		"""Fetch item values from backend.
		"""
		if self._is_modified:
			_log.Log(gmLog.lPanic, '[%s:%s]: cannot reload, payload changed' % (self.__class__.__name__, self.pk_obj))
			return False
		self._payload = None
		data, self._idx = gmPG.run_ro_query(
			self.__class__._service,
			self.__class__._cmd_fetch_payload,
			True,
			self.pk_obj)
		if data is None:
			_log.Log(gmLog.lErr, '[%s:%s]: error retrieving instance' % (self.__class__.__name__, self.pk_obj))
			return False
		if len(data) == 0:
			_log.Log(gmLog.lErr, '[%s:%s]: no such instance' % (self.__class__.__name__, self.pk_obj))
			return None
		self._payload = data[0]
		return True
	#--------------------------------------------------------
	def save_payload(self):
		if not self._is_modified:
			return (True, None)
		params = {}
		for field in self._idx.keys():
			params[field] = self._payload[self._idx[field]]
		queries = []
		for query in self.__class__._cmds_store_payload:
			queries.append((query, [params]))
		status, err = gmPG.run_commit(self.__class__._service, queries, True)
		if status is None:
			_log.Log(gmLog.lErr, '[%s:%s]: cannot update instance' % (self.__class__.__name__, self.pk_obj))
			_log.Log(gmLog.lData, params)
			return (None, err)
		self._is_modified = False
		return (True, None)
#============================================================
# $Log: gmClinItem.py,v $
# Revision 1.16  2004-06-02 21:50:32  ncq
# - much improved error logging in set/getitem()
#
# Revision 1.15  2004/06/02 12:51:47  ncq
# - add exceptions tailored to cClinItem __set/getitem__()
#   errors as per Syan's suggestion
#
# Revision 1.14  2004/05/22 08:09:10  ncq
# - more in line w/ coding style
# - _service will never change (or else it wouldn't
#   be cCLINitem) but it's still good coding practice
#   to put it into a class attribute
#
# Revision 1.13  2004/05/21 15:36:51  sjtan
#
# moved 'historica' into the class attribute SERVICE , in case gmClinItem can
# be reused in other services.
#
# Revision 1.12  2004/05/12 14:28:53  ncq
# - allow dict style pk definition in __init__ for multicolum primary keys (think views)
# - self.pk -> self.pk_obj
# - __init__(aPKey) -> __init__(aPK_obj)
#
# Revision 1.11  2004/05/08 22:13:11  ncq
# - cleanup
#
# Revision 1.10  2004/05/08 17:27:21  ncq
# - speed up __del__
# - use NoSuchClinItemError
#
# Revision 1.9  2004/04/20 13:32:33  ncq
# - improved __str__ output
#
# Revision 1.8  2004/04/19 12:41:30  ncq
# - self-check in __del__
#
# Revision 1.7  2004/04/18 18:50:36  ncq
# - override __init__() thusly removing the unholy _pre/post_init() business
#
# Revision 1.6  2004/04/18 17:51:28  ncq
# - it's surely helpful to be able to say <item>.is_modified() and know the status...
#
# Revision 1.5  2004/04/16 12:46:35  ncq
# - set is_modified=False after save_payload
#
# Revision 1.4  2004/04/16 00:00:59  ncq
# - Carlos fixes
# - save_payload should now work
#
# Revision 1.3  2004/04/12 22:53:19  ncq
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
