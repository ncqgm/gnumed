

import gmDispatcher, gmSignals
from gmPatient import gmCurrentPatient


class PatientHolder:
	def __init__(self):
		gmDispatcher.connect( self._setPatientModel, gmSignals.patient_selected() )

	def _setPatientModel( self, kwds):
		print kwds
		self.patient = gmCurrentPatient(kwds['ID'])
		self._updateUI()
	
	def _updateUI(self):
		print "please override _updateUI() in ", self.__class__.__name__
