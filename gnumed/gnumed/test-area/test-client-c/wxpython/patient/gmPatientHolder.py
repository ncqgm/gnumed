

import gmDispatcher, gmSignals
from gmPatient import gmCurrentPatient
import sys, traceback


class PatientHolder:
	def __init__(self):
		gmDispatcher.connect( self._setPatientModel, gmSignals.patient_selected() )

	def _setPatientModel( self, kwds):
		print kwds
		self.patient = gmCurrentPatient(kwds['ID'])
		try:
			self._updateUI()
		except:
			for i in xrange(0,1):
				print sys.exc_info()[i]
			traceback.print_tb( sys.exc_info()[2])
	
	def get_patient(self):
		return self.patient

	def get_clinical_record(self):
		return self.get_patient().get_clinical_record()

	def get_past_history(self):
		return self.get_clinical_record().get_past_history()

	def get_allergies(self):
		return self.get_clinical_record().get_allergies()
	
	def _updateUI(self):
		print "please override _updateUI() in ", self.__class__.__name__
