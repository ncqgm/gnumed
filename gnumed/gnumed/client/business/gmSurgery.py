"""GNUmed Surgery related middleware."""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmSurgery.py,v $
# $Id: gmSurgery.py,v 1.9 2008-07-16 10:32:50 ncq Exp $
__license__ = "GPL"
__version__ = "$Revision: 1.9 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"


import sys, os


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmPG2, gmTools, gmBorg, gmCfg2

_cfg = gmCfg2.gmCfgData()
#============================================================
class gmCurrentPractice(gmBorg.cBorg):

	def __init__(self):
		try:
			self.already_inited
			return
		except AttributeError:
			pass

		self.__helpdesk = None
		self.__active_workplace = None

		self.already_inited = True
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _set_helpdesk(self, helpdesk):
		return

	def _get_helpdesk(self):

		if self.__helpdesk is not None:
			return self.__helpdesk

		self.__helpdesk = gmTools.coalesce (
			_cfg.get (
				group = u'workplace',
				option = u'help desk',
				source_order = [
					('explicit', 'return'),
					('workbase', 'return'),
					('local', 'return'),
					('user', 'return'),
					('system', 'return')
				]
			),
			u'http://wiki.gnumed.de'
		)

		return self.__helpdesk

	helpdesk = property(_get_helpdesk, _set_helpdesk)
	#--------------------------------------------------------
	def _get_db_logon_banner(self):
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': u'select _(message) from cfg.db_logon_banner'}])
		if len(rows) == 0:
			return u''
		return gmTools.coalesce(rows[0][0], u'').strip()

	def _set_db_logon_banner(self, banner):
		queries = [
			{'cmd': u'delete from cfg.db_logon_banner'}
		]
		if banner.strip() != u'':
			queries.append ({
				'cmd': u'insert into cfg.db_logon_banner (message) values (%(msg)s)',
				'args': {'msg': banner.strip()}
			})
		rows, idx = gmPG2.run_rw_queries(queries = queries, end_tx = True)

	db_logon_banner = property(_get_db_logon_banner, _set_db_logon_banner)
	#--------------------------------------------------------
	def _set_workplace(self, workplace):
		# maybe later allow switching workplaces on the fly
		return True

	def _get_workplace(self):
		"""Return the current workplace (client profile) definition.

		The first occurrence counts.
		"""
		if self.__active_workplace is not None:
			return self.__active_workplace

		self.__active_workplace = gmTools.coalesce (
			_cfg.get (
				group = u'workplace',
				option = u'name',
				source_order = [
					('explicit', 'return'),
					('workbase', 'return'),
					('local', 'return'),
					('user', 'return'),
					('system', 'return'),
				]
			),
			u'GNUmed Default'
		)

		return self.__active_workplace

	active_workplace = property(_get_workplace, _set_workplace)
	#--------------------------------------------------------
	def _set_workplaces(self, val):
		pass

	def _get_workplaces(self):
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': u'select distinct workplace from cfg.cfg_item'}])
		return [ r[0] for r in rows ]

	workplaces = property(_get_workplaces, _set_workplaces)
	#--------------------------------------------------------
	def _get_user_email(self):
		# FIXME: get this from the current users staff record in the database
		return _cfg.get (
			group = u'preferences',
			option = u'user email',
			source_order = [
				('explicit', 'return'),
				('user', 'return'),
				('local', 'return'),
				('workbase', 'return'),
				('system', 'return')
			]
		)

	def _set_user_email(self, val):
		prefs_file = _cfg.get(option = 'user_preferences_file')
		gmCfg2.set_option_in_INI_file (
			filename = prefs_file,
			group = u'preferences',
			option = u'user email',
			value = val
		)
		_cfg.reload_file_source(file = prefs_file)

	user_email = property(_get_user_email, _set_user_email)
#============================================================
class cSurgery(object):

	#--------------------------------------------------------
	# reports API
	#--------------------------------------------------------
	def report_exists(self, name=None):
		rows, idx = gmPG2.run_ro_query(queries = [{
			'cmd': 'select exists(select 1 from cfg.report_query where label=%(name)s)',
			'args': {'name': name}
		}])
		return rows[0][0]
	#--------------------------------------------------------
	def save_report_definition(self, name=None, query=None, overwrite=False):
		if not overwrite:
			if self.report_exists(name=name):
				return False

		queries = [
			{'cmd': u'delete from cfg.report_query where label=%(name)s', 'args': {'name': name}},
			{'cmd': u'insert into cfg.report_query (label, cmd) values (%(name)s, %(query)s)',
			 'args': {'name': name, 'query': query}}
		]
		rows, idx = gmPG2.run_rw_queries(queries=queries)
		return True

#============================================================
if __name__ == '__main__':

	def run_tests():
		prac = gmCurrentPractice()
#		print "help desk:", prac.helpdesk
#		print "active workplace:", prac.active_workplace

		old_banner = prac.db_logon_banner
		test_banner = u'a test banner'
		prac.db_logon_banner = test_banner
		if prac.db_logon_banner != test_banner:
			print 'Cannot set logon banner to', test_banner
			return False
		prac.db_logon_banner = u''
		if prac.db_logon_banner != u'':
			print 'Cannot set logon banner to ""'
			return False
		prac.db_logon_banner = old_banner

		return True

	if len(sys.argv) > 1 and sys.argv[1] == 'test':
		if not run_tests():
			print "regression tests failed"
		print "regression tests succeeded"

#============================================================
# $Log: gmSurgery.py,v $
# Revision 1.9  2008-07-16 10:32:50  ncq
# - add .user_email property
#
# Revision 1.8  2007/12/23 11:55:49  ncq
# - cleanup, use gmCfg2
#
# Revision 1.7  2007/10/23 21:20:24  ncq
# - cleanup
#
# Revision 1.6  2007/10/21 20:16:29  ncq
# - fix setting db logon banner
# - add test suite
#
# Revision 1.5  2007/10/07 12:28:09  ncq
# - workplace property now on gmSurgery.gmCurrentPractice() borg
#
# Revision 1.4  2007/09/20 21:29:38  ncq
# - add db_logon_banner handling
#
# Revision 1.3  2007/08/07 21:34:19  ncq
# - cPaths -> gmPaths
#
# Revision 1.2  2007/05/11 14:11:20  ncq
# - add gmCurrentPractice borg
#
# Revision 1.1  2007/04/07 23:00:01  ncq
# - Medical Practice (Surgery) related stuff
#
#