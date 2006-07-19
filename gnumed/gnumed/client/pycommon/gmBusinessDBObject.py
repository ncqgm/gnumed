"""GnuMed database object business class.

Overview
--------
This class wraps a source relation (table, view) which
represents an entity that makes immediate business sense
such as a vaccination or a medical document. In many if
not most cases this source relation is a denormalizing
view. The data in that view will in most cases, however,
originate from several normalized tables. One instance
of this class represents one row of said source relation.

Note, however, that this class does not *always* simply
wrap a single table or view. It can also encompass several
relations (views, tables, sequences etc) that taken together
form an object meaningful to *business* logic.

Initialization
--------------
There are two ways to initialize an instance with values.
One way is to pass a "primary key equivalent" object into
__init__(). Refetch_payload() will then pull the data from
the backend. Another way would be to fetch the data outside
the instance and pass it in via the <row> argument. In that
case the instance will not initially connect to the databse
which may offer a great boost to performance.

Values API
----------
Field values are cached for later access. They can be accessed
by a dictionary API, eg:

	old_value = object['field']
	object['field'] = new_value

The field names correspond to the respective column names
in the "main" source relation. Accessing non-existant field
names will raise an error, so does trying to set fields not
listed in self.__class__._updatable_fields. To actually
store updated values in the database one must explicitely
call save_payload().

The class will in many cases be enhanced by accessors to
related data that is not directly part of the business
object itself but are closely related, such as codes
linked to a clinical narrative entry (eg a diagnosis). Such
accessors in most cases start with get_*. Related setters
start with set_*. The values can be accessed via the
object['field'] syntax, too, but they will be cached
independantly.

Concurrency handling
--------------------
GnuMed connections always run transactions in isolation level
"serializable". This prevents transactions happening at the
*very same time* to overwrite each other's data. All but one
of them will abort with a concurrency error (eg if a transaction
runs a select-for-update later than another one it will hang
until the first transaction ends. Then it will suceed or fail
depending on what the first transaction did).

However, another transaction may have updated our row between
the time we first fetched the data and the time we start the
update transaction. This is noticed by getting the XMIN system
column for the row when initially fetching the data and using
that value as a where condition value when locking the row for
update. If the row had been updated (xmin changed) or deleted
(primary key disappeared) in the meantime then getting the row
lock will touch zero rows even if the query itself formally
succeeds.

When detecting a change in a row due to XMIN being different
one needs to be careful how to represent that to the user.
The row may simply have changed but it also might have been
deleted and a completely new and unrelated row which happens
to have the same primary key might have been created ! This
row might relate to a totally different context (eg. patient,
episode, encounter).

One can offer all the data to the user:

self.original_payload
- contains the data at the last successful refetch

self.modified_payload
- contains the modified payload just before the last
  failure of save_payload()

self._payload
- contains the currently active payload which may or
  may not contain changes

For discussion on this see the thread starting at:

http://archives.postgresql.org/pgsql-general/2004-10/msg01352.php
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/gmBusinessDBObject.py,v $
# $Id: gmBusinessDBObject.py,v 1.34 2006-07-19 20:27:03 ncq Exp $
__version__ = "$Revision: 1.34 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

import sys, copy, types, inspect

from Gnumed.pycommon import gmExceptions, gmLog, gmPG

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)
#============================================================
class cBusinessDBObject:
	"""Represents business objects in the database.

	Rules:
	- instances ARE ASSUMED TO EXIST in the database
	- PK construction (aPK_obj): DOES verify its existence on instantiation
	                             (fetching data fails)
	- Row construction (row): allowed by using a dict of pairs
	                               field name: field value (PERFORMANCE improvement)
	- does NOT verify FK target existence
	- does NOT create new entries in the database
	- does NOT lazy-fetch fields on access

	Class scope SQL commands:
	<_cmd_fetch_payload>
		- must return exactly one row
		- where clause argument values are expected
		  in self._pk_obj (taken from __init__(aPK_obj))
		- must return xmin of all rows that _cmds_store_payload
		  will be updating
	"""
	_conn_pool = None
	#--------------------------------------------------------
	def __init__(self, aPK_obj=None, row=None):
		"""Init business object.
		"""
		self._is_modified = False
		# check descendants
		#<DEBUG>
		self.__class__._cmd_fetch_payload
			# must fetch xmin ! (and the view must support that ...)
		self.__class__._cmds_lock_rows_for_update
			# must do "select for update" and use xmin in where clause,
			# each query must return exactly 1 row
		self.__class__._cmds_store_payload
			# one or multiple "update ... set ..." statements which
			# actually update the database from the data in self._payload,
			# the last query must refetch the XMIN values needed to detect
			# concurrent updates, their field names had better be the same as
			# in _cmd_fetch_payload
		self.__class__._updatable_fields
			# a list of fields available to users via object['field']
		self.__class__._service
			# the service in which our source relation is found,
			# this is used for establishing connections
		# FIXME: if you want this check to be done please update all the child classes, too
#		self.__class__._subtable_dml_templates
			# a dictionary of subtables by name,
			# values are dictionaries  of 3 queries keyed 'select', 'insert' and 'delete',
			#
			# The 'select' query accepts one parameter (this object's primary
			# key) and returns some rows. One column in which must be 'pk'.
			# These rows, as dictionaries, are avaiable as attributes of the
			# business object, by the name of the key in _subtable_dml_templates.
			#
			# The 'insert' query is called by add_to_subtable(). It must have
			# %(labelled)s parameters for the columns to insert into from
			# the dictionary passed to add_to_subtable(). 'pk_master' is also
			# available in this dictionary, being the primary key of the
			# 'master' table.
			#
			# The 'delete' is called from del_from_subtable(). Two parameters
			# in the order: pk for the master object and pk of the
			# subtable row to be deleted.
		#</DEBUG>
		self._payload = []		# the cache for backend object values (mainly table fields)
		self._ext_cache = {}	# the cache for extended method's results
		self._idx = {}
		self._subtable_cmd_queue = []		# must be suitable to be passed as <queries> argument to gmPG.run_commit2()
		if cBusinessDBObject._conn_pool is None:
			# once for ALL descendants :-)
			cBusinessDBObject._conn_pool = gmPG.ConnectionPool()
		if aPK_obj is not None:
			self.__init_from_pk(aPK_obj=aPK_obj)
		else:
			self._init_from_row_data(row=row)
		self._is_modified = False
#		self._flagged = False
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
			self.original_payload = {}
			for field in self._idx.keys():
				self.original_payload[field] = self._payload[self._idx[field]]
			return True
		if result is None:
			raise gmExceptions.NoSuchBusinessObjectError, "[%s:%s]: cannot find instance" % (self.__class__.__name__, self.pk_obj)
		if result is False:
			raise gmExceptions.ConstructorError, "[%s:%s]: error loading instance" % (self.__class__.__name__, self.pk_obj)
	#--------------------------------------------------------
	def _init_from_row_data(self, row=None):
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
			raise gmExceptions.ConstructorError, "[%s:??]: error loading instance from row data" % self.__class__.__name__
		if len(self._idx.keys()) != len(self._payload):
			_log.Log(gmLog.lPanic, 'field index vs. payload length mismatch: %s field names vs. %s fields' % (len(self._idx.keys()), len(self._payload)))
			_log.LogException('faulty <row> argument structure: %s' % row, sys.exc_info())
			raise gmExceptions.ConstructorError, "[%s:??]: error loading instance from row data" % self.__class__.__name__
		self.original_payload = {}
		for field in self._idx.keys():
			self.original_payload[field] = self._payload[self._idx[field]]
	#--------------------------------------------------------
	def __del__(self):
		if self.__dict__.has_key('_is_modified'):
			if self._is_modified:
				_log.Log(gmLog.lPanic, '[%s:%s]: loosing payload changes' % (self.__class__.__name__, self.pk_obj))
				_log.Log(gmLog.lData, 'original: %s' % self.original_payload)
				_log.Log(gmLog.lData, 'modified: %s' % self._payload)
	#--------------------------------------------------------
	def __str__(self):
		tmp = []
		[tmp.append('%s: %s' % (attr, self._payload[self._idx[attr]])) for attr in self._idx.keys()]
		return '[%s:%s]: %s' % (self.__class__.__name__, self.pk_obj, str(tmp))
	#--------------------------------------------------------
	def __getitem__(self, attribute):
		# use try: except: as it is faster and we want this as fast as possible
		# 1) backend payload cache
		try:
			return self._payload[self._idx[attribute]]
		except KeyError:
			pass
		# 2) cached extension method results ...
		try:
			return self._ext_cache[attribute] # FIXME: when do we evict this cache ?
		except KeyError:
			pass
		# 3) subtable
		try:
			subtable = self._subtable_dml_templates[attribute]
			try:
				query = subtable['select']
				rows, idx = gmPG.run_ro_query(self.__class__._service, query, True, self.pk_obj)
				if rows is not None:
					self._ext_cache[attribute] = [dict([(name, row[i]) for name, i in idx.items()]) for row in rows]
					return self._ext_cache[attribute]
				_log.Log(gmLog.lErr, '[%s:%s]: error getting subtable [%s] values' % (self.__class__.__name__, self.pk_obj, attribute))
				# FIXME: should actually fail and return appropriate error
			except KeyError:
				_log.LogException('[%s:%s]: subtable support error, no "select" for subtable [%s]' % (self.__class__.__name__, self.pk_obj, attribute), sys.exc_info(), verbose=0)
				# FIXME: should actually fail and return appropriate error
				pass
		except (KeyError, AttributeError):
			# either
			# - no subtable support (no attribute _subtable_dml_templates)
			# - or no known subtable <attribute>
			pass
		# 4) getters providing extensions
		getter = getattr(self, 'get_%s' % attribute, None)
		if not callable(getter):
			_log.Log(gmLog.lWarn, '[%s]: no attribute [%s]' % (self.__class__.__name__, attribute))
			_log.Log(gmLog.lWarn, '[%s]: valid attributes: %s' % (self.__class__.__name__, str(self._idx.keys())))
			_log.Log(gmLog.lWarn, '[%s]: no getter method [get_%s]' % (self.__class__.__name__, attribute))
			methods = filter(lambda x: x[0].startswith('get_'), inspect.getmembers(self, inspect.ismethod))
			_log.Log(gmLog.lWarn, '[%s]: valid getter methods: %s' % (self.__class__.__name__, str(methods)))
			raise gmExceptions.NoSuchBusinessObjectAttributeError, '[%s]: cannot access [%s]' % (self.__class__.__name__, attribute)
		self._ext_cache[attribute] = getter()
		return self._ext_cache[attribute]
	#--------------------------------------------------------
	def __setitem__(self, attribute, value):
		# 1) backend payload cache
		if attribute in self.__class__._updatable_fields:
			try:
				if self._payload[self._idx[attribute]] != value:
					self._payload[self._idx[attribute]] = value
					self._is_modified = True
				return
			except KeyError:
				_log.Log(gmLog.lWarn, '[%s]: cannot set attribute <%s> despite marked settable' % (self.__class__.__name__, attribute))
				_log.Log(gmLog.lWarn, '[%s]: supposedly settable attributes: %s' % (self.__class__.__name__, str(self.__class__._updatable_fields)))
				raise gmExceptions.NoSuchBusinessObjectAttributeError, '[%s]: cannot access [%s]' % (self.__class__.__name__, attribute)
		# 2) setters providing extensions
		if hasattr(self, 'set_%s' % attribute):
			setter = getattr(self, "set_%s" % attribute)
			if not callable(setter):
				raise gmExceptions.NoSuchBusinessObjectAttributeError, '[%s] setter [set_%s] not callable' % (self.__class__.__name__, attribute)
			try:
				del self._ext_cache[attribute]
			except KeyError:
				pass
			if type(value) is types.TupleType:
				if setter(*value):
					self._is_modified = True
					return
				raise gmExceptions.BusinessObjectAttributeNotSettableError, '[%s]: setter [%s] failed for [%s]' % (self.__class__.__name__, setter, value)
			if setter(value):
				self._is_modified = True
				return
		# 3) don't know what to do with <attribute>
		_log.Log(gmLog.lErr, '[%s]: cannot find attribute <%s> or setter method [set_%s]' % (self.__class__.__name__, attribute, attribute))
		_log.Log(gmLog.lWarn, '[%s]: settable attributes: %s' % (self.__class__.__name__, str(self.__class__._updatable_fields)))
		methods = filter(lambda x: x[0].startswith('set_'), inspect.getmembers(self, inspect.ismethod))
		_log.Log(gmLog.lWarn, '[%s]: valid setter methods: %s' % (self.__class__.__name__, str(methods)))
		raise gmExceptions.BusinessObjectAttributeNotSettableError, '[%s]: cannot set [%s]' % (self.__class__.__name__, attribute)
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
	def __noop(self):
		pass
	#--------------------------------------------------------
	def save_payload(self, conn=None):
		"""Store updated values (if any) in database.

		Optionally accepts a pre-existing connection
		- returns a tuple (<True|False>, <data>)
		- True: success
		- False: an error occurred
			* data is (error, message)
			* for error meanings see gmPG.run_commit2()
		"""
		if not self._is_modified:
			return (True, None)
		params = {}
		for field in self._idx.keys():
			params[field] = self._payload[self._idx[field]]
		self.modified_payload = params
		close_conn = self.__noop
		if conn is None:
			conn = self.__class__._conn_pool.GetConnection(self.__class__._service, readonly=0)
			close_conn = conn.close
		if conn is None:
			_log.Log(gmLog.lErr, '[%s:%s]: cannot update instance' % (self.__class__.__name__, self.pk_obj))
			return (False, (1, _('Cannot connect to database.')))

		# try to lock rows
		for query in self.__class__._cmds_lock_rows_for_update:
			successful, result = gmPG.run_commit2(link_obj = conn, queries = [(query, [params])], extra_verbose = False)
			# error
			if not successful:
				conn.rollback()
				close_conn()
				_log.Log(gmLog.lErr, '[%s:%s]: cannot update instance, error locking row' % (self.__class__.__name__, self.pk_obj))
				return (False, result)
			# query succeeded but failed to find the row to lock
			# because another transaction committed an UPDATE or
			# DELETE *before* we attempted to lock it ...
			# FIXME: this can fail if savepoints are used since subtransactions change the xmin/xmax ...
			data, idx = result
			if len(data) == 0:
				conn.rollback()
				close_conn()
				_log.Log(gmLog.lErr, '[%s:%s]: cannot update instance, concurrency conflict (lock query succeeded but did not find row to lock)' % (self.__class__.__name__, self.pk_obj))
				_log.Log(gmLog.lErr, query)
				_log.Log(gmLog.lErr, params)
				# store current content so user can still play with it ...
				self.modified_payload = params
				# update from backend
				self._is_modified = False
				if self.refetch_payload():
					return (False, (2, 'c'))
				else:
					return (False, (2, 'd'))
			# uh oh
			if len(data) > 1:
				conn.rollback()
				close_conn()
				_log.Log(gmLog.lErr, '[%s:%s]: cannot update instance, deep sh*t' % (self.__class__.__name__, self.pk_obj))
				_log.Log(gmLog.lPanic, '[%s:%s]: integrity violation, more than one matching row' % (self.__class__.__name__, self.pk_obj))
				_log.Log(gmLog.lPanic, 'HINT: shut down application and backup database immediately')
				_log.Log(gmLog.lErr, query)
				_log.Log(gmLog.lErr, params)
				return (False, (1, _('Database integrity violation detected. Immediate shutdown strongly advisable.')))
		# successfully locked, now actually run update
		queries = []
		for query in self.__class__._cmds_store_payload:
			queries.append((query, [params]))
		successful, result = gmPG.run_commit2(link_obj = conn, queries = queries, get_col_idx = True)
		if not successful:
			conn.rollback()
			close_conn()
			_log.Log(gmLog.lErr, '[%s:%s]: cannot update instance' % (self.__class__.__name__, self.pk_obj))
			_log.Log(gmLog.lErr, params)
			return (False, result)
		rows, idx = result
		if rows is None:
			conn.rollback()
			close_conn()
			_log.Log(gmLog.lErr, '[%s:%s]: cannot update instance, last query did not return XMIN values' % (self.__class__.__name__, self.pk_obj))
			return (False, result)
		# update cached XMIN values
		row = rows[0]
		for key in idx.keys():
			try:
				self._payload[self._idx[key]] = row[idx[key]]
			except KeyError:
				conn.rollback()
				close_conn()
				_log.Log(gmLog.lErr, '[%s:%s]: cannot update instance, XMIN refetch key mismatch on [%s]' % (self.__class__.__name__, self.pk_obj, key))
				_log.Log(gmLog.lErr, 'payload keys: %s' % str(self._idx))
				_log.Log(gmLog.lErr, 'XMIN refetch keys: %s' % str(idx))
				_log.Log(gmLog.lErr, params)
				return (False, data)
		# execute cached changes to subtables
		if len(self._subtable_cmd_queue) > 0:
			successful, result = gmPG.run_commit2(link_obj = conn, queries=self._subtable_cmd_queue)
			if not successful:
				conn.rollback()
				close_conn()
				_log.Log(gmLog.lErr, '[%s:%s]: cannot change subtables' % (self.__class__.__name__, self.pk_obj))
				return (False, result)
			self._subtable_cmd_queue = []
		try:
			conn.commit()
			close_conn()
		except:
			typ, val, tb = sys.exc_info() 
			return (False, (1, val))
		self._is_modified = False
		# update to new "original" payload
		self.original_payload = {}
		for field in self._idx.keys():
			self.original_payload[field] = self._payload[self._idx[field]]
		return (True, None)
	#----------------------------------------------------
	def del_from_subtable(self, table, row):
		"""Delete a row from a subtable.

		1) remove from subtable cache
		2) queue backend subtable delete for save_payload()
		"""
		try:
			row_count = len(self._ext_cache[table])
		except KeyError:
			_log.Log(gmLog.lErr, 'table [%s] not registered as subtable in class [%s]' % (table, self.__class__.__name__))
			return False
		for i in range(row_count):
			if self._ext_cache[table][i]['pk'] == row['pk']:
				del self._ext_cache[table][i]
		self._subtable_cmd_queue.append((self._subtable_dml_templates[table]['delete'], [self.pk_obj, row['pk']]))
		self._is_modified = True
		return True
	#-----------------------------------------------------
	def add_to_subtable(self, table, row):
		"""Add a row to a subtable.

		1) add to subtable cache
		2) queue backend subtable insert for save_payload()
		"""
		row['pk_master'] = self.pk_obj
		try:
			self._ext_cache[table].append(row)
			self._subtable_cmd_queue.append((self._subtable_dml_templates[table]['insert'], [row]))
		except KeyError:
			_log.Log(gmLog.lErr, 'table [%s] not registered as subtable in class [%s]' % (table, self.__class__.__name__))
			return False
		self._is_modified = True
		return True
	#----------------------------------------------------
	def sync_subtable(self, table, items):
		"""FIXME: is this actually used anywhere ?

		Ensures that a new version of the subtable matches whats in the
		database, adding and deleting as appropriate.
		"""
		print "WARNING: %s.sync_subtable() is likely broken" % self.__class__.__name__
		table_cache = self._ext_cache[table][:]
		# FIXME: this ain't gonna work as t is undefined
		# FIXME: leave it in for now so we find out whether this method is used anywhere
		# FIXME: should be: for row_idx in range (len(table_cache)):
		for row_idx in range (len(t)):
			for j in range (items):
				eqn = 1
				for k in items[j].keys():
					if items[j][k] != self._ext_cache[table][row_idx][k]:
						eqn = 0
				if eqn: # these dicts are considered equal
					items[j]['__same'] = 1
					table_cache[row_idx]['__same'] = 1
		for i in items:
			if not i.has_key('__same'):
				self.add_to_subtable (table, i)
		for i in table_cache:
			if not i.has_key('__same'):
				self.del_from_subtable (table, i)

#============================================================
if __name__ == '__main__':
	_log.SetAllLogLevels(gmLog.lData)
	#--------------------------------------------------------
	class cTestObj(cBusinessDBObject):
		_cmd_fetch_payload = None
		_cmds_lock_rows_for_update = None
		_cmds_store_payload = None
		_updatable_fields = []
		_service = None
		#----------------------------------------------------
		def get_something(self):
			pass
		#----------------------------------------------------
		def set_something(self):
			pass
	#--------------------------------------------------------
	data = {
		'pk_field': 'bogus_pk',
		'idx': {'bogus_pk': 0, 'bogus_field': 1},
		'data': [-1, 'bogus_data']
	}
	obj = cTestObj(row=data)
#	print obj['wrong_field']
	obj['wrong_field'] = 1

#============================================================
# $Log: gmBusinessDBObject.py,v $
# Revision 1.34  2006-07-19 20:27:03  ncq
# - gmPyCompat.py is history
#
# Revision 1.33  2006/06/18 13:20:29  ncq
# - cleanup, better logging
#
# Revision 1.32  2006/06/17 16:41:30  ncq
# - only modify self._data if it actually changes
# - don't close the connection if it was passed in
#
# Revision 1.31  2005/11/19 08:47:56  ihaywood
# tiny bugfixes
#
# Revision 1.30  2005/10/19 09:12:00  ncq
# - cleanup
#
# Revision 1.29  2005/10/15 18:17:06  ncq
# - error detection in subtable support much improved
#
# Revision 1.28  2005/10/10 17:40:57  ncq
# - slightly enhance Syans fixes on AttributeError
#
# Revision 1.27  2005/10/08 12:33:08  sjtan
# tree can be updated now without refetching entire cache; done by passing emr object to create_xxxx methods and calling emr.update_cache(key,obj);refresh_historical_tree non-destructively checks for changes and removes removed nodes and adds them if cache mismatch.
#
# Revision 1.26  2005/10/04 11:39:58  sjtan
# catch missing attribute error.
#
# Revision 1.25  2005/06/15 22:26:20  ncq
# - CAVEAT regarding XMIN vs. savepoints
#
# Revision 1.24  2005/05/04 08:54:00  ncq
# - improved __setitem__ handling
# - add_to_subtable()/del_from_subtable() now set _is_modified appropriately
# - some internal renaming for clarification
#
# Revision 1.23  2005/04/29 15:28:47  ncq
# - one fix to del_from_subtable() as approved by Ian
# - some internal renaming to clear things up
#
# Revision 1.22  2005/04/28 21:10:20  ncq
# - improved _subtable docs
# - avoid confusion:
#   - add_subtable -> add_to_subtable
#   - del_subtable -> del_from_subtable
#
# Revision 1.21  2005/04/18 19:19:15  ncq
# - cleanup
#
# Revision 1.20  2005/04/14 18:58:59  cfmoro
# Commented line to avoid hiding _subtables
#
# Revision 1.19  2005/04/11 17:55:10  ncq
# - update self.original_payload in the right places
#
# Revision 1.18  2005/03/20 16:49:56  ncq
# - improve concurrency error handling docs
#
# Revision 1.17  2005/03/14 14:31:17  ncq
# - add support for self.original_payload such that we can make
#   available all the information to the user when concurrency
#   conflicts are detected
# - init _subtables so child classes don't HAVE to have it
#
# Revision 1.16  2005/03/06 21:15:13  ihaywood
# coment expanded on _subtables
#
# Revision 1.15  2005/03/06 14:44:02  ncq
# - cleanup
#
# Revision 1.14  2005/03/06 08:17:02  ihaywood
# forms: back to the old way, with support for LaTeX tables
#
# business objects now support generic linked tables, demographics
# uses them to the same functionality as before (loading, no saving)
# They may have no use outside of demographics, but saves much code already.
#
# Revision 1.13  2005/02/03 20:20:14  ncq
# - really use class level static connection pool
#
# Revision 1.12  2005/02/01 10:16:07  ihaywood
# refactoring of gmDemographicRecord and follow-on changes as discussed.
#
# gmTopPanel moves to gmHorstSpace
# gmRichardSpace added -- example code at present, haven't even run it myself
# (waiting on some icon .pngs from Richard)
#
# Revision 1.11  2005/01/31 12:56:55  ncq
# - properly update xmin in save_payload()
#
# Revision 1.10  2005/01/31 06:25:35  ncq
# - brown paper bag bug, I wonder how it ever worked:
#   connections are gotten from an instance of the pool
#
# Revision 1.9  2005/01/19 06:52:24  ncq
# - improved docstring
#
# Revision 1.8  2005/01/02 19:58:02  ncq
# - remove _xmins_refetch_col_pos
#
# Revision 1.7  2005/01/02 16:16:52  ncq
# - by Ian: improve XMIN update on save by using new commit() get_col_idx
#
# Revision 1.6  2004/12/20 16:46:55  ncq
# - improve docs
# - close last known concurrency issue (reget xmin values after save)
#
# Revision 1.5  2004/12/17 16:15:36  ncq
# - add extension method result caching as suggested by Ian
# - I maintain a bad feeling due to cache eviction policy being murky at best
#
# Revision 1.4  2004/11/03 22:30:35  ncq
# - improved docs
# - introduce class level SQL query _cmds_lock_rows_for_update
# - rewrite save_payload() to use that via gmPG.run_commit2()
# - report concurrency errors from save_payload()
#
# Revision 1.3  2004/10/27 12:13:37  ncq
# - __init_from_row_data -> _init_from_row_data so we can override it
# - more sanity checks
#
# Revision 1.2  2004/10/12 18:37:45  ncq
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
