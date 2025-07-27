"""GNUmed immunisation/vaccination widgets.

Modelled after Richard Terry's design document.

copyright: authors
"""
#======================================================================
__author__ = "R.Terry, S.J.Tan, K.Hilbert"
__license__ = "GPL v2 or later (details at https://www.gnu.org)"

import sys
import logging
import urllib
#from typing import overload


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmMatchProvider
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmCfgDB
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmNetworkTools
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmMimeLib

from Gnumed.business import gmPerson
from Gnumed.business import gmStaff
from Gnumed.business import gmVaccination
from Gnumed.business import gmVaccDefs
from Gnumed.business import gmPraxis
from Gnumed.business import gmProviderInbox

from Gnumed.wxpython import gmPhraseWheel
from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmEditArea
from Gnumed.wxpython import gmListWidgets
from Gnumed.wxpython import gmFormWidgets
from Gnumed.wxpython import gmAuthWidgets
from Gnumed.wxpython import gmCfgWidgets
from Gnumed.wxpython import gmSubstanceMgmtWidgets


_log = logging.getLogger('gm.vacc')

#======================================================================
# vaccine related widgets
#----------------------------------------------------------------------
def regenerate_generic_vaccines():

	dbo_conn = gmAuthWidgets.get_dbowner_connection(procedure = _('Regenerating generic vaccines'))
	if dbo_conn is None:
		return False

	wx.BeginBusyCursor()
	sql_script_fname = gmTools.get_unique_filename(suffix = '.sql')
	with open(sql_script_fname, mode = 'w', encoding = 'utf8') as sql_script:
		sql_script.write(gmVaccDefs.v23_generate_generic_vaccines_SQL())
	_log.debug('regenerating generic vaccines, SQL script: %s', sql_script_fname)
	if not gmPG2.run_sql_script(sql_script_fname, conn = dbo_conn):
		wx.EndBusyCursor()
		w = _('Error regenerating generic vaccines.\n\nSee [%s]') % sql_script_fname
		t = _('Regenerating generic vaccines')
		gmGuiHelpers.warn(warning = w, title = t)
		return False

	gmDispatcher.send(signal = 'statustext', msg = _('Successfully regenerated generic vaccines.'), beep = False)
	wx.EndBusyCursor()
	return True

#----------------------------------------------------------------------
def edit_vaccine(parent=None, vaccine=None, single_entry=True):
	ea = cVaccineEAPnl(parent, -1)
	ea.data = vaccine
	ea.mode = gmTools.coalesce(vaccine, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2(parent, -1, edit_area = ea, single_entry = single_entry)
	dlg.SetTitle(gmTools.coalesce(vaccine, _('Adding new vaccine'), _('Editing vaccine')))
	result = dlg.ShowModal()
	dlg.DestroyLater()
	return result

#----------------------------------------------------------------------
def manage_vaccines(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#------------------------------------------------------------
	def delete(vaccine=None):
		if not vaccine:
			return False

		title = _('Removing vaccine')
		if vaccine.is_in_use:
			info = _(
				'Cannot remove vaccine\n'
				'\n'
				' %s [#%s]\n'
				'\n'
				'It is in use documenting a vaccination.'
			) % (
				gmTools.coalesce(vaccine['vaccine'], _('generic vaccine')),
				vaccine['pk_vaccine']
			)
			gmGuiHelpers.inform(info, title)
			return False

		delete_product = False
		if vaccine['pk_drug_product']:
			q = _(
				'Also delete the drug product\n'
				'\n'
				' "%s"\n'
				'\n'
				'associated with this vaccine ?'
			) % vaccine['vaccine']
			delete_product = gmGuiHelpers.ask(question = q, title = title)
		deleted = gmVaccination.delete_vaccine (
			pk_vaccine = vaccine['pk_vaccine'],
			also_delete_product = delete_product
		)
		if not deleted:
			error = _(
				'Cannot remove vaccine and/or drug product\n'
				'\n'
				' %s [#%s]'
			) % (
				gmTools.coalesce(vaccine['vaccine'], _('generic vaccine')),
				vaccine['pk_vaccine']
			)
			gmGuiHelpers.gm_show_error(error = error, title = title)
			return False

		return True

	#------------------------------------------------------------
	def manage_drug_products(vaccine):
		gmSubstanceMgmtWidgets.manage_drug_products(parent = parent)
		return True

	#------------------------------------------------------------
	def edit(vaccine=None):
		return edit_vaccine(parent = parent, vaccine = vaccine, single_entry = True)

	#------------------------------------------------------------
	def get_tooltip(vaccine):
		if vaccine is None:
			return None

		return '\n'.join(vaccine.format())

	#------------------------------------------------------------
	def refresh(lctrl):
		vaccines = gmVaccination.get_vaccines(order_by = 'vaccine')
		items = [ [
			gmTools.coalesce (
				v['vaccine'],
				_('generic: %s') % '/'.join([ ind['l10n_indication'] for ind in v['indications'] ])
			),
			'%s - %s' % (
				gmDateTime.format_interval(interval = v['min_age'], accuracy_wanted = gmDateTime.ACC_MONTHS, none_string = ''),
				gmDateTime.format_interval(interval = v['max_age'], accuracy_wanted = gmDateTime.ACC_MONTHS, none_string = '')
			),
			gmTools.coalesce(v['comment'], ''),
			'%s%s' % (
				v['pk_vaccine'],
				gmTools.coalesce(v['pk_drug_product'], '', '::%s')
			)
		] for v in vaccines ]
		lctrl.set_string_items(items)
		lctrl.set_data(vaccines)

	#------------------------------------------------------------
	gmListWidgets.get_choices_from_list (
		parent = parent,
		caption = _('Showing vaccine details'),
		columns = [ _('Vaccine'), _('Age range'), _('Comment'), '#' ],
		single_selection = True,
		refresh_callback = refresh,
		edit_callback = edit,
		new_callback = edit,
		delete_callback = delete,
		list_tooltip_callback = get_tooltip,
		left_extra_button = (_('Products'), _('Manage drug products'), manage_drug_products)
	)

#----------------------------------------------------------------------
class cBatchNoPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)

		context = {
			'ctxt_vaccine': {
				'where_part': 'AND pk_vaccine = %(pk_vaccine)s',
				'placeholder': 'pk_vaccine'
			}
		}

		query = """
SELECT data, field_label, list_label FROM (

	SELECT distinct on (field_label)
		data,
		field_label,
		list_label,
		rank
	FROM ((
			-- batch_no by vaccine
			SELECT
				batch_no AS data,
				batch_no AS field_label,
				batch_no || ' (' || coalesce(vaccine, 'generic') || ')' AS list_label,
				1 as rank
			FROM
				clin.v_vaccinations
			WHERE
				batch_no %(fragment_condition)s
				%(ctxt_vaccine)s
		) UNION ALL (
			-- batch_no for any vaccine
			SELECT
				batch_no AS data,
				batch_no AS field_label,
				batch_no || ' (' || coalesce(vaccine, 'generic') || ')' AS list_label,
				2 AS rank
			FROM
				clin.v_vaccinations
			WHERE
				batch_no %(fragment_condition)s
		)

	) AS matching_batch_nos

) as unique_matches

ORDER BY rank, list_label
LIMIT 25
"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries = query, context = context)
		mp.setThresholds(1, 2, 3)
		self.matcher = mp

		self.unset_context(context = 'pk_vaccine')
		self.SetToolTip(_('Enter or select the batch/lot number of the vaccine used.'))
		self.selection_only = False

#----------------------------------------------------------------------
class cVaccinePhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		query = """-- vaccine PRW query
SELECT data, list_label, field_label
FROM (
	SELECT DISTINCT ON (data)
		data,
		list_label,
		field_label
	FROM (
			(	-- search fragment in vaccine names
				SELECT
					r_v_v.pk_vaccine
						AS data,
					r_v_v.vaccine || ' ('
					||	(SELECT string_agg(l10n_inds.ind_desc::text, ', ') FROM (
							SELECT unnest(r_v_v.indications)->>'l10n_indication' AS ind_desc
						) AS l10n_inds)
					|| ')'
						AS list_label,
					r_v_v.vaccine
						AS field_label
				FROM
					ref.v_vaccines r_v_v
				WHERE
					r_v_v.vaccine %(fragment_condition)s
			) UNION ALL (
				-- search fragment in localized indications and map to vaccine
				SELECT
					 r_vi4v.pk_vaccine
						AS data,
					coalesce(r_vi4v.vaccine, 'generic') || ' ('
					||	(SELECT string_agg(l10n_inds.ind_desc::text, ', ') FROM (
							SELECT unnest(r_vi4v.all_indications)->>'l10n_indication' AS ind_desc
						) AS l10n_inds)
					|| ')'
						AS list_label,
					coalesce(r_vi4v.vaccine, 'generic') || ' ('
					||	(SELECT string_agg(l10n_inds.ind_desc::text, ', ') FROM (
							SELECT unnest(r_vi4v.all_indications)->>'l10n_indication' AS ind_desc
						) AS l10n_inds)
					|| ')'
						AS field_label
				FROM
					ref.v_indications4vaccine r_vi4v
				WHERE
					 r_vi4v.l10n_indication %(fragment_condition)s
			) UNION ALL (
				-- search fragment in non-localized indications and map to vaccines
				SELECT
					r_vi4v.pk_vaccine
						AS data,
					coalesce(r_vi4v.vaccine, 'generic') || ' ('
					||	(SELECT string_agg(l10n_inds.ind_desc::text, ', ') FROM (
							SELECT unnest(r_vi4v.all_indications)->>'l10n_indication' AS ind_desc
						) AS l10n_inds)
					|| ')'
						AS list_label,
					coalesce(r_vi4v.vaccine, 'generic') || ' ('
					||	(SELECT string_agg(l10n_inds.ind_desc::text, ', ') FROM (
							SELECT unnest(r_vi4v.all_indications)->>'l10n_indication' AS ind_desc
						) AS l10n_inds)
					|| ')'
						AS field_label
				FROM
					ref.v_indications4vaccine r_vi4v
				WHERE
					r_vi4v.indication %(fragment_condition)s
		)
	) AS DISTINCTed_total
) AS total
ORDER by list_label
LIMIT 25"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries = query)
		mp.setThresholds(1, 2, 3)
		self.matcher = mp
		self.selection_only = True
	#------------------------------------------------------------------
	def _data2instance(self, link_obj=None):
		return gmVaccination.cVaccine(aPK_obj = self.GetData())

#----------------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgVaccineEAPnl

class cVaccineEAPnl(wxgVaccineEAPnl.wxgVaccineEAPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwargs) -> None:
		try:
			data = kwargs['vaccine']
			del kwargs['vaccine']
		except KeyError:
			data = None

		wxgVaccineEAPnl.wxgVaccineEAPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		self.mode = 'new'
		self.__indications:list[int] = []		# will contain ref.vacc_indication.pk values, if picked
		self.data = data
		if data:
			self.mode = 'edit'

		self._LBL_name.ToolTip = self._PRW_drug_product.ToolTip
		self._PRW_drug_product.ToolTip = None

	#----------------------------------------------------------------
	def __refresh_indications(self):
		self._TCTRL_indications.SetValue('')
		if self.data:
			lines = [ i['l10n_indication'] for i in self.data['indications'] ]
			self._TCTRL_indications.SetValue('- ' + '\n- '.join(lines))
			return

		if not self.__indications:
			return

		known_indications = gmVaccination.get_vaccination_indications()
		lines = [ i['target'] for i in known_indications if i['pk'] in self.__indications ]
		self._TCTRL_indications.SetValue('- ' + '\n- '.join(lines))

	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):

		self.StatusText = ''
		has_errors = False

		atc = self._PRW_atc.Value.strip()
		if (atc == '') or (atc.startswith('J07')):
			self._PRW_atc.display_as_valid(True)
		else:
			if self._PRW_atc.GetData() is None:
				self._PRW_atc.display_as_valid(True)
			else:
				has_errors = True
				self._PRW_atc.display_as_valid(False)
				self._PRW_atc.SetFocus()

		val = self._PRW_age_min.Value.strip()
		if val == '':
			self._PRW_age_min.display_as_valid(True)
		else:
			if gmDateTime.str2interval(val) is None:
				has_errors = True
				self._PRW_age_min.display_as_valid(False)
				self._PRW_age_min.SetFocus()
			else:
				self._PRW_age_min.display_as_valid(True)

		val = self._PRW_age_max.Value.strip()
		if val == '':
			self._PRW_age_max.display_as_valid(True)
		else:
			if gmDateTime.str2interval(val) is None:
				has_errors = True
				self._PRW_age_max.display_as_valid(False)
				self._PRW_age_max.SetFocus()
			else:
				self._PRW_age_max.display_as_valid(True)

		if self.mode == 'new':
			if not self.__indications:
				has_errors = True
				self.StatusText = _('ERROR: No indications for new vaccine.')

		return (has_errors is False)

	#----------------------------------------------------------------
	def _save_as_new(self):
		vaccine = gmVaccination.create_vaccine (
			pk_drug_product = self._PRW_drug_product.GetData(),
			product_name = self._PRW_drug_product.Value.strip(),
			is_live = self._CHBOX_live.GetValue()
		)
		val = self._PRW_age_min.Value.strip()
		if val:
			vaccine['min_age'] = gmDateTime.str2interval(val)
		val = self._PRW_age_max.Value.strip()
		if val:
			vaccine['max_age'] = gmDateTime.str2interval(val)
		val = self._TCTRL_comment.Value.strip()
		if val:
			vaccine['comment'] = val
		atc = self._PRW_atc.GetData()
		if atc and atc != 'J07':
			vaccine['atc_vaccine'] = atc
			drug = vaccine.product
			if drug:
				if drug['atc'] and not drug['atc'].startswith('J07'):
					self.StatusText = _('Product not a vaccine (ATC does not start with J07) !')
				if not drug['atc']:
					drug['atc'] = atc
					drug.save()
		vaccine.save()
		vaccine.set_indications(pk_indications = self.__indications)
		# must be done very late or else the property access
		# will refresh the display such that later field
		# access will return empty values
		self.data = vaccine
		return True

	#----------------------------------------------------------------
	def _save_as_update(self):
		val = self._PRW_atc.GetData()
		if val and val.strip != 'J07':
			val = val.strip()
			self.data['atc_vaccine'] = val
			drug = self.data.product
			if drug:
				if drug['atc'] and not drug['atc'].startswith('J07'):
					self.StatusText = _('Product not a vaccine (ATC does not start with J07) !')
				if not drug['atc']:
					drug['atc'] = val
					drug.save()
		self.data['is_live'] = self._CHBOX_live.GetValue()
		val = self._PRW_age_min.GetValue().strip()
		if val == '':
			self.data['min_age'] = None
		else:
			self.data['min_age'] = gmDateTime.str2interval(val)
		val = self._PRW_age_max.GetValue().strip()
		if val == '':
			self.data['max_age'] = None
		else:
			self.data['max_age'] = gmDateTime.str2interval(val)
		val = self._TCTRL_comment.GetValue().strip()
		if val != '':
			self.data['comment'] = val
		self.data.save()
		# no need to update indications because in 'edit' mode
		# indications are updated after having been picked
		return True

	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._PRW_drug_product.Enable()
		self._PRW_drug_product.SetText(value = '', data = None, suppress_smarts = True)
		self._CHBOX_live.SetValue(False)
		self._PRW_atc.SetText(value = '', data = None, suppress_smarts = True)
		self._PRW_age_min.SetText(value = '', data = None, suppress_smarts = True)
		self._PRW_age_max.SetText(value = '', data = None, suppress_smarts = True)
		self._TCTRL_comment.SetValue('')
		self.__indications = []
		self.__refresh_indications()
		self._PRW_drug_product.SetFocus()

	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		self._PRW_drug_product.Disable()
		if self.data['pk_drug_product']:
			self._PRW_drug_product.SetText(value = self.data['vaccine'], data = self.data['pk_drug_product'])
		else:
			self._PRW_drug_product.SetText(value = _('generic/unknown'), data = None, suppress_smarts = True)
		self._CHBOX_live.SetValue(self.data['is_live'])
		self._PRW_atc.SetText(value = self.data['atc_vaccine'], data = self.data['atc_vaccine'])
		if self.data['min_age'] is None:
			self._PRW_age_min.SetText(value = '', data = None, suppress_smarts = True)
		else:
			self._PRW_age_min.SetText (
				value = gmDateTime.format_interval(self.data['min_age'], gmDateTime.ACC_YEARS),
				data = self.data['min_age']
			)
		if self.data['max_age'] is None:
			self._PRW_age_max.SetText(value = '', data = None, suppress_smarts = True)
		else:
			self._PRW_age_max.SetText (
				value = gmDateTime.format_interval(self.data['max_age'], gmDateTime.ACC_YEARS),
				data = self.data['max_age']
			)
		self._TCTRL_comment.SetValue(gmTools.coalesce(self.data['comment'], ''))
		self.__indications = []
		self.__refresh_indications()
		self._PRW_drug_product.SetFocus()

	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._refresh_as_new()

	#----------------------------------------------------------------
	# event handlers
	#----------------------------------------------------------------
	def _on_button_pick_targets_pressed(self, event):
		event.Skip()

		if self.data:
			vaccine = gmTools.coalesce(self.data['vaccine'], _('generic vaccine'), '"%s"')
		else:
			vaccine = _('new vaccine')
		picker = gmListWidgets.cItemPickerDlg(self, -1, msg = _('Pick target indications.'))
		picker.ignore_dupes_on_picking = True
		picker.set_columns (
			columns = [_('Known indications')],
			columns_right = [_('Targets of %s') % vaccine]
		)
		known_indications = gmVaccination.get_vaccination_indications(order_by = 'target')
		data = [ i['pk'] for i in known_indications ]
		choices = [ '%s%s' % (
			i['target'],
			gmTools.coalesce(i['atc'], '', ' [ATC:%s]')
		) for i in known_indications ]
		picker.set_choices(choices = choices, data = data)
		if self.mode == 'edit':
			picks = [ '%s%s' % (
				i['l10n_indication'],
				gmTools.coalesce(i['atc_indication'], '', ' [ATC:%s]')
			) for i in  self.data['indications'] ]
			data = [ i['pk_indication'] for i in self.data['indications'] ]
			picker.set_picks(picks, data)
		else:
			self.__indications = []
		result = picker.ShowModal()
		if result == wx.ID_CANCEL:
			picker.DestroyLater()
			return

		picked = picker.get_picks()
		picker.DestroyLater()
		if self.mode == 'new':
			self.__indications = picked
			self.__refresh_indications()
			return

		if not picked:
			return

		vacc_inds = [ i['pk_indication'] for i in self.data['indications'] ]
		if set(picked) == set(vacc_inds):
			return

		if self.data.is_in_use:
			q = _(
				'Are you positively sure you want to *change*\n'
				'the target indications for this vaccine ?\n'
				'\n'
				'Doing so will modify the documented vaccination\n'
				'status of ALL patients having received this vaccine.\n'
			)
			do_update = gmGuiHelpers.ask(question = q, title = _('Modifying vaccine.'))
			if not do_update:
				return

		if self.data.set_indications(pk_indications = picked):
			self.StatusText = _('Vaccine indications updated.')
			self.__refresh_indications()
			return

		self.StatusText = _('ERROR: Cannot update vaccine in database.')

#======================================================================
# vaccination related widgets
#----------------------------------------------------------------------
def configure_vaccine_ADR_url():

	def is_valid(value):
		value = value.strip()
		if value == '':
			return True, gmVaccination.URL_vaccine_ADR_german_default
		try:
			urllib.request.urlopen(value)
			return True, value
		except Exception:			# FIXME: more specific
			return True, value

	gmCfgWidgets.configure_string_option (
		message = _(
			'GNUmed will use this URL to access a website which lets\n'
			'you report an adverse vaccination reaction (vADR).\n'
			'\n'
			'If you set it to a specific address that URL must be\n'
			'accessible now. If you leave it empty it will fall back\n'
			'to the URL for reporting other adverse drug reactions.'
		),
		option = 'external.urls.report_vaccine_ADR',
		bias = 'user',
		default_value = gmVaccination.URL_vaccine_ADR_german_default,
		validator = is_valid
	)

#----------------------------------------------------------------------
def configure_vaccination_plans_url():

	def is_valid(value):
		value = value.strip()
		if value == '':
			return True, gmVaccination.URL_vaccination_plan
		try:
			urllib.request.urlopen(value)
			return True, value
		except Exception:			# FIXME: more specific
			return True, value

	gmCfgWidgets.configure_string_option (
		message = _(
			'GNUmed will use this URL to access a page showing\n'
			'vaccination schedules.\n'
			'\n'
			'You can leave this empty but to set it to a specific\n'
			'address the URL must be accessible now.'
		),
		option = 'external.urls.vaccination_plans',
		bias = 'user',
		default_value = gmVaccination.URL_vaccination_plan,
		validator = is_valid
	)

#------------------------------------------------------------
def generate_failsafe_vaccination_history(pk_patient:int=None, max_width:int=80, eol:None|str=None) -> str|list[str]:
	if not pk_patient:
		pk_patient = gmPerson.gmCurrentPatient().ID
	lines, footer = gmFormWidgets.generate_failsafe_form_wrapper (
		pk_patient = pk_patient,
		title = _('Vaccination history -- %s') % gmDateTime.pydt_now_here().strftime('%Y %b %d'),
		max_width = max_width
	)
	lines.append('')
	lines.append('#' + '-' * (max_width - 2) + '#')
	lines.extend(gmVaccination.format_vaccinations_by_indication_for_failsafe_output (
		pk_patient = pk_patient,
		max_width = max_width
	))
	lines.append('')
	lines.extend(footer)
	if eol:
		return eol.join(lines)

	return lines

#------------------------------------------------------------
def save_failsafe_vaccination_history(pk_patient:int=None, max_width:int=80, filename:str=None) -> str:
	if not filename:
		filename = gmTools.get_unique_filename()
	with open(filename, 'w', encoding = 'utf8') as vacc_file:
		vacc_file.write(generate_failsafe_vaccination_history(pk_patient = pk_patient, max_width = max_width, eol = '\n'))
	return filename

#----------------------------------------------------------------------
def print_vaccinations(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	vaccs_printout = gmFormWidgets.generate_form_from_template (
		parent = parent,
		template_types = [
			'Medical statement',
			'vaccination report',
			'vaccination record',
			'reminder'
		],
		edit = False
	)
	if vaccs_printout is None:
		gmGuiHelpers.gm_show_info (
			title = _('Printing vaccination history'),
			info = _('Pretty vaccination history form failed. Generating failsafe version.')
		)
		vaccs_printout = save_failsafe_vaccination_history(max_width = 80)
		gmMimeLib.call_editor_on_file(filename = vaccs_printout, block = True)
		return True

	return gmFormWidgets.act_on_generated_forms (
		parent = parent,
		forms = [vaccs_printout],
		jobtype = 'vaccinations',
		episode_name = 'administrative',
		review_copy_as_normal = True
	)

#----------------------------------------------------------------------
def edit_vaccination(parent=None, vaccination=None, single_entry=True):
	ea = cVaccinationEAPnl(parent, -1)
	ea.data = vaccination
	ea.mode = gmTools.coalesce(vaccination, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2(parent, -1, edit_area = ea, single_entry = single_entry)
	dlg.SetTitle(gmTools.coalesce(vaccination, _('Adding new vaccinations'), _('Editing vaccination')))
	if dlg.ShowModal() == wx.ID_OK:
		dlg.DestroyLater()
		return True
	dlg.DestroyLater()
	if not single_entry:
		return True
	return False

#----------------------------------------------------------------------
def manage_vaccinations(parent=None, latest_only:bool=False, expand_indications=False):

	pat = gmPerson.gmCurrentPatient()
	emr = pat.emr

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#------------------------------------------------------------
	def browse2schedules(vaccination=None):
		url = gmCfgDB.get4user (
			option = 'external.urls.vaccination_plans',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
			default = gmVaccination.URL_vaccination_plan
		)
		gmNetworkTools.open_url_in_browser(url = url)
		return False

	#------------------------------------------------------------
	def print_vaccs(vaccination=None):
		print_vaccinations(parent = parent)
		return False

	#------------------------------------------------------------
	def add_recall(vaccination=None):
		if vaccination is None:
			subject = _('vaccination recall')
		else:
			if vaccination['vaccine']:
				subject = _('vaccination recall (%s)') % vaccination['vaccine']
			else:
				subject = _('vaccination recall')
		recall = gmProviderInbox.create_inbox_message (
			message_type = _('Vaccination'),
			subject = subject,
			patient = pat.ID,
			staff = None
		)
		if vaccination:
			recall['data'] = _('Existing vaccination:\n\n%s') % '\n'.join(vaccination.format(
				with_indications = True,
				with_comment = True,
				with_reaction = False,
				date_format = '%Y %b %d'
			))
			recall.save()
		from Gnumed.wxpython import gmProviderInboxWidgets
		gmProviderInboxWidgets.edit_inbox_message (
			parent = parent,
			message = recall,
			single_entry = False
		)
		return False

	#------------------------------------------------------------
	def get_tooltip(vaccination):
		if vaccination is None:
			return None
		return '\n'.join(vaccination.format (
			with_indications = True,
			with_comment = True,
			with_reaction = True,
			date_format = '%Y %b %d'
		))

	#------------------------------------------------------------
	def edit(vaccination=None):
		return edit_vaccination(parent = parent, vaccination = vaccination, single_entry = (vaccination is not None))

	#------------------------------------------------------------
	def delete(vaccination=None):
		gmVaccination.delete_vaccination(vaccination = vaccination['pk_vaccination'])
		return True

	#------------------------------------------------------------
	def refresh(lctrl):

		items = []
		data = []
		if latest_only:
			latest_vaccs = emr.latest_vaccinations
			for indication in sorted(latest_vaccs):
				no_of_shots4ind, latest_vacc4ind = latest_vaccs[indication]
				items.append ([
					indication,
					_('%s (latest of %s: %s ago)') % (
						latest_vacc4ind['date_given'].strftime('%Y %b'),
						no_of_shots4ind,
						gmDateTime.format_interval_medically(gmDateTime.pydt_now_here() - latest_vacc4ind['date_given'])
					),
					gmTools.coalesce(latest_vacc4ind['vaccine'], _('generic')),
					latest_vacc4ind['batch_no'],
					gmTools.coalesce(latest_vacc4ind['site'], ''),
					gmTools.coalesce(latest_vacc4ind['reaction'], ''),
					gmTools.coalesce(latest_vacc4ind['comment'], '')
				])
				data.append(latest_vacc4ind)
		else:
			shots = emr.get_vaccinations(order_by = 'date_given DESC, pk_vaccination')
			if expand_indications:
				shots_by_ind = {}
				for shot in shots:
					for ind in shot['indications']:
						try:
							shots_by_ind[ind['l10n_indication']].append(shot)
						except KeyError:
							shots_by_ind[ind['l10n_indication']] = [shot]
				for ind in sorted(shots_by_ind):
					idx = len(shots_by_ind[ind])
					for shot in shots_by_ind[ind]:
						items.append ([
							'%s (#%s)' % (ind, idx),
							_('%s (%s ago)') % (
								shot['date_given'].strftime('%Y %b %d'),
								gmDateTime.format_interval_medically(gmDateTime.pydt_now_here() - shot['date_given'])
							),
							gmTools.coalesce(shot['vaccine'], _('generic')),
							shot['batch_no'],
							gmTools.coalesce(shot['site'], ''),
							gmTools.coalesce(shot['reaction'], ''),
							gmTools.coalesce(shot['comment'], '')
						])
						idx -= 1
						data.append(shot)
			else:
				items = [ [
					s['date_given'].strftime('%Y %b %d'),
					gmTools.coalesce(s['vaccine'], _('generic')),
					', '.join([ i['l10n_indication'] for i in s['indications'] ]),
					s['batch_no'],
					gmTools.coalesce(s['site'], ''),
					gmTools.coalesce(s['reaction'], ''),
					gmTools.coalesce(s['comment'], '')
				] for s in shots ]
				data = shots

		lctrl.set_string_items(items)
		lctrl.set_data(data)

	#------------------------------------------------------------
	if latest_only:
		msg = _('Most recent vaccination for each indication.\n')
		cols = [ _('Indication'), _('Date'), _('Vaccine'), _('Batch'), _('Site'), _('Reaction'), _('Comment') ]
	else:
		if expand_indications:
			msg = _('Complete vaccination history (per indication).\n')
			cols = [ _('Indication'), _('Date'), _('Vaccine'), _('Batch'), _('Site'), _('Reaction'), _('Comment') ]
		else:
			msg = _('Complete vaccination history (by shot).\n')
			cols = [ _('Date'), _('Vaccine'), _('Intended to protect from'), _('Batch'), _('Site'), _('Reaction'), _('Comment') ]

	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = msg,
		caption = _('Showing vaccinations.'),
		columns = cols,
		single_selection = True,
		refresh_callback = refresh,
		new_callback = edit,
		edit_callback = edit,
		delete_callback = delete,
		list_tooltip_callback = get_tooltip,
		left_extra_button = (_('Print'), _('Print vaccinations or recalls.'), print_vaccs),
		middle_extra_button = (_('Recall'), _('Add a recall for a vaccination'), add_recall),
		right_extra_button = (_('Vx schedules'), _('Open a browser showing vaccination schedules.'), browse2schedules)
	)

#----------------------------------------------------------------------
from Gnumed.wxGladeWidgets.wxgVaccinationEAPnl import wxgVaccinationEAPnl

class cVaccinationEAPnl(wxgVaccinationEAPnl, gmEditArea.cGenericEditAreaMixin):
	"""
	- warn on apparent duplicates
	- ask if "missing" (= previous, non-recorded) vaccinations
	  should be estimated and saved (add note "auto-generated")

	Batch No (http://www.fao.org/docrep/003/v9952E12.htm)
	"""
	def __init__(self, *args, **kwargs):

		try:
			data = kwargs['vaccination']
			del kwargs['vaccination']
		except KeyError:
			data = None

		wxgVaccinationEAPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		self.mode = 'new'
		self.data = data
		if data is not None:
			self.mode = 'edit'

		self.__init_ui()

	#----------------------------------------------------------------
	def __init_ui(self):
		# adjust phrasewheels etc
		self._PRW_vaccine.add_callback_on_lose_focus(self._on_PRW_vaccine_lost_focus)
		self._PRW_provider.selection_only = False
		url = gmCfgDB.get4user (
			option = 'external.urls.report_vaccine_ADR',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace
		)
		if url:
			url = url.strip()
		if not url:
			url = gmCfgDB.get4user (
				option = 'external.urls.report_ADR',
				workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace
			)
			if url:
				url = url.strip()
		if url:
			self._HL_report_ADR.SetURL(url)
		else:
			self._HL_report_ADR.Disable()

	#----------------------------------------------------------------
	def _on_PRW_vaccine_lost_focus(self):

		vaccine = self._PRW_vaccine.GetData(as_instance=True)

		if self.mode == 'edit':
			if vaccine is None:
				self._PRW_batch.unset_context(context = 'pk_vaccine')
			else:
				self._PRW_batch.set_context(context = 'pk_vaccine', val = vaccine['pk_vaccine'])
		# we are entering a new vaccination
		else:
			if vaccine is None:
				self._PRW_batch.unset_context(context = 'pk_vaccine')
			else:
				self._PRW_batch.set_context(context = 'pk_vaccine', val = vaccine['pk_vaccine'])

		self.__refresh_indications()

	#----------------------------------------------------------------
	def __refresh_indications(self):
		self._TCTRL_indications.SetValue('')
		vaccine = self._PRW_vaccine.GetData(as_instance = True)
		if vaccine is None:
			return

		lines = []
		emr = gmPerson.gmCurrentPatient().emr
		atcs = [ i['atc_indication'] for i in vaccine['indications'] ]
		latest_vaccs = emr.get_latest_vaccinations(atc_indications = atcs)
		for l10n_ind in [ i['l10n_indication'] for i in vaccine['indications'] ]:
			try:
				no_of_shots4ind, latest_vacc4ind = latest_vaccs[l10n_ind]
				ago = gmDateTime.format_interval_medically(gmDateTime.pydt_now_here() - latest_vacc4ind['date_given'])
				lines.append(_('%s  (most recent shot of %s: %s ago)') % (l10n_ind, no_of_shots4ind, ago))
			except KeyError:
				lines.append(_('%s  (no previous vaccination recorded)') % l10n_ind)
		self._TCTRL_indications.SetValue('\n '.join(lines))

	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):

		has_errors = False

		if not self._PRW_date_given.is_valid_timestamp(empty_is_valid = False):
			has_errors = True

		vaccine = self._PRW_vaccine.GetData(as_instance = True)
		if vaccine is None:
			has_errors = True
			self._PRW_vaccine.display_as_valid(False)
		else:
			self._PRW_vaccine.display_as_valid(True)

		if self._PRW_batch.GetValue().strip() == '':
			has_errors = True
			self._PRW_batch.display_as_valid(False)
		else:
			self._PRW_batch.display_as_valid(True)

		if self._PRW_episode.GetValue().strip() == '':
			self._PRW_episode.SetText(value = _('prevention'))

		return (has_errors is False)

	#----------------------------------------------------------------
	def _save_as_new(self):

		pk_vaccine = self._PRW_vaccine.GetData()
		data = self.__save_new_from_vaccine(pk_vaccine = pk_vaccine)
		# must be done very late or else the property access
		# will refresh the display such that later field
		# access will return empty values
		self.data = data
		return True

	#----------------------------------------------------------------
	def __save_new_from_vaccine(self, pk_vaccine=None):
		emr = gmPerson.gmCurrentPatient().emr
		data = emr.add_vaccination (
			episode = self._PRW_episode.GetData(can_create = True, is_open = False),
			pk_vaccine = pk_vaccine,
			batch_no = self._PRW_batch.GetValue().strip()
		)
		if self._CHBOX_anamnestic.GetValue() is True:
			data['soap_cat'] = 's'
		else:
			data['soap_cat'] = 'p'
		data['date_given'] = self._PRW_date_given.GetData()
		data['site'] = self._PRW_site.GetValue().strip()
		data['pk_provider'] = self._PRW_provider.GetData()
		data['reaction'] = self._PRW_reaction.GetValue().strip()
		data['comment'] = self._TCTRL_comment.GetValue().strip()
		data.save()
		return data

	#----------------------------------------------------------------
	def _save_as_update(self):
		if self._CHBOX_anamnestic.GetValue() is True:
			self.data['soap_cat'] = 's'
		else:
			self.data['soap_cat'] = 'p'
		self.data['date_given'] = self._PRW_date_given.GetData()
		self.data['pk_vaccine'] = self._PRW_vaccine.GetData()
		self.data['batch_no'] = self._PRW_batch.GetValue().strip()
		self.data['pk_episode'] = self._PRW_episode.GetData(can_create = True, is_open = False)
		self.data['site'] = self._PRW_site.GetValue().strip()
		self.data['pk_provider'] = self._PRW_provider.GetData()
		self.data['reaction'] = self._PRW_reaction.GetValue().strip()
		self.data['comment'] = self._TCTRL_comment.GetValue().strip()
		self.data.save()
		return True

	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._PRW_date_given.SetText(data = gmDateTime.pydt_now_here())
		self._CHBOX_anamnestic.SetValue(False)
		self._PRW_vaccine.SetText(value = '', data = None, suppress_smarts = True)
		self._PRW_batch.unset_context(context = 'pk_vaccine')
		self._PRW_batch.SetValue('')
		self._PRW_episode.SetText(value = '', data = None, suppress_smarts = True)
		self._PRW_site.SetValue('')
		self._PRW_provider.SetData(data = None)
		self._PRW_reaction.SetText(value = '', data = None, suppress_smarts = True)
		self._TCTRL_comment.SetValue('')

		self.__refresh_indications()

		self._PRW_date_given.SetFocus()

	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		self._PRW_date_given.SetText(data = self.data['date_given'])
		if self.data['soap_cat'] == 's':
			self._CHBOX_anamnestic.SetValue(True)
		else:
			self._CHBOX_anamnestic.SetValue(False)
		self._PRW_vaccine.SetText(value = self.data['vaccine'], data = self.data['pk_vaccine'])

		self._PRW_batch.SetValue(self.data['batch_no'])
		self._PRW_episode.SetData(data = self.data['pk_episode'])
		self._PRW_site.SetValue(gmTools.coalesce(self.data['site'], ''))
		self._PRW_provider.SetData(self.data['pk_provider'])
		self._PRW_reaction.SetValue(gmTools.coalesce(self.data['reaction'], ''))
		self._TCTRL_comment.SetValue(gmTools.coalesce(self.data['comment'], ''))

		self.__refresh_indications()

		self._PRW_date_given.SetFocus()

	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._PRW_date_given.SetText(data = self.data['date_given'])
		#self._CHBOX_anamnestic.SetValue(False)
		self._PRW_vaccine.SetText(value = self.data['vaccine'], data = self.data['pk_vaccine'])

		self._PRW_batch.set_context(context = 'pk_vaccine', val = self.data['pk_vaccine'])
		self._PRW_batch.SetValue('')

		self._PRW_episode.SetData(data = self.data['pk_episode'])
		self._PRW_site.SetValue(gmTools.coalesce(self.data['site'], ''))
		self._PRW_provider.SetData(self.data['pk_provider'])
		self._PRW_reaction.SetValue('')
		self._TCTRL_comment.SetValue('')

		self.__refresh_indications()

		self._PRW_date_given.SetFocus()

	#----------------------------------------------------------------
	# event handlers
	#----------------------------------------------------------------
	def _on_add_vaccine_button_pressed(self, event):
		edit_vaccine(parent = self, vaccine = None, single_entry = False)
		# FIXME: could set newly generated vaccine here

#======================================================================
# main
#----------------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.pycommon import gmLog2

	#------------------------------------------------------------------
	def test_failsafe_vacc_hx():
		print(save_failsafe_vaccination_history())

	#------------------------------------------------------------------
	def test_manage_vaccines():
		from Gnumed.wxpython import gmGuiTest
		frame = gmGuiTest.setup_widget_test_env(patient = 12)
		gmStaff.set_current_provider_to_logged_on_user()
		wx.CallLater(2000, manage_vaccines, parent = frame)
		wx.GetApp().MainLoop()

	#------------------------------------------------------------------
	def test_manage_vaccinations():
		from Gnumed.wxpython import gmGuiTest
		frame = gmGuiTest.setup_widget_test_env(patient = 12)
		gmStaff.set_current_provider_to_logged_on_user()
		wx.CallLater(2000, manage_vaccinations, parent = frame)
		wx.GetApp().MainLoop()
		#manage_vaccinations(parent=None, latest_only=False, expand_indications=False)

	#------------------------------------------------------------------
	def test_cVaccinePhraseWheel():
		from Gnumed.wxpython import gmGuiTest
		frame = gmGuiTest.setup_widget_test_env(patient = 12)
		gmStaff.set_current_provider_to_logged_on_user()
		wx.CallLater(2000, cVaccinePhraseWheel, parent = frame)
		wx.GetApp().MainLoop()

	#------------------------------------------------------------------
	gmLog2.print_logfile_name()
	#test_manage_vaccines()
	test_manage_vaccinations()
	#test_cVaccinePhraseWheel()

#	gmPG2.request_login_params(setup_pool = True, force_tui = True)
#	gmPraxis.gmCurrentPraxisBranch.from_first_branch()
#	gmStaff.set_current_provider_to_logged_on_user()
#	gmPerson.set_active_patient(patient = 12)
#
#	#test_failsafe_vacc_hx()
#	#sys.exit()
#
#	#pat = gmPerson.cPerson(12)
#	#gmGuiTest.test_widget(cCurrentSubstancesGrid, patient = 12)
#	main_frame = gmGuiTest.setup_widget_test_env(patient = 12)
#	gmStaff.set_current_provider_to_logged_on_user()
#	vaccs_hx = save_failsafe_vaccination_history(max_width = 80)
#	gmMimeLib.call_editor_on_file(filename = vaccs_hx, block = True)
