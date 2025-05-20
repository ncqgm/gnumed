"""GNUmed database object business class.

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
case the instance will not initially connect to the database
which may offer a great boost to performance.

Values API
----------
Field values are cached for later access. They can be accessed
by a dictionary API, eg:

	old_value = object['field']
	object['field'] = new_value

The field names correspond to the respective column names
in the "main" source relation. Accessing non-existent field
names will raise an error, so does trying to set fields not
listed in self.__class__._updatable_fields. To actually
store updated values in the database one must explicitly
call save_payload().

The class will in many cases be enhanced by accessors to
related data that is not directly part of the business
object itself but are closely related, such as codes
linked to a clinical narrative entry (eg a diagnosis). Such
accessors in most cases start with get_*. Related setters
start with set_*. The values can be accessed via the
object['field'] syntax, too, but they will be cached
independently.

Concurrency handling
--------------------
GNUmed connections always run transactions in isolation level
"serializable". This prevents transactions happening at the
*very same time* to overwrite each other's data. All but one
of them will abort with a concurrency error (eg if a
transaction runs a select-for-update later than another one
it will hang until the first transaction ends. Then it will
succeed or fail depending on what the first transaction
did). This is standard transactional behaviour.

However, another transaction may have updated our row
between the time we first fetched the data and the time we
start the update transaction. This is noticed by getting the
XMIN system column for the row when initially fetching the
data and using that value as a where condition value when
updating the row later. If the row had been updated (xmin
changed) or deleted (primary key disappeared) in the
meantime the update will touch zero rows (as no row with
both PK and XMIN matching is found) even if the query itself
syntactically succeeds.

When detecting a change in a row due to XMIN being different
one needs to be careful how to represent that to the user.
The row may simply have changed but it also might have been
deleted and a completely new and unrelated row which happens
to have the same primary key might have been created ! This
row might relate to a totally different context (eg. patient,
episode, encounter).

One can offer all the data to the user:

* self.payload_most_recently_fetched:

  contains the data at the last successful refetch

* self.payload_most_recently_attempted_to_store:

  contains the modified payload just before the last
  failure of save_payload() - IOW what is currently
  in the database

* self._payload:

  contains the currently active payload which may or
  may not contain changes

For discussion on this see the thread starting at:

	http://archives.postgresql.org/pgsql-general/2004-10/msg01352.php

and here

	http://groups.google.com/group/pgsql.general/browse_thread/thread/e3566ba76173d0bf/6cf3c243a86d9233
	(google for "XMIN semantic at peril")

Problem cases with XMIN:

1) not unlikely:

* a very old row is read with XMIN
* vacuum comes along and sets XMIN to FrozenTransactionId

	* now XMIN changed but the row actually didn't !

* an update with "... where xmin = old_xmin ..." fails although there is no need to fail

2) quite unlikely:

* a row is read with XMIN
* a long time passes
* the original XMIN gets frozen to FrozenTransactionId
* another writer comes along and changes the row
* incidentally the exact same old row gets the old XMIN *again*

	* now XMIN is (again) the same but the data changed !

* a later update fails to detect the concurrent change !!

TODO:
The solution is to use our own column for optimistic locking
which gets updated by an AFTER UPDATE trigger.
"""
#============================================================
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"


import sys
import logging
import datetime
from typing import Any


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.pycommon import gmExceptions
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon.gmDateTime import pydt_strftime
from Gnumed.pycommon.gmTools import tex_escape_string
from Gnumed.pycommon.gmTools import xetex_escape_string
from Gnumed.pycommon.gmTools import compare_dict_likes
from Gnumed.pycommon.gmTools import format_dict_like
from Gnumed.pycommon.gmTools import dicts2table_columns
from Gnumed.pycommon.gmTools import u_left_arrow
from Gnumed.pycommon.gmTools import u_ellipsis


_log = logging.getLogger('gm.db')

#============================================================
# business object template
#------------------------------------------------------------
__TEMPLATE = """
#------------------------------------------------------------
from Gnumed.pycommon import gmBusinessDBObject
from Gnumed.pycommon import gmPG2

#============================================================
# short description
#------------------------------------------------------------
# search/replace "" " -> 3 "s
#
# search-replace get_XXX, use plural form
_SQL_get_XXX = "" "
	SELECT *, (xmin AS xmin_XXX)
	FROM XXX.v_XXX
	WHERE %s
"" "

class cXxxXxx(gmBusinessDBObject.cBusinessDBObject):
	"" "Represents ..."" "

	_cmd_fetch_payload = _SQL_get_XXX % 'pk_XXX = %s'
	_cmds_store_payload = [
		"" "
			-- typically the underlying table name
			UPDATE xxx.xxx SET
				-- typically "table_col = % (view_col)s"
				xxx = %(xxx)s,
				xxx = gm.nullify_empty_string(%(xxx)s)
			WHERE
				pk = %(pk_XXX)s
					AND
				xmin = %(xmin_XXX)s
			RETURNING
				xmin AS xmin_XXX
				-- also return columns which are calculated in the view used by
				-- the initial SELECT such that they will further on contain their
				-- updated value:
				--, ...
				--, ...
		"" "
	]
	# view columns that can be updated:
	_updatable_fields = [
		'xxx',
		'xxx'
	]
	#--------------------------------------------------------
#	def format(self):
#		return '%s' % self

#------------------------------------------------------------
def get_XXX(order_by=None):
	if order_by is None:
		order_by = 'true'
	else:
		order_by = 'true ORDER BY %s' % order_by

	cmd = _SQL_get_XXX % order_by
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd}])
	return [ cXxxXxx(row = {'data': r, 'pk_field': 'pk_XXX'}) for r in rows ]
#------------------------------------------------------------
def create_xxx(xxx1=None, xxx2=None):

	args = {
		'xxx1': xxx1,
		'xxx2': xxx2
	}
	cmd = "" "
		INSERT INTO xxx.xxx (
			xxx1,
			xxx2,
			xxx
		) VALUES (
			%(xxx1)s,
			%(xxx2)s,
			gm.nullify_empty_string(%(xxx)s)
		)
		RETURNING pk
		--RETURNING *
	"" "
	rows = gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}], return_data = True)

	return cXxxXxx(aPK_obj = rows[0]['pk'])
	#return cXxxXxx(row = {'data': r, 'pk_field': 'pk_XXX'})

#------------------------------------------------------------
def delete_xxx(pk_XXX=None):
	args = {'pk': pk_XXX}
	cmd = u"DELETE FROM xxx.xxx WHERE pk = %(pk)s"
	gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])
	return True
#------------------------------------------------------------

#------------------------------------------------------------
# widget code
#------------------------------------------------------------
#def edit_xxx(parent=None, xxx=None, single_entry=False, presets=None):
#	pass

#------------------------------------------------------------
#def delete_xxx():
#	pass

#------------------------------------------------------------
#def manage_xxx():
#	pass

#------------------------------------------------------------
# remember to add in clinical item generic workflows and generic clinical item formatting
"""

#============================================================
class cBusinessDBObject(object):
	"""Represents business objects in the database.

	Rules:
		* instances ARE ASSUMED TO EXIST in the database
		* PK construction (aPK_obj): DOES verify its existence on instantiation (fetching data fails)
		* Row construction (row): allowed by using a dict of pairs of field name: field value (PERFORMANCE improvement)
		* does NOT verify FK target existence
		* does NOT create new entries in the database
		* does NOT lazy-fetch fields on access

	Class scope SQL commands and variables:

	_cmd_fetch_payload:

	* must return exactly one row
	* WHERE clause argument values are expected in
	  self.pk_obj (taken from __init__(aPK_obj))
	* must return xmin of all rows that _cmds_store_payload
	  will be updating, so views must support the xmin columns
	  of their underlying tables

	_cmds_store_payload:

	* one or multiple "update ... set ... where xmin_* = ... and pk* = ..."
	  statements which actually update the database from the data in self._payload,
	* the last query must refetch at least the XMIN values needed to detect
	  concurrent updates, their field names had better be the same as
	  in _cmd_fetch_payload,
	* the last query CAN return other fields which is particularly
	  useful when those other fields are computed in the backend
	  and may thus change upon save but will not have been set by
	  the client code explicitly - this is only really of concern
	  if the saved subclass is to be reused after saving rather
	  than re-instantiated
	* when subclasses tend to live a while after save_payload() was
	  called and they support computed fields (say, _(some_column)
	  you need to return *all* columns (see cEncounter)

	_updatable_fields:

	* a list of fields available for update via object['field']
	"""
	_cmd_fetch_payload:str = None
	_cmds_store_payload:list[str] = None
	_updatable_fields:list[str] = None
	#--------------------------------------------------------
	def __init__(self, aPK_obj:int|dict=None, row:dict=None, link_obj=None):
		"""Call __init__ from child classes like so:

			super().__init__(aPK_obj = aPK_obj, row = row, link_obj = link_obj)

		Args:
			aPK_obj: retrieve data from backend

			* an scalar value
				the ._cmd_fetch_payload WHERE condition must be a simple column: "... WHERE pk_col = %s"
			* a dictionary of values
				the ._cmd_fetch_payload WHERE condition must consume the
				dictionary and produce a unique row

			row: must hold the fields

			* data: list of column values for the row selected by ._cmd_fetch_payload (as returned by cursor.fetchone() in the DB-API)
			* pk_field: the name of the primary key column
				OR
			* pk_obj: a dictionary suitable for being passed to cursor.execute
			    and holding the primary key values, used for composite PKs
			* for example:

				row = {
					'data': rows[0],
					'pk_field': 'pk_XXX (the PK column name)',
					'pk_obj': {'pk_col1': pk_col1_val, 'pk_col2': pk_col2_val}
				}

				rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
				objects = [ cChildClass(row = {'data': r, 'pk_field': 'the PK column name'}) for r in rows ]
		"""
		# initialize those "too early" because sanity checking descendants might
		# fail which will then call __str__ in stack trace logging if --debug
		# was given which in turn needs those instance variables
		self.pk_obj:int|dict = -1
#		self._idx:dict[str, int|str] = {}
		self._payload:dict|gmPG2._TRow = {}	# the cache for backend object values (mainly table fields)
		self._is_modified:bool = False
		self.original_payload:list = None
		# only now check child classes
		assert self.__class__._cmd_fetch_payload is not None, '<_cmd_fetch_payload> undefined'
		assert self.__class__._cmds_store_payload is not None, '<_cmds_store_payload> undefined'
		assert self.__class__._updatable_fields is not None, '<_updatable_fields> undefined'

		if aPK_obj is not None:
			self.__init_from_pk(aPK_obj = aPK_obj, link_obj = link_obj)
		else:
			self.__init_from_row_data(row = row)
		self._is_modified = False

	#--------------------------------------------------------
	def __init_from_pk(self, aPK_obj:int|dict=None, link_obj=None):
		"""Creates a new clinical item instance by its PK.

		Args:
			aPK_obj:

			* a simple value -> the primary key WHERE condition must be	a simple column
			* a dictionary of values -> the primary key WHERE condition must be a
			    subselect consuming the dict and producing the single-value primary key
		"""
		self.pk_obj = aPK_obj
		if self.refetch_payload(link_obj = link_obj):
			self.payload_most_recently_fetched = {}
			for field in self._payload.keys():
				self.payload_most_recently_fetched[field] = self._payload[field]
			return

		raise gmExceptions.ConstructorError("[%s:%s]: error loading instance" % (self.__class__.__name__, self.pk_obj))

	#--------------------------------------------------------
	def __init_from_row_data(self, row:dict|gmPG2._TRow=None):
		"""Creates a new clinical item instance given its fields.

		Args:
			row: EITHER {'data': ..., 'pk_field': ...}

				* data: list of column values for the row selected by the PK (as returned by cursor.fetchone() in the DB-API)
				* pk_field: the name of the primary key column

			OR

				* pk_obj: a dictionary suitable for passing to cursor.execute(),
				  holding the primary key values; used for composite PKs

		Examples:

				rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
				objects = [ cChildClass(row = {'data': r, 'pk_field': 'the PK column name'}) for r in rows ]

		Copy/Paste:

				row = {
					'data': rows[0],
					'pk_field': 'pk_XXX (the PK column name)',
					#'pk_obj': {'pk_col1': pk_col1_val, 'pk_col2': pk_col2_val}
				}
		"""
		assert ('data' in row), "[%s:??]: 'data' missing from <row> argument: %s" % (self.__class__.__name__, row)
		faulty_pk = (('pk_field' not in row) and ('pk_obj' not in row))
		assert not faulty_pk, "[%s:??]: either 'pk_field' or 'pk_obj' must exist in <row> argument: %s" % (self.__class__.__name__, row)

		self._payload = row['data']
		if 'pk_field' in row:
			self.pk_obj = self._payload[row['pk_field']]
		else:
			self.pk_obj = row['pk_obj']
		self.payload_most_recently_fetched = {}
		for field in self._payload.keys():
			self.payload_most_recently_fetched[field] = self._payload[field]

	#--------------------------------------------------------
	#--------------------------------------------------------
	def __del__(self):
		if '_is_modified' in self.__dict__:
			if self._is_modified:
				_log.critical('[%s:%s]: losing payload changes' % (self.__class__.__name__, self.pk_obj))
				_log.debug('most recently fetched: %s' % self.payload_most_recently_fetched)
				_log.debug('modified: %s' % self._payload)

	#--------------------------------------------------------
	def __str__(self):
		lines = []
		try:
			for attr in self._payload.keys():
				if self._payload[attr] is None:
					lines.append('%s: NULL' % attr)
				else:
					lines.append('%s [%s]: %s' % (
						attr,
						type(self._payload[attr]),
						self._payload[attr]
					))
			return '[%s:%s] %s:\n%s' % (
				self.__class__.__name__,
				self.pk_obj,
				self._is_modified,
				'\n'.join(lines)
			)

		except Exception:
			return '[%s @ %s], cannot show payload and primary key, nascent ?' % (self.__class__.__name__, id(self))

	#--------------------------------------------------------
	def __getitem__(self, attribute):
		return self._payload[attribute]

	#--------------------------------------------------------
	def __setitem__(self, attribute, value):
		assert attribute in self.__class__._updatable_fields, '[%s]: field <%s> not declared updatable' % (self.__class__.__name__, attribute)

		try:
			if self._payload[attribute] == value:
				return

		except KeyError:
			_log.exception('[%s]: cannot set attribute <%s>', self.__class__.__name__, attribute)
			_log.debug('[%s]: settable attributes: %s', self.__class__.__name__, str(self.__class__._updatable_fields))
			raise KeyError('[%s]: cannot set [%s]' % (self.__class__.__name__, attribute))

		self._payload[attribute] = value
		self._is_modified = True

	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def same_payload(self, another_object:'cBusinessDBObject'=None) -> bool:
		"""Check whether *self* and *another_object* hold the same payload."""
		raise NotImplementedError('comparison between [%s] and [%s] not implemented' % (self, another_object))

	#--------------------------------------------------------
	def is_modified(self) -> bool:
		"""Whether data in this business object has been modified."""
		return self._is_modified

	#--------------------------------------------------------
	def get_fields(self) -> list[str]:
		"""Return list of accessible fields."""
		keys = list(self._payload.keys())
		if not keys:
			keys = [
				'[%s @ %s]' % (self.__class__.__name__, id(self)),
				'no keys, nascent instance ?'
			]
		return keys

	keys = property(get_fields)

	#--------------------------------------------------------
	def get_updatable_fields(self) -> list[str]:
		"""Return a list of fields that can be updated."""
		return self.__class__._updatable_fields

	#--------------------------------------------------------
	def fields_as_dict(self, date_format:str='%Y %b %d  %H:%M', none_string:str='', escape_style:str=None, bool_strings:list[str]=None) -> dict:
		"""Return field values as a dictionary of strings."""
		if bool_strings is None:
			bools = {True: 'True', False: 'False'}
		else:
			bools = {True: bool_strings[0], False: bool_strings[1]}
		data = {}
		for field in self._payload.keys():
			# harden against BYTEA fields
			if isinstance(self._payload[field], memoryview):
				val = _('binary data: %s%s (total: %s bytes)') % (
					self._payload[field].obj[:10],
					u_ellipsis,
					self._payload[field].nbytes
				)
			else:
				val = self._payload[field]
			if val is None:
				data[field] = none_string
				continue
			if isinstance(val, bool):
				data[field] = bools[val]
				continue
			if isinstance(val, datetime.datetime):
				if date_format is None:
					data[field] = str(val)			# x-type: ignore [assignment]
					continue
				data[field] = val.strftime(date_format)
				if escape_style in ['latex', 'tex']:
					data[field] = tex_escape_string(data[field])
				elif escape_style in ['xetex', 'xelatex']:
					data[field] = xetex_escape_string(data[field])
				continue
			try:
				data[field] = str(val, encoding = 'utf8', errors = 'replace')
			except TypeError:
				try:
					data[field] = str(val)
				except (UnicodeDecodeError, TypeError):
					val = '%s' % str(val)
					data[field] = val.decode('utf8', 'replace')
			if escape_style in ['latex', 'tex']:
				data[field] = tex_escape_string(data[field])
			elif escape_style in ['xetex', 'xelatex']:
				data[field] = xetex_escape_string(data[field])
		return data

	#--------------------------------------------------------
	def get_patient(self):
		"""Get associated patient object."""
		_log.error('[%s:%s]: forgot to override get_patient()' % (self.__class__.__name__, self.pk_obj))
		return None

	#--------------------------------------------------------
	def _get_patient_pk(self) -> int:
		"""Get primary key of associated patient if any."""
		pk_patient = None
		try:
			pk_patient = self._payload['pk_patient']
		except KeyError:
			pass
		try:
			pk_patient = self._payload['pk_identity']
		except KeyError:
			pass

		return pk_patient

	patient_pk = property(_get_patient_pk)

	#--------------------------------------------------------
	def _get_staff_id(self) -> int:
		"""Get staff id of associated staff if any."""
		try:
			return self._payload['pk_staff']

		except KeyError:
			_log.debug('[%s]: .pk_staff should be added to the view', self.__class__.__name__)
		try:
			return self._payload['pk_provider']

		except KeyError:
			pass
		mod_by = None
		try:
			mod_by = self._payload['modified_by_raw']
		except KeyError:
			_log.debug('[%s]: .modified_by_raw should be added to the view', self.__class__.__name__)
		if mod_by is not None:
			# find by DB account
			args = {'db_u': mod_by}
			cmd = "SELECT pk FROM dem.staff WHERE db_user = %(db_u)s"
			rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
			if rows:
				# logically, they are all the same provider, because they share the DB account
				return rows[0]['pk']

		mod_by = self._payload['modified_by']
		# is .modified_by a "<DB-account>" ?
		if mod_by.startswith('<') and mod_by.endswith('>'):
			# find by DB account
			args = {'db_u': mod_by.lstrip('<').rstrip('>')}
			cmd = "SELECT pk FROM dem.staff WHERE db_user = %(db_u)s"
			rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
			if rows:
				# logically, they are all the same provider, because they share the DB account
				return rows[0]['pk']

		# .modified_by is probably dem.staff.short_alias
		args = {'alias': mod_by}
		cmd = "SELECT pk FROM dem.staff WHERE short_alias = %(alias)s"
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		if rows:
			# logically, they are all the same provider, because they share the DB account
			return rows[0]['pk']

		_log.error('[%s]: cannot retrieve staff ID for [%s]', self.__class__.__name__, mod_by)
		return None

	staff_id = property(_get_staff_id)

	#--------------------------------------------------------
	def format(self, *args, **kwargs) -> list[str]:
		"""Return instance data generically formatted as a table."""
		return format_dict_like (
			self.fields_as_dict(none_string = '<?>'),
			tabular = True,
			value_delimiters = None
		).split('\n')

	#--------------------------------------------------------
	def _get_revision_history(self, query:str, args:dict, title:str) -> list[str]:
		rows = gmPG2.run_ro_queries(queries = [{'sql': query, 'args': args}])
		if not rows:
			return ['%s (no versions)' % title]

		lines = ['%s (%s versions)' % (title, rows[0]['row_version'] + 1)]
		column_labels = [ 'rev %s (%s)' % (r['row_version'], pydt_strftime(r['audit__action_when'], format = '%Y %b %d %H:%M', none_str = 'live row')) for r in rows ]
		lines.extend (dicts2table_columns (
			rows,
			left_margin = 1,
			eol = None,
			keys2ignore = ['audit__action_when', 'row_version', 'pk_audit'],
			show_only_changes = True,
			column_labels = column_labels,
			date_format = '%Y %b %d %H:%M',
			equality_value = u_left_arrow
		))
		return lines

	#--------------------------------------------------------
	def refetch_payload(self, ignore_changes:bool=False, link_obj=None) -> bool:
		"""Fetch field values from backend.

		Args:
			ignore_changes: True -> loose local changes if data on the backend changed
		"""
		if self._is_modified:
			compare_dict_likes(self.original_payload, self.fields_as_dict(date_format = None, none_string = None), 'original payload', 'modified payload')
			if ignore_changes:
				_log.critical('[%s:%s]: losing payload changes' % (self.__class__.__name__, self.pk_obj))
				#_log.debug('most recently fetched: %s' % self.payload_most_recently_fetched)
				#_log.debug('modified: %s' % self._payload)
			else:
				_log.critical('[%s:%s]: cannot reload, payload changed' % (self.__class__.__name__, self.pk_obj))
				return False

		if isinstance(self.pk_obj, dict):
			args:dict = self.pk_obj
		else:
			args:list = [self.pk_obj]		# type: ignore [no-redef]
		queries = [{'sql': self.__class__._cmd_fetch_payload, 'args': args}]
		rows = gmPG2.run_ro_queries (
			link_obj = link_obj,
			queries = queries
		)
		if len(rows) == 0:
			_log.error('[%s:%s]: no such instance' % (self.__class__.__name__, self.pk_obj))
			return False

		if len(rows) > 1:
			raise AssertionError('[%s:%s]: %s instances !' % (self.__class__.__name__, self.pk_obj, len(rows)))

		self._payload = rows[0]
		return True

	#--------------------------------------------------------
	def save(self, conn:gmPG2.dbapi.extras.DictConnection=None) -> tuple[bool, tuple]:
		"""Just calls save_payload()."""
		return self.save_payload(conn = conn)

	#--------------------------------------------------------
	def save_payload(self, conn:gmPG2.dbapi.extras.DictConnection=None) -> tuple[bool, tuple]:
		"""Store updated values (if any) into database.

		Optionally accepts a pre-existing connection

		Returns:
			a tuple (True|False, data)
			True: success
			False: an error occurred,
			data: (error, message), for error meanings see gmPG2.run_rw_queries()
		"""
		if not self._is_modified:
			return (True, None)

		args:dict[str, Any] = {}
		for field in self._payload.keys():
			args[field] = self._payload[field]
		self.payload_most_recently_attempted_to_store = args
		close_conn = lambda : None
		commit_conn = lambda : None
		if conn is None:
			conn = gmPG2.get_connection(readonly=False)
			close_conn = conn.close
			commit_conn = conn.commit
		queries = []
		for query in self.__class__._cmds_store_payload:
			queries.append({'sql': query, 'args': args})
		rows = gmPG2.run_rw_queries (
			link_obj = conn,
			queries = queries,
			return_data = True
		)
		# success ?
		if len(rows) == 0:
			# nothing updated - this can happen if:
			# - someone else updated the row so XMIN does not match anymore
			# - the PK went away (rows were deleted from under us)
			# - another WHERE condition of the UPDATE did not produce any rows to update
			# - savepoints are used since subtransactions may relevantly change the xmin/xmax ...
			return (False, ('cannot update row', _('[%s:%s]: row not updated (nothing returned), row in use ?') % (self.__class__.__name__, self.pk_obj)))

		# update cached values from should-be-first-and-only
		# result row of last query,
		# update all fields returned such that computed
		# columns see their new values (given they are
		# returned by the query)
		row = rows[0]
		for key in row.keys():
			try:
				self._payload[key] = row[key]
			except KeyError:
				conn.rollback()
				close_conn()
				_log.error('[%s:%s]: cannot update instance, XMIN-refetch key mismatch on [%s]' % (self.__class__.__name__, self.pk_obj, key))
				_log.error('payload keys: %s' % str(self._payload.keys()))
				_log.error('XMIN-refetch keys: %s' % str(row.keys()))
				_log.error(args)
				raise

		# only at commit time will data actually
		# get committed (and thusly trigger based notifications
		# be sent out), so reset the local modification flag
		# right before that
		self._is_modified = False
		commit_conn()
		close_conn()
		# update to new "original" payload
		self.payload_most_recently_fetched = {}
		for field in self._payload.keys():
			self.payload_most_recently_fetched[field] = self._payload[field]
		return (True, None)

#============================================================
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	#--------------------------------------------------------
	class cTestObj(cBusinessDBObject):
		_cmd_fetch_payload = ''
		_cmds_store_payload:list[str] = []
		_updatable_fields = ['test']
		#----------------------------------------------------
		def get_something(self):
			pass
		#----------------------------------------------------
		def set_something(self):
			pass
	#--------------------------------------------------------
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()

	db_row = {'bogus_pk': -1, 'bogus_field': 'bogus_data', 'bogus_date': datetime.datetime.now(), 'test': -1, 'bogus_binary': memoryview(b'123456789012345678901234567890123456789012345678901234567890')}
	row_data = {
		'pk_field': 'bogus_pk',
		'data': db_row
	}
	obj = cTestObj(row = row_data)
	#print('format():', obj.format())
	print('as_dict():', obj.fields_as_dict())
	#print('test:', obj['test'])
	#obj['test'] = 'test'
	#print('test:', obj['test'])
	#print(obj['wrong_field'])
	#obj['wrong_field'] = 1
	#print(obj['wrong_field'])

#============================================================
