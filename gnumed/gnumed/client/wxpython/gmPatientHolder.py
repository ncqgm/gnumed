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
			wxCallAfter(self._updateUI)
		except:
			gmLog.gmDefLog.LogException( "updateUI problem in [%s]" % self.__class__.__name__, sys.exc_info(), verbose=0)

	def get_past_history(self):
		return self.patient.get_clinical_record().get_past_history()

	def get_allergies(self):
		return self.patient.get_clinical_record().get_allergies_manager()
	
	def _updateUI(self):
		gmLog.gmDefLog.Log(gmLog.lWarn, "please override me in %s" % self.__class__.__name__)
