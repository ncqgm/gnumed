"""GNUmed configuration handling.

Two sources of configuration information are supported:

 - database tables

Theory of operation:

It is helpful to have a solid log target set up before importing this
module in your code. This way you will be able to see even those log
messages generated during module import.

Once your software has established database connectivity you can
set up a config source from the database. You can limit the option
applicability by the constraints "workplace", "user", and "cookie".

The basic API for handling items is get()/set().
The database config objects auto-syncs with the backend.

@copyright: GPL
"""
# TODO:
# - optional arg for set -> type
#==================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/gmCfg.py,v $
__version__ = "$Revision: 1.60 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"

# standard modules
import sys, types, cPickle, decimal, logging, re as regex


# gnumed modules
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmPG2, gmTools


_log = logging.getLogger('gm.cfg')
_log.info(__version__)

# don't change this without knowing what you do as
# it will already be in many databases
cfg_DEFAULT = "xxxDEFAULTxxx"
#==================================================================
# FIXME: make a cBorg around this
class cCfgSQL:
	def __init__(self):
		self.ro_conn = gmPG2.get_connection()
	#-----------------------------------------------
	# external API
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

		# this is the one to use (Sa 17 Feb 2007 12:16:56 CET)

		if None in [option, workplace]:
			raise ValueError, 'neither <option> (%s) nor <workplace> (%s) may be [None]' % (option, workplace)
		if bias not in ['user', 'workplace']:
			raise ValueError, '<bias> must be "user" or "workplace"'

		# does this option exist ?
		cmd = u"select type from cfg.cfg_template where name=%(opt)s"
		rows, idx = gmPG2.run_ro_queries(link_obj=self.ro_conn, queries = [{'cmd': cmd, 'args': {'opt': option}}])
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

		if cfg_table_type_suffix == u'data':
			sql_return_type = u''
		else:
			sql_return_type = gmTools.coalesce (
				initial = sql_return_type,
				instead = u'',
				template_initial = u'::%s'
			)

		# 1) search value with explicit workplace and current user
		where_parts = [
			u'vco.owner = CURRENT_USER',
			u'vco.workplace = %(wp)s',
			u'vco.option = %(opt)s'
		]
		where_parts.append(gmTools.coalesce (
			initial = cookie,
			instead = u'vco.cookie is null',
			template_initial = u'vco.cookie = %(cookie)s'
		))
		cmd = u"select vco.value%s from cfg.v_cfg_opts_%s vco where %s limit 1" % (
			sql_return_type,
			cfg_table_type_suffix,
			u' and '.join(where_parts)
		)
		rows, idx = gmPG2.run_ro_queries(link_obj=self.ro_conn, queries = [{'cmd': cmd, 'args': args}])
		if len(rows) > 0:
			if cfg_table_type_suffix == u'data':
				return cPickle.loads(str(rows[0][0]))
			return rows[0][0]

		_log.warning('no user AND workplace specific value for option [%s] in config database' % option)

		# 2) search value with biased query
		if bias == 'user':
			# did *I* set this option on *any* workplace ?
			where_parts = [
				u'vco.option = %(opt)s',
				u'vco.owner = CURRENT_USER',
			]
		else:
			# did *anyone* set this option on *this* workplace ?
			where_parts = [
				u'vco.option = %(opt)s',
				u'vco.workplace = %(wp)s'
			]
		where_parts.append(gmTools.coalesce (
			initial = cookie,
			instead = u'vco.cookie is null',
			template_initial = u'vco.cookie = %(cookie)s'
		))
		cmd = u"select vco.value%s from cfg.v_cfg_opts_%s vco where %s" % (
			sql_return_type,
			cfg_table_type_suffix,
			u' and '.join(where_parts)
		)
		rows, idx = gmPG2.run_ro_queries(link_obj=self.ro_conn, queries = [{'cmd': cmd, 'args': args}])
		if len(rows) > 0:
			# set explicitely for user/workplace
			self.set (
				workplace = workplace,
				cookie = cookie,
				option = option,
				value = rows[0][0]
			)
			if cfg_table_type_suffix == u'data':
				return cPickle.loads(str(rows[0][0]))
			return rows[0][0]

		_log.warning('no user OR workplace specific value for option [%s] in config database' % option)

		# 3) search value within default site policy
		where_parts = [
			u'vco.owner = %(def)s',
			u'vco.workplace = %(def)s',
			u'vco.option = %(opt)s'
		]
		cmd = u"select vco.value%s from cfg.v_cfg_opts_%s vco where %s" % (
			sql_return_type,
			cfg_table_type_suffix,
			u' and '.join(where_parts)
		)
		rows, idx = gmPG2.run_ro_queries(link_obj=self.ro_conn, queries = [{'cmd': cmd, 'args': args}])
		if len(rows) > 0:
			# set explicitely for user/workplace
			self.set (
				workplace = workplace,
				cookie = cookie,
				option = option,
				value = rows[0]['value']
			)
			if cfg_table_type_suffix == u'data':
				return cPickle.loads(str(rows[0]['value']))
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
		cmd = u"""
select vco.pk_cfg_item
from cfg.v_cfg_options vco
where %s
limit 1""" % where_clause

		rows, idx = gmPG2.run_ro_queries(link_obj=self.ro_conn, queries = [{'cmd': cmd, 'args': where_args}], return_data=True)
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
		sql_type_cast = u''
		if isinstance(value, basestring):
			sql_type_cast = u'::text'
		elif isinstance(value, types.BooleanType):
			opt_value = int(opt_value)
		elif isinstance(value, (types.FloatType, types.IntType, types.LongType, decimal.Decimal, types.BooleanType)):
			sql_type_cast = u'::numeric'
		elif isinstance(value, types.ListType):
			# there can be different syntaxes for list types so don't try to cast them
			pass
		elif isinstance(value, types.BufferType):
			# can go directly into bytea
			pass
		else:
			try:
				opt_value = gmPG2.dbapi.Binary(cPickle.dumps(value))
				sql_type_cast = '::bytea'
			except cPickle.PicklingError:
				_log.error("cannot pickle option of type [%s] (key: %s, value: %s)", type(value), alias, str(value))
				raise
			except:
				_log.error("don't know how to store option of type [%s] (key: %s, value: %s)", type(value), alias, str(value))
				raise

		cmd = u'select cfg.set_option(%%(opt)s, %%(val)s%s, %%(wp)s, %%(cookie)s, NULL)' % sql_type_cast
		args = {
			'opt': option,
			'val': opt_value,
			'wp': workplace,
			'cookie': cookie
		}
		try:
			rows, idx = gmPG2.run_rw_queries(link_obj=rw_conn, queries=[{'cmd': cmd, 'args': args}], return_data=True)
			result = rows[0][0]
		except:
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
			u'cfg_template.pk=cfg_item.fk_template',
			u'cfg_item.workplace=%(wplace)s'
		]
		where_args = {'wplace': workplace}

		# if no user given: current db user
		if user is None:
			where_snippets.append(u'cfg_item.owner=CURRENT_USER')
		else:
			where_snippets.append(u'cfg_item.owner=%(usr)s')
			where_args['usr'] = user

		where_clause = u' and '.join(where_snippets)

		cmd = u"""
select name, cookie, owner, type, description
from cfg.cfg_template, cfg.cfg_item
where %s""" % where_clause

		# retrieve option definition
		rows, idx = gmPG2.run_ro_queries(link_obj=self.ro_conn, queries = [{'cmd': cmd, 'args': where_args}], return_data=True)
		return rows
	#----------------------------
	def delete(self, workplace = None, cookie = None, option = None):
		"""
		Deletes an option or a whole group.
		Note you have to call store() in order to save
		the changes.
		"""
		if option is None:
			raise ValueError('<option> cannot be None')

		if cookie is None:
			cmd = u"""
delete from cfg.cfg_item where
	fk_template=(select pk from cfg.cfg_template where name = %(opt)s) and
	owner = CURRENT_USER and
	workplace = %(wp)s and
	cookie is Null
"""
		else:
			cmd = u"""
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

	root = logging.getLogger()
	root.setLevel(logging.DEBUG)

	#---------------------------------------------------------
	def test_db_cfg():
		print "testing database config"
		print "======================="

		myDBCfg = cCfgSQL()

		print "delete() works:", myDBCfg.delete(option='font name', workplace = 'test workplace')
		print "font is initially:", myDBCfg.get2(option = 'font name', workplace = 'test workplace', bias = 'user')
		print "set() works:", myDBCfg.set(option='font name', value="Times New Roman", workplace = 'test workplace')
		print "font after set():", myDBCfg.get2(option = 'font name', workplace = 'test workplace', bias = 'user')
		print "delete() works:", myDBCfg.delete(option='font name', workplace = 'test workplace')
		print "font after delete():", myDBCfg.get2(option = 'font name', workplace = 'test workplace', bias = 'user')
		print "font after get() with default:", myDBCfg.get2(option = 'font name', workplace = 'test workplace', bias = 'user', default = 'WingDings')
		print "font right after get() with another default:", myDBCfg.get2(option = 'font name', workplace = 'test workplace', bias = 'user', default = 'default: Courier')
		print "set() works:", myDBCfg.set(option='font name', value="Times New Roman", workplace = 'test workplace')
		print "font after set() on existing option:", myDBCfg.get2(option = 'font name', workplace = 'test workplace', bias = 'user')

		print "setting array option"
		print "array now:", myDBCfg.get2(option = 'test array', workplace = 'test workplace', bias = 'user')
		aList = ['val 1', 'val 2']
		print "set():", myDBCfg.set(option='test array', value = aList, workplace = 'test workplace')
		print "array now:", myDBCfg.get2(option = 'test array', workplace = 'test workplace', bias = 'user')
		aList = ['val 11', 'val 12']
		print "set():", myDBCfg.set(option='test array', value = aList, workplace = 'test workplace')
		print "array now:", myDBCfg.get2(option = 'test array', workplace = 'test workplace', bias = 'user')
		print "delete() works:", myDBCfg.delete(option='test array', workplace='test workplace')
		print "array now:", myDBCfg.get2(option = 'test array', workplace = 'test workplace', bias = 'user')

		print "setting complex option"
		data = {1: 'line 1', 2: 'line2', 3: {1: 'line3.1', 2: 'line3.2'}, 4: 1234}
		print "set():", myDBCfg.set(option = "complex option test", value = data, workplace = 'test workplace')
		print "complex option now:", myDBCfg.get2(workplace = 'test workplace', option = "complex option test", bias = 'user')
		print "delete() works:", myDBCfg.delete(option = "complex option test", workplace = 'test workplace')
		print "complex option now:", myDBCfg.get2(workplace = 'test workplace', option = "complex option test", bias = 'user')

	#---------------------------------------------------------
	if (len(sys.argv) > 1) and (sys.argv[1] == 'test'):
		try:
			test_db_cfg()
		except:
			_log.exception('test suite failed')
			raise

#=============================================================
# $Log: gmCfg.py,v $
# Revision 1.60  2008-08-20 13:53:45  ncq
# - robustify type handling in get2/set:
#   - explicitely support buffer()
#   - properly handle _data table
#   - unpickle retrieved bytea
#
# Revision 1.59  2008/04/13 13:57:32  ncq
# - lay to rest the venerable cCfgFile, it
#   has served us well
#
# Revision 1.58  2008/01/30 14:04:32  ncq
# - disable support from gmCfgFile()
#
# Revision 1.57  2007/12/26 18:34:02  ncq
# - no more old CLI lib
#
# Revision 1.56  2007/12/23 11:57:14  ncq
# - cleanup
#
# Revision 1.55  2007/12/11 15:35:28  ncq
# - use std lib logging
#
# Revision 1.54  2007/02/22 17:41:13  ncq
# - adjust to gmPerson changes
#
# Revision 1.53  2007/02/17 14:11:56  ncq
# - better get2 docs
# - allow custom cast on get2() return value
#
# Revision 1.52  2007/01/30 17:38:06  ncq
# - cleanup and a comment
#
# Revision 1.51  2006/12/22 15:20:12  ncq
# - do not fail hard if config file not found, after all, user
#   may want to set it later, but still do not hide exceptions
#
# Revision 1.50  2006/12/21 10:49:38  ncq
# - do not hide exceptiosn
#
# Revision 1.49  2006/12/13 14:55:56  ncq
# - remove get() from SQL source
#
# Revision 1.48  2006/12/05 13:54:02  ncq
# - better error messages
# - u''ify some query parts
# - simplify some code
#
# Revision 1.47  2006/11/14 16:27:36  ncq
# - improved test suite
#
# Revision 1.46  2006/11/07 00:27:45  ncq
# - psycopg2 knows how to adapt lists/tuples to ARRAY syntax, at
#   least when SQL_IN is loaded, so we can't use explicit casts with
#   <datatype>[] anymore in our SQL
#
# Revision 1.45  2006/11/05 16:00:17  ncq
# - unicode is text so don't pickle it
#
# Revision 1.44  2006/10/25 07:19:03  ncq
# - no more gmPG
#
# Revision 1.43  2006/10/08 11:02:02  ncq
# - support decimal type, too
# - make queries unicode
#
# Revision 1.42  2006/09/21 19:41:21  ncq
# - convert to use gmPG2
# - axe cCfgBase
# - massive cCfgSQL cleanup
#   - axe get()
#   - axe get_by_workplace()
#   - pump up get2(), set() and delete()
#   - getID() still pending review
#   - get2(bytea) still pending fixes
# - fix up database config test suite
#
# Revision 1.41  2006/09/12 17:20:36  ncq
# - mark up the deprecated sql get()ters
#
# Revision 1.40  2006/07/24 14:16:56  ncq
# - get_by_user() never worked so axe it
#
# Revision 1.39  2006/05/16 15:50:07  ncq
# - several small fixes in get2() regarding
#   less travelled codepathes
#
# Revision 1.38  2006/05/01 18:44:43  ncq
# - fix gmPG -> gmPG_ usage
#
# Revision 1.37  2006/02/27 15:39:06  ncq
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
