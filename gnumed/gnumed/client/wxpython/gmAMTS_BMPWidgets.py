# -*- coding: utf-8 -*-

"""GNUmed AMTS BMP handling widgets."""

#================================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"

import logging
import sys
import typing


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x

from Gnumed.pycommon import gmTools

from Gnumed.business import gmAMTS_BMP
from Gnumed.business import gmPerson

from Gnumed.wxpython import gmGuiHelpers


_log = logging.getLogger('gm.amts_bmp')

#================================================================
def import_amts_bmp_for_patient(parent=None, patient=None):
	# check for xml files in /gnumed and /.local/gnumed
	# check xml files for bmp
	# check bmps for potentially belonging to patient
	bmp_filename = 'current_pat_bmp.xml'
	import_amts_bmp(parent = parent, bmp_filename = bmp_filename)

#----------------------------------------------------------------


#----------------------------------------------------------------
def import_amts_bmp(parent=None, bmp_filename:str=None) -> typing.Union[bool, None]:
	if bmp_filename is None:
		dlg = wx.FileDialog (
			parent = parent,
			message = _('Choose an AMTS BMP medication plan.'),
			defaultDir = gmTools.gmPaths().user_work_dir,
			defaultFile = '',
			wildcard = "%s (*.xml)|*.xml|%s (*)|*" % (_('BMP files'), _('all files')),
			style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
		)
		result = dlg.ShowModal()
		if result == wx.ID_CANCEL:
			return None
		bmp_filename = dlg.GetPath()
		dlg.DestroyLater()

	dlg_title = _('Importing AMTS BMP Medikationsplan')
	bmp = gmAMTS_BMP.cAmtsBmpFile(bmp_filename)
	if not bmp.valid():
		gmGuiHelpers.gm_show_error (
			title = dlg_title,
			error = _(
				'The file\n'
				'\n'
				' [%s]\n'
				'\n'
				'does not seem to be a Medikationsplan.'
			) % bmp_filename
		)
		return False

	dto = bmp.patient_as_dto
	person = dto.unambiguous_identity
	if person is None:
		candidates = dto.candidate_identities
		if len(candidates) == 0:
			# no match found -> ask for creation or ask whether to import for the current patient
			curr_pat = gmPerson.gmCurrentPatient()
			if curr_pat.is_connected:
				gmGuiHelpers.c3ButtonQuestionDlg (
					parent = parent,
					caption = dlg_title,
					question = _(
						'No matching patient found in GNUmed.\n'
						'\n'
						'The patient in the Medikationsplan is:\n'
						'\n'
						' %s\n'
						'\n'
						'Do you want to create that patient ?'
				) % dto.format(),
					button_defs = [
					]
				)
			else:
				gmGuiHelpers.gm_show_question (
					title = dlg_title,
					question = _(
						'No matching patient found in GNUmed.\n'
						'\n'
						'The patient in the Medikationsplan is:\n'
						'\n'
						' %s\n'
						'\n'
						'Do you want to create that patient ?'
					) % dto.format()
				)

		elif len(candidates) == 1:
			# one match found -> ask whether to import
			pass
		else:
			# several found -> ask which to use
			pass

#		msg = _('None or several matching patients found.')
#		gmGuiHelpers.gm_show_info (
#			title = _('Importing AMTS BMP Medikationsplan'),
#			info = msg + '\n\n' + bmp.format(eol = '\n')
#		)
	else:
		gmGuiHelpers.gm_show_info (
			title = _('Importing AMTS BMP Medikationsplan'),
			info = bmp.format(eol = '\n')
		)
	return True
	# - import patient
	# - import provider as praxis
	# - import bmp as document
	#		type AMTS BMP
	#		comment UID
	# - link provider as document source

	# - import allergies (confirm)
	# - import other notes (schwanger, stillend) - confirm

	# - import drugs from bmp


#================================================================
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()
