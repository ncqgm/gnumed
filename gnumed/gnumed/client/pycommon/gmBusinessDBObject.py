"""GnuMed database object business class.

This class in most cases wraps a denormalizing view which
represents an entity that makes immediate business sense
such as a vaccination or a medical document. The data in
that view will in most cases, however, originate from
several normalized tables. One instance of this class
represents one row of the "main" source (eg. mostly view).

There are two ways to initialize an instance with values.
One way is to pass a "primary key equivalent" object into
__init__(). Refetch_payload() will then pull the data from
the backend. Another way would be to fetch the data outside
the instance and pass it in via the <row> argument. In that
case the instance will not initially connect to the databse
which may offer a great boost to performance.

Field values are cached for later access. They can be accessed
by a dictionary API, eg:

	old_value = object['field']
	object['field'] = new_value

The field names correspond to the respective column names
in the "main" source. Accessing non-existant field names
will raise an error, so does trying to set fields not
listed in self.__class__._updatable_fields. To actually
store updated values in the database one must explicitely
call save_payload().

The class will in many cases be enhanced by accessors to
related data that is not directly part of the business
object itself but are closely related, such as codes
linked to a clinical narrative entry (eg a diagnosis). Such
accessors in most cases start with get_*.

Note that this class does not always simply wrap a single
table or view, however. It can also encompass several
relations (views, tables, sequences etc) that taken together
form an object meaningful to *business* logic.
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/gmBusinessDBObject.py,v $
# $Id: gmBusinessDBObject.py,v 1.2 2004-10-12 18:37:45 ncq Exp $
__version__ = "$Revision: 1.2 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

from Gnumed.pycommon import gmExceptions, gmLog, gmPG
from Gnumed.pycommon.gmPyCompat import *

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)
#============================================================
class cBusinessDBObject:
	"""Represents business objects in the database.

	Rules:
	- instances ARE ASSUMED TO EXIST in the database
	- PK construction (aPK_obj): DOES verify its existence on instantiation
	                             (fetching data fails)
	- Row construction (row_data): allowed by using a dict of pairs
	                               field name: field value (PERFORMANCE improvement)
	- does NOT verify FK target existence
	- does NOT create new entries in the database
	- does NOT lazy-fetch fields on access
	"""
	#--------------------------------------------------------
	def __init__(self, aPK_obj=None, row=None, debug=False):
		"""Init from backend.

		Eventually, if debug is true, the class may verify the
		row data structure and existence.
		"""
		self._is_modified = False
		# check descendants
		#<DEBUG>
		self.__class__._cmd_fetch_payload
		self.__class__._cmds_store_payload
		self.__class__._updatable_fields
		self.__class__._service
#		if self.__class__._service is None:
#			raise AttributeError, '[%s:%s]: _service must be overriden' % (self.__class__.__name__, self.pk_obj)
		#</DEBUG>
		if aPK_obj is not None:
			self.__init_from_pk(aPK_obj=aPK_obj)
		else:
			self.__init_from_row_data(row=row)
	#--------------------------------------------------------
	def __init_from_pk(self, aPK_obj=None):
		"""Creates a new clinical item instance by its PK.

		aPK_obj can be:
			- a simple value
			  * the primary key WHERE condition must be
				a simple column
			- a dictionary of values
			  * the primary key where condition must be a
				subselect consuming the dict and producing
				the single-value primary key
		"""
		self.pk_obj = aPK_obj
		result = self.refetch_payload()
		if result is True:
			return True
		if result is None:
			raise gmExceptions.NoSuchBusinessObjectError, "[%s:%s]: cannot find instance" % (self.__class__.__name__, self.pk_obj)
		if result is False:
			raise gmExceptions.ConstructorError, "[%s:%s]: error loading instance" % (self.__class__.__name__, self.pk_obj)
	#--------------------------------------------------------
	def __init_from_row_data(self, row=None):
		"""Creates a new clinical item instance given its fields.

		row must be a dict with the fields:
			- pk_field: the name of the primary key field
			- idx: a dict mapping field names to position
			- data: the field values in a list (as returned by
			  cursor.fetchone() in the DB-API)
		"""
		try:
			self._idx = row['idx']
			self._payload = row['data']
			self.pk_obj = self._payload[self._idx[row['pk_field']]]
		except:
			_log.LogException('faulty <row> argument structure: %s' % row, sys.exc_info())
#		self._idx = {}
#		self._payload = []
#		if row_data is None or len(row_data) == 0:
			raise gmExceptions.ConstructorError, "[%s:??]: error loading instance from row data" % self.__class__.__name__
#		try:
#			for field_name in row_data.keys():
#				self._idx[field_name] = len(self._payload)
#				self._payload.append(row_data[field_name])
#			self.pk_obj = self._payload[self._idx[self.__class__._pk_field]]
#		except:
#			raise gmExceptions.ConstructorError, "[%s:%s]: error loading bulk instance" % (self.__class__.__name__, row_data)
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
		return '[%s:%s]: %s' % (self.__class__.__name__, self.pk_obj, str(tmp))
	#--------------------------------------------------------
	def __getitem__(self, attribute):
		try:
			return self._payload[self._idx[attribute]]
		except KeyError:
			_log.Log(gmLog.lWarn, '[%s]: no attribute [%s]' % (self.__class__.__name__, attribute))
			_log.Log(gmLog.lWarn, '[%s]: valid attributes: %s' % (self.__class__.__name__, str(self._idx.keys())))
			raise gmExceptions.NoSuchBusinessObjectAttributeError, '[%s]: no attribute [%s]' % (self.__class__.__name__, attribute)
	#--------------------------------------------------------
	def __setitem__(self, attribute, value):
		if attribute not in self.__class__._updatable_fields:
			_log.Log(gmLog.lWarn, '[%s]: settable attributes: %s' % (self.__class__.__name__, str(self.__class__._updatable_fields)))
			raise gmExceptions.BusinessObjectAttributeNotSettableError, '[%s]: attribute <%s> not settable' % (self.__class__.__name__, attribute)
		try:
			self._idx[attribute]
		except KeyError:
			_log.Log(gmLog.lWarn, '[%s]: valid attributes: %s' % (self.__class__.__name__, str(self.__class__._updatable_fields)))
			raise gmExceptions.NoSuchBusinessObjectAttributeError, '[%s]: no attribute <%s>' % (self.__class__.__name__, attribute)
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
	def get_patient(self):
		_log.Log(gmLog.lErr, '[%s:%s]: forgot to override get_patient()' % (self.__class__.__name__, self.pk_obj))
		return None
	#--------------------------------------------------------
	def refetch_payload(self):
		"""Fetch field values from backend.
		"""
		if self._is_modified:
			_log.Log(gmLog.lPanic, '[%s:%s]: cannot reload, payload changed' % (self.__class__.__name__, self.pk_obj))
			return False
		self._payload = None
		data, self._idx = gmPG.run_ro_query (
			self.__class__._service,
			self.__class__._cmd_fetch_payload,
			True,
			self.pk_obj
		)
		if data is None:
			_log.Log(gmLog.lErr, '[%s:%s]: error retrieving instance' % (self.__class__.__name__, self.pk_obj))
			return False
		if len(data) == 0:
			_log.Log(gmLog.lErr, '[%s:%s]: no such instance' % (self.__class__.__name__, self.pk_obj))
			return False
		self._payload = data[0]
		return True
	#--------------------------------------------------------
	def save_payload(self):
		"""Store updated values (if any) in database.

		- returns a tuple (<True|False>, err_msg)
		"""
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
			return (False, err)
		self._is_modified = False
		return (True, None)
#============================================================
if __name__ == '__main__':
	_log.SetAllLogLevels(gmLog.lData)

#============================================================
# $Log: gmBusinessDBObject.py,v $
# Revision 1.2  2004-10-12 18:37:45  ncq
# - Carlos added passing in possibly bulk-fetched row data w/o
#   touching the database in __init__()
# - note that some higher level things will be broken until all
#   affected child classes are fixed
# - however, note that child classes that don't overload __init__()
#   are NOT affected and support no-DB init transparently
# - changed docs accordingly
# - this is the initial bulk-loader work that is hoped to gain
#   quite some performance in some areas (think lab results)
#
# Revision 1.1  2004/10/11 19:05:41  ncq
# - business object-in-db root class, used by cClinItem etc.
#
# Revision 1.17  2004/06/18 13:31:21  ncq
# - return False from save_payload on failure to update
#
# Revision 1.16  2004/06/02 21:50:32  ncq
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
