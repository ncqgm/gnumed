#############################################################################
# gmPatientHolder
#
# This is an abstract ancestor for widgets which care when a new patient is loaded
#
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: wxPython (>= version 2.3.1)
############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/Attic/gmPatientHolder.py,v $
# $Id: gmPatientHolder.py,v 1.17 2005-09-26 18:01:51 ncq Exp $
__version__ = "$Revision: 1.17 $"
__author__ = "R.Terry, SJ Tan"

from Gnumed.pycommon import gmDispatcher, gmSignals, gmLog, gmExceptions
from Gnumed.business import gmPerson
from Gnumed.wxpython import gmGuiHelpers
import sys

try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx

#====================================================
class PatientHolder:
	def __init__(self):
		# patient is about to change
		gmDispatcher.connect(self._on_activating_patient, gmSignals.activating_patient())
		# new patient has been selected
		gmDispatcher.connect(self._on_patient_selected, gmSignals.patient_selected())
		self.patient = gmPerson.gmCurrentPatient()
	#------------------------------------------------
	def _on_patient_selected( self, **kwds):
		try:
			wxCallAfter(self._updateUI_wrapper)
		except:
			gmLog.gmDefLog.LogException( "updateUI problem in [%s]" % self.__class__.__name__, sys.exc_info(), verbose=0)
	#------------------------------------------------
	def _on_activating_patient (self, **kwds):
		# this needs to work synchronously, otherwise
		# gmCurrentPatient will have changed by the
		# time we save the data
		self._save_data_wrapper()
	#------------------------------------------------
	def _updateUI_wrapper(self):
		try:
			self._updateUI()
		except:
			gmLog.gmDefLog.LogException( "updateUI problem in [%s]" % self.__class__.__name__, sys.exc_info(), verbose=0)
	#------------------------------------------------
	def _save_data_wrapper(self):
		try:
			self._save_data ()
		except gmExceptions.InvalidInputError, err:
			# nasty evil popup dialogue box
			# but for invalid input we want to interrupt user
			print "invalid input %s" % err
			try:
				gmGuiHelpers.gm_show_error (err, _("Invalid Input"))
			except:
				gmLog.gmDefLog.LogException ("", sys.exc_info (), verbose=0)
		except:
			gmLog.gmDefLog.LogException( "save data  problem in [%s]" % self.__class__.__name__, sys.exc_info(), verbose=0)
	#------------------------------------------------
	def _updateUI(self):
		gmLog.gmDefLog.Log(gmLog.lWarn, "please override me in %s" % self.__class__.__name__)
	#------------------------------------------------
	def _save_data (self):
		gmLog.gmDefLog.Log(gmLog.lWarn, "please override me in %s" % self.__class__.__name__)
	#------------------------------------------------
	# FIXME: what are these 2 for???
	def get_past_history(self):
		return self.patient.get_clinical_record().get_past_history()

#====================================================
# $Log: gmPatientHolder.py,v $
# Revision 1.17  2005-09-26 18:01:51  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.16  2005/01/31 10:37:26  ncq
# - gmPatient.py -> gmPerson.py
#
# Revision 1.15  2004/04/20 00:17:55  ncq
# - allergies API revamped, kudos to Carlos
#
# Revision 1.14  2004/04/11 10:09:38  ncq
# - cleanup
#
# Revision 1.13  2004/04/10 01:48:31  ihaywood
# can generate referral letters, output to xdvi at present
#
# Revision 1.12  2004/03/28 11:24:12  ncq
# - just some cleanup/comments
#
