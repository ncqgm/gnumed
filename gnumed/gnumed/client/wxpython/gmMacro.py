"""GnuMed macro primitives.

This module implements functions a macro can legally use.
"""
#=====================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmMacro.py,v $
__version__ = "$Revision: 1.1 $"
__author__ = "K.Hilbert <karsten.hilbert@gmx.net>"

import sys, time
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

import gmPatient

#=====================================================================
class cMacroPrimitives:
	"""Functions a macro can legally use.

	An instance of this class is passed to the GnuMed scripting
	listener. Hence, all actions a macro can legally take must
	be defined in this class. Thus we achieve some screening for
	security and also thread safety handling.
	"""
	def version(self):
		return "%s $Revision: 1.1 $" % self.__class__.__name__
	#-----------------------------------------------------------------
	def raise_gnumed(self):
		"""Raise ourselves to the top of the desktop."""
		return "cMacroPrimitives.raise_gnumed() not implemented"
	#-----------------------------------------------------------------
	def raise_plugin(self, a_plugin = None):
		"""Raise a notebook plugin within GnuMed."""
		return "cMacroPrimitives.raise_plugin() not implemented"
	#-----------------------------------------------------------------
	def lock_into_patient(self, a_search_term = None):
		pat = gmPatient.gmCurrentPatient()
		if pat.is_locked():
			_log.Log(gmLog.lErr, 'patient [%s] is locked' % a_search_term)
			return (0, _('patient [%s] is locked') % a_search_term)
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
		return 1
	#-----------------------------------------------------------------
	def unlock_patient(self):
		pat = gmPatient.gmCurrentPatient()
		pat.unlock()
		return 1
#=====================================================================
# main
#=====================================================================
if __name__ == '__main__':
	import gmScriptingListener
	import xmlrpclib
	listener = gmScriptingListener.cScriptingListener(macro_executor = cMacroPrimitives(), port=9999)

	s = xmlrpclib.Server('http://localhost:9999')
	print s.version()
	print s.raise_gnumed()
	print s.raise_plugin('test plugin')
	print s.lock_into_patient('kirk, james')
	print s.unlock_patient()
	del s

	listener.tell_thread_to_stop()
#=====================================================================
# $Log: gmMacro.py,v $
# Revision 1.1  2004-02-05 18:10:44  ncq
# - actually minimally functional macro executor with test code
#
