#############################################################################
# gmPatientHolder
# ----------------------------------
#
# This is an abstract ancestor for widgets which care when a new patient is loaded
#
# If you don't like it - change this code 
#
# @copyright: authorcd
# @license: GPL (details at http://www.gnu.org)
# @dependencies: wxPython (>= version 2.3.1)
############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/Attic/gmPatientHolder.py,v $
# $Id: gmPatientHolder.py,v 1.11 2004-03-28 04:09:31 ihaywood Exp $
__version__ = "$Revision: 1.11 $"
__author__ = "R.Terry, SJ Tan"

from Gnumed.pycommon import gmDispatcher, gmSignals, gmLog, gmExceptions
from Gnumed.business.gmPatient import gmCurrentPatient
from Gnumed.wxpython import gmGuiHelpers
import sys
from wxPython.wx import *

class PatientHolder:
	def __init__(self):
		gmDispatcher.connect(self._setPatientModel, gmSignals.patient_selected())
		gmDispatcher.connect(self._saveOurData, gmSignals.activating_patient ())
		self.patient = gmCurrentPatient()

	def _setPatientModel( self, **kwds):
		try:
			wxCallAfter(self._updateUI_wrapper)
		except:
			gmLog.gmDefLog.LogException( "updateUI problem in [%s]" % self.__class__.__name__, sys.exc_info(), verbose=0)
			
	def _saveOurData (self, **kwds):
		#FIXME: this event need to happen synchronously
		# (otherwise gmCurrentPatient will have changed by the time
		# we save the data)
		#wxCallAfter (self._save_data_wrapper)
		self._save_data_wrapper ()
		
	def _updateUI_wrapper (self):
		try:
			self._updateUI ()
		except:
			gmLog.gmDefLog.LogException( "updateUI problem in [%s]" % self.__class__.__name__, sys.exc_info(), verbose=0)

	def _save_data_wrapper (self):
		"""
		Becuase we are calling from wxCallAfter, we need to capture exceptions here
		"""
		try:
			self._save_data ()
		except gmExceptions.InvalidInputError, err:
			# nasty evil popup dialogue box
			# but for invalid input we want to interrupt user
			gmGuiHelpers.gm_show_error (err, _("Invalid Input"))
		except:
			gmLog.gmDefLog.LogException( "save data  problem in [%s]" % self.__class__.__name__, sys.exc_info(), verbose=0)

	# FIXME: what are these 2 for???
	def get_past_history(self):
		return self.patient.get_clinical_record().get_past_history()

	def get_allergies(self):
		return self.patient.get_clinical_record().get_allergies_manager()
	
	def _updateUI(self):
		gmLog.gmDefLog.Log(gmLog.lWarn, "please override me in %s" % self.__class__.__name__)

	def _save_data (self):
		gmLog.gmDefLog.Log(gmLog.lWarn, "please override me in %s" % self.__class__.__name__)
