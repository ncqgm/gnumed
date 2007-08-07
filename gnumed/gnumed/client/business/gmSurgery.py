"""GNUmed Surgery related middleware."""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmSurgery.py,v $
# $Id: gmSurgery.py,v 1.3 2007-08-07 21:34:19 ncq Exp $
__license__ = "GPL"
__version__ = "$Revision: 1.3 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"


import sys, os


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmPG2, gmTools, gmBorg, gmCLI, gmCfg

#============================================================
class gmCurrentPractice(gmBorg.cBorg):

	def __init__(self):
		gmBorg.cBorg.__init__(self)

		try:
			self.already_inited
			return
		except AttributeError:
			pass

		self.__helpdesk = None

		self.already_inited = True
	#--------------------------------------------------------
	def _set_helpdesk(self, helpdesk):
		return

	def _get_helpdesk(self):

		if self.__helpdesk is not None:
			return self.__helpdesk

		candidates = []
		if gmCLI.has_arg('--conf-file'):
			candidates.append(gmCLI.arg['--conf-file'])
		paths = gmTools.gmPaths()
		candidates.extend ([
			os.path.join(paths.working_dir, 'gnumed.conf'),
			os.path.join(paths.local_base_dir, 'gnumed.conf'),
			os.path.join(paths.user_config_dir, 'gnumed.conf'),
			os.path.join(paths.system_config_dir, 'gnumed-client.conf')
		])

		self.__helpdesk = None
		for candidate in candidates:
			try:
				cfg = gmCfg.cCfgFile(aFile = candidate)
			except IOError:
				continue
			tmp = cfg.get('workplace', 'help desk')
			if tmp is not None:
				self.__helpdesk = tmp
				break

		if self.__helpdesk is None:
			self.__helpdesk = 'http://wiki.gnumed.de'

		return self.__helpdesk

	helpdesk = property(_get_helpdesk, _set_helpdesk)
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
	#--------------------------------------------------------

#============================================================
if __name__ == '__main__':

	prac = gmCurrentPractice()
	print "help desk:", prac.helpdesk

#============================================================
# $Log: gmSurgery.py,v $
# Revision 1.3  2007-08-07 21:34:19  ncq
# - cPaths -> gmPaths
#
# Revision 1.2  2007/05/11 14:11:20  ncq
# - add gmCurrentPractice borg
#
# Revision 1.1  2007/04/07 23:00:01  ncq
# - Medical Practice (Surgery) related stuff
#
#