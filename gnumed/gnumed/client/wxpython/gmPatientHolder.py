import gmDispatcher, gmSignals
from gmPatient import gmCurrentPatient
import sys
import gmLog

class PatientHolder:
	def __init__(self):
		gmDispatcher.connect(self._setPatientModel, gmSignals.patient_selected())
		self.patient = gmCurrentPatient()

	def _setPatientModel( self, **kwds):
		try:
			self._updateUI()
		except:
			gmLog.gmDefLog.LogException( "updateUI problem", sys.exc_info(), verbose=1)

	def get_demographic_record(self):
		return self.get_patient().get_demographic_record()

	def get_clinical_record(self):
		return self.get_patient().get_clinical_record()

	def get_past_history(self):
		return self.get_clinical_record().get_past_history()

	def get_allergies(self):
		return self.get_clinical_record().get_allergies_manager()
	
	def _updateUI(self):
		gmLog.gmDefLog.Log(gmLog.lWarn, "please override me in %s", self.__class__.__name__)
