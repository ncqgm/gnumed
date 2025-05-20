"""GNUmed database-backed configuration handling.

Once your software has established database connectivity you can
set up a config source from the database. You can limit the option
applicability by the constraints "workplace", "user", and "cookie".

GNUmed tries to centralize configuration in the backend as
much as possible (as opposed to in client-side files).
"""
#==================================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later (details at https://www.gnu.org)"

# standard modules
import sys
import logging

# gnumed modules
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmPG2


_log = logging.getLogger('gm.cfg')


_DB_CFG = None

#==================================================================
# convenience functions
#------------------------------------------------------------------
def get(option:str=None, workplace:str=None, cookie:str=None, bias:str=None, default=None):
	"""Return configuration value.

	Calls get(...) on a module global instance of cCfgSQL().
	"""
	return __get_db_cfg_object().get (
		option = option,
		workplace = workplace,
		cookie = cookie,
		bias = bias,
		default = default
	)

#------------------------------------------------------------------
def get4user(option:str=None, workplace:str=None, cookie:str=None, default=None):
	"""Return configuration value.

	Calls get4user(...) on a module global instance of cCfgSQL().
	"""
	return __get_db_cfg_object().get4user (
		option = option,
		workplace = workplace,
		cookie = cookie,
		default = default
	)

#------------------------------------------------------------------
def get4workplace(option:str=None, workplace:str=None, cookie:str=None, default=None):
	"""Return configuration value.

	Calls get4workplace(...) on a module global instance of cCfgSQL().
	"""
	return __get_db_cfg_object().get4workplace (
		option = option,
		workplace = workplace,
		cookie = cookie,
		default = default
	)

#------------------------------------------------------------------
def get4site(option:str=None, default=None):
	"""Retrieve site-wide configuration option from backend.

	Site-wide means owner=NULL and workplace=NULL.
	"""
	return __get_db_cfg_object().get4site(option = option, default = default)

#------------------------------------------------------------------
def set(owner:str=None, workplace:str=None, cookie:str=None, option:str=None, value=None) -> bool:
	"""Set configuration value.

	Calls set(...) on a module global instance of cCfgSQL().
	"""
	return __get_db_cfg_object().set (
		owner = owner,
		workplace = workplace,
		cookie = cookie,
		option = option,
		value = value
	)

#------------------------------------------------------------------
def delete(conn=None, pk_option:int=None):
	"""Delete configuration value.

	Calls delete(...) on a module global instance of cCfgSQL().
	"""
	return __get_db_cfg_object().delete (
		conn = conn,
		pk_option = pk_option
	)

#------------------------------------------------------------------
def get_all_options(order_by:str=None) -> list:
	"""Return a list of all configuration items.

	Args:
		order_by: optionally, columns to order the SQL output by

	Returns:
		A list of all configuration items in the database along with their metadata.
	"""
	if order_by is None:
		order_by = ''
	else:
		order_by = 'ORDER BY %s' % order_by
	cmd = 'SELECT * FROM cfg.v_cfg_options %s' % order_by
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd}])
	return rows

#------------------------------------------------------------------
def log_all_options() -> None:
	_log.debug('client configuration stored in the database:')
	for opt in get_all_options(order_by = 'option, owner, workplace'):
		_log.debug('option [%s] -- owner [%s] -- workplace [%s]', opt['option'], opt['owner'], opt['workplace'])
		_log.debug(' %s: %s', type(opt['value']), opt['value'])

#==================================================================
def __get_db_cfg_object():
	"""Setup a module global instance of cCfgSQL()."""
	global _DB_CFG
	if _DB_CFG is None:
		_DB_CFG = cCfgSQL()
	return _DB_CFG

#==================================================================
class cCfgSQL:
	"""Handles configuration options stored in a PostgreSQL database."""

	#-----------------------------------------------
	# external API
	#-----------------------------------------------
	def get4user(self, option:str=None, workplace:str=None, cookie:str=None, default=None):
		"""Retrieve configuration option from backend, biased to current user.

		Calls self.get(..., bias = 'user', ...).
		"""
		return self.get (
			option = option,
			workplace = workplace,
			cookie = cookie,
			bias = 'user',
			default = default
		)

	#-----------------------------------------------
	def get4workplace(self, option:str=None, workplace:str=None, cookie:str=None, default=None):
		"""Retrieve configuration option from backend, biased to workplace.

		Calls self.get(..., bias = 'workplace', ...).
		"""
		return self.get (
			option = option,
			workplace = workplace,
			cookie = cookie,
			bias = 'workplace',
			default = default
		)

	#-----------------------------------------------
	def get4site(self, option:str=None, default=None):
		"""Retrieve site-wide configuration option from backend."""
		return self.__get4site(option = option, default = default)

	#-----------------------------------------------
	def get(self, option:str=None, workplace:str=None, cookie:str=None, bias:str=None, default=None):
		"""Retrieve configuration option from backend for current user.

		This method will look for option values in a
		more-specific to less-specific order, namely

		1) specific to the workplace, if given, plus the current user

		2) either
			if bias is "user", specific to the current user, *regardless* of workplace
			("Did *I* set the option anywhere on this site ? If so, use that value.")
		   OR
			if bias is "workplace", specific to the given workplace, *regardless* of user
			"Did anyone set the option for *this workplace* ? If so, use that value."
		  OR
			if bias is None, skip biased search

		3) explicitely not specific to any user or workplace (both being searched
		   as NULL), IOW the site-wide default

		When no value is found at all, the default (if given) is stored in the
		database as site-wide default and returned.

		Args:
			option: the configuration item name
			workplace: the workplace for which to retrieve the value, None = site-wide default
			cookie: an opaque value further restricting the scope of the configuration item value search, say, a particular patient's ID
			bias: the "direction" into which to search for config options
				'user': When no value is found for "current_user/workplace" look for a value for "current_user" regardless of workspace.
				'workplace': When no value is found for "current_user/workplace" look for a value for "workplace" regardless of user.
			default: the default configuration value to use if no value is found

		Returns:
			The configuration value found, or the default, or else None.
		"""
		_log.debug('option [%s], workplace [%s], cookie [%s], bias [%s], default [%s]', option, workplace, cookie, bias, default)
		if option is None:
			raise ValueError('<option> (name) must not be None')
		if bias not in ['user', 'workplace', None]:
			raise ValueError('<bias> must be "user" or "workplace", or None')
		if (bias == 'workplace') and not workplace:
			raise ValueError('if <bias> is "workplace", then <workplace> must not be None or empty')
		if (bias == 'workplace') and (workplace.strip() == ''):
			raise ValueError('if <bias> is "workplace", then <workplace> must not be empty')

		args = {
			'opt': option,
			'wp': workplace,
			'cookie': cookie
		}
		# 1) search value with explicit workplace and current user
		where_parts = [
			'c_vco.option = %(opt)s',
			'c_vco.owner = CURRENT_USER',
			'c_vco.workplace = %(wp)s'
		]
		if cookie:
			where_parts.append('c_vco.cookie = %(cookie)s')
		cmd = 'SELECT * FROM cfg.v_cfg_options c_vco WHERE %s LIMIT 1' % (' AND '.join(where_parts))
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		if rows:
			return self.__auto_heal_pseudo_boolean_setting(setting = rows[0], default = default)

		# 2) search value with biased query
		_log.warning('no user+workplace specific value for option [%s] in database', option)
		value = self.__get_with_bias (
			option = option,
			workplace = workplace,
			cookie = cookie,
			bias = bias,
			default = default
		)
		if value is not None:
			return value

		# 3) search site-wide default value, or default, if given
		_log.warning('no %s-biased value for option [%s] in database, or no bias given', bias, option)
		return self.__get4site(option = option, default = default)

	#----------------------------
	def set(self, owner:str=None, workplace:str=None, cookie:str=None, option:str=None, value=None, description:str=None) -> bool:
		"""Set (create or update) option+value in database.

		Any argument that is None will be set to NULL, meaning site-wide default.

		Note:
			*value* cannot be None (and thusly map to NULL) as None is
			used to denote "no value found" in .get*() methods

		Args:
			owner: the user this value applies to,
				'' -> CURRENT_USER,
				None -> NULL=site-wide default,
			workplace: the workplace the value applies to,
				None -> NULL=site-wide default,
			option: the configuration item name
			cookie: an opaque value further restricting the scope of the configuration item value, say, a particular patient's ID
			value: the actual configuration value, anything that can be turned into JSON will be returned as it was stored

		Returns:
			True/False based on success.
		"""
		if None in [option, value]:
			raise ValueError('invalid arguments (option=<%s>, value=<%s>)' % (option, value))

		args = {
			'opt': option,
			'val': gmPG2.dbapi.extras.Json(value),
			'wp': workplace,
			'cookie': cookie,
			'usr': owner,
			'desc': description
		}
		_log.debug('value:  [%s]', value)
		_log.debug('JSON: >>>%s<<<', args['val'])
		SQL = 'SELECT cfg.set_option(%(opt)s, %(val)s, %(wp)s, %(cookie)s, %(usr)s, %(desc)s)'
		queries = [{'sql': SQL, 'args': args}]
		try:
			rows = gmPG2.run_rw_queries(queries = queries, return_data = True)
			result = rows[0][0]
		except Exception:
			_log.exception('cannot set option: [%s]=<%s>', option, value)
			result = False
		return result

	#-----------------------------------------------
	def delete(self, conn=None, pk_option:int=None):
		"""Delete configuration value from database.

		Args:
			conn: optionally, a connection to use, note that you can only
				delete your own options, unless conn belongs to gm-dbo
			pk_option: primary key in cfg.cfg_item
		"""
		if conn is None:
			cmd = "DELETE FROM cfg.cfg_item WHERE pk = %(pk)s AND owner = CURRENT_USER"
		else:
			cmd = "DELETE FROM cfg.cfg_item WHERE pk = %(pk)s"
		args = {'pk': pk_option}
		gmPG2.run_rw_queries(link_obj = conn, queries = [{'sql': cmd, 'args': args}], end_tx = True)

	#-----------------------------------------------
	# helper functions
	#-----------------------------------------------
	def __auto_heal_pseudo_boolean_setting(self, setting=None, default=None):
		if not isinstance(default, bool):
			# apparently not intended to be boolean, leave alone
			return setting['value']

		_log.debug('current setting [%s], default [%s]', setting, default)
		if setting['value'] not in [0,1]:
			_log.error('default suggests boolean, but current setting not 0/1, returning bool() of current value, but leaving database unchanged')
			return bool(setting['value'])

		_log.debug('auto-healing boolean from 0/1 to False/True')
		self.set (
			owner = setting['owner'],
			workplace = setting['workplace'],
			cookie = setting['cookie'],
			option = setting['option'],
			value = bool(setting['value'])
		)
		return bool(setting['value'])

	#-----------------------------------------------
	def __get_with_bias(self, option:str=None, workplace:str=None, cookie:str=None, bias:str=None, default=None):
		if bias is None:
			return None

		args = {
			'opt': option,
			'wp': workplace,
			'cookie': cookie
		}
		where_parts = ['c_vco.option = %(opt)s']
		if cookie:
			where_parts.append('c_vco.cookie = %(cookie)s')
		if bias == 'user':
			# "Did *I* set this option for *any* workplace ?"
			where_parts.append('c_vco.owner = CURRENT_USER')
		elif bias == 'workplace':
			# "Did *anyone* set this option for *this* workplace ?"
			where_parts.append('c_vco.workplace = %(wp)s')
		else:
			# well ...
			raise ValueError('<bias> must be "user" or "workplace", or None')

		cmd = 'SELECT * FROM cfg.v_cfg_options c_vco WHERE %s LIMIT 1' % (' AND '.join(where_parts))
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		if rows:
			return self.__auto_heal_pseudo_boolean_setting(setting = rows[0], default = default)

		return None

	#-----------------------------------------------
	def __get4site(self, option:str=None, default=None):
		_log.debug('option [%s], default [%s]', option, default)
		args = {'opt': option}
		where_parts = [
			'c_vco.owner IS NULL',
			'c_vco.workplace IS NULL',
			'c_vco.option = %(opt)s'
		]
		cmd = 'SELECT * FROM cfg.v_cfg_options c_vco WHERE %s LIMIT 1' % (' AND '.join(where_parts))
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		if not rows:
			_log.warning('no site-wide default value for option [%s] in database' % option)
			if default is None:
				_log.warning('no default value for option [%s] supplied by caller' % option)
				return None

			_log.info('setting site-wide default for option [%s] to [%s]' % (option, default))
			self.set(option = option, value = default)
			return default

		return self.__auto_heal_pseudo_boolean_setting(setting = rows[0], default = default)

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
			print('')
			print('%s -- %s@%s -- "%s"' % (type(opt['value']), opt['owner'], opt['workplace'], opt['option']))
			print('  value: %s' % opt['value'])
			print('  descr: %s' % opt['description'])

	#---------------------------------------------------------
	def test_set():
		print('set: ', set(option = 'test', value = 'mal sehen 4'))
		print(get(option = 'test'))

	#---------------------------------------------------------
	def test_db_cfg():
		print("testing database config")
		print("=======================")

		myDBCfg = cCfgSQL()

#		print("delete() works:", myDBCfg.delete(option='font name', workplace = 'test workplace'))
		print("font is initially:", myDBCfg.get(option = 'font name', workplace = 'test workplace', bias = 'user'))
		print("set() works:", myDBCfg.set(option='font name', value="Times New Roman", workplace = 'test workplace'))
		print("font after set():", myDBCfg.get(option = 'font name', workplace = 'test workplace', bias = 'user'))
#		print("delete() works:", myDBCfg.delete(option='font name', workplace = 'test workplace'))
		print("font after delete():", myDBCfg.get(option = 'font name', workplace = 'test workplace', bias = 'user'))
		print("font after get() with default:", myDBCfg.get(option = 'font name', workplace = 'test workplace', bias = 'user', default = 'WingDings'))
		print("font right after get() with another default:", myDBCfg.get(option = 'font name', workplace = 'test workplace', bias = 'user', default = 'default: Courier'))
		print("set() works:", myDBCfg.set(option='font name', value="Times New Roman", workplace = 'test workplace'))
		print("font after set() on existing option:", myDBCfg.get(option = 'font name', workplace = 'test workplace', bias = 'user'))

		print("setting array option")
		print("array now:", myDBCfg.get(option = 'test array', workplace = 'test workplace', bias = 'user'))
		aList = ['val 1', 'val 2']
		print("set():", myDBCfg.set(option='test array', value = aList, workplace = 'test workplace'))
		print("array now:", myDBCfg.get(option = 'test array', workplace = 'test workplace', bias = 'user'))
		aList = ['val 11', 'val 12']
		print("set():", myDBCfg.set(option='test array', value = aList, workplace = 'test workplace'))
		print("array now:", myDBCfg.get(option = 'test array', workplace = 'test workplace', bias = 'user'))
#		print("delete() works:", myDBCfg.delete(option='test array', workplace='test workplace'))
		print("array now:", myDBCfg.get(option = 'test array', workplace = 'test workplace', bias = 'user'))

		print("setting complex option")
		data = {1: 'line 1', 2: 'line2', 3: {1: 'line3.1', 2: 'line3.2'}, 4: 1234}
		print("set():", myDBCfg.set(option = "complex option test", value = data, workplace = 'test workplace'))
		print("complex option now:", myDBCfg.get(workplace = 'test workplace', option = "complex option test", bias = 'user'))
#		print("delete() works:", myDBCfg.delete(option = "complex option test", workplace = 'test workplace'))
		print("complex option now:", myDBCfg.get(workplace = 'test workplace', option = "complex option test", bias = 'user'))

	#---------------------------------------------------------
	gmPG2.request_login_params(setup_pool = True)

	log_all_options()
	#test_get_all_options()
	#test_set()
	#test_db_cfg()
