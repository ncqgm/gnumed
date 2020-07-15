__doc__ = """GNUmed database object business class.

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
in the "main" source relation. Accessing non-existant field
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
independantly.

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

self.payload_most_recently_fetched
- contains the data at the last successful refetch

self.payload_most_recently_attempted_to_store
- contains the modified payload just before the last
  failure of save_payload() - IOW what is currently
  in the database

self._payload
- contains the currently active payload which may or
  may not contain changes

For discussion on this see the thread starting at:

	http://archives.postgresql.org/pgsql-general/2004-10/msg01352.php

and here

	http://groups.google.com/group/pgsql.general/browse_thread/thread/e3566ba76173d0bf/6cf3c243a86d9233
	(google for "XMIN semantic at peril")

Problem cases with XMIN:

1) not unlikely
- a very old row is read with XMIN
- vacuum comes along and sets XMIN to FrozenTransactionId
  - now XMIN changed but the row actually didn't !
- an update with "... where xmin = old_xmin ..." fails
  although there is no need to fail

2) quite unlikely
- a row is read with XMIN
- a long time passes
- the original XMIN gets frozen to FrozenTransactionId
- another writer comes along and changes the row
- incidentally the exact same old row gets the old XMIN *again*
  - now XMIN is (again) the same but the data changed !
- a later update fails to detect the concurrent change !!

TODO:
The solution is to use our own column for optimistic locking
which gets updated by an AFTER UPDATE trigger.
"""
#============================================================
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"


import sys
import inspect
import logging
import datetime


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmExceptions
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon.gmDateTime import pydt_strftime
from Gnumed.pycommon.gmTools import tex_escape_string
from Gnumed.pycommon.gmTools import xetex_escape_string
from Gnumed.pycommon.gmTools import compare_dict_likes
from Gnumed.pycommon.gmTools import format_dict_like
from Gnumed.pycommon.gmTools import dicts2table
from Gnumed.pycommon.gmTools import u_left_arrow


_log = logging.getLogger('gm.db')

#============================================================
class cBusinessDBObject(object):
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

	Class scope SQL commands and variables:

	<_cmd_fetch_payload>
		- must return exactly one row
		- WHERE clause argument values are expected in
		  self.pk_obj (taken from __init__(aPK_obj))
		- must return xmin of all rows that _cmds_store_payload
		  will be updating, so views must support the xmin columns
		  of their underlying tables

	<_cmds_store_payload>
		- one or multiple "update ... set ... where xmin_* = ... and pk* = ..."
		  statements which actually update the database from the data in self._payload,
		- the last query must refetch at least the XMIN values needed to detect
		  concurrent updates, their field names had better be the same as
		  in _cmd_fetch_payload,
		- the last query CAN return other fields which is particularly
		  useful when those other fields are computed in the backend
		  and may thus change upon save but will not have been set by
		  the client code explicitely - this is only really of concern
		  if the saved subclass is to be reused after saving rather
		  than re-instantiated
		- when subclasses tend to live a while after save_payload() was
		  called and they support computed fields (say, _(some_column)
		  you need to return *all* columns (see cEncounter)

	<_updatable_fields>
		- a list of fields available for update via object['field']


	A template for new child classes:

*********** start of template ***********

#------------------------------------------------------------
from Gnumed.pycommon import gmBusinessDBObject
from Gnumed.pycommon import gmPG2

#============================================================
# short description
#------------------------------------------------------------
# search/replace "" " -> 3 "s
#
# search-replace get_XXX, use plural form
_SQL_get_XXX = u"" "
	SELECT *, (xmin AS xmin_XXX)
	FROM XXX.v_XXX
	WHERE %s
"" "

class cXxxXxx(gmBusinessDBObject.cBusinessDBObject):
	"" "Represents ..."" "

	_cmd_fetch_payload = _SQL_get_XXX % u"pk_XXX = %s"
	_cmds_store_payload = [
		u"" "
			-- typically the underlying table name
			UPDATE xxx.xxx SET
				-- typically "table_col = %(view_col)s"
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
		u'xxx',
		u'xxx'
	]
	#--------------------------------------------------------
#	def format(self):
#		return u'%s' % self

#------------------------------------------------------------
def get_XXX(order_by=None):
	if order_by is None:
		order_by = u'true'
	else:
		order_by = u'true ORDER BY %s' % order_by

	cmd = _SQL_get_XXX % order_by
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = True)
	return [ cXxxXxx(row = {'data': r, 'idx': idx, 'pk_field': 'pk_XXX'}) for r in rows ]
#------------------------------------------------------------
def create_xxx(xxx=None, xxx=None):

	args = {
		u'xxx': xxx,
		u'xxx': xxx
	}
	cmd = u"" "
		INSERT INTO xxx.xxx (
			xxx,
			xxx,
			xxx
		) VALUES (
			%(xxx)s,
			%(xxx)s,
			gm.nullify_empty_string(%(xxx)s)
		)
		RETURNING pk
		--RETURNING *
	"" "
	rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True, get_col_idx = False)
	#rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True, get_col_idx = True)

	return cXxxXxx(aPK_obj = rows[0]['pk'])
	#return cXxxXxx(row = {'data': r, 'idx': idx, 'pk_field': 'pk_XXX'})

#------------------------------------------------------------
def delete_xxx(pk_XXX=None):
	args = {'pk': pk_XXX}
	cmd = u"DELETE FROM xxx.xxx WHERE pk = %(pk)s"
	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
	return True
#------------------------------------------------------------

#------------------------------------------------------------
# widget code
#------------------------------------------------------------
def edit_xxx(parent=None, xxx=None, single_entry=False, presets=None):

#------------------------------------------------------------
def delete_xxx()

#------------------------------------------------------------
def manage_xxx()

#------------------------------------------------------------
# remember to add in clinical item generic workflows


*********** end of template ***********

	"""
	#--------------------------------------------------------
	def __init__(self, aPK_obj=None, row=None, link_obj=None):
		"""Init business object.

		Call from child classes:

			super(cChildClass, self).__init__(aPK_obj = aPK_obj, row = row, link_obj = link_obj)
		"""
		# initialize those "too early" because checking descendants might
		# fail which will then call __str__ in stack trace logging if --debug
		# was given which in turn needs those instance variables
		self.pk_obj = '<uninitialized>'
		self._idx = {}
		self._payload = []		# the cache for backend object values (mainly table fields)
		self._ext_cache = {}	# the cache for extended method's results
		self._is_modified = False

		# sanity check child implementions
		self.__class__._cmd_fetch_payload
		self.__class__._cmds_store_payload
		self.__class__._updatable_fields

		if aPK_obj is not None:
			self.__init_from_pk(aPK_obj = aPK_obj, link_obj = link_obj)
		else:
			self._init_from_row_data(row = row)

		self._is_modified = False

	#--------------------------------------------------------
	def __init_from_pk(self, aPK_obj=None, link_obj=None):
		"""Creates a new clinical item instance by its PK.

		aPK_obj can be:
			- a simple value
			  * the primary key WHERE condition must be
				a simple column
			- a dictionary of values
			  * the primary key WHERE condition must be a
				subselect consuming the dict and producing
				the single-value primary key
		"""
		self.pk_obj = aPK_obj
		result = self.refetch_payload(link_obj = link_obj)
		if result is True:
			self.payload_most_recently_fetched = {}
			for field in self._idx:
				self.payload_most_recently_fetched[field] = self._payload[self._idx[field]]
			return True

		if result is False:
			raise gmExceptions.ConstructorError("[%s:%s]: error loading instance" % (self.__class__.__name__, self.pk_obj))

	#--------------------------------------------------------
	def _init_from_row_data(self, row=None):
		"""Creates a new clinical item instance given its fields.

		row must be a dict with the fields:
			- idx: a dict mapping field names to position
			- data: the field values in a list (as returned by
			  cursor.fetchone() in the DB-API)
			- pk_field: the name of the primary key field
			OR
			- pk_obj: a dictionary suitable for passed to cursor.execute
			  and holding the primary key values, used for composite PKs

		row = {
			'data': rows[0],
			'idx': idx,
			'pk_field': 'pk_XXX (the PK column name)',
			'pk_obj': {'pk_col1': pk_col1_val, 'pk_col2': pk_col2_val}
		}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		objects = [ cChildClass(row = {'data': r, 'idx': idx, 'pk_field': 'the PK column name'}) for r in rows ]
		"""
		assert ('data' in row), "[%s:??]: 'data' missing from <row> argument: %s" % (self.__class__.__name__, row)
		assert ('idx' in row), "[%s:??]: 'idx' missing from <row> argument: %s" % (self.__class__.__name__, row)
		assert (len(row['idx']) == len(row['data'])), "[%s:??]: 'idx'<->'data' field count mismatch: %s" % (self.__class__.__name__, row)
		faulty_pk = (('pk_field' not in row) and ('pk_obj' not in row))
		assert not faulty_pk, "[%s:??]: either 'pk_field' or 'pk_obj' must exist in <row> argument: %s" % (self.__class__.__name__, row)

		self._idx = row['idx']
		self._payload = row['data']
		if 'pk_field' in row:
			self.pk_obj = row['data'][row['idx'][row['pk_field']]]
		else:
			self.pk_obj = row['pk_obj']

		self.payload_most_recently_fetched = {}
		for field in self._idx:
			self.payload_most_recently_fetched[field] = self._payload[self._idx[field]]

	#--------------------------------------------------------
	def __del__(self):
		if '_is_modified' in self.__dict__:
			if self._is_modified:
				_log.critical('[%s:%s]: loosing payload changes' % (self.__class__.__name__, self.pk_obj))
				_log.debug('most recently fetched: %s' % self.payload_most_recently_fetched)
				_log.debug('modified: %s' % self._payload)

	#--------------------------------------------------------
	def __str__(self):
		lines = []
		try:
			for attr in self._idx:
				if self._payload[self._idx[attr]] is None:
					lines.append('%s: NULL' % attr)
				else:
					lines.append('%s: %s [%s]' % (
						attr,
						self._payload[self._idx[attr]],
						type(self._payload[self._idx[attr]])
					))
			return '[%s:%s]:\n%s' % (self.__class__.__name__, self.pk_obj, '\n'.join(lines))
		except Exception:
			return 'likely nascent [%s @ %s], cannot show payload and primary key' %(self.__class__.__name__, id(self))

	#--------------------------------------------------------
	def __getitem__(self, attribute):
		# use try: except KeyError: as it is faster and we want this as fast as possible

		# 1) backend payload cache
		try:
			return self._payload[self._idx[attribute]]
		except KeyError:
			pass

		# 2) extension method results ...
		getter = getattr(self, 'get_%s' % attribute, None)
		if not callable(getter):
			_log.warning('[%s]: no attribute [%s]' % (self.__class__.__name__, attribute))
			_log.warning('[%s]: valid attributes: %s', self.__class__.__name__, list(self._idx))
			_log.warning('[%s]: no getter method [get_%s]' % (self.__class__.__name__, attribute))
			methods = [ m for m in inspect.getmembers(self, inspect.ismethod) if m[0].startswith('get_') ]
			_log.warning('[%s]: valid getter methods: %s' % (self.__class__.__name__, str(methods)))
			raise KeyError('[%s]: cannot read from key [%s]' % (self.__class__.__name__, attribute))

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
				_log.warning('[%s]: cannot set attribute <%s> despite marked settable' % (self.__class__.__name__, attribute))
				_log.warning('[%s]: supposedly settable attributes: %s' % (self.__class__.__name__, str(self.__class__._updatable_fields)))
				raise KeyError('[%s]: cannot write to key [%s]' % (self.__class__.__name__, attribute))

		# 2) setters providing extensions
		if hasattr(self, 'set_%s' % attribute):
			setter = getattr(self, "set_%s" % attribute)
			if not callable(setter):
				raise AttributeError('[%s] setter [set_%s] not callable' % (self.__class__.__name__, attribute))
			try:
				del self._ext_cache[attribute]
			except KeyError:
				pass
			if type(value) == tuple:
				if setter(*value):
					self._is_modified = True
					return
				raise AttributeError('[%s]: setter [%s] failed for [%s]' % (self.__class__.__name__, setter, value))
			if setter(value):
				self._is_modified = True
				return

		# 3) don't know what to do with <attribute>
		_log.error('[%s]: cannot find attribute <%s> or setter method [set_%s]' % (self.__class__.__name__, attribute, attribute))
		_log.warning('[%s]: settable attributes: %s' % (self.__class__.__name__, str(self.__class__._updatable_fields)))
		methods = [ m for m in inspect.getmembers(self, inspect.ismethod) if m[0].startswith('set_') ]
		_log.warning('[%s]: valid setter methods: %s' % (self.__class__.__name__, str(methods)))
		raise AttributeError('[%s]: cannot set [%s]' % (self.__class__.__name__, attribute))

	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def same_payload(self, another_object=None):
		raise NotImplementedError('comparison between [%s] and [%s] not implemented' % (self, another_object))

	#--------------------------------------------------------
	def is_modified(self):
		return self._is_modified

	#--------------------------------------------------------
	def get_fields(self):
		try:
			return list(self._idx)
		except AttributeError:
			return 'nascent [%s @ %s], cannot return keys' %(self.__class__.__name__, id(self))

	#--------------------------------------------------------
	def get_updatable_fields(self):
		return self.__class__._updatable_fields

	#--------------------------------------------------------
	def fields_as_dict(self, date_format='%Y %b %d  %H:%M', none_string='', escape_style=None, bool_strings=None):
		if bool_strings is None:
			bools = {True: 'True', False: 'False'}
		else:
			bools = {True: bool_strings[0], False: bool_strings[1]}
		data = {}
		for field in self._idx:
			# FIXME: harden against BYTEA fields
			#if type(self._payload[self._idx[field]]) == ...
			#	data[field] = _('<%s bytes of binary data>') % len(self._payload[self._idx[field]])
			#	continue
			val = self._payload[self._idx[field]]
			if val is None:
				data[field] = none_string
				continue
			if isinstance(val, bool):
				data[field] = bools[val]
				continue

			if isinstance(val, datetime.datetime):
				if date_format is None:
					data[field] = val
					continue
				data[field] = pydt_strftime(val, format = date_format)
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
		_log.error('[%s:%s]: forgot to override get_patient()' % (self.__class__.__name__, self.pk_obj))
		return None

	#--------------------------------------------------------
	def _get_patient_pk(self):
		try:
			return self._payload[self._idx['pk_patient']]
		except KeyError:
			pass
		try:
			return self._payload[self._idx['pk_identity']]
		except KeyError:
			return None

	patient_pk = property(_get_patient_pk)

	#--------------------------------------------------------
	def _get_staff_id(self):
		try:
			return self._payload[self._idx['pk_staff']]
		except KeyError:
			_log.debug('[%s]: .pk_staff should be added to the view', self.__class__.__name__)
		try:
			return self._payload[self._idx['pk_provider']]
		except KeyError:
			pass
		mod_by = None
		try:
			mod_by = self._payload[self._idx['modified_by_raw']]
		except KeyError:
			_log.debug('[%s]: .modified_by_raw should be added to the view', self.__class__.__name__)
		if mod_by is not None:
			# find by DB account
			args = {'db_u': mod_by}
			cmd = "SELECT pk FROM dem.staff WHERE db_user = %(db_u)s"
			rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
			if len(rows) > 0:
				# logically, they are all the same provider, because they share the DB account
				return rows[0][0]

		mod_by = self._payload[self._idx['modified_by']]
		# is .modified_by a "<DB-account>" ?
		if mod_by.startswith('<') and mod_by.endswith('>'):
			# find by DB account
			args = {'db_u': mod_by.lstrip('<').rstrip('>')}
			cmd = "SELECT pk FROM dem.staff WHERE db_user = %(db_u)s"
			rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
			if len(rows) > 0:
				# logically, they are all the same provider, because they share the DB account
				return rows[0][0]

		# .modified_by is probably dem.staff.short_alias
		args = {'alias': mod_by}
		cmd = "SELECT pk FROM dem.staff WHERE short_alias = %(alias)s"
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		if len(rows) > 0:
			# logically, they are all the same provider, because they share the DB account
			return rows[0][0]

		_log.error('[%s]: cannot retrieve staff ID for [%s]', self.__class__.__name__, mod_by)
		return None

	staff_id = property(_get_staff_id)

	#--------------------------------------------------------
	def format(self, *args, **kwargs):
		return format_dict_like (
			self.fields_as_dict(none_string = '<?>'),
			tabular = True,
			value_delimiters = None
		).split('\n')

	#--------------------------------------------------------
	def _get_revision_history(self, query, args, title):
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': query, 'args': args}], get_col_idx = True)

		lines = []
		if rows == 0:
			lines.append('%s (no versions)' % title)
		else:
			lines.append('%s (%s versions)' % (title, rows[0]['row_version'] + 1))
			column_labels = [ 'rev %s (%s)' % (r['row_version'], pydt_strftime(r['audit__action_when'], format = '%Y %b %d %H:%M', none_str = 'live row')) for r in rows ]
			lines.extend (dicts2table (
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
	def refetch_payload(self, ignore_changes=False, link_obj=None):
		"""Fetch field values from backend."""
		if self._is_modified:
			compare_dict_likes(self.original_payload, self.fields_as_dict(date_format = None, none_string = None), 'original payload', 'modified payload')
			if ignore_changes:
				_log.critical('[%s:%s]: loosing payload changes' % (self.__class__.__name__, self.pk_obj))
				#_log.debug('most recently fetched: %s' % self.payload_most_recently_fetched)
				#_log.debug('modified: %s' % self._payload)
			else:
				_log.critical('[%s:%s]: cannot reload, payload changed' % (self.__class__.__name__, self.pk_obj))
				return False

		if isinstance(self.pk_obj, dict):
			args = self.pk_obj
		else:
			args = [self.pk_obj]
		rows, self._idx = gmPG2.run_ro_queries (
			link_obj = link_obj,
			queries = [{'cmd': self.__class__._cmd_fetch_payload, 'args': args}],
			get_col_idx = True
		)
		if len(rows) == 0:
			_log.error('[%s:%s]: no such instance' % (self.__class__.__name__, self.pk_obj))
			return False

		if len(rows) > 1:
			raise AssertionError('[%s:%s]: %s instances !' % (self.__class__.__name__, self.pk_obj, len(rows)))

		self._payload = rows[0]
		return True

	#--------------------------------------------------------
	def __noop(self):
		pass

	#--------------------------------------------------------
	def save(self, conn=None):
		return self.save_payload(conn = conn)

	#--------------------------------------------------------
	def save_payload(self, conn=None):
		"""Store updated values (if any) in database.

		Optionally accepts a pre-existing connection
		- returns a tuple (<True|False>, <data>)
		- True: success
		- False: an error occurred
			* data is (error, message)
			* for error meanings see gmPG2.run_rw_queries()
		"""
		if not self._is_modified:
			return (True, None)

		args = {}
		for field in self._idx:
			args[field] = self._payload[self._idx[field]]
		self.payload_most_recently_attempted_to_store = args

		close_conn = self.__noop
		if conn is None:
			conn = gmPG2.get_connection(readonly=False)
			close_conn = conn.close

		queries = []
		for query in self.__class__._cmds_store_payload:
			queries.append({'cmd': query, 'args': args})
		rows, idx = gmPG2.run_rw_queries (
			link_obj = conn,
			queries = queries,
			return_data = True,
			get_col_idx = True
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
		for key in idx:
			try:
				self._payload[self._idx[key]] = row[idx[key]]
			except KeyError:
				conn.rollback()
				close_conn()
				_log.error('[%s:%s]: cannot update instance, XMIN-refetch key mismatch on [%s]' % (self.__class__.__name__, self.pk_obj, key))
				_log.error('payload keys: %s' % str(self._idx))
				_log.error('XMIN-refetch keys: %s' % str(idx))
				_log.error(args)
				raise

		# only at conn.commit() time will data actually
		# get committed (and thusly trigger based notifications
		# be sent out), so reset the local modification flag
		# right before that
		self._is_modified = False
		conn.commit()
		close_conn()

		# update to new "original" payload
		self.payload_most_recently_fetched = {}
		for field in self._idx:
			self.payload_most_recently_fetched[field] = self._payload[self._idx[field]]

		return (True, None)

#============================================================
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	#--------------------------------------------------------
	class cTestObj(cBusinessDBObject):
		_cmd_fetch_payload = None
		_cmds_store_payload = None
		_updatable_fields = []
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

	data = {
		'pk_field': 'bogus_pk',
		'idx': {'bogus_pk': 0, 'bogus_field': 1, 'bogus_date': 2},
		'data': [-1, 'bogus_data', datetime.datetime.now()]
		#'data': {'bogus_pk': -1, 'bogus_field': 'bogus_data', 'bogus_date': datetime.datetime.now()}
	}
	obj = cTestObj(row=data)
	print(obj.format())
	#print(obj['wrong_field'])
	#obj['wrong_field'] = 1
	print(obj.fields_as_dict())

#============================================================
