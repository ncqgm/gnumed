"""GNUmed immunisation/vaccination widgets.

Modelled after Richard Terry's design document.

copyright: authors
"""
#======================================================================
__author__ = "R.Terry, S.J.Tan, K.Hilbert"
__license__ = "GPL v2 or later (details at http://www.gnu.org)"

import sys
import logging


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmMatchProvider
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmI18N
from Gnumed.pycommon import gmCfg
from Gnumed.pycommon import gmCfg2
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmNetworkTools
from Gnumed.pycommon import gmPrinting
from Gnumed.pycommon import gmPG2

from Gnumed.business import gmPerson
from Gnumed.business import gmVaccination
from Gnumed.business import gmPraxis
from Gnumed.business import gmProviderInbox

from Gnumed.wxpython import gmPhraseWheel
from Gnumed.wxpython import gmTerryGuiParts
from Gnumed.wxpython import gmRegetMixin
from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmEditArea
from Gnumed.wxpython import gmListWidgets
from Gnumed.wxpython import gmFormWidgets
from Gnumed.wxpython import gmMacro
from Gnumed.wxpython import gmAuthWidgets
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
	_cfg = gmCfg2.gmCfgData()
	sql_script = gmVaccination.write_generic_vaccine_sql (
		'client-%s' % _cfg.get(option = 'client_version'),
		include_indications_mapping = False
	)
	_log.debug('regenerating generic vaccines, SQL script: %s', sql_script)
	if not gmPG2.run_sql_script(sql_script, conn = dbo_conn):
		wx.EndBusyCursor()
		gmGuiHelpers.gm_show_warning (
			aMessage = _('Error regenerating generic vaccines.\n\nSee [%s]') % sql_script,
			aTitle = _('Regenerating generic vaccines')
		)
		return False

	gmDispatcher.send(signal = 'statustext', msg = _('Successfully regenerated generic vaccines ...'), beep = False)
	wx.EndBusyCursor()
	return True

#----------------------------------------------------------------------
def edit_vaccine(parent=None, vaccine=None, single_entry=True):
	ea = cVaccineEAPnl(parent, -1)
	ea.data = vaccine
	ea.mode = gmTools.coalesce(vaccine, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2(parent, -1, edit_area = ea, single_entry = single_entry)
	dlg.SetTitle(gmTools.coalesce(vaccine, _('Adding new vaccine'), _('Editing vaccine')))
	if dlg.ShowModal() == wx.ID_OK:
		dlg.DestroyLater()
		return True
	dlg.DestroyLater()
	return False

#----------------------------------------------------------------------
def manage_vaccines(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

#	#------------------------------------------------------------
#	def delete(vaccine=None):
#		product = vaccine.product
#		deleted = gmVaccination.delete_vaccine(vaccine = vaccine['pk_vaccine'])
#		if not deleted:
#			gmGuiHelpers.gm_show_info (
#				_(	'Cannot delete vaccine\n'
#					'\n'
#					' %s - %s (#%s)\n'
#					'\n'
#					'It is probably documented in a vaccination.'
#				) % (
#					vaccine['vaccine'],
#					vaccine['l10n_preparation'],
#					vaccine['pk_vaccine']
#				),
#				_('Deleting vaccine')
#			)
#			return False
#		delete_product = gmGuiHelpers.gm_show_question (
#			title = _('Deleting vaccine'),
#			question = _(
#				u'Fully delete the vaccine (including the associated drug product) ?\n'
#				u'\n'
#				u' "%s" (%s)'
#			) % (product['product'], product['l10n_preparation'])
#		)
#		if delete_product:
#			pass
#		return True

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
			'%s' % v['pk_drug_product'],
			'%s%s' % (
				v['vaccine'],
				gmTools.bool2subst (
					v['is_fake_vaccine'],
					' (%s)' % _('fake'),
					''
				)
			),
			v['l10n_preparation'],
			gmTools.coalesce(v['atc_code'], ''),
			'%s - %s' % (
				gmTools.coalesce(v['min_age'], '?'),
				gmTools.coalesce(v['max_age'], '?'),
			),
			gmTools.coalesce(v['comment'], '')
		] for v in vaccines ]
		lctrl.set_string_items(items)
		lctrl.set_data(vaccines)

	#------------------------------------------------------------
	gmListWidgets.get_choices_from_list (
		parent = parent,
		caption = _('Showing vaccine details'),
		columns = [ '#', _('Vaccine'), _('Preparation'), _('ATC'), _('Age range'), _('Comment') ],
		single_selection = True,
		refresh_callback = refresh,
		edit_callback = edit,
		new_callback = edit,
		#delete_callback = delete,
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
				batch_no || ' (' || vaccine || ')' AS list_label,
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
				batch_no || ' (' || vaccine || ')' AS list_label,
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

		# consider ATCs in ref.drug_product and ref.vacc_indication
		query = """
SELECT data, list_label, field_label FROM (

	SELECT DISTINCT ON (data)
		data,
		list_label,
		field_label
	FROM ((
			-- fragment -> vaccine
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

		) union all (

			-- fragment -> localized indication -> vaccines
			SELECT
				 r_vi4v.pk_vaccine
					AS data,
				r_vi4v.vaccine || ' ('
				||	(SELECT string_agg(l10n_inds.ind_desc::text, ', ') FROM (
						SELECT unnest(r_vi4v.indications)->>'l10n_indication' AS ind_desc
					) AS l10n_inds)
				|| ')'
					AS list_label,
				r_vi4v.vaccine
					AS field_label
			FROM
				ref.v_indications4vaccine r_vi4v
			WHERE
				 r_vi4v.l10n_indication %(fragment_condition)s

		) union all (

			-- fragment -> indication -> vaccines
			SELECT
				r_vi4v.pk_vaccine
					AS data,
				r_vi4v.vaccine || ' ('
				||	(SELECT string_agg(l10n_inds.ind_desc::text, ', ') FROM (
						SELECT unnest(r_vi4v.indications)->>'l10n_indication' AS ind_desc
					) AS l10n_inds)
				|| ')'
					AS list_label,
				r_vi4v.vaccine
					AS field_label
			FROM
				ref.v_indications4vaccine r_vi4v
			WHERE
				r_vi4v.indication %(fragment_condition)s
		)
	) AS distinct_total

) AS total

ORDER by list_label
LIMIT 25
"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries = query)
		mp.setThresholds(1, 2, 3)
		self.matcher = mp

		self.selection_only = True
	#------------------------------------------------------------------
	def _data2instance(self):
		return gmVaccination.cVaccine(aPK_obj = self.GetData())

#----------------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgVaccineEAPnl

class cVaccineEAPnl(wxgVaccineEAPnl.wxgVaccineEAPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwargs):
		try:
			data = kwargs['vaccine']
			del kwargs['vaccine']
		except KeyError:
			data = None

		wxgVaccineEAPnl.wxgVaccineEAPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		self.mode = 'new'
		self.data = data
		if data is not None:
			self.mode = 'edit'

		self.__indications = None

	#----------------------------------------------------------------
	def __refresh_indications(self):
		self._TCTRL_indications.SetValue('')
		if self.data is None:
			return
		self._TCTRL_indications.SetValue('- ' + '\n- '.join([ i['l10n_indication'] for i in self.data['indications'] ]))

	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):

		has_errors = False

		if self._PRW_drug_product.GetValue().strip() == '':
			has_errors = True
			self._PRW_drug_product.display_as_valid(False)
		else:
			self._PRW_drug_product.display_as_valid(True)

		atc = self._PRW_atc.GetValue().strip()
		if (atc == '') or (atc.startswith('J07')):
			self._PRW_atc.display_as_valid(True)
		else:
			if self._PRW_atc.GetData() is None:
				self._PRW_atc.display_as_valid(True)
			else:
				has_errors = True
				self._PRW_atc.display_as_valid(False)

		val = self._PRW_age_min.GetValue().strip()
		if val == '':
			self._PRW_age_min.display_as_valid(True)
		else:
			if gmDateTime.str2interval(val) is None:
				has_errors = True
				self._PRW_age_min.display_as_valid(False)
			else:
				self._PRW_age_min.display_as_valid(True)

		val = self._PRW_age_max.GetValue().strip()
		if val == '':
			self._PRW_age_max.display_as_valid(True)
		else:
			if gmDateTime.str2interval(val) is None:
				has_errors = True
				self._PRW_age_max.display_as_valid(False)
			else:
				self._PRW_age_max.display_as_valid(True)

		# complex conditions
		# are we editing ?
		if self.mode == 'edit':
			change_of_product = self.data['pk_drug_product'] != self._PRW_drug_product.GetData()
			if change_of_product and self.data.is_in_use:
				do_it = gmGuiHelpers.gm_show_question (
					aTitle = _('Saving vaccine'),
					aMessage = _(
						'This vaccine is already in use:\n'
						'\n'
						' "%s"\n'
						'\n'
						'Are you absolutely positively sure that\n'
						'you really want to edit this vaccine ?\n'
						'\n'
						'This will change the vaccine name and/or target\n'
						'conditions in each patient this vaccine was\n'
						'used in to document a vaccination with.\n'
					) % self._PRW_drug_product.GetValue().strip()
				)
				if not do_it:
					has_errors = True
		else:
			if self._PRW_drug_product.GetData() is None:
				# need to ask for indications ?
				if self._PRW_drug_product.GetValue().strip() != '':
					self.__indications = gmSubstanceMgmtWidgets.manage_substance_doses(vaccine_indications_only = True)
					if self.__indications is None:
						has_errors = True
			else:
				# existing drug product selected
				pass

		return (has_errors is False)

	#----------------------------------------------------------------
	def _save_as_new(self):

		# save the data as a new instance
		vaccine = gmVaccination.create_vaccine (
			pk_drug_product = self._PRW_drug_product.GetData(),
			product_name = self._PRW_drug_product.GetValue().strip(),
			indications = self.__indications,
			is_live = self._CHBOX_live.GetValue()
		)
		val = self._PRW_age_min.GetValue().strip()
		if val != '':
			vaccine['min_age'] = gmDateTime.str2interval(val)
		val = self._PRW_age_max.GetValue().strip()
		if val != '':
			vaccine['max_age'] = gmDateTime.str2interval(val)
		val = self._TCTRL_comment.GetValue().strip()
		if val != '':
			vaccine['comment'] = val
		vaccine.save()

		drug = vaccine.product
		drug['is_fake_product'] = self._CHBOX_fake.GetValue()
		val = self._PRW_atc.GetData()
		if val is not None:
			if val != 'J07':
				drug['atc'] = val.strip()
		drug.save()

		# must be done very late or else the property access
		# will refresh the display such that later field
		# access will return empty values
		self.data = vaccine

		return True

	#----------------------------------------------------------------
	def _save_as_update(self):

		drug = self.data.product
		drug['product'] = self._PRW_drug_product.GetValue().strip()
		drug['is_fake_product'] = self._CHBOX_fake.GetValue()
		val = self._PRW_atc.GetData()
		if val is not None:
			if val != 'J07':
				drug['atc'] = val.strip()
		drug.save()

		self.data['is_live'] = self._CHBOX_live.GetValue()
		val = self._PRW_age_min.GetValue().strip()
		if val != '':
			self.data['min_age'] = gmDateTime.str2interval(val)
		if val != '':
			self.data['max_age'] = gmDateTime.str2interval(val)
		val = self._TCTRL_comment.GetValue().strip()
		if val != '':
			self.data['comment'] = val
		self.data.save()

		return True

	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._PRW_drug_product.SetText(value = '', data = None, suppress_smarts = True)
		self._CHBOX_live.SetValue(False)
		self._CHBOX_fake.SetValue(False)
		self._PRW_atc.SetText(value = '', data = None, suppress_smarts = True)
		self._PRW_age_min.SetText(value = '', data = None, suppress_smarts = True)
		self._PRW_age_max.SetText(value = '', data = None, suppress_smarts = True)
		self._TCTRL_comment.SetValue('')

		self.__refresh_indications()

		self._PRW_drug_product.SetFocus()

	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		self._PRW_drug_product.SetText(value = self.data['vaccine'], data = self.data['pk_drug_product'])
		self._CHBOX_live.SetValue(self.data['is_live'])
		self._CHBOX_fake.SetValue(self.data['is_fake_vaccine'])
		self._PRW_atc.SetText(value = self.data['atc_code'], data = self.data['atc_code'])
		if self.data['min_age'] is None:
			self._PRW_age_min.SetText(value = '', data = None, suppress_smarts = True)
		else:
			self._PRW_age_min.SetText (
				value = gmDateTime.format_interval(self.data['min_age'], gmDateTime.acc_years),
				data = self.data['min_age']
			)
		if self.data['max_age'] is None:
			self._PRW_age_max.SetText(value = '', data = None, suppress_smarts = True)
		else:
			self._PRW_age_max.SetText (
				value = gmDateTime.format_interval(self.data['max_age'], gmDateTime.acc_years),
				data = self.data['max_age']
			)
		self._TCTRL_comment.SetValue(gmTools.coalesce(self.data['comment'], ''))

		self.__refresh_indications()

		self._PRW_drug_product.SetFocus()

	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._refresh_as_new()

#======================================================================
# vaccination related widgets
#----------------------------------------------------------------------
def configure_adr_url():

	def is_valid(value):
		value = value.strip()
		if value == '':
			return True, gmVaccination.URL_vaccine_adr_german_default
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
		default_value = gmVaccination.URL_vaccine_adr_german_default,
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
		return False

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
def manage_vaccinations(parent=None, latest_only=False, expand_indications=False):

	pat = gmPerson.gmCurrentPatient()
	emr = pat.emr

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#------------------------------------------------------------
	def browse2schedules(vaccination=None):
		dbcfg = gmCfg.cCfgSQL()
		url = dbcfg.get2 (
			option = 'external.urls.vaccination_plans',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
			bias = 'user',
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
			subject = _('vaccination recall (%s)') % vaccination['vaccine']

		recall = gmProviderInbox.create_inbox_message (
			message_type = _('Vaccination'),
			subject = subject,
			patient = pat.ID,
			staff = None
		)

		if vaccination is not None:
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
			latest_vaccs = emr.get_latest_vaccinations()
			for indication in sorted(latest_vaccs):
				no_of_shots4ind, latest_vacc4ind = latest_vaccs[indication]
				items.append ([
					indication,
					_('%s (latest of %s: %s ago)') % (
						gmDateTime.pydt_strftime(latest_vacc4ind['date_given'], format = '%Y %b'),
						no_of_shots4ind,
						gmDateTime.format_interval_medically(gmDateTime.pydt_now_here() - latest_vacc4ind['date_given'])
					),
					latest_vacc4ind['vaccine'],
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
								gmDateTime.pydt_strftime(shot['date_given'], '%Y %b %d'),
								gmDateTime.format_interval_medically(gmDateTime.pydt_now_here() - shot['date_given'])
							),
							shot['vaccine'],
							shot['batch_no'],
							gmTools.coalesce(shot['site'], ''),
							gmTools.coalesce(shot['reaction'], ''),
							gmTools.coalesce(shot['comment'], '')
						])
						idx -= 1
						data.append(shot)
			else:
				items = [ [
					gmDateTime.pydt_strftime(s['date_given'], '%Y %b %d'),
					s['vaccine'],
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
from Gnumed.wxGladeWidgets import wxgVaccinationEAPnl

class cVaccinationEAPnl(wxgVaccinationEAPnl.wxgVaccinationEAPnl, gmEditArea.cGenericEditAreaMixin):
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

		wxgVaccinationEAPnl.wxgVaccinationEAPnl.__init__(self, *args, **kwargs)
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
		self._PRW_reaction.add_callback_on_lose_focus(self._on_PRW_reaction_lost_focus)

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
	def _on_PRW_reaction_lost_focus(self):
		if self._PRW_reaction.GetValue().strip() == '':
			self._BTN_report.Enable(False)
		else:
			self._BTN_report.Enable(True)

	#----------------------------------------------------------------
	def __refresh_indications(self):
		self._TCTRL_indications.SetValue('')
		vaccine = self._PRW_vaccine.GetData(as_instance = True)
		if vaccine is None:
			return
		lines = []
		emr = gmPerson.gmCurrentPatient().emr
		latest_vaccs = emr.get_latest_vaccinations (
			atc_indications = [ i['atc_indication'] for i in vaccine['indications'] ]
		)
		for l10n_ind in [ i['l10n_indication'] for i in vaccine['indications'] ]:
			try:
				no_of_shots4ind, latest_vacc4ind = latest_vaccs[l10n_ind]
				ago = gmDateTime.format_interval_medically(gmDateTime.pydt_now_here() - latest_vacc4ind['date_given'])
				lines.append(_('%s  (most recent shot of %s: %s ago)') % (l10n_ind, no_of_shots4ind, ago))
			except KeyError:
				lines.append(_('%s  (no previous vaccination recorded)') % l10n_ind)

		self._TCTRL_indications.SetValue(_('Protects against:\n ') + '\n '.join(lines))

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

		vaccine = self._PRW_vaccine.GetData()
		data = self.__save_new_from_vaccine(vaccine = vaccine)

		# must be done very late or else the property access
		# will refresh the display such that later field
		# access will return empty values
		self.data = data

		return True

	#----------------------------------------------------------------
	def __save_new_from_vaccine(self, vaccine=None):

		emr = gmPerson.gmCurrentPatient().emr

		data = emr.add_vaccination (
			episode = self._PRW_episode.GetData(can_create = True, is_open = False),
			vaccine = vaccine,
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
		self._BTN_report.Enable(False)
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
		if self.data['reaction'] is None:
			self._BTN_report.Enable(False)
		else:
			self._BTN_report.Enable(True)
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
		self._BTN_report.Enable(False)
		self._TCTRL_comment.SetValue('')

		self.__refresh_indications()

		self._PRW_date_given.SetFocus()

	#----------------------------------------------------------------
	# event handlers
	#----------------------------------------------------------------
	def _on_report_button_pressed(self, event):
		event.Skip()
		dbcfg = gmCfg.cCfgSQL()
		url = dbcfg.get2 (
			option = 'external.urls.report_vaccine_ADR',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
			bias = 'user'
		)
		if url.strip() == '':
			url = dbcfg.get2 (
				option = 'external.urls.report_ADR',
				workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
				bias = 'user'
			)
		gmNetworkTools.open_url_in_browser(url = url)

	#----------------------------------------------------------------
	def _on_add_vaccine_button_pressed(self, event):
		edit_vaccine(parent = self, vaccine = None, single_entry = False)
		# FIXME: could set newly generated vaccine here

#======================================================================
#======================================================================
#======================================================================
#======================================================================
class cImmunisationsPanel(wx.Panel, gmRegetMixin.cRegetOnPaintMixin):

	def __init__(self, parent, id):
		wx.Panel.__init__(self, parent, id, wx.DefaultPosition, wx.DefaultSize, wx.RAISED_BORDER)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)
		self.__pat = gmPerson.gmCurrentPatient()
		# do this here so "import cImmunisationsPanel from gmVaccWidgets" works
		self.ID_VaccinatedIndicationsList = wx.NewId()
		self.ID_VaccinationsPerRegimeList = wx.NewId()
		self.ID_MissingShots = wx.NewId()
		self.ID_ActiveSchedules = wx.NewId()
		self.__do_layout()
		self.__register_interests()
		self.__reset_ui_content()
	#----------------------------------------------------
	def __do_layout(self):
		#-----------------------------------------------
		# top part
		#-----------------------------------------------
		pnl_UpperCaption = gmTerryGuiParts.cHeadingCaption(self, -1, _("  IMMUNISATIONS  "))
		self.editarea = cVaccinationEditArea(self, -1, wx.DefaultPosition, wx.DefaultSize, wx.NO_BORDER)

		#-----------------------------------------------
		# middle part
		#-----------------------------------------------
		# divider headings below editing area
		indications_heading = gmTerryGuiParts.cDividerCaption(self, -1, _("Indications"))
		vaccinations_heading = gmTerryGuiParts.cDividerCaption(self, -1, _("Vaccinations"))
		schedules_heading = gmTerryGuiParts.cDividerCaption(self, -1, _("Active Schedules"))
		szr_MiddleCap = wx.BoxSizer(wx.HORIZONTAL)
		szr_MiddleCap.Add(indications_heading, 4, wx.EXPAND)
		szr_MiddleCap.Add(vaccinations_heading, 6, wx.EXPAND)
		szr_MiddleCap.Add(schedules_heading, 10, wx.EXPAND)

		# left list: indications for which vaccinations have been given
		self.LBOX_vaccinated_indications = wx.ListBox(
			parent = self,
			id = self.ID_VaccinatedIndicationsList,
			choices = [],
			style = wx.LB_HSCROLL | wx.LB_NEEDED_SB | wx.SUNKEN_BORDER
		)
		self.LBOX_vaccinated_indications.SetFont(wx.Font(12,wx.SWISS, wx.NORMAL, wx.NORMAL, False, ''))

		# right list: when an indication has been selected on the left
		# display the corresponding vaccinations on the right
		self.LBOX_given_shots = wx.ListBox(
			parent = self,
			id = self.ID_VaccinationsPerRegimeList,
			choices = [],
			style = wx.LB_HSCROLL | wx.LB_NEEDED_SB | wx.SUNKEN_BORDER
		)
		self.LBOX_given_shots.SetFont(wx.Font(12,wx.SWISS, wx.NORMAL, wx.NORMAL, False, ''))

		self.LBOX_active_schedules = wx.ListBox (
			parent = self,
			id = self.ID_ActiveSchedules,
			choices = [],
			style = wx.LB_HSCROLL | wx.LB_NEEDED_SB | wx.SUNKEN_BORDER
		)
		self.LBOX_active_schedules.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL, False, ''))

		szr_MiddleLists = wx.BoxSizer(wx.HORIZONTAL)
		szr_MiddleLists.Add(self.LBOX_vaccinated_indications, 4, wx.EXPAND)
		szr_MiddleLists.Add(self.LBOX_given_shots, 6, wx.EXPAND)
		szr_MiddleLists.Add(self.LBOX_active_schedules, 10, wx.EXPAND)

		#---------------------------------------------
		# bottom part
		#---------------------------------------------
		missing_heading = gmTerryGuiParts.cDividerCaption(self, -1, _("Missing Immunisations"))
		szr_BottomCap = wx.BoxSizer(wx.HORIZONTAL)
		szr_BottomCap.Add(missing_heading, 1, wx.EXPAND)

		self.LBOX_missing_shots = wx.ListBox (
			parent = self,
			id = self.ID_MissingShots,
			choices = [],
			style = wx.LB_HSCROLL | wx.LB_NEEDED_SB | wx.SUNKEN_BORDER
		)
		self.LBOX_missing_shots.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL, False, ''))

		szr_BottomLists = wx.BoxSizer(wx.HORIZONTAL)
		szr_BottomLists.Add(self.LBOX_missing_shots, 1, wx.EXPAND)

		# alert caption
		pnl_AlertCaption = gmTerryGuiParts.cAlertCaption(self, -1, _('  Alerts  '))

		#---------------------------------------------
		# add all elements to the main background sizer
		#---------------------------------------------
		self.mainsizer = wx.BoxSizer(wx.VERTICAL)
		self.mainsizer.Add(pnl_UpperCaption, 0, wx.EXPAND)
		self.mainsizer.Add(self.editarea, 6, wx.EXPAND)
		self.mainsizer.Add(szr_MiddleCap, 0, wx.EXPAND)
		self.mainsizer.Add(szr_MiddleLists, 4, wx.EXPAND)
		self.mainsizer.Add(szr_BottomCap, 0, wx.EXPAND)
		self.mainsizer.Add(szr_BottomLists, 4, wx.EXPAND)
		self.mainsizer.Add(pnl_AlertCaption, 0, wx.EXPAND)

		self.SetAutoLayout(True)
		self.SetSizer(self.mainsizer)
		self.mainsizer.Fit(self)
	#----------------------------------------------------
	def __register_interests(self):
		# wxPython events
		wx.EVT_SIZE(self, self.OnSize)
		wx.EVT_LISTBOX(self, self.ID_VaccinatedIndicationsList, self._on_vaccinated_indication_selected)
		wx.EVT_LISTBOX_DCLICK(self, self.ID_VaccinationsPerRegimeList, self._on_given_shot_selected)
		wx.EVT_LISTBOX_DCLICK(self, self.ID_MissingShots, self._on_missing_shot_selected)
#		wx.EVT_RIGHT_UP(self.lb1, self.EvtRightButton)

		# client internal signals
		gmDispatcher.connect(signal= 'post_patient_selection', receiver=self._schedule_data_reget)
		gmDispatcher.connect(signal= 'vaccinations_updated', receiver=self._schedule_data_reget)
	#----------------------------------------------------
	# event handlers
	#----------------------------------------------------
	def OnSize (self, event):
		w, h = event.GetSize()
		self.mainsizer.SetDimension (0, 0, w, h)
	#----------------------------------------------------
	def _on_given_shot_selected(self, event):
		"""Paste previously given shot into edit area.
		"""
		self.editarea.set_data(aVacc=event.GetClientData())
	#----------------------------------------------------
	def _on_missing_shot_selected(self, event):
		self.editarea.set_data(aVacc = event.GetClientData())
	#----------------------------------------------------
	def _on_vaccinated_indication_selected(self, event):
		"""Update right hand middle list to show vaccinations given for selected indication."""
		ind_list = event.GetEventObject()
		selected_item = ind_list.GetSelection()
		ind = ind_list.GetClientData(selected_item)
		# clear list
		self.LBOX_given_shots.Set([])
		emr = self.__pat.emr
		shots = emr.get_vaccinations(indications = [ind])
		# FIXME: use Set() for entire array (but problem with client_data)
		for shot in shots:
			if shot['is_booster']:
				marker = 'B'
			else:
				marker = '#%s' % shot['seq_no']
			label = '%s - %s: %s' % (marker, shot['date'].strftime('%m/%Y'), shot['vaccine'])
			self.LBOX_given_shots.Append(label, shot)
	#----------------------------------------------------
	def __reset_ui_content(self):
		# clear edit area
		self.editarea.set_data()
		# clear lists
		self.LBOX_vaccinated_indications.Clear()
		self.LBOX_given_shots.Clear()
		self.LBOX_active_schedules.Clear()
		self.LBOX_missing_shots.Clear()
	#----------------------------------------------------
	def _populate_with_data(self):
		# clear lists
		self.LBOX_vaccinated_indications.Clear()
		self.LBOX_given_shots.Clear()
		self.LBOX_active_schedules.Clear()
		self.LBOX_missing_shots.Clear()

		emr = self.__pat.emr

		t1 = time.time()
		# populate vaccinated-indications list
		# FIXME: consider adding virtual indication "most recent" to
		# FIXME: display most recent of all indications as suggested by Syan
		status, indications = emr.get_vaccinated_indications()
		# FIXME: would be faster to use Set() but can't
		# use Set(labels, client_data), and have to know
		# line position in SetClientData :-(
		for indication in indications:
			self.LBOX_vaccinated_indications.Append(indication[1], indication[0])
#		self.LBOX_vaccinated_indications.Set(lines)
#		self.LBOX_vaccinated_indications.SetClientData(data)
		print("vaccinated indications took", time.time()-t1, "seconds")

		t1 = time.time()
		# populate active schedules list
		scheds = emr.get_scheduled_vaccination_regimes()
		if scheds is None:
			label = _('ERROR: cannot retrieve active vaccination schedules')
			self.LBOX_active_schedules.Append(label)
		elif len(scheds) == 0:
			label = _('no active vaccination schedules')
			self.LBOX_active_schedules.Append(label)
		else:
			for sched in scheds:
				label = _('%s for %s (%s shots): %s') % (sched['regime'], sched['l10n_indication'], sched['shots'], sched['comment'])
				self.LBOX_active_schedules.Append(label)
		print("active schedules took", time.time()-t1, "seconds")

		t1 = time.time()
		# populate missing-shots list
		missing_shots = emr.get_missing_vaccinations()
		print("getting missing shots took", time.time()-t1, "seconds")
		if missing_shots is None:
			label = _('ERROR: cannot retrieve due/overdue vaccinations')
			self.LBOX_missing_shots.Append(label, None)
			return True
		# due
		due_template = _('%.0d weeks left: shot %s for %s in %s, due %s (%s)')
		overdue_template = _('overdue %.0dyrs %.0dwks: shot %s for %s in schedule "%s" (%s)')
		for shot in missing_shots['due']:
			if shot['overdue']:
				years, days_left = divmod(shot['amount_overdue'].days, 364.25)
				weeks = days_left / 7
				# amount_overdue, seq_no, indication, regime, vacc_comment
				label = overdue_template % (
					years,
					weeks,
					shot['seq_no'],
					shot['l10n_indication'],
					shot['regime'],
					shot['vacc_comment']
				)
				self.LBOX_missing_shots.Append(label, shot)
			else:
				# time_left, seq_no, regime, latest_due, vacc_comment
				label = due_template % (
					shot['time_left'].days / 7,
					shot['seq_no'],
					shot['indication'],
					shot['regime'],
					shot['latest_due'].strftime('%m/%Y'),
					shot['vacc_comment']
				)
				self.LBOX_missing_shots.Append(label, shot)
		# booster
		lbl_template = _('due now: booster for %s in schedule "%s" (%s)')
		for shot in missing_shots['boosters']:
			# indication, regime, vacc_comment
			label = lbl_template % (
				shot['l10n_indication'],
				shot['regime'],
				shot['vacc_comment']
			)
			self.LBOX_missing_shots.Append(label, shot)
		print("displaying missing shots took", time.time()-t1, "seconds")

		return True
	#----------------------------------------------------
	def _on_post_patient_selection(self, **kwargs):
		return 1
		# FIXME:
#		if has_focus:
#			wxCallAfter(self.__reset_ui_content)
#		else:
#			return 1
	#----------------------------------------------------
	def _on_vaccinations_updated(self, **kwargs):
		return 1
		# FIXME:
#		if has_focus:
#			wxCallAfter(self.__reset_ui_content)
#		else:
#			is_stale == True
#			return 1
#======================================================================
# main
#----------------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	app = wx.PyWidgetTester(size = (600, 600))
	app.SetWidget(cXxxPhraseWheel, -1)
	app.MainLoop()
