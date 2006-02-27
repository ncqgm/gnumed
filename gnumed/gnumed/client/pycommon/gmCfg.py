"""GnuMed configuration handling.

Two sources of configuration information are supported:

 - INI-style configuration files
 - database tables

Just import this module to have access to a default config file:

> from Gnumed.pycommon import gmCfg
> _cfg = gmCfg.gmDefCfgFile
> option = _cfg.get(group, option)

Theory of operation:

Upon importing this module a "default" config file will be parsed. This
file is registered as the default source for configuration information.

The module will look for the config file in the following standard
places:

1) programmer supplied arguments
2) user supplied command line (getopt style):	--conf-file=<a file name>
3) user supplied $aName_DIR environment variable (all uppercase)
4) ~/.<aDir>/<aName>.conf
5) ~/.<aName>.conf
6) /etc/<aDir>/<aName>.conf
7) /etc/<aName>.conf
8) ./<aName>.conf		- last resort for DOS/Win

<aDir> and <aName> will be derived automatically from the name of
the main script.

It is helpful to have a solid log target set up before importing this
module in your code. This way you will be able to see even those log
messages generated during module import.

It is also possible to instantiate objects for other config files
later on.

Once your software has established database connectivity you can
set up a config source from the database. You can limit the option
applicability by the constraints "workplace", "user", and "cookie".

The basic API for handling items is get()/set() which works for both
database and INI file access. Both sources cache data. The database
config objects auto-syncs with the backend. To make INI file changes
permanent you need to call store() on the file object.

@copyright: GPL
"""
# TODO:
# - optional arg for set -> type
#==================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/gmCfg.py,v $
__version__ = "$Revision: 1.37 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"

# standard modules
import os.path, fileinput, string, sys, shutil, types

# gnumed modules
import gmLog, gmNull

_log = gmLog.gmDefLog
gmPG_ = None
gmCLI_ = None
cPickle_ = None

# flags for __get_conf_name
cfg_SEARCH_STD_DIRS = 1
cfg_IGNORE_CMD_LINE = 2

# don't change this without knowing what you do as
# it will already be in many databases
cfg_DEFAULT = "xxxDEFAULTxxx"

_log.Log(gmLog.lInfo, __version__)

gmDefCfgFile = gmNull.cNull()	# default config file initializes to Null object
#================================
class cCfgBase:
	def __init__(self):
		pass

	def get(workplace = None, user = None, cookie = None, option = None):
		pass

	def set(workplace = None, user = None, cookie = None, option = None, value = None):
		pass
#================================
class cCfgSQL:
	def __init__(self, aConn = None, aDBAPI = None):
		global gmPG_
		if gmPG_ is None:
			from Gnumed.pycommon import gmPG
			gmPG_ = gmPG

		if aConn is None:
			self.__conn = gmPG_.ConnectionPool().GetConnection(service = 'default')
			self.__dbapi = gmPG_.dbapi
		else:
			self.__dbapi = aDBAPI
			self.__conn = aConn

		global cPickle_
		if cPickle_ is None:
			import cPickle
			cPickle_ = cPickle
	#----------------------------
	# external API
	#----------------------------
	def get(self, workplace = None, user = None, cookie = None, option = None):
		"""Get config value from database.

		- works for
			- strings
			- ints/floats
			- (string) lists
		- string lists currently only work with pyPgSQL >= 2.3
		  due to the need for a PgArray data type
		- also string lists will work with PostgreSQL only

		- unset arguments are assumed to mean database defaults except for <cookie>
		"""
		# sanity checks
		if option is None:
			_log.Log(gmLog.lErr, "Need to know which option to retrieve.")
			return None

		cache_key = self.__make_key(workplace, user, cookie, option)

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
		if user is None:
			where_parts.append('vco.owner=CURRENT_USER')
		else:
			where_parts.append('vco.owner=%(owner)s')
			where_args['owner'] = user
		if cookie is not None:
			where_parts.append('vco.cookie=%(cookie)s')
			where_args['cookie'] = cookie
		where_clause = ' and '.join(where_parts)
		cmd = """
select vco.pk_cfg_item, vco.type
from cfg.v_cfg_options vco
where %s
limit 1""" % where_clause

		curs = self.__conn.cursor()
		rows = gmPG_.run_ro_query(curs, cmd, None, where_args)
		if rows is None:
			curs.close()
			_log.Log(gmLog.lErr, 'unable to get option definition for [%s]' % cache_key)
			return None
		if len(rows) == 0:
			curs.close()
			_log.Log(gmLog.lInfo, 'option definition for [%s] not in config database' % cache_key)
			return None
		item_id = rows[0][0]
		value_type = rows[0][1]

		# retrieve value from appropriate table
		cmd = "select value from cfg.cfg_%s where fk_item=%%s limit 1" % value_type
		rows = gmPG_.run_ro_query(curs, cmd, None, item_id)
		curs.close()
		if rows is None:
			_log.Log(gmLog.lErr, 'unable to get option value for [%s]' % cache_key)
			return None
		if len(rows) == 0:
			_log.Log(gmLog.lInfo, 'option value for [%s] not in config database' % cache_key)
			return None
		val = rows[0][0]
		if value_type == 'data':
			val = str(val)
			try:
				val = cPickle_.loads(val)
			except cPickle_.UnpickleError:
				_log.Log(gmLog.lErr, 'cannot unpickle [%s] (type [%s])' % (val, type(val)))
			except:
				_log.LogException("don't know how to cast [%s] (type [%s])" % (val, type(val)), sys.exc_info(), verbose=0)
		return val
	#-----------------------------------------------
	def get2(self, option=None, workplace=None, cookie=None, bias=None, default=None):
		"""Retrieve configuration option from backend.

		- bias 'user'
			When no value is found for "current_user/workplace" look for a value
			for "current_user" regardless of workspace. The corresponding concept is:
			"Did *I* set this option anywhere on this site ? If so, reuse the value."

		- bias 'workplace'
			When no value is found for "current_user/workplace" look for a value
			for "workplace" regardless of user. The corresponding concept is:
			"Did anyone set this option for *this workplace* ? If so, reuse that value."
		"""

		if None in [option, workplace, bias]:
			raise ValueError, 'neither <option> (%s) nor <workplace> (%s) nor <bias> (%s) may be [None]' % (option, workplace, bias)
		if str(bias).lower() not in ['user', 'workplace']:
			raise ValueError, '<bias> must be in [user], [workplace]'
		bias = str(bias).lower()

		# does this option exist ?
		cmd = "select type from cfg.cfg_template where name=%s"
		rows = gmPG.run_ro_query(self.__conn, cmd, None, option)
		if rows is None:
			_log.Log(gmLog.lErr, 'error getting option definition for [%s]' % option)
			return None
		if len(rows) == 0:
			if default is None:
				return None
			_log.Log(gmLog.lInfo, 'creating option [%s] with default [%s]' % (option, default))
			success = self.set (
				workplace = workplace,
				cookie = cookie,
				option = option,
				value = default
			)
			if not success:
				return None
			return default

		cfg_type = rows[0][1]
		args = {
			'opt': option,
			'wp': workplace,
			'cookie': cookie
		}

		# 1) search value with explicit workplace and current user
		where_parts = [
			'vco.owner = CURRENT_USER',
			'vco.workplace = %(wp)s',
			'vco.option = %(opt)s'
		]
		if cookie is not None:
			where_parts.append('vco.cookie = %(cookie)s')
		cmd = "select vco_.value from v_cfg_opts_%s vco_ where\n\t%s\nlimit 1" % (cfg_type, '\tand\n'.join(where_parts))
		rows = gmPG.run_ro_query(self.__conn, cmd, None, args)
		# error
		if rows is None:
			_log.Log(gmLog.lErr, 'error getting value for option [%s]' % option)
			return None
		# found
		if len(rows) > 0:
			return rows[0][0]
		_log.Log(gmLog.lWarn, 'no user AND workplace specific value for option [%s] in config database' % option)

		# 2) search value with biased query
		if bias == 'user':
			# did *I* set this option on *any* workplace ?
			where_parts = [
				'vco.owner = CURRENT_USER',
				'vco.option = %(opt)s'
			]
		else:
			# did *anyone* set this option on *this* workplace ?
			where_parts = [
				'vco.workplace = %(wp)s',
				'vco.option = %(opt)s'
			]
		if cookie is not None:
			where_parts.append('vco.cookie = %(cookie)s')
		cmd = "select vco_.value from v_cfg_opts_%s vco_ where\n\t%s\nlimit 1" % (cfg_type, '\tand\n'.join(where_parts))
		rows = gmPG.run_ro_query(self.__conn, cmd, None, args)
		# error
		if rows is None:
			_log.Log(gmLog.lErr, 'error getting value for option [%s]' % option)
			return None
		# found
		if len(rows) > 0:
			# set explicitely for user/workplace
			self.set (
				workplace = workplace,
				cookie = cookie,
				option = option,
				value = rows[0][0]
			)
			return rows[0][0]
		_log.Log(gmLog.lWarn, 'no user OR workplace specific value for option [%s] in config database' % option)

		# 3) search value within default site policy
		where_parts = [
			'vco.owner = %s' % cfg_DEFAULT,
			'vco.workplace = %s' % cfg_DEFAULT,
			'vco.option = %(opt)s'
		]
		cmd = "select vco_.value from v_cfg_opts_%s vco_ where\n\t%s\nlimit 1" % (cfg_type, '\tand\n'.join(where_parts))
		rows = gmPG.run_ro_query(self.__conn, cmd, None, args)
		# error
		if rows is None:
			_log.Log(gmLog.lErr, 'error getting value for option [%s]' % option)
			return None
		# found
		if len(rows) > 0:
			# set explicitely for user/workplace
			self.set (
				workplace = workplace,
				cookie = cookie,
				option = option,
				value = rows[0][0]
			)
			return rows[0][0]
		_log.Log(gmLog.lWarn, 'no default site policy value for option [%s] in config database' % option)

		# 4) not found, set default ?
		if default is None:
			_log.Log(gmLog.lWarn, 'no default value for option [%s] supplied by caller' % option)
			return None
		_log.Log(gmLog.lInfo, 'setting option [%s] to default [%s]' % (option, default))
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
	def get_by_user(self, option=None, cookie=None, default=None):
		"""Get config option from database w/o regard for the workplace.

		Use this for options in which the workplace does not
		matter. Will search for matches in this order:
			- current user, any workplace
			- default user, default workplace
		The latter is used so an admin can set defaults. If a default
		option is found it is automatically stored for the user.

		Returns None if not found.
		"""
		if option is None:
			raise ValueError, 'option cannot be <None>'

		args = {
			'opt': option,
			'usr': cfg_DEFAULT,
			'cookie': cookie
		}
		# generate query with current user
		where_parts = [
			'(vco.owner = %(usr)s) or (vco.owner = CURRENT_USER)',
			'vco.option = %(opt)s'
		]
		if cookie is not None:
			where_parts.append('vco.cookie = %(cookie)s')
		cmd = """
select
	vco.pk_cfg_item,
	vco.type,
	vco.owner
from cfg.v_cfg_options vco
where
	%s
order by vco.owner
limit 1""" % (' and '.join(where_parts))

		# run it
		rows = gmPG_.run_ro_query(self.__conn, cmd, None, args)
		if rows is None:
			_log.Log(gmLog.lErr, 'error getting option definition')
			return None
		if len(rows) == 0:
			_log.Log(gmLog.lWarn, 'option definition [%s] not in config database' % option)
			# - cannot create default
			if default is None:
				return None
			# - create default
			else:
				_log.Log(gmLog.lInfo, 'setting option [%s] to default [%s]' % (option, default))
				success = self.set (
					option = option,
					value = default
				)
				# - error
				if not success:
					return None
				return default
		# if default option used try to store for user
		if rows[0][2] == cfg_DEFAULT:
			self.set (
				option = option,
				cookie = cookie,
				value = rows[0][0]
			)

		return rows[0][0]
	#-----------------------------------------------
	def get_by_workplace(self, option=None, workplace=None, cookie=None, default=None):
		"""Get config option from database w/o regard for the user.

		Use this for options in which the user does not
		matter. It will search for matches in this order:
			- current workplace, any user
			- default workplace, default user
		The latter is used so an admin can set defaults. If a default
		option is found it is automatically stored specific to the workplace.

		Returns None if not found.
		"""
		if option is None or workplace is None:
			raise ValueError, 'option and/or workplace cannot be <None>'

		args = {
			'opt': option,
			'wplace': workplace,
			'defwplace': cfg_DEFAULT,
			'cookie': cookie
		}
		where_parts_given_workplace = [
			'vco.workplace = %(wplace)s',
			'vco.option = %(opt)s'
		]
		where_parts_default_workplace = [
			'vco.workplace = %(defwplace)s',
			'vco.option = %(opt)s'
		]
		if cookie is not None:
			where_parts_given_workplace.append('vco.cookie = %(cookie)s')
			where_parts_default_workplace.append('vco.cookie = %(cookie)s')

		cmd1 = """
select
	vco.pk_cfg_item,
	vco.type
from cfg.v_cfg_options vco
where
	%s""" % (' and '.join(where_parts_given_workplace))

		cmd2 = """
select
	vco.pk_cfg_item,
	vco.type
from cfg.v_cfg_options vco
where
	%s""" % (' and '.join(where_parts_default_workplace))

		# run it
		rows = gmPG_.run_ro_query(self.__conn, cmd1, None, args)
		# - error
		if rows is None:
			_log.Log(gmLog.lErr, 'error getting option definition')
			return default
		# - not found for given workplace
		if len(rows) == 0:
			# run it for default workplace
			rows = gmPG_.run_ro_query(self.__conn, cmd2, None, args)
			# - error
			if rows is None:
				_log.Log(gmLog.lErr, 'error getting option definition')
				return default
			if len(rows) == 0:
				_log.Log(gmLog.lWarn, 'option definition [%s] not in config database' % option)
				# - cannot create default
				if default is None:
					return None
				# - create default
				_log.Log(gmLog.lInfo, 'setting option [%s] to default [%s]' % (option, default))
#				# try to store specific to *this* workplace
#				self.set (
#					option = option,
#					workplace = workplace,
#					value = default
#				)
				return default
		# found for given or default workplace, now get value
		cmd = """select value from cfg.v_cfg_opts_%s where pk_cfg_item=%%(pk)s""" % rows[0][1]
		args = {'pk': rows[0][0]}
		rows = gmPG_.run_ro_query(self.__conn, cmd, None, args)
		# - error
		if rows is None:
			_log.Log(gmLog.lErr, 'error getting option value')
			return default
		# - not found
		if len(rows) == 0:
			_log.Log(gmLog.lWarn, 'no value for option [%s] in config database' % option)
			# - cannot create default
			if default is None:
				return None
			# - create default
#			_log.Log(gmLog.lInfo, 'setting option [%s] to default [%s]' % (option, default))
#			self.set (
#				option = option,
#				workplace = workplace,
#				value = default
#			)
			return default
		return rows[0][0]
	#-----------------------------------------------
	def getID(self, workplace = None, user = None, cookie = None, option = None):
		"""Get config value from database.

		- unset arguments are assumed to mean database defaults except for <cookie>
		"""
		# sanity checks
		if option is None:
			_log.Log(gmLog.lErr, "Need to know which option to retrieve.")
			return None

		cache_key = self.__make_key(workplace, user, cookie, option)

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
		if user is None:
			where_parts.append('vco.owner=CURRENT_USER')
		else:
			where_parts.append('vco.owner=%(owner)s')
			where_args['owner'] = user
		if cookie is not None:
			where_parts.append('vco.cookie=%(cookie)s')
			where_args['cookie'] = cookie
		where_clause = ' and '.join(where_parts)
		cmd = """
select vco.pk_cfg_item
from cfg.v_cfg_options vco
where %s
limit 1""" % where_clause

		curs = self.__conn.cursor()
		rows = gmPG_.run_ro_query (curs, cmd, None, where_args)
		if rows is None:
			curs.close()
			_log.Log(gmLog.lErr, 'unable to get option definition for [%s]' % cache_key)
			return None
		if len(rows) == 0:
			curs.close()
			_log.Log(gmLog.lWarn, 'option definition for [%s] not in config database' % cache_key)
			return None
		return rows[0][0]
	#----------------------------
	def set(self, workplace = None, user = None, cookie = None, option = None, value = None, aRWConn = None):
		"""Set (insert or update) option value in database.

		Any parameter that is None will be set to the database default.

		Note: you can't change the type of a parameter once it has been
		created in the backend. If you want to change the type you will
		have to delete the parameter and recreate it using the new type.
		"""
		# sanity checks
		if None in [option, value]:
			_log.Log(gmLog.lErr, "option and/or value are None")
			return False

		if aRWConn is None:
			aRWConn = gmPG_.ConnectionPool().GetConnection(service = 'default', readonly=0)

		cache_key = self.__make_key(workplace, user, cookie, option)
		opt_value = value
		if type(value) is types.StringType:
			opt_type = 'string'
		elif type(value) in [types.FloatType, types.IntType, types.LongType]:
			opt_type = 'numeric'
		elif type(value) is types.ListType:
			opt_type = 'str_array'
			try:
				opt_value = self.__dbapi.PgArray(value)
			except AttributeError:
				_log.LogException('this dbapi does not support PgArray', sys.exc_info())
				print "This Python DB-API module does not support the PgArray data type."
				print "It is recommended to install at least version 2.3 of pyPgSQL from"
				print "<http://pypgsql.sourceforge.net>."
				return False
		elif isinstance(value, self.__dbapi.PgArray):
			opt_type = 'str_array'
		# FIXME: UnicodeType ?
		else:
			opt_type = 'data'
			try:
				# the DB-API 2.0 says Binary() is a function at the module
				# level, however, pyPgSQL prides itself to define this at
				# the connection level, arghh !! also, it does not work
				# so this needs to be pgByteA with pyPgSQL while it should
				# be Binary
				opt_value = self.__dbapi.PgBytea(cPickle_.dumps(value))
			except cPickle_.PicklingError:
				_log.Log(gmLog.lErr, "cannot pickle option of type [%s] (key: %s, value: %s)" % (type(value), cache_key, str(value)))
				return False
			except:
				msg = "don't know how to store option of type [%s] (key: %s, value: %s)" % (type(value), cache_key, str(value))
				_log.LogException(msg, sys.exc_info(), verbose=0)
				return False

		# FIXME: we must check if template with same name and 
		# different type exists -> error (won't find double entry on get())
		# get id of option template
		curs = aRWConn.cursor()
		cmd = "select pk from cfg.cfg_template where name=%s and type=%s limit 1"
		rows = gmPG_.run_ro_query(curs, cmd, None, option, opt_type)
		if rows is None:
			curs.close()
			_log.Log(gmLog.lErr, 'cannot find cfg item template for [%s->%s]' % (opt_type, option))
			return False
		# if not in database insert new option template
		if len(rows) == 0:
			# insert new template
			queries = []
			cmd = "insert into cfg.cfg_template (name, type) values (%s, %s)"
			queries.append((cmd, [option, opt_type]))
			cmd = "select currval('cfg.cfg_template_pk_seq')"
			queries.append((cmd, []))
			rows = gmPG_.run_commit(curs, queries)
			if rows is None:
				curs.close()
				_log.Log(gmLog.lErr, 'cannot insert cfg item template for [%s->%s]' % (opt_type, option))
				return False
			aRWConn.commit()
		template_id = rows[0][0]

		# set up field/value pairs
		ins_fields = ['fk_template']
		ins_val_templates = ['%(templ_id)s']
		ins_where_args = {}
		if user is not None:
			ins_fields.append('owner')
			ins_val_templates.append('%(owner)s')
			ins_where_args['owner'] = str(user)

		if workplace is not None:
			ins_fields.append('workplace')
			ins_val_templates.append('%(wplace)s')
			ins_where_args['wplace'] = str(workplace)

		if cookie is not None:
			ins_fields.append('cookie')
			ins_val_templates.append('%(cookie)s')
			ins_where_args[''] = str(cookie)

		# FIXME: this does not always find the existing entry (in particular if user=None)
		# reason: different handling of None in set() and get()
		# do we need to insert a new option or update an existing one ?
		# FIXME: this should be autofixed now since we don't do user/_user anymore, please verify
		if self.get(workplace, user, cookie, option) is None:
			_log.Log(gmLog.lData, 'inserting new option [%s]' % cache_key)
			ins_fields_str = ', '.join(ins_fields)
			ins_val_templates_str = ', '.join(ins_val_templates)
			ins_where_args['templ_id'] = template_id
			queries = []
			cmd = "insert into cfg.cfg_item (%s) values (%s)" % (ins_fields_str, ins_val_templates_str)
			queries.append((cmd, [ins_where_args]))
			cmd = "insert into cfg.cfg_%s (fk_item, value)" % opt_type + " values (currval('cfg.cfg_item_pk_seq'), %s)"
			queries.append((cmd, [opt_value]))
			success = gmPG_.run_commit(curs, queries)
			if success is None:
				curs.close()
				_log.Log(gmLog.lErr, 'cannot insert option [%s]' % cache_key)
				return False
		else:
			_log.Log(gmLog.lData, 'updating existing option [%s]' % cache_key)
			item_id = self.getID(workplace, user, cookie, option)
			if item_id is None:
				curs.close()
				return False
			# update option instance
			args = {'val': opt_value, 'item_id': item_id}
			cmd = "update cfg.cfg_%s" % opt_type + " set value=%(val)s where fk_item=%(item_id)s"
			if gmPG_.run_query(curs, None, cmd, args) is None:
				curs.close()
				return False

		aRWConn.commit()
		curs.close()
		return True
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

		curs = self.__conn.cursor()

		# retrieve option definition
		if gmPG_.run_query(curs, None, cmd, where_args) is None:
			curs.close()
			return None

		# result should contain a list of strings
		result = curs.fetchall()
		curs.close()

		if result is None:
			_log.Log(gmLog.lWarn, 'no parameters stored for [%s@%s] in config database' % (user, workplace))
			return None

		return result
	#----------------------------
	def delete(self, workplace = cfg_DEFAULT, user = None, cookie = cfg_DEFAULT, option = None, aRWConn = None):
		"""
		Deletes an option or a whole group.
		Note you have to call store() in order to save
		the changes.
		"""
		# sanity checks
		if option is None:
			_log.Log(gmLog.lErr, "Need to know which option to delete.")
			return None
		if aRWConn is None:
			_log.Log(gmLog.lErr, "Need rw connection to database to delete the value.")
			return None

		cache_key = self.__make_key(workplace, user, cookie, option)
		
		curs = aRWConn.cursor()

		# get item id
		item_id = self.getID(workplace, user, cookie, option)
		if item_id is None:
			curs.close()
			return None

		# get template id, template type
		cmd = """
select fk_template, type from cfg.cfg_item, cfg.cfg_template
where cfg.cfg_item.pk = %s and cfg.cfg_item.fk_template = cfg.cfg_template.pk
limit 1"""
		if gmPG_.run_query(curs, None, cmd, item_id) is None:
			curs.close()
			return None
		result = curs.fetchone()		
		template_id, template_type = result

		# check if this is the only reference to this template
		# if yes, delete template, too
		# here we assume that only 
		cmd = "select pk from cfg.cfg_item where fk_template = %s"
		if gmPG_.run_query(curs, None, cmd, template_id) is None:
			curs.close()
			return None
		result = curs.fetchall()		
		template_ref_count = len(result)

		# delete option 
		cmd = """
		delete from cfg.cfg_%s where fk_item=%s;
		delete from cfg.cfg_item where pk='%s';""" % (template_type, item_id, item_id)
		if gmPG_.run_query(curs, None, cmd) is None:
			curs.close()
			return None

		# delete template if last reference
		if template_ref_count == 1:
			cmd = "delete from cfg.cfg_template where pk=%s"
			if gmPG_.run_query(curs, None, cmd, template_id) is None:
				curs.close()
				return None
		
		# actually commit our stuff
		aRWConn.commit()
		curs.close()

		return 1
	#----------------------------
	def __make_key(self, workplace, user, cookie, option):
		return '%s-%s-%s-%s' % (workplace, user, cookie, option)
#================================
class cCfgFile:
	"""Handle common INI-style config files.

	The INI file structure follows the common rules. Option values
	can be strings or lists of strings. Lists are handled transparently.
	The list format is as follows:

	listname = $listname$ # comment
	item 1
	item 2
	item 3
	$listname$

	Config data is cached in the following layout:

	self._cfg_data	= {dict}
	|
	|-> 'comment'	= [list of strings]
	`-> 'groups'	= {dict}
	 |
	 |-> group 1	= {dict}
	 | ...
	 `-> group n
	  |
	  |-> 'comment' = [list of strings]
	  `-> 'options'	= {dict}
	   |
	   |-> option 1	= {dict}
	   | ...
	   `-> option n
		|
		|-> 'comment' [list of strings]
		`-> 'value'
	"""

	_modified = None
	#----------------------------
	def __init__(self, aPath = None, aFile = None, flags = 0, aContents = None):
		"""Init ConfigFile object. For valid combinations of these
		parameters see above. Raises a ConfigError exception if
		no config file could be found. 
		"""
		self._cfg_data = {}
		# lazy import gmCLI
		global gmCLI_
		if gmCLI_ is None:
			from Gnumed.pycommon import gmCLI
			gmCLI_ = gmCLI
		if aContents:
			if not self.__parse_conf(aContents.split('\n')):
				raise SyntaxError, "cannot parse config file"
		else:
			# get conf file name
			if not self.__get_conf_name(aPath, aFile, flags):
				raise IOError, "cannot find config file"
			# load config file
			if not self.__parse_conf_file():
				raise SyntaxError, "cannot parse config file"
	#----------------------------
	# API - access config data
	#----------------------------
	def getCfg(self):
		"""Return handle to entire config dict."""
		return self._cfg_data
	#----------------------------
	def getGroups(self):
		"""Return list of all groups in config dict."""
		return self._cfg_data['groups'].keys()
	#----------------------------
	def getOptions(self, aGroup = None):
		"""Return list of all options in a group."""
		if not self._cfg_data['groups'].has_key(aGroup):
			_log.Log(gmLog.lWarn, "Cannot return options for [%s]. No such group." % aGroup)
			return None

		return self._cfg_data['groups'][aGroup]['options'].keys()
	#----------------------------
	def get(self, aGroup = None, anOption = None):
		if not self._cfg_data['groups'].has_key(aGroup):
			_log.Log(gmLog.lWarn, 'group [%s] not found' % aGroup)
			return None

		group = self._cfg_data['groups'][aGroup]

		if not group['options'].has_key(anOption):
			_log.Log(gmLog.lWarn, 'option <%s> not found in group [%s]' % (anOption, aGroup))
			return None

		return group['options'][anOption]['value']
	#----------------------------
	def getComment(self, aGroup = None, anOption = None):
		# file level
		if aGroup is None:
			# return file level comment if available
			if self._cfg_data.has_key('comment'):
				return self._cfg_data['comment']
			else:
				_log.Log(gmLog.lWarn, 'file [%s] has no comment' % self.cfgName)
				return None

		# group or option level
		if self._cfg_data['groups'].has_key(aGroup):
			if anOption is None:
				if self._cfg_data['groups'][aGroup].has_key('comment'):
					return self._cfg_data['groups'][aGroup]['comment']
				else:
					_log.Log(gmLog.lWarn, 'group [%s] (in [%s]) has no comment' % (aGroup, self.cfgName))
					return None
			else:
				if self._cfg_data['groups'][aGroup]['options'].has_key(anOption):
					if self._cfg_data['groups'][aGroup]['options'][anOption].has_key('comment'):
						return self._cfg_data['groups'][aGroup]['options'][anOption]['comment']
					else:
						_log.Log(gmLog.lWarn, 'option [%s] in group [%s] (in [%s]) has no comment' % (anOption, aGroup, self.cfgName))
						return None
				else:
					_log.Log(gmLog.lErr, 'option [%s] not in group [%s] in file [%s]' % (anOption, aGroup, self.cfgName))
					return None
		else:
			_log.Log(gmLog.lErr, 'group [%s] not in file [%s]' % (aGroup, self.cfgName))
			return None
	#----------------------------
	# API - setting config items
	#----------------------------
	def set(self, aGroup = None, anOption = None, aValue = None, aComment = None):
		"""Set an option to an arbitrary type.

		This does not write the changed configuration to a file !
		"""
		# setting file level comment ?
		if aGroup is None:
			if aComment is None:
				_log.Log(gmLog.lErr, "don't know what to do with (aGroup = %s, anOption = %s, aValue = %s, aComment = %s)" % (aGroup, anOption, aValue, aComment))
				return None
			self._cfg_data['comment'] = [str(aComment)]
			self._modified = 1
			return 1

		# make sure group is there
		if not self._cfg_data['groups'].has_key(aGroup):
			self._cfg_data['groups'][aGroup] = {'options': {}}

		# setting group level comment ?
		if anOption is None:
			if aComment is None:
				_log.Log(gmLog.lErr, "don't know what to do with (aGroup = %s, anOption = %s, aValue = %s, aComment = %s)" % (aGroup, anOption, aValue, aComment))
				return None
			self._cfg_data['groups'][aGroup]['comment'] = aComment
			self._modified = 1
			return 1

		# setting option
		if aValue is None:
			_log.Log(gmLog.lErr, "don't know what to do with (aGroup = %s, anOption = %s, aValue = %s, aComment = %s)" % (aGroup, anOption, aValue, aComment))
			return None
		# make sure option is there
		if not self._cfg_data['groups'][aGroup]['options'].has_key(anOption):
			self._cfg_data['groups'][aGroup]['options'][anOption] = {}
		# set value
		self._cfg_data['groups'][aGroup]['options'][anOption]['value'] = aValue
		# set comment
		if not aComment is None:
			self._cfg_data['groups'][aGroup]['options'][anOption]['comment'] = aComment
		self._modified = 1
		return 1
	#----------------------------
	def store(self):
		"""Store changed configuration in config file.

		- first backup old config file in case we want to take
		  back changes of content
		- then create the new config file with a separate name
		- only copy the new file to the old name if writing the
		  new file succeeds
		# FIXME: actually we need to reread the config file here before writing
		"""
		if not self._modified:
			_log.Log(gmLog.lInfo, "No changed items: nothing to be stored.")
			return 1

		bak_name = "%s.gmCfg.bak" % self.cfgName
		try:
			os.remove(bak_name)
		except:
			pass

		try:
			shutil.copyfile(self.cfgName, bak_name)
		except:
			_log.LogException("Problem backing up config file !", sys.exc_info(), verbose=0)

		# open new file for writing
		new_name = "%s.gmCfg.new" % self.cfgName
		new_file = open(new_name, "wb")

		# file level comment
		if self._cfg_data.has_key('comment'):
			if not self._cfg_data['comment'] == []:
				for line in self._cfg_data['comment']:
					new_file.write("# %s\n" % line)
				new_file.write("\n")
		# loop over groups
		for group in self._cfg_data['groups'].keys():
			gdata = self._cfg_data['groups'][group]
			# group level comment
			if gdata.has_key('comment'):
				if not gdata['comment'] == []:
					for line in gdata['comment']:
						new_file.write("# %s\n" % line)
			new_file.write("[%s]\n" % group)
			# loop over options for group
			for opt in gdata['options'].keys():
				odata = gdata['options'][opt]
				# option level comment
				if odata.has_key('comment'):
					for line in odata['comment']:
						new_file.write("# %s\n" % line)
				if type(odata['value']) == type([]):
					new_file.write("%s = $%s$\n" % (opt, opt))
					for line in odata['value']:
						new_file.write("%s\n" % line)
					new_file.write("$%s$\n" % opt)
				else:
					new_file.write("%s = %s\n" % (opt, odata['value']))
			new_file.write("\n\n")

		new_file.close()
		# copy new file to old file
		try:
			shutil.copyfile(new_name, self.cfgName)
		except StandardError:
			_log.LogException('cannot move modified options into config file', verbose=0)

		os.remove(new_name)
		return 1
	#----------------------------
	def delete(self, aGroup = None, anOption = None):
		"""
		Deletes an option or a whole group.
		Note that you have to call store() in order to save
		the changes.
		"""
		# check if the group exists
		if aGroup is not None:
			if not self._cfg_data['groups'].has_key(aGroup):
				_log.Log(gmLog.lWarn, 'group [%s] not found' % aGroup)
				return None
		else:
			_log.Log(gmLog.lWarn, 'No group to delete specified.')
			return None
		
		# now we know that the group exists
		if anOption is None:
			del self._cfg_data['groups'][aGroup]
			return 1
		else:			
			group = self._cfg_data['groups'][aGroup]

			if not group['options'].has_key(anOption):
				_log.Log(gmLog.lWarn, 'option <%s> not found in group [%s]' % (anOption, aGroup))
				return None
			else:
				del group['options'][anOption]
		return 1

	#----------------------------
	# internal methods
	#----------------------------
	def __get_conf_name(self, aDir = None, aName = None, flags = 0):
		"""Try to construct a valid config file name.

		- None: no valid name found
		- true(1): valid name found
		"""
		_log.Log(gmLog.lData, '(<aDir=%s>, <aName=%s>)' % (aDir, aName))

		# did the user manually supply a config file on the command line ?
		if not (flags & cfg_IGNORE_CMD_LINE):
			# and check command line options
			if gmCLI_.has_arg('--conf-file'):
				self.cfgName = gmCLI_.arg['--conf-file']
				# file valid ?
				if os.path.isfile(self.cfgName):
					_log.Log(gmLog.lData, 'found config file [--conf-file=%s]' % self.cfgName)
					return 1
				else:
					_log.Log(gmLog.lErr, "config file [--conf-file=%s] not found, aborting" % self.cfgName)
					return None
			else:
				_log.Log(gmLog.lData, "No config file given on command line. Format: --conf-file=<config file>")
		else:
			_log.Log(gmLog.lInfo, 'ignoring command line per cfg_IGNORE_CMD_LINE')

		candidate_files = []

		# now make base path components
		base_name = None
		base_dir = None
		# 1) get base name:
		if aName is None:
			# - from name of script if no file name given
			base_name = os.path.splitext(os.path.basename(sys.argv[0]))[0] + ".conf"
		else:
			# - from given file name/dir
			# don't try to expand give file name if
			# explicitely asked to search in standard dirs
			if (flags & cfg_SEARCH_STD_DIRS):
				base_name = aName
			# else do try to expand
			else:
				if aDir is None:
					absName = os.path.abspath(aName)
				else :
					absName = os.path.abspath(os.path.join(aDir, aName))
				# this candidate will stay the only one
				candidate_files.append(absName)
		# 2) get base dir
		if aDir is None:
			# from name of script
			base_dir = os.path.splitext(os.path.basename(sys.argv[0]))[0]
		else:
			# or from path in arguments
			base_dir = aDir

		# if we don't have a filename given we explicitly want
		# to search various locations -> create location list
		# if the programmer specified a filename and 
		# does NOT want to search standard dirs then only try
		# to find that very location (i.e. skip std dir generation)
		if (flags & cfg_SEARCH_STD_DIRS) or aName is None:
			# create list of standard config file locations
			std_dirs = []
			# - $(<script-name>_DIR)/etc/
			env_key = "%s_DIR" % string.upper(os.path.splitext(os.path.basename(sys.argv[0]))[0])
			if os.environ.has_key(env_key):
				env_key_val = os.environ[env_key]
				a_dir = os.path.abspath(os.path.expanduser(os.path.join(env_key_val, 'etc')))
				std_dirs.append(a_dir)
			else:
				_log.Log(gmLog.lInfo, "$%s not set" % env_key)

			# - ~/.base_dir/
			a_dir = os.path.expanduser(os.path.join('~', '.' + base_dir))
			std_dirs.append(a_dir)	

			# - /etc/base_dir/
			a_dir = os.path.join('/etc', base_dir)
			std_dirs.append(a_dir)

			# - /etc/
			std_dirs.append('/etc')

			# - ./
			# last resort for inferior operating systems such as DOS/Windows
			a_dir = os.path.abspath(os.path.split(sys.argv[0])[0])
			std_dirs.append(a_dir)
			std_dirs.append(os.path.join (a_dir, '..', 'etc'))

			# compile candidate file names from
			# standard dirs and base name
			for a_dir in std_dirs:
				candidate_files.append(os.path.join(a_dir, base_name))

			# eventually add hidden file:
			# - ~/.base_name
			cfgNameHidden = os.path.expanduser(os.path.join('~', '.' + base_name))
			candidate_files.insert(1, cfgNameHidden)

		_log.Log(gmLog.lData, "config file search order: %s" % str(candidate_files))

		# eventually loop through all candidates
		for candidate in (candidate_files):
			if not os.path.isfile(candidate):
				_log.Log(gmLog.lInfo, "config file [%s] not found" % candidate)
			else:
				_log.Log(gmLog.lInfo, 'found config file [%s]' % candidate)
				self.cfgName = candidate
				return 1

		# still don't have a valid config file name ?!?
		# we can't help it
		_log.Log(gmLog.lErr, "cannot find config file in any of the standard paths")
		return None
	#----------------------------
	def __parse_conf_file(self):
		if not os.path.exists(self.cfgName):
			_log.Log(gmLog.lWarn, "config file [%s] not found" % self.cfgName)

		_log.Log(gmLog.lData, "parsing config file [%s]" % self.cfgName)

		return self.__parse_conf (fileinput.input(self.cfgName))

	#-------------------------------------------------
	def __parse_conf (self, conf_file):
		self._cfg_data['groups'] = {}

		curr_group = None
		curr_opt = None
		in_list = None
		comment_buf = []
		file_comment_buf = []
		for line in conf_file:
			# remove trailing CR and/or LF
			line = string.replace(line,'\015','')
			line = string.replace(line,'\012','')
			# remove leading/trailing whitespace
			line = string.strip(line)

			#-----------------------
			# are we inside a list ?
			if in_list:
				# end of list ?
				if line == ("$%s$" % curr_opt):
					in_list = None
					continue
				# else keep unmodified line as list item
				self._cfg_data['groups'][curr_group]['options'][curr_opt]['value'].append(line)
				continue

			#-----------------------
			# ignore empty lines
			if line == "":
				# if before first group
				if curr_group is None:
					if self._cfg_data.has_key('comment'):
						self._cfg_data['comment'].append(comment_buf)
					else:
						self._cfg_data['comment'] = comment_buf
					comment_buf = []
				continue

			#----------
			# comment ?
			if line.startswith('#') or line.startswith(';'):
				comment = string.strip(line[1:])
				if not comment == "":
					comment_buf.append(comment)
				continue

			#----------
			# [group] ?
			if line.startswith('['):
				try:
					tmp, comment = line.split(']', 1)
				except:
					_log.Log(gmLog.lErr, 'parse error in line #%s of config file [%s]' % (fileinput.filelineno(), fileinput.filename()))
					raise
				if tmp == "[":
					_log.Log(gmLog.lErr, 'empty group definition "[]" not allowed')
					continue

				comment = string.strip(comment)
				if not comment == "":
					comment_buf.append(comment)

				curr_group = tmp[1:]
				if self._cfg_data['groups'].has_key(curr_group):
					_log.Log(gmLog.lWarn, 'duplicate group [%s] (file [%s]) - overriding options' % (curr_group, self.cfgName))
				else:
					self._cfg_data['groups'][curr_group] = {'options': {}}

				self._cfg_data['groups'][curr_group]['comment'] = comment_buf
				comment_buf = []
				continue

			#----------
			# option= ?
			if not curr_group:
				_log.Log(gmLog.lErr, 'option found before first group statement')
				continue

			#  normalize
			colon_pos = line.find(":")
			equal_pos = line.find("=")
			if colon_pos == -1 and equal_pos == -1:
				_log.Log(gmLog.lErr, 'option [%s] does not contain a separator ("=" or ":")' % line)
				continue
			if colon_pos < equal_pos:
				line = line.replace(':', '=', 1)

			#  separate <opt_name> = <opt_val # opt_comment>
			name, tmp = line.split('=', 1)
			name = string.strip(name)
			if name == "":
				_log.Log(gmLog.lErr, 'option name must not be empty')
				continue
			curr_opt = name
			if self._cfg_data['groups'][curr_group]['options'].has_key(curr_opt):
				_log.Log(gmLog.lWarn, 'duplicate option [%s] (group [%s], file [%s]) - overriding value' % (curr_opt, curr_group, self.cfgName))
			else:
				self._cfg_data['groups'][curr_group]['options'][curr_opt] = {}

			#  normalize again
			tmp = string.replace(tmp, ';', '#', 1)
			if tmp.find("#") == -1:
				val = tmp
				comment = ""
			else:
				#  separate <opt_val> # <opt_comment>
				val, comment = tmp.split('#', 1)
				comment = string.strip(comment)
			val = string.strip(val)
			if comment != "":
				comment_buf.append(comment)

			self._cfg_data['groups'][curr_group]['options'][curr_opt]['comment'] = comment_buf
			comment_buf = []

			# start of list ?
			if val == ("$%s$" % curr_opt):
				in_list = 1
				self._cfg_data['groups'][curr_group]['options'][curr_opt]['value'] = []
			else:
				self._cfg_data['groups'][curr_group]['options'][curr_opt]['value'] = val

		return 1
#=============================================================
def create_default_cfg_file():
	# get base dir from name of script
	base_dir = os.path.splitext(os.path.basename(sys.argv[0]))[0]

	# make sure base directory is there
	# FIXME: this isn't portable very well
	# - should we rather use the current dir ?
	# - but no, this may not be writeable
	tmp = os.path.expanduser(os.path.join('~', "." + base_dir))
	if not os.path.exists(tmp):
		os.mkdir(tmp)

	base_dir = tmp

	# get base name from name of script
	base_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
	conf_name = base_name + ".conf"

	# - now the path exists but we still need to
	#   make sure the file itself exists
	tmp = os.path.join(base_dir, conf_name)
	if not os.path.exists(tmp):
		try:
			f = open(tmp, "wb")
			f.write('# [%s]: empty default config file\n' % base_name)
			f.write('# -------------------------------------------------------------\n')
			f.write('# created by gmCfg because no other config file could be found,\n')
			f.write('# please check the docs that came with the software\n')
			f.write('# to find out what options you can set in here\n')
			f.write('\n')
			f.close()
		except StandardError:
			_log.LogException("Cannot create empty default config file [%s]." % tmp, sys.exc_info(), verbose=0)
			return None

	_log.Log(gmLog.lErr, 'Created empty config file [%s].' % tmp)
	print "Had to create empty (default) config file [%s].\nPlease check the docs for possible settings." % tmp
	return 1
#-------------------------------------------------------------
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

	global gmPG_
	if gmPG_ is None:
		from Gnumed.pycommon import gmPG
		gmPG_ = gmPG

	# connect to database (imports gmPG if need be)
	db = gmPG_.ConnectionPool()
	conn = db.GetConnection(service = "default", extra_verbose=0)
	dbcfg = cCfgSQL (
		aConn = conn,
		aDBAPI = gmPG_.dbapi
	)

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
		_log.Log(gmLog.lData, '[%s] not found for [%s@%s]' % (option, set[1], set[2]))

	# cleanup
	db.ReleaseConnection(service = "default")
	if matchingSet is None:
		_log.Log (gmLog.lWarn, 'no config data for [%s]' % option)
	return (result, matchingSet)
#-------------------------------------------------------------
def setDBParam(workplace = None, user = None, cookie = None, option = None, value = None):
	"""Convenience function to store config values in database.

	We assume that the config tables are found on service "default".
	That way we can handle the db connection inside this function.

	Omitting any parameter (or setting to None) will store database defaults for it.

	- returns True/False
	"""
	# import gmPG if need be
	global gmPG_
	if gmPG_ is None:
		from Gnumed.pycommon import gmPG
		gmPG_ = gmPG

	# connect to database
	db = gmPG_.ConnectionPool()
	conn = db.GetConnection(service = "default")
	dbcfg = cCfgSQL(aConn = conn, aDBAPI = gmPG_.dbapi)
	rwconn = db.GetConnection(service = "default", readonly = 0)
	if rwconn is None:
		_log.Log(gmLog.lWarn, 'unable to get a rw connection')
		db.ReleaseConnection(service = "default")
		return False
	# set value
	success = dbcfg.set(
		workplace = workplace,
		user = user,
		option = option,
		value = value,
		aRWConn = rwconn
	)
	rwconn.close()
	db.ReleaseConnection(service = "default")

	if not success:
		return False
	return True
#=============================================================
# main
#=============================================================
if __name__ == "__main__":
	_log.SetAllLogLevels(gmLog.lData)
	# if there's an argument assume it to be a config
	# file and test that
	if len(sys.argv) > 1:
		print "testing config file handling"
		print "============================"
		try:
			myCfg = cCfgFile(aFile = sys.argv[1])
#			myCfg = cCfgFile(aFile = sys.argv[1],flags=cfg_SEARCH_STD_DIRS)
		except:
			exc = sys.exc_info()
			_log.LogException('unhandled exception', exc, verbose=1)
			raise

		print myCfg

		# display file level data
		print "file: %s" % myCfg.cfgName
		tmp = myCfg.getComment()
		if not tmp is None:
			print "comment:", tmp

		# display group level data
		groups = myCfg.getGroups()
		print "groups:", str(groups)

		# recurse groups
		for group in groups:
			print "GROUP [%s]" % group

			tmp = myCfg.getComment(aGroup = group)
			if not tmp is None:
				print " ", tmp

			# recurse options
			options = myCfg.getOptions(group)
			for option in options:
				tmp = myCfg.get(group, option)
				if not tmp is None:
					print "OPTION <%s> = >>>%s<<<" % (option, tmp)
				tmp = myCfg.getComment(group, option)
				if not tmp is None:
					print "  %s" % tmp

		myCfg.set("date", "modified", "right now", ["should always be rather current"])
		myCfg.store()

		sys.exit(0)

	# else test database config
	print "testing database config"
	print "======================="
#	from pyPgSQL import PgSQL
#	dsn = "%s:%s:%s:%s:%s:%s:%s" % ('localhost', '5432', 'gnumed_v2', 'any-doc', 'any-doc', '', '')
#	conn = PgSQL.connect(dsn)
	myDBCfg = cCfgSQL()

	font = myDBCfg.get(option = 'font name')
	print "font is currently:", font

	new_font = "huh ?"
	if font == "Times New Roman":
		new_font = "Courier"
	if font == "Courier":
		new_font = "Times New Roman"
#	myDBCfg.set(option='font name', value=new_font, aRWConn=conn)
	myDBCfg.set(option='font name', value=new_font)

	font = myDBCfg.get(option = 'font name')
	print "font is now:", font

	import random
	random.seed()
	new_opt = str(random.random())
	print "setting new option", new_opt
#	myDBCfg.set(option=new_opt, value = "I do not know.", aRWConn=conn)
	myDBCfg.set(option=new_opt, value = "I do not know.")
	print "new option is now:", myDBCfg.get(option = new_opt)

	print "setting array option"
	aList = []
	aList.append("val 1")
	aList.append("val 2")
	new_opt = str(random.random())
#	myDBCfg.set(option=new_opt, value = aList, aRWConn=conn)
	myDBCfg.set(option=new_opt, value = aList)
	aList = []
	aList.append("val 2")
	aList.append("val 1")
#	myDBCfg.set(option=new_opt, value = aList, aRWConn=conn)
	myDBCfg.set(option=new_opt, value = aList)

#	myDBCfg.set(user = cfg_DEFAULT, option = "blatest", value = "xxx", aRWConn = conn)
	myDBCfg.set(user = cfg_DEFAULT, option = "blatest", value = "xxx")
	print "blatest set to:", myDBCfg.get(workplace = cfg_DEFAULT, user=cfg_DEFAULT, option = "blatest")
		
#	myDBCfg.delete(user = cfg_DEFAULT, option = "blatest", aRWConn = conn)
	myDBCfg.delete(user = cfg_DEFAULT, option = "blatest")
	print "after deletion blatest set to:", myDBCfg.get(workplace = cfg_DEFAULT, user=cfg_DEFAULT, option = "blatest")

	print "setting complex option"
	data = {1: 'line 1', 2: 'line2', 3: {1: 'line3.1', 2: 'line3.2'}}
#	myDBCfg.set(user = cfg_DEFAULT, option = "complex option test", value = data, aRWConn = conn)
	myDBCfg.set(user = cfg_DEFAULT, option = "complex option test", value = data)
	print "complex option set to:", myDBCfg.get(workplace = cfg_DEFAULT, user=cfg_DEFAULT, option = "complex option test")
#	myDBCfg.delete(user=cfg_DEFAULT, option = "complex option test", aRWConn = conn)
	myDBCfg.delete(user=cfg_DEFAULT, option = "complex option test")

#	conn.close()

#	val, set = getDBParam(workplace = "test", cookie = "gui", option = "plugin load order")
#	print "found set for [plugin load order.gui] for %s: \n%s" % (set,str(val))

else:
	# - we are being imported

	# - IF the caller really knows what she does she can handle
	#   that exception in her own code
	try:
		gmDefCfgFile = cCfgFile()
	except:
		_log.LogException('unhandled exception', sys.exc_info(), verbose=0)

#=============================================================
# $Log: gmCfg.py,v $
# Revision 1.37  2006-02-27 15:39:06  ncq
# - add cCfg_SQL.get2()
#
# Revision 1.36  2006/01/13 14:57:14  ncq
# - really fix get_by_workplace() - still needs set() functionality
#
# Revision 1.35  2006/01/01 17:22:08  ncq
# - get_by_workplace always returns default value in case of
#   errors/option not found except when there is not default given
#   in which case it will return None on error
#
# Revision 1.34  2005/12/30 16:51:03  ncq
# - slightly improved method documentation
#
# Revision 1.33  2005/12/14 16:56:09  ncq
# - enhance get_by_user() and get_by_workplace() with a default
#   which if set will enable to store the option even if there's
#   no template in the database
# - fix unit test
#
# Revision 1.32  2005/12/14 10:41:11  ncq
# - allow cCfgSQL to set up its own connection if none given
# - add cCfgSQL.get_by_user()
# - smarten up cCfgSQL.get()
#
# Revision 1.31  2005/11/19 08:47:56  ihaywood
# tiny bugfixes
#
# Revision 1.30  2005/11/18 15:48:44  ncq
# - config tables now in cfg.* schema so adjust to that
# - also some id -> pk changes
#
# Revision 1.29  2005/10/10 18:05:46  ncq
# - ignore error on failing to delete non-existant backup config
#   file as that was way over the top behaviour
#
# Revision 1.28  2005/10/08 09:24:09  ihaywood
# lack of a backup config file is now an warning only.
#
# Revision 1.27  2005/08/14 15:35:31  ncq
# - cleanup
#
# Revision 1.26  2005/02/05 10:58:09  ihaywood
# fixed patient picture problem (gratutious use of a named parameter)
# more rationalisation of loggin in gmCfg
#
# Revision 1.24  2005/01/10 11:46:51  ncq
# - make cCfgSQL also support arbitrary option values in cfg_data
#
# Revision 1.23  2004/09/06 22:18:12  ncq
# - eventually fix the get/setDBParam(), at least it appears to work
#
# Revision 1.22  2004/09/02 00:39:27  ncq
# - use new v_cfg_options
# - remove personalize argument from getDBParam() in favour of clarity
#
# Revision 1.21  2004/08/24 13:40:43  ncq
# - when cleaning up cfgSQL.set() I screwed up, fixed
#
# Revision 1.20  2004/08/23 10:24:10  ncq
# - made setdbparam saner re default params, eg. param=None will set to
#   database default, eg if anything else wanted user needs to explicitely
#   set
# - cleanup
#
# Revision 1.19  2004/08/20 13:22:13  ncq
# - cleanup
# - getFirstMatchingDBSet() -> getDBParam()
# - argument personalize default true in getDBParam() stores
#   option value if found for other that current user/current workspace
#
# Revision 1.18  2004/08/16 12:15:20  ncq
# - don't hide module global gmDefCfgFile inside "if __name__ == '__main__'" so
#   that epydoc picks it up properly for documentation
#
# Revision 1.17  2004/08/16 12:06:50  ncq
# - hopefully improve docstring by including import example
#
# Revision 1.16  2004/08/11 11:07:33  ncq
# - needless args on cfg queries removed
#
# Revision 1.15  2004/08/11 08:00:05  ncq
# - improve log prefix
# - cleanup SQL cfg/remove old use of _USER
#
# Revision 1.14  2004/07/24 17:10:09  ncq
# - fix getAllParams()
#
# Revision 1.13  2004/07/19 13:53:35  ncq
# - some cleanup re setDBParam()/getFirstMatchingDBset()
#
# Revision 1.12  2004/07/19 11:50:42  ncq
# - cfg: what used to be called "machine" really is "workplace", so fix
#
# Revision 1.11  2004/07/17 21:08:51  ncq
# - gmPG.run_query() now has a verbosity parameter, so use it
#
# Revision 1.10  2004/07/12 13:49:39  ncq
# - log version
#
# Revision 1.9  2004/07/12 02:48:40  ihaywood
# same again
#
# Revision 1.8  2004/07/12 02:44:12  ihaywood
# it should not be neccessary to specify the full path when
# importing from the same package.
# It makes the file gratutiously dependent on being in the gnumed
# directory structure.
#
# Revision 1.7  2004/07/06 00:25:17  ncq
# - assign Null design pattern instance if no default cfg file found
#
# Revision 1.6  2004/06/28 22:36:33  hinnef
# added lazy loading of gmPG to gmCfgSQL:getAllParams
#
# Revision 1.5  2004/06/22 07:58:47  ihaywood
# minor bugfixes
# let gmCfg cope with config files that are not real files
#
# Revision 1.4  2004/06/19 18:55:44  shilbert
# - fixes for various import statements
#
# Revision 1.3  2004/02/26 14:32:46  ncq
# - fixed and lazied even more
#
# Revision 1.2  2004/02/25 22:56:38  sjtan
#
# probably a typo ; temp fix until authors see it.
#
# Revision 1.1  2004/02/25 09:30:13  ncq
# - moved here from python-common
#
# Revision 1.71  2004/02/25 08:46:12  ncq
# - hopefully lazyied the import of gmCLI, too
#
# Revision 1.70  2004/02/25 08:39:04  ncq
# - I think I removed the dependancy on gmPG as long as cCfgSQL isn't used
#
# Revision 1.69  2004/01/06 23:44:40  ncq
# - __default__ -> xxxDEFAULTxxx
#
# Revision 1.68  2003/11/22 02:03:48  ihaywood
# reverted to version 1.66
#
# Revision 1.66  2003/10/22 22:05:18  ncq
# - cleanup, coding style
#
# Revision 1.65  2003/10/22 21:37:04  hinnef
# added convenience function setDBParam() to reduce redundant code on setting backend parameters
#
# Revision 1.64  2003/10/02 20:01:15  hinnef
# fixed selection of user in gmcfgSQL.get/getID/getAllParams so that _user will be found, too
#
# Revision 1.63  2003/09/26 19:35:21  hinnef
# - added delete() methods in cCfgFile and cCfgSQL, small fixes in cfgSQL.set()
#
# Revision 1.62  2003/09/24 10:32:13  ncq
# - in _get_conf_name() we need to make std_dirs when aName is None,
#   not aDir, also init base_name/base_dir to a known state
#
# Revision 1.61  2003/09/21 08:37:47  ihaywood
# database code now properly escaped
#
# Revision 1.60  2003/08/24 13:36:39  hinnef
# added getFirstMatchingDBSet() for convenient config data retrieval
#
# Revision 1.59  2003/08/24 08:01:44  ncq
# - removed some dead code, cleanup
#
# Revision 1.58  2003/08/23 18:33:50  hinnef
# added small comment in __get_conf_name(), commented out two verbose debug messages
#
# Revision 1.57  2003/08/10 00:53:09  ncq
# - cleanup to Hilmars nice additions
#
# Revision 1.56  2003/08/07 23:31:04  hinnef
# changed CfgFile.__get_conf_name so that files can be searched in more than one location
#
# Revision 1.55  2003/07/21 20:53:50  ncq
# - fix string screwup
#
# Revision 1.54  2003/07/21 19:18:06  ncq
# - use gmPG.run_query(), not home-brew
# - kill gmPG.esc() use
# - cleanup/comments
#
# Revision 1.53  2003/06/26 21:29:58  ncq
# - (cmd, arg) style, fatal->verbose
#
# Revision 1.52  2003/06/26 04:18:40  ihaywood
# Fixes to gmCfg for commas
#
# Revision 1.51  2003/06/21 10:44:09  ncq
# - handle read-only media better when modifying config file
#
# Revision 1.50  2003/06/17 22:21:53  ncq
# - improve __get_conf_name()
#
# Revision 1.49  2003/06/03 21:52:23  hinnef
# - fixed a bug in cfgSQL.set() when updating a value
#
# Revision 1.48  2003/05/12 09:12:48  ncq
# - minor cleanups
#
# Revision 1.47  2003/05/10 18:45:52  hinnef
# - added getAllParams for use in gmConfigRegistry
#
# Revision 1.46  2003/04/14 07:45:47  ncq
# - better temp names in cfgFile.store()
#
# Revision 1.45  2003/03/31 00:26:46  ncq
# - forgot "\n"
#
# Revision 1.44  2003/03/30 21:38:28  ncq
# - put some blurb in new, empty config files
#
# Revision 1.43  2003/03/27 21:10:12  ncq
# - move '__default__' to cfg_DEFAULT constant
#
# Revision 1.42  2003/03/23 10:32:50  ncq
# - improve console messages a bit
#
# Revision 1.41  2003/02/21 08:58:51  ncq
# - improve PgArray detection even more
#
# Revision 1.40  2003/02/21 08:51:57  ncq
# - catch exception on missing PgArray
#
# Revision 1.39  2003/02/15 08:51:05  ncq
# - don't remove empty lines in lists
#
# Revision 1.38  2003/02/11 16:52:36  ncq
# - log one more failing corner case
#
# Revision 1.37  2003/02/09 09:48:28  ncq
# - revert breakage created by sjtan
#
# Revision 1.36  2003/02/09 02:02:30  sjtan
#
# allows first time run of gmGuiMain without a conf file. A Default conf file called gnumed.conf is created.
#
# Revision 1.35  2003/01/28 10:53:09  ncq
# - clarification to test code
#
# Revision 1.34  2003/01/12 11:53:58  ncq
# - fixed subtle bug resulting from ro/rw connections:
#  - set() would request a rw conn thus CURRENT_USER = "_user"
#  - get() would use a ro conn, thus CURRENT_USER == "user"
#  - there'd never be a match and the items would keep proliferating
#
# Revision 1.33  2003/01/05 09:56:58  ncq
# - ironed out some bugs in the array handling
# - streamlined code
# - have cfg.set() explicitely use rw conn to DB only when needed
#
# Revision 1.32  2003/01/04 12:19:04  ncq
# - better comment
#
# Revision 1.31  2003/01/04 12:17:05  ncq
# - backup old config file before overwriting
#
# Revision 1.30  2002/12/26 15:49:10  ncq
# - better comments
#
# Revision 1.29  2002/12/26 15:21:18  ncq
# - database config now works even with string lists
#
# Revision 1.28  2002/12/01 01:11:42  ncq
# - log config file line number on parse errors
#
# Revision 1.27  2002/11/28 11:40:12  ncq
# - added database config
# - reorganized self test
#
# Revision 1.26  2002/11/18 09:41:25  ncq
# - removed magic #! interpreter incantation line to make Debian happy
#
# Revision 1.25  2002/11/17 20:09:10  ncq
# - always display __doc__ when called standalone
#
# Revision 1.24  2002/11/05 18:15:03  ncq
# - new helper getOptions()
# - modified example code to show real use
#
# Revision 1.23  2002/11/04 15:38:28  ncq
# - moved empty config file creation to helper function
#
# Revision 1.22  2002/11/03 14:11:19  ncq
# - autocreate log file on failing to find one
#
# Revision 1.21  2002/11/03 13:21:05  ncq
# - phase 1: error levels more suitable
#
# Revision 1.20  2002/10/22 21:11:44  ncq
# - throwing exception ImportError on failing to load the
#   default config file wasn't such a good idea after all
#   since we might _actually_ only be interested in a different
#   file ...
#
# Revision 1.19  2002/10/22 15:30:16  ncq
# - added getGroups()
#
# Revision 1.18  2002/10/19 19:30:13  ncq
# - on being imported always raise ImportError on failing to use default config file
#
# Revision 1.17  2002/10/19 19:24:37  ncq
# - fixed some whitespace breakage
# - raise error on failing to parse default config file, if you really want
#   to override this you should handle that exception in your own code
#
# Revision 1.16  2002/10/18 19:57:09  hinnef
# fixed problems when a invalid filename is given, static class variables and
# changed the initialization of gmDefCfgFile so that it can be imported from
# standalone modules
#
# Revision 1.15  2002/09/30 10:58:27  ncq
# - consistently spell GnuMed
#
# Revision 1.14  2002/09/26 13:21:37  ncq
# - log version
#
# Revision 1.13  2002/09/12 23:11:14  ncq
# - fixed one nasty overwriting bug in store()
#
# Revision 1.12  2002/09/12 10:07:29  ncq
# - properly normalize : -> =
#
# Revision 1.11  2002/09/12 09:17:11  ncq
# - windows unsucked
#
# Revision 1.10  2002/09/10 18:43:02  ncq
# - windows sucks !
#
# Revision 1.9  2002/09/10 18:31:45  ncq
# - windows is strange: os.rename -> shutil.copyfile + os.remove
#
# Revision 1.8  2002/09/10 18:15:28  ncq
# - os.rename() over existing files fails on non-UNIX
#
# Revision 1.7  2002/09/10 17:51:33  ncq
# - more sensible log levels for some data
#
# Revision 1.6  2002/09/08 15:55:47  ncq
# - added log cvs keyword
#
