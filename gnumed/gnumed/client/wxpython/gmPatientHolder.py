

import gmDispatcher, gmSignals
from gmPatient import gmCurrentPatient
import sys, traceback
import gmLog

def _print(*kargs):
	l = []
	for x in kargs:
		l.append(str(x))
	msg = "  ".join(l)

	gmLog.gmDefLog.Log( gmLog.lInfo, msg )	

class PatientHolder:
	def __init__(self):
		gmDispatcher.connect( self._setPatientModel, gmSignals.patient_selected() )

	def _setPatientModel( self, kwds = None):
		print kwds
		self.patient = gmCurrentPatient()
		try:
			self._updateUI()
		except:
			gmLog.gmDefLog.LogException( "updateUI problem", sys.exc_info(), verbose=1)
	
	def get_patient(self):
		return self.patient

	def get_demographic_record(self):
		return self.get_patient().get_demographic_record()

	def get_clinical_record(self):
		return self.get_patient().get_clinical_record()

	def get_past_history(self):
		return self.get_clinical_record().get_past_history()

	def get_allergies(self):
		return self.get_clinical_record().get_allergies_manager()
	
	def _updateUI(self):
		_print("please override _updateUI() in ", self.__class__.__name__)
