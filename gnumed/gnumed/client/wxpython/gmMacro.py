"""GnuMed macro primitives.

This module implements functions a macro can legally use.
"""
#=====================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmMacro.py,v $
__version__ = "$Revision: 1.2 $"
__author__ = "K.Hilbert <karsten.hilbert@gmx.net>"

import sys, time, random
if __name__ == "__main__":
	sys.path.append('.')
	sys.path.append ("../python-common/")
	sys.path.append ("../business/")

import gmLog
_log = gmLog.gmDefLog
if __name__ == "__main__":
	_log.SetAllLogLevels(gmLog.lData)

if __name__ == "__main__":
	import gmI18N

import gmPatient, gmExceptions

#=====================================================================
class cMacroPrimitives:
	"""Functions a macro can legally use.

	An instance of this class is passed to the GnuMed scripting
	listener. Hence, all actions a macro can legally take must
	be defined in this class. Thus we achieve some screening for
	security and also thread safety handling.
	"""
	#-----------------------------------------------------------------
	def __init__(self, a_cookie = None):
		if a_cookie is None:
			raise gmExceptions.ConstructorError, 'must specify cookie'
		self.__attach_cookie = a_cookie
		self.__attached = 0
	#-----------------------------------------------------------------
	# public API
	#-----------------------------------------------------------------
	def attach(self, a_cookie = None):
		if a_cookie != self.__attach_cookie:
			_log.Log(gmLog.lErr, 'rejecting attach() with cookie [%s], only servicing [%s]' % (a_cookie, self.__attach_cookie))
			return (0, _('attach with cookie [%s] rejected') % a_cookie)
		# FIXME: ask user what to do
		if self.__attached:
			_log.Log(gmLog.lErr, 'a [%s] client already attached' % a_cookie)
			return (0, _('attach with [%s] rejected, already serving a client') % a_cookie)
		self.__attached = 1
		return (1, '')
	#-----------------------------------------------------------------
	def detach(self):
		self.__attached = 0
		return 1
	#-----------------------------------------------------------------
	def version(self):
		if not self.__attached:
			return 0
		return "%s $Revision: 1.2 $" % self.__class__.__name__
	#-----------------------------------------------------------------
	def raise_gnumed(self):
		"""Raise ourselves to the top of the desktop."""
		if not self.__attached:
			return 0
		return "cMacroPrimitives.raise_gnumed() not implemented"
	#-----------------------------------------------------------------
	def raise_plugin(self, a_plugin = None):
		"""Raise a notebook plugin within GnuMed."""
		if not self.__attached:
			return 0
		return "cMacroPrimitives.raise_plugin() not implemented"
	#-----------------------------------------------------------------
	def lock_into_patient(self, a_search_term = None):
		if not self.__attached:
			return (0, _('request rejected, you are not attach()ed'))
		pat = gmPatient.gmCurrentPatient()
		if pat.is_locked():
			_log.Log(gmLog.lErr, 'patient [%s] is already locked' % a_search_term)
			return (0, _('patient [%s] already locked') % a_search_term)
		searcher = gmPatient.cPatientSearcher_SQL()
		pat_id = searcher.get_patient_ids(a_search_term)
		if pat_id is None:
			return (0, _('error searching for patient with [%s]') % a_search_term)
		if len(pat_id) == 0:
			return (0, _('no patient found for [%s]') % a_search_term)
		# FIXME: let user select patient
		if len(pat_id) > 1:
			return (0, _('several matching patients found for [%s]') % a_search_term)
		if not gmPatient.set_active_patient(pat_id[0][0]):
			return 0
			return (0, _('cannot activate patient [%s] (%s)') % (pat_id[0][0], a_search_term))
		pat.lock()
		self.__pat_lock_cookie = str(random.random())
		return (1, self.__pat_lock_cookie)
	#-----------------------------------------------------------------
	def unlock_patient(self, unlock_cookie = None):
		if not self.__attached:
			return (0, _('request rejected, you are not attach()ed'))
		pat = gmPatient.gmCurrentPatient()
		# we ain't locked anyways, so succeed
		if not pat.is_locked():
			return (1, '')
		# FIXME: ask user what to do about wrong cookie
		if unlock_cookie != self.__pat_lock_cookie:
			return (0, _('patient unlock request rejected, wrong cookie provided'))
		pat.unlock()
		return (1, '')
	#-----------------------------------------------------------------
	# internal helpers
	#-----------------------------------------------------------------
#=====================================================================
# main
#=====================================================================
if __name__ == '__main__':
	import gmScriptingListener
	import xmlrpclib
	listener = gmScriptingListener.cScriptingListener(macro_executor = cMacroPrimitives('unit test cookie'), port=9999)

	s = xmlrpclib.ServerProxy('http://localhost:9999')
	print s.attach()
	print s.attach('wrong cookie')
	print s.version()
	print s.raise_gnumed()
	print s.raise_plugin('test plugin')
	print s.lock_into_patient('kirk, james')
	print s.unlock_patient()
	print s.attach('unit test cookie')
	print s.version()
	print s.raise_gnumed()
	print s.raise_plugin('test plugin')
	data = s.lock_into_patient('kirk, james')
	print data
	print s.unlock_patient('wrong cookie')
	print s.unlock_patient(data[1])
	del s

	listener.tell_thread_to_stop()
#=====================================================================
# $Log: gmMacro.py,v $
# Revision 1.2  2004-02-05 20:40:34  ncq
# - added attach()
# - only allow attach()ed clients to call methods
# - introduce patient locking/unlocking cookie
# - enhance unit test
#
# Revision 1.1  2004/02/05 18:10:44  ncq
# - actually minimally functional macro executor with test code
#
