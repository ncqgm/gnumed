"""GNUmed medication handling workflows."""

#================================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "SPDX-License-Identifier: GPL-2.0-or-later"


import logging
import sys
import urllib


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
else:
	try:
		_
	except NameError:
		from Gnumed.pycommon import gmI18N
		gmI18N.activate_locale()
		gmI18N.install_domain()

from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmCfgDB
from Gnumed.pycommon import gmCfgINI
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmMimeLib

from Gnumed.business import gmPerson
from Gnumed.business import gmPraxis
from Gnumed.business import gmMedication
from Gnumed.business import gmForms
from Gnumed.business import gmStaff
from Gnumed.business import gmPathLab

from Gnumed.wxpython import gmCfgWidgets
from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmFormWidgets
from Gnumed.wxpython import gmListWidgets
from Gnumed.wxpython import gmSubstanceMgmtWidgets


_log = logging.getLogger('gm.ui')

_cfg = gmCfgINI.gmCfgData()

#============================================================
def configure_drug_ADR_url():

	def is_valid(value):
		value = value.strip()
		if value == '':
			return True, gmMedication.URL_drug_ADR_german_default

		try:
			urllib.request.urlopen(value)
			return True, value

		except Exception:
			return True, value

	gmCfgWidgets.configure_string_option (
		message = _(
			'GNUmed will use this URL to access a website which lets\n'
			'you report an adverse drug reaction (ADR).\n'
			'\n'
			'If you leave this empty it will fall back\n'
			'to an URL for reporting ADRs in Germany.'
		),
		option = 'external.urls.report_ADR',
		bias = 'user',
		default_value = gmMedication.URL_drug_ADR_german_default,
		validator = is_valid
	)

#============================================================
def configure_default_medications_lab_panel(parent=None):

	panels = gmPathLab.get_test_panels(order_by = 'description')
	gmCfgWidgets.configure_string_from_list_option (
		parent = parent,
		message = _(
			'\n'
			'Select the measurements panel to show in the medications plugin.'
			'\n'
		),
		option = 'horstspace.medications_plugin.lab_panel',
		bias = 'user',
		default_value = None,
		choices = [ '%s%s' % (p['description'], gmTools.coalesce(p['comment'], '', ' (%s)')) for p in panels ],
		columns = [_('Measurements panel')],
		data = [ p['pk_test_panel'] for p in panels ],
		caption = _('Configuring medications plugin measurements panel')
	)

#============================================================
def configure_medication_list_template(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	template = gmFormWidgets.manage_form_templates (
		parent = parent,
		template_types = ['current medication list']
	)
	option = 'form_templates.medication_list'

	if template is None:
		gmDispatcher.send(signal = 'statustext', msg = _('No medication list template configured.'), beep = True)
		return None

	if template['engine'] not in ['L', 'X', 'T']:
		gmDispatcher.send(signal = 'statustext', msg = _('No medication list template configured.'), beep = True)
		return None

	gmCfgDB.set (
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
		option = option,
		value = '%s - %s' % (template['name_long'], template['external_version'])
	)
	return template

#------------------------------------------------------------
def generate_failsafe_medication_list(pk_patient:int=None, max_width:int=80, eol:str=None) -> str|list:
	if not pk_patient:
		pk_patient = gmPerson.gmCurrentPatient().ID
	lines, footer = gmFormWidgets.generate_failsafe_form_wrapper (
		pk_patient = pk_patient,
		title = _('Medication List -- %s') % gmDateTime.pydt_now_here().strftime('%Y %b %d'),
		max_width = max_width
	)
	lines.extend(gmMedication.generate_failsafe_medication_list_entries (
		pk_patient = pk_patient,
		max_width = max_width,
		eol = None
	))
	lines.append('')
	emr = gmPerson.cPatient(pk_patient).emr
	if not emr.allergy_state:
		lines.append(_('Allergies: unknown'))
	else:
		for a in emr.get_allergies():
			lines.extend(a.format_for_failsafe_output(max_width = max_width))
	lines.append('')
	lines.extend(footer)
	if eol:
		return eol.join(lines)

	return lines

#------------------------------------------------------------
def save_failsafe_medication_list(pk_patient=None, max_width:int=80, filename:str=None) -> str:
	if not filename:
		filename = gmTools.get_unique_filename()
	with open(filename, 'w', encoding = 'utf8') as ml_file:
		ml_file.write(generate_failsafe_medication_list(pk_patient = pk_patient, max_width = max_width, eol = '\n'))
	return filename

#------------------------------------------------------------
def print_medication_list(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	# 1) get template
	option = 'form_templates.medication_list'
	template = gmCfgDB.get4user (
		option = option,
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
	)
	title = _('Printing medication list')
	if template is None:
		template = configure_medication_list_template(parent = parent)
		if template is None:
			gmGuiHelpers.gm_show_error (
				error = _('There is no medication list template configured.'),
				title = title
			)
			return False

	else:
		try:
			name, ver = template.split(' - ')
		except Exception:
			_log.exception('problem splitting medication list template name [%s]', template)
			gmDispatcher.send(signal = 'statustext', msg = _('Problem loading medication list template.'), beep = True)
			return False

		template = gmForms.get_form_template(name_long = name, external_version = ver)
		if template is None:
			gmGuiHelpers.gm_show_error (
				error = _('Cannot load medication list template [%s - %s]') % (name, ver),
				title = title
			)
			return False

	# 2) process template
	meds_list = gmFormWidgets.generate_form_from_template (
		parent = parent,
		template = template,
		edit = False
	)
	if not meds_list:
		gmGuiHelpers.gm_show_info (
			title = title,
			info = _('Pretty medication list form failed. Generating failsafe version.')
		)
		meds_list = save_failsafe_medication_list(max_width = 80)
		gmMimeLib.call_editor_on_file(filename = meds_list, block = True)
		return True

	# 3) print template
	return gmFormWidgets.act_on_generated_forms (
		parent = parent,
		forms = [meds_list],
		jobtype = 'medication_list',
		episode_name = gmMedication.DEFAULT_MEDICATION_HISTORY_EPISODE,
		progress_note = _('generated medication list document'),
		review_copy_as_normal = True
	)

#------------------------------------------------------------
def configure_prescription_template(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	template = gmFormWidgets.manage_form_templates (
		parent = parent,
		msg = _('Select the default prescription template:'),
		template_types = ['prescription', 'current medication list']
	)

	if template is None:
		gmDispatcher.send(signal = 'statustext', msg = _('No prescription template configured.'), beep = True)
		return None

	if template['engine'] not in ['L', 'X', 'T']:
		gmDispatcher.send(signal = 'statustext', msg = _('No prescription template configured.'), beep = True)
		return None

	option = 'form_templates.prescription'
	gmCfgDB.set (
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
		option = option,
		value = '%s - %s' % (template['name_long'], template['external_version'])
	)

	return template

#------------------------------------------------------------
def get_prescription_template(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	option = 'form_templates.prescription'
	template_name = gmCfgDB.get4user (
		option = option,
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace
	)

	if template_name is None:
		template = configure_prescription_template(parent = parent)
		if template is None:
			gmGuiHelpers.gm_show_error (
				error = _('There is no prescription template configured.'),
				title = _('Printing prescription')
			)
			return None
		return template

	try:
		name, ver = template_name.split(' - ')
	except Exception:
		_log.exception('problem splitting prescription template name [%s]', template_name)
		gmDispatcher.send(signal = 'statustext', msg = _('Problem loading prescription template.'), beep = True)
		return False
	template = gmForms.get_form_template(name_long = name, external_version = ver)
	if template is None:
		gmGuiHelpers.gm_show_error (
			error = _('Cannot load prescription template [%s - %s]') % (name, ver),
			title = _('Printing prescription')
		)
		return None
	return template

#------------------------------------------------------------
# prescription workflows
#------------------------------------------------------------
def generate_failsafe_prescription(pk_patient:int=None, max_width:int=80, eol:str=None) -> str|list:
	if not pk_patient:
		pk_patient = gmPerson.gmCurrentPatient().ID
	lines, footer = gmFormWidgets.generate_failsafe_form_wrapper (
		pk_patient = pk_patient,
		title = _('Prescription -- %s') % gmDateTime.pydt_now_here().strftime('%Y %b %d'),
		max_width = max_width
	)
	lines.extend(gmMedication.generate_failsafe_medication_list_entries (
		pk_patient = pk_patient,
		max_width = max_width,
		eol = None
	))
	lines.append('')
	lines.extend(footer)
	if eol:
		return eol.join(lines)

	return lines

#------------------------------------------------------------
def save_failsafe_prescription(pk_patient=None, max_width:int=80, filename:str=None) -> str:
	if not filename:
		filename = gmTools.get_unique_filename()
	with open(filename, 'w', encoding = 'utf8') as rx_file:
		rx_file.write(generate_failsafe_prescription(pk_patient = pk_patient, max_width = max_width, eol = '\n'))
	return filename

#------------------------------------------------------------
def print_prescription(parent=None, emr=None):
	# 1) get template
	rx_template = get_prescription_template(parent = parent)
	if rx_template is None:
		return False

	# 2) process template
	rx = gmFormWidgets.generate_form_from_template (
		parent = parent,
		template = rx_template,
		edit = False
	)
	if not rx:
		gmGuiHelpers.gm_show_info (
			title = _('Printing prescription'),
			info = _('Pretty prescription form failed. Generating failsafe version.')
		)
		rx = save_failsafe_prescription(pk_patient = emr.pk_patient, max_width = 80)
		gmMimeLib.call_editor_on_file(filename = rx, block = True)
		return True

	# 3) print template
	return gmFormWidgets.act_on_generated_forms (
		parent = parent,
		forms = [rx],
		jobtype = 'prescription',
		#episode_name = u'administrative',
		episode_name = gmMedication.DEFAULT_MEDICATION_HISTORY_EPISODE,
		progress_note = _('generated prescription'),
		review_copy_as_normal = True
	)

#------------------------------------------------------------
def prescribe_drugs(parent=None, emr=None):
	rx_mode = gmCfgDB.get4user (
		option = 'horst_space.default_prescription_mode',
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
		default = 'form'			# set to 'database' to access database
	)

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	if rx_mode == 'form':
		return print_prescription(parent = parent, emr = emr)

	if rx_mode == 'database':
		drug_db = gmSubstanceMgmtWidgets.get_drug_database()		#gmPerson.gmCurrentPatient() xxxxxxx ?
		if drug_db is None:
			return
		drug_db.reviewer = gmStaff.gmCurrentProvider()
		prescribed_drugs = drug_db.prescribe()
		update_substance_intake_list_from_prescription (
			parent = parent,
			prescribed_drugs = prescribed_drugs,
			emr = emr
		)

#------------------------------------------------------------
def update_substance_intake_list_from_prescription(parent=None, prescribed_drugs=None, emr=None):

	if len(prescribed_drugs) == 0:
		return

	curr_meds =  [ i['pk_drug_product'] for i in emr.get_current_medications() if i['pk_drug_product'] is not None ]
	new_drugs = []
	for drug in prescribed_drugs:
		if drug['pk_drug_product'] not in curr_meds:
			new_drugs.append(drug)

	if len(new_drugs) == 0:
		return

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	picker = gmListWidgets.cItemPickerDlg (
		parent,
		-1,
		msg = _(
			'These products have been prescribed but are not listed\n'
			'in the current medication list of this patient.\n'
			'\n'
			'Please select those you want added to the medication list.'
		)
	)
	picker.set_columns (
		columns = [_('Newly prescribed drugs')],
		columns_right = [_('Add to medication list')]
	)
	choices = [ ('%s %s (%s)' % (d['product'], d['l10n_preparation'], '; '.join(d['components']))) for d in new_drugs ]
	picker.set_choices (
		choices = choices,
		data = new_drugs
	)
	picker.ShowModal()
	drugs2add = picker.get_picks()
	picker.DestroyLater()

	if drugs2add is None:
		return

	if len(drugs2add) == 0:
		return

	for drug in drugs2add:
		# only add first component since all other components get added by a trigger ...
		intake = emr.add_substance_intake(pk_component = drug['components'][0]['pk_component'])
		if intake is None:
			continue
		intake.save()

	return

#============================================================
# main
#------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	del _
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain('gnumed')

	from Gnumed.wxpython import gmGuiTest

	#----------------------------------------
	main_frame = gmGuiTest.setup_widget_test_env(patient = 12)
	#print(generate_failsafe_medication_list(patient = gmPerson.gmCurrentPatient(), max_width = 80, eol = '\n'))
	gmStaff.set_current_provider_to_logged_on_user()
	meds_list = save_failsafe_medication_list(max_width = 80)
	gmMimeLib.call_editor_on_file(filename = meds_list, block = True)
