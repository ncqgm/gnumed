import gmDispatcher, gmSignals
from gmPatient import gmCurrentPatient
import sys
import gmLog
from wxPython.wx import wxCallAfter

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
