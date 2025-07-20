"""GNUmed generic clinical item business object workflows."""
#================================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later (details at https://www.gnu.org)"

import sys
import logging


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x

from Gnumed.pycommon import gmDispatcher

from Gnumed.business.gmHealthIssue import cHealthIssue
from Gnumed.business.gmEpisode import cEpisode
from Gnumed.business.gmEncounter import cEncounter
from Gnumed.business.gmHospitalStay import cHospitalStay
from Gnumed.business.gmPerformedProcedure import cPerformedProcedure
from Gnumed.business.gmPathLab import cTestResult
from Gnumed.business.gmMedication import cSubstanceIntakeEntry
from Gnumed.business.gmMedication import cIntakeWithRegimen
from Gnumed.business.gmFamilyHistory import cFamilyHistory
from Gnumed.business.gmVaccination import cVaccination
from Gnumed.business.gmExternalCare import cExternalCareItem
from Gnumed.business.gmClinNarrative import cNarrative
from Gnumed.business.gmAllergy import cAllergy
from Gnumed.business.gmAllergy import cAllergyState
from Gnumed.business.gmDocuments import cDocument
from Gnumed.business.gmDocuments import cDocumentPart

from Gnumed.wxpython.gmEMRStructWidgets import edit_health_issue
from Gnumed.wxpython.gmEMRStructWidgets import edit_episode
from Gnumed.wxpython.gmEncounterWidgets import edit_encounter
from Gnumed.wxpython.gmHospitalStayWidgets import edit_hospital_stay
from Gnumed.wxpython.gmMeasurementWidgets import edit_measurement
from Gnumed.wxpython.gmSubstanceIntakeWidgets import edit_intake_with_regimen
from Gnumed.wxpython.gmFamilyHistoryWidgets import edit_family_history
from Gnumed.wxpython.gmVaccWidgets import edit_vaccination
from Gnumed.wxpython.gmProcedureWidgets import edit_procedure
from Gnumed.wxpython.gmExternalCareWidgets import edit_external_care_item
from Gnumed.wxpython.gmNarrativeWorkflows import edit_narrative
from Gnumed.wxpython.gmAllergyWidgets import edit_allergies
from Gnumed.wxpython.gmDocumentWidgets import edit_document_or_part


_log = logging.getLogger('gm.ui')

#c: {'edit_in_dlg': edit_}
__map_class2edit_call = {
	cEpisode: {'edit_in_dlg': edit_episode},
	cHealthIssue: {'edit_in_dlg': edit_health_issue},
	cHospitalStay: {'edit_in_dlg': edit_hospital_stay},
	cTestResult: {'edit_in_dlg': edit_measurement},
	cEncounter: {'edit_in_dlg': edit_encounter},
	cSubstanceIntakeEntry: {'edit_in_dlg': edit_intake_with_regimen},
	cIntakeWithRegimen: {'edit_in_dlg': edit_intake_with_regimen},
	cFamilyHistory: {'edit_in_dlg': edit_family_history},
	cVaccination: {'edit_in_dlg': edit_vaccination},
	cPerformedProcedure: {'edit_in_dlg': edit_procedure},
	cExternalCareItem: {'edit_in_dlg': edit_external_care_item},
	cNarrative: {'edit_in_dlg': edit_narrative},
	cAllergy: {'edit_in_dlg': edit_allergies},
	cAllergyState: {'edit_in_dlg': edit_allergies},
	cDocument: {'edit_in_dlg': edit_document_or_part},
	cDocumentPart: {'edit_in_dlg': edit_document_or_part}
}

#================================================================
def edit_item_in_dlg(parent=None, item=None):
	try:
		edit_func = __map_class2edit_call[type(item)]['edit_in_dlg']
	except KeyError:
		gmDispatcher.send('statustext', msg = _('No editor for [%s]') % type(item))
		return None

	return edit_func(parent, item, single_entry = True)

#================================================================
if __name__ == '__main__':
	pass
