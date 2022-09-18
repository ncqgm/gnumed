"""GNUmed configuration handling.

This source of configuration information is supported:

 - database tables

Theory of operation:

It is helpful to have a solid log target set up before importing this
module in your code. This way you will be able to see even those log
messages generated during module import.

Once your software has established database connectivity you can
set up a config source from the database. You can limit the option
applicability by the constraints "workplace", "user", and "cookie".

The basic API for handling items is get()/set().
The database config objects auto-sync with the backend.

@copyright: GPL v2 or later
"""
# TODO:
# - optional arg for set -> type
#==================================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"

# standard modules
import sys, pickle, decimal, logging, re as regex


# gnumed modules
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmPG2, gmTools


_log = logging.getLogger('gm.cfg')

# don't change this without knowing what you do as
# it will already be in many databases
cfg_DEFAULT = "xxxDEFAULTxxx"
#==================================================================
def get_all_options(order_by=None):

	if order_by is None:
		order_by = ''
	else:
		order_by = 'ORDER BY %s' % order_by

	cmd = """
SELECT * FROM (

SELECT
	vco.*,
	cs.value
FROM
	cfg.v_cfg_options vco
		JOIN cfg.cfg_string cs ON (vco.pk_cfg_item = cs.fk_item)

UNION ALL

SELECT
	vco.*,
	cn.value::text
FROM
	cfg.v_cfg_options vco
		JOIN cfg.cfg_numeric cn ON (vco.pk_cfg_item = cn.fk_item)

UNION ALL

SELECT
	vco.*,
	csa.value::text
FROM
	cfg.v_cfg_options vco
		JOIN cfg.cfg_str_array csa ON (vco.pk_cfg_item = csa.fk_item)

UNION ALL

SELECT
	vco.*,
	cd.value::text
FROM
	cfg.v_cfg_options vco
		JOIN cfg.cfg_data cd ON (vco.pk_cfg_item = cd.fk_item)

) as option_list
%s""" % order_by

	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = False)

	return rows
#==================================================================
# FIXME: make a cBorg around this
class cCfgSQL:

#	def __init__(self):
#		pass

	#-----------------------------------------------
	# external API
	#-----------------------------------------------
	def get(self, option=None, workplace=None, cookie=None, bias=None, default=None, sql_return_type=None):
		return self.get2 (
			option = option,
			workplace = workplace,
			cookie = cookie,
			bias = bias,
			default = default,
			sql_return_type = sql_return_type
		)
	#-----------------------------------------------
	def get2(self, option=None, workplace=None, cookie=None, bias=None, default=None, sql_return_type=None):
		"""Retrieve configuration option from backend.

		@param bias: Determine the direction into which to look for config options.

			'user': When no value is found for "current_user/workplace" look for a value
				for "current_user" regardless of workspace. The corresponding concept is:

				"Did *I* set this option anywhere on this site ? If so, reuse the value."

			'workplace': When no value is found for "current_user/workplace" look for a value
				for "workplace" regardless of user. The corresponding concept is:

				"Did anyone set this option for *this workplace* ? If so, reuse that value."

		@param default: if no value is found for the option this value is returned
			instead, also the option is set to this value in the backend, if <None>
			a missing option will NOT be created in the backend
		@param sql_return_type: a PostgreSQL type the value of the option is to be
			cast to before returning, if None no cast will be applied, you will
			want to make sure that sql_return_type and type(default) are compatible
		"""
		if None in [option, workplace]:
			raise ValueError('neither <option> (%s) nor <workplace> (%s) may be [None]' % (option, workplace))
		if bias not in ['user', 'workplace']:
			raise ValueError('<bias> must be "user" or "workplace"')

		# does this option exist ?
		cmd = "select type from cfg.cfg_template where name=%(opt)s"
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': {'opt': option}}])
		if len(rows) == 0:
			# not found ...
			if default is None:
				# ... and no default either
				return None
			_log.info('creating option [%s] with default [%s]' % (option, default))
			success = self.set(workplace = workplace, cookie = cookie, option = option, value = default)
			if not success:
				# ... but cannot create option with default value either
				_log.error('creating option failed')
			return default

		cfg_table_type_suffix = rows[0][0]
		args = {
			'opt': option,
			'wp': workplace,
			'cookie': cookie,
			'def': cfg_DEFAULT
		}

		if cfg_table_type_suffix == 'data':
			sql_return_type = ''
		else:
			sql_return_type = gmTools.coalesce (
				value2test = sql_return_type,
				return_instead = '',
				template4value = '::%s'
			)

		# 1) search value with explicit workplace and current user
		where_parts = [
			'vco.owner = CURRENT_USER',
			'vco.workplace = %(wp)s',
			'vco.option = %(opt)s'
		]
		where_parts.append(gmTools.coalesce (
			value2test = cookie,
			return_instead = 'vco.cookie is null',
			template4value = 'vco.cookie = %(cookie)s'
		))
		cmd = "select vco.value%s from cfg.v_cfg_opts_%s vco where %s limit 1" % (
			sql_return_type,
			cfg_table_type_suffix,
			' and '.join(where_parts)
		)
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])
		if len(rows) > 0:
			if cfg_table_type_suffix == 'data':
				return pickle.loads(str(rows[0][0]))
			return rows[0][0]

		_log.warning('no user AND workplace specific value for option [%s] in config database' % option)

		# 2) search value with biased query
		if bias == 'user':
			# did *I* set this option on *any* workplace ?
			where_parts = [
				'vco.option = %(opt)s',
				'vco.owner = CURRENT_USER',
			]
		else:
			# did *anyone* set this option on *this* workplace ?
			where_parts = [
				'vco.option = %(opt)s',
				'vco.workplace = %(wp)s'
			]
		where_parts.append(gmTools.coalesce (
			value2test = cookie,
			return_instead = 'vco.cookie is null',
			template4value = 'vco.cookie = %(cookie)s'
		))
		cmd = "select vco.value%s from cfg.v_cfg_opts_%s vco where %s" % (
			sql_return_type,
			cfg_table_type_suffix,
			' and '.join(where_parts)
		)
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])
		if len(rows) > 0:
			# set explicitely for user/workplace
			self.set (
				workplace = workplace,
				cookie = cookie,
				option = option,
				value = rows[0][0]
			)
			if cfg_table_type_suffix == 'data':
				return pickle.loads(str(rows[0][0]))
			return rows[0][0]

		_log.warning('no user OR workplace specific value for option [%s] in config database' % option)

		# 3) search value within default site policy
		where_parts = [
			'vco.owner = %(def)s',
			'vco.workplace = %(def)s',
			'vco.option = %(opt)s'
		]
		cmd = "select vco.value%s from cfg.v_cfg_opts_%s vco where %s" % (
			sql_return_type,
			cfg_table_type_suffix,
			' and '.join(where_parts)
		)
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])
		if len(rows) > 0:
			# set explicitely for user/workplace
			self.set (
				workplace = workplace,
				cookie = cookie,
				option = option,
				value = rows[0]['value']
			)
			if cfg_table_type_suffix == 'data':
				return pickle.loads(str(rows[0]['value']))
			return rows[0]['value']

		_log.warning('no default site policy value for option [%s] in config database' % option)

		# 4) not found, set default ?
		if default is None:
			_log.warning('no default value for option [%s] supplied by caller' % option)
			return None
		_log.info('setting option [%s] to default [%s]' % (option, default))
		success = self.set (
			workplace = workplace,
			cookie = cookie,
			option = option,
			value = default
		)
		if not success:
			return None

		return default
	#-----------------------------------------------
	def getID(self, workplace = None, cookie = None, option = None):
		"""Get config value from database.

		- unset arguments are assumed to mean database defaults except for <cookie>
		"""
		# sanity checks
		if option is None:
			_log.error("Need to know which option to retrieve.")
			return None

		alias = self.__make_alias(workplace, 'CURRENT_USER', cookie, option)

		# construct query
		where_parts = [
			'vco.option=%(opt)s',
			'vco.workplace=%(wplace)s'
			]
		where_args = {
			'opt': option,
			'wplace': workplace
		}
		if workplace is None:
			where_args['wplace'] = cfg_DEFAULT

		where_parts.append('vco.owner=CURRENT_USER')

		if cookie is not None:
			where_parts.append('vco.cookie=%(cookie)s')
			where_args['cookie'] = cookie
		where_clause = ' and '.join(where_parts)
		cmd = """
select vco.pk_cfg_item
from cfg.v_cfg_options vco
where %s
limit 1""" % where_clause

		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': where_args}], return_data=True)
		if len(rows) == 0:
			_log.warning('option definition for [%s] not in config database' % alias)
			return None
		return rows[0][0]
	#----------------------------
	def set(self, workplace = None, cookie = None, option = None, value = None):
		"""Set (insert or update) option value in database.

		Any parameter that is None will be set to the database default.

		Note: you can't change the type of a parameter once it has been
		created in the backend. If you want to change the type you will
		have to delete the parameter and recreate it using the new type.
		"""
		# sanity checks
		if None in [option, value]:
			raise ValueError('invalid arguments (option=<%s>, value=<%s>)' % (option, value))

		rw_conn = gmPG2.get_connection(readonly=False)

		alias = self.__make_alias(workplace, 'CURRENT_USER', cookie, option)

		opt_value = value
		sql_type_cast = ''
		if isinstance(value, str):
			sql_type_cast = '::text'
		elif isinstance(value, bool):
			opt_value = int(opt_value)
		elif isinstance(value, (float, int, decimal.Decimal, bool)):
			sql_type_cast = '::numeric'
		elif isinstance(value, list):
			# there can be different syntaxes for list types so don't try to cast them
			pass
		elif isinstance(value, (bytes, memoryview)):
			# can go directly into bytea
			pass
		else:
			opt_value = gmPG2.dbapi.Binary(pickle.dumps(value))
			sql_type_cast = '::bytea'

		cmd = 'select cfg.set_option(%%(opt)s, %%(val)s%s, %%(wp)s, %%(cookie)s, NULL)' % sql_type_cast
		args = {
			'opt': option,
			'val': opt_value,
			'wp': workplace,
			'cookie': cookie
		}
		try:
			rows, idx = gmPG2.run_rw_queries(link_obj=rw_conn, queries=[{'cmd': cmd, 'args': args}], return_data=True)
			result = rows[0][0]
		except Exception:
			_log.exception('cannot set option')
			result = False

		rw_conn.commit()		# will rollback if transaction failed
		rw_conn.close()

		return result

	#-------------------------------------------
	def getAllParams(self, user = None, workplace = cfg_DEFAULT):
		"""Get names of all stored parameters for a given workplace/(user)/cookie-key.
		This will be used by the ConfigEditor object to create a parameter tree.
		"""
		# if no workplace given: any workplace (= cfg_DEFAULT)
		where_snippets = [
			'cfg_template.pk=cfg_item.fk_template',
			'cfg_item.workplace=%(wplace)s'
		]
		where_args = {'wplace': workplace}

		# if no user given: current db user
		if user is None:
			where_snippets.append('cfg_item.owner=CURRENT_USER')
		else:
			where_snippets.append('cfg_item.owner=%(usr)s')
			where_args['usr'] = user

		where_clause = ' and '.join(where_snippets)

		cmd = """
select name, cookie, owner, type, description
from cfg.cfg_template, cfg.cfg_item
where %s""" % where_clause

		# retrieve option definition
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': where_args}], return_data=True)
		return rows

	#----------------------------
	def delete(self, conn=None, pk_option=None):
		if conn is None:
			# without a gm-dbo connection you can only delete your own options :-)
			cmd = "DELETE FROM cfg.cfg_item WHERE pk = %(pk)s AND owner = CURRENT_USER"
		else:
			cmd = "DELETE FROM cfg.cfg_item WHERE pk = %(pk)s"
		args = {'pk': pk_option}
		gmPG2.run_rw_queries(link_obj = conn, queries = [{'cmd': cmd, 'args': args}], end_tx = True)
	#----------------------------
	def delete_old(self, workplace = None, cookie = None, option = None):
		"""
		Deletes an option or a whole group.
		Note you have to call store() in order to save
		the changes.
		"""
		if option is None:
			raise ValueError('<option> cannot be None')

		if cookie is None:
			cmd = """
delete from cfg.cfg_item where
	fk_template=(select pk from cfg.cfg_template where name = %(opt)s) and
	owner = CURRENT_USER and
	workplace = %(wp)s and
	cookie is Null
"""
		else:
			cmd = """
delete from cfg.cfg_item where
	fk_template=(select pk from cfg.cfg_template where name = %(opt)s) and
	owner = CURRENT_USER and
	workplace = %(wp)s and
	cookie = %(cookie)s
"""
		args = {'opt': option, 'wp': workplace, 'cookie': cookie}
		gmPG2.run_rw_queries(queries=[{'cmd': cmd, 'args': args}])
		return True
	#----------------------------
	def __make_alias(self, workplace, user, cookie, option):
		return '%s-%s-%s-%s' % (workplace, user, cookie, option)
#===================================================================
def getDBParam(workplace = None, cookie = None, option = None):
	"""Convenience function to get config value from database.

	will search for context dependant match in this order:
		- CURRENT_USER_CURRENT_WORKPLACE
		- CURRENT_USER_DEFAULT_WORKPLACE
		- DEFAULT_USER_CURRENT_WORKPLACE
		- DEFAULT_USER_DEFAULT_WORKPLACE

	We assume that the config tables are found on service "default".
	That way we can handle the db connection inside this function.

	Returns (value, set) of first match.
	"""

	# FIXME: depending on set store for user ...

	if option is None:
		return (None, None)

	# connect to database (imports gmPG2 if need be)
	dbcfg = cCfgSQL()

	# (set_name, user, workplace)
	sets2search = []
	if workplace is not None:
		sets2search.append(['CURRENT_USER_CURRENT_WORKPLACE', None, workplace])
	sets2search.append(['CURRENT_USER_DEFAULT_WORKPLACE', None, None])
	if workplace is not None:
		sets2search.append(['DEFAULT_USER_CURRENT_WORKPLACE', cfg_DEFAULT, workplace])
	sets2search.append(['DEFAULT_USER_DEFAULT_WORKPLACE', cfg_DEFAULT, None])
	# loop over sets
	matchingSet = None
	result = None
	for set in sets2search:
		result = dbcfg.get(
			workplace = set[2],
			user = set[1],
			option = option,
			cookie = cookie
		)
		if result is not None:
			matchingSet = set[0]
			break
		_log.debug('[%s] not found for [%s@%s]' % (option, set[1], set[2]))

	# cleanup
	if matchingSet is None:
		_log.warning('no config data for [%s]' % option)
	return (result, matchingSet)
#-------------------------------------------------------------
def setDBParam(workplace = None, user = None, cookie = None, option = None, value = None):
	"""Convenience function to store config values in database.

	We assume that the config tables are found on service "default".
	That way we can handle the db connection inside this function.

	Omitting any parameter (or setting to None) will store database defaults for it.

	- returns True/False
	"""
	# connect to database
	dbcfg = cCfgSQL()
	# set value
	success = dbcfg.set(
		workplace = workplace,
		user = user,
		option = option,
		value = value
	)

	if not success:
		return False
	return True
#=============================================================
# main
#=============================================================
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	root = logging.getLogger()
	root.setLevel(logging.DEBUG)
	#---------------------------------------------------------
	def test_get_all_options():
		for opt in get_all_options():
			print('%s (%s): %s (%s@%s)' % (opt['option'], opt['type'], opt['value'], opt['owner'], opt['workplace']))
#			print(u' %s' % opt['description'])
#			print(u' %s on %s' % (opt['owner'], opt['workplace']))
	#---------------------------------------------------------
	def test_db_cfg():
		print("testing database config")
		print("=======================")

		myDBCfg = cCfgSQL()

		print("delete() works:", myDBCfg.delete(option='font name', workplace = 'test workplace'))
		print("font is initially:", myDBCfg.get2(option = 'font name', workplace = 'test workplace', bias = 'user'))
		print("set() works:", myDBCfg.set(option='font name', value="Times New Roman", workplace = 'test workplace'))
		print("font after set():", myDBCfg.get2(option = 'font name', workplace = 'test workplace', bias = 'user'))
		print("delete() works:", myDBCfg.delete(option='font name', workplace = 'test workplace'))
		print("font after delete():", myDBCfg.get2(option = 'font name', workplace = 'test workplace', bias = 'user'))
		print("font after get() with default:", myDBCfg.get2(option = 'font name', workplace = 'test workplace', bias = 'user', default = 'WingDings'))
		print("font right after get() with another default:", myDBCfg.get2(option = 'font name', workplace = 'test workplace', bias = 'user', default = 'default: Courier'))
		print("set() works:", myDBCfg.set(option='font name', value="Times New Roman", workplace = 'test workplace'))
		print("font after set() on existing option:", myDBCfg.get2(option = 'font name', workplace = 'test workplace', bias = 'user'))

		print("setting array option")
		print("array now:", myDBCfg.get2(option = 'test array', workplace = 'test workplace', bias = 'user'))
		aList = ['val 1', 'val 2']
		print("set():", myDBCfg.set(option='test array', value = aList, workplace = 'test workplace'))
		print("array now:", myDBCfg.get2(option = 'test array', workplace = 'test workplace', bias = 'user'))
		aList = ['val 11', 'val 12']
		print("set():", myDBCfg.set(option='test array', value = aList, workplace = 'test workplace'))
		print("array now:", myDBCfg.get2(option = 'test array', workplace = 'test workplace', bias = 'user'))
		print("delete() works:", myDBCfg.delete(option='test array', workplace='test workplace'))
		print("array now:", myDBCfg.get2(option = 'test array', workplace = 'test workplace', bias = 'user'))

		print("setting complex option")
		data = {1: 'line 1', 2: 'line2', 3: {1: 'line3.1', 2: 'line3.2'}, 4: 1234}
		print("set():", myDBCfg.set(option = "complex option test", value = data, workplace = 'test workplace'))
		print("complex option now:", myDBCfg.get2(workplace = 'test workplace', option = "complex option test", bias = 'user'))
		print("delete() works:", myDBCfg.delete(option = "complex option test", workplace = 'test workplace'))
		print("complex option now:", myDBCfg.get2(workplace = 'test workplace', option = "complex option test", bias = 'user'))

	#---------------------------------------------------------
	test_get_all_options()
#		test_db_cfg()

#=============================================================

