

import gmDispatcher, gmSignals


class PatientHolder:
	def __init__(self):
		gmDispatcher.connect( self._setPatientModel, gmSignals.patient_object_changed() )

	def _setPatientModel( self, patient):
		self.patient = patient
		self._updateUI()
	
	def _updateUI(self):
		print "please override _updateUI() in ", self.__class__.__name__
