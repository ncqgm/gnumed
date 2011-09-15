"""GNUmed immunisation/vaccination widgets.

Modelled after Richard Terry's design document.

copyright: authors
"""
#======================================================================
__version__ = "$Revision: 1.36 $"
__author__ = "R.Terry, S.J.Tan, K.Hilbert"
__license__ = "GPL v2 or later (details at http://www.gnu.org)"

import sys, time, logging, webbrowser


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmDispatcher, gmMatchProvider, gmTools, gmI18N
from Gnumed.pycommon import gmCfg, gmDateTime
from Gnumed.business import gmPerson, gmVaccination, gmSurgery
from Gnumed.wxpython import gmPhraseWheel, gmTerryGuiParts, gmRegetMixin, gmGuiHelpers
from Gnumed.wxpython import gmEditArea, gmListWidgets


_log = logging.getLogger('gm.vaccination')
_log.info(__version__)

#======================================================================
# vaccination indication related widgets
#----------------------------------------------------------------------
def manage_vaccination_indications(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()
	#------------------------------------------------------------
	def refresh(lctrl):
		inds = gmVaccination.get_indications(order_by = 'description')

		items = [ [
			i['description'],
			gmTools.coalesce (
				i['atcs_single_indication'],
				u'',
				u'%s'
			),
			gmTools.coalesce (
				i['atcs_combi_indication'],
				u'',
				u'%s'
			),
			u'%s' % i['id']
		] for i in inds ]

		lctrl.set_string_items(items)
		lctrl.set_data(inds)
	#------------------------------------------------------------
	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = _('\nConditions preventable by vaccination as currently known to GNUmed.\n'),
		caption = _('Showing vaccination preventable conditions.'),
		columns = [ _('Condition'), _('ATCs: single-condition vaccines'), _('ATCs: multi-condition vaccines'), u'#' ],
		single_selection = True,
		refresh_callback = refresh
	)
#----------------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgVaccinationIndicationsPnl

class cVaccinationIndicationsPnl(wxgVaccinationIndicationsPnl.wxgVaccinationIndicationsPnl):

	def __init__(self, *args, **kwargs):

		wxgVaccinationIndicationsPnl.wxgVaccinationIndicationsPnl.__init__(self, *args, **kwargs)

		self.__indication2field = {
			u'coxiella burnetii (Q fever)': self._CHBOX_coxq,
			u'salmonella typhi (typhoid)': self._CHBOX_typhoid,
			u'varicella (chickenpox, shingles)': self._CHBOX_varicella,
			u'influenza (seasonal)': self._CHBOX_influenza,
			u'bacillus anthracis (Anthrax)': self._CHBOX_anthrax,
			u'human papillomavirus': self._CHBOX_hpv,
			u'rotavirus': self._CHBOX_rota,
			u'tuberculosis': self._CHBOX_tuberculosis,
			u'variola virus (smallpox)': self._CHBOX_smallpox,
			u'influenza (H1N1)': self._CHBOX_h1n1,
			u'cholera': self._CHBOX_cholera,
			u'diphtheria': self._CHBOX_diphtheria,
			u'haemophilus influenzae b': self._CHBOX_hib,
			u'hepatitis A': self._CHBOX_hepA,
			u'hepatitis B': self._CHBOX_hepB,
			u'japanese B encephalitis': self._CHBOX_japanese,
			u'measles': self._CHBOX_measles,
			u'meningococcus A': self._CHBOX_menA,
			u'meningococcus C': self._CHBOX_menC,
			u'meningococcus W': self._CHBOX_menW,
			u'meningococcus Y': self._CHBOX_menY,
			u'mumps': self._CHBOX_mumps,
			u'pertussis': self._CHBOX_pertussis,
			u'pneumococcus': self._CHBOX_pneumococcus,
			u'poliomyelitis': self._CHBOX_polio,
			u'rabies': self._CHBOX_rabies,
			u'rubella': self._CHBOX_rubella,
			u'tetanus': self._CHBOX_tetanus,
			u'tick-borne meningoencephalitis': self._CHBOX_fsme,
			u'yellow fever': self._CHBOX_yellow_fever,
			u'yersinia pestis': self._CHBOX_yersinia_pestis
		}
	#------------------------------------------------------------------
	def enable_all(self):
		for field in self.__dict__.keys():
			if field.startswith('_CHBOX_'):
				self.__dict__[field].Enable()
		self.Enable()
	#------------------------------------------------------------------
	def disable_all(self):
		for field in self.__dict__.keys():
			if field.startswith('_CHBOX_'):
				self.__dict__[field].Disable()
		self.Disable()
	#------------------------------------------------------------------
	def clear_all(self):
		for field in self.__dict__.keys():
			if field.startswith('_CHBOX_'):
				self.__dict__[field].SetValue(False)
	#------------------------------------------------------------------
	def select(self, indications=None):
		for indication in indications:
			self.__indication2field[indication].SetValue(True)
	#------------------------------------------------------------------
	def _get_selected_indications(self):
		indications = []
		for indication in self.__indication2field.keys():
			if self.__indication2field[indication].IsChecked():
				indications.append(indication)
		return indications

	selected_indications = property(_get_selected_indications, lambda x:x)
	#------------------------------------------------------------------
	def _get_has_selection(self):
		for indication in self.__indication2field.keys():
			if self.__indication2field[indication].IsChecked():
				return True
		return False

	has_selection = property(_get_has_selection, lambda x:x)

#======================================================================
# vaccines related widgets
#----------------------------------------------------------------------
def edit_vaccine(parent=None, vaccine=None, single_entry=True):
	ea = cVaccineEAPnl(parent = parent, id = -1)
	ea.data = vaccine
	ea.mode = gmTools.coalesce(vaccine, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2(parent = parent, id = -1, edit_area = ea, single_entry = single_entry)
	dlg.SetTitle(gmTools.coalesce(vaccine, _('Adding new vaccine'), _('Editing vaccine')))
	if dlg.ShowModal() == wx.ID_OK:
		dlg.Destroy()
		return True
	dlg.Destroy()
	return False
#----------------------------------------------------------------------
def manage_vaccines(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()
	#------------------------------------------------------------
	def delete(vaccine=None):
		deleted = gmVaccination.delete_vaccine(vaccine = vaccine['pk_vaccine'])
		if deleted:
			return True

		gmGuiHelpers.gm_show_info (
			_(
				'Cannot delete vaccine\n'
				'\n'
				' %s - %s (#%s)\n'
				'\n'
				'It is probably documented in a vaccination.'
			) % (
				vaccine['vaccine'],
				vaccine['preparation'],
				vaccine['pk_vaccine']
			),
			_('Deleting vaccine')
		)

		return False
	#------------------------------------------------------------
	def edit(vaccine=None):
		return edit_vaccine(parent = parent, vaccine = vaccine, single_entry = True)
	#------------------------------------------------------------
	def refresh(lctrl):
		vaccines = gmVaccination.get_vaccines(order_by = 'vaccine')

		items = [ [
			u'%s' % v['pk_brand'],
			u'%s%s' % (
				v['vaccine'],
				gmTools.bool2subst (
					v['is_fake_vaccine'],
					u' (%s)' % _('fake'),
					u''
				)
			),
			v['preparation'],
			u'%s (%s)' % (v['route_abbreviation'], v['route_description']),
			gmTools.bool2subst(v['is_live'], gmTools.u_checkmark_thin, u'', u'?'),
			gmTools.coalesce(v['atc_code'], u''),
			u'%s%s' % (
				gmTools.coalesce(v['min_age'], u'?'),
				gmTools.coalesce(v['max_age'], u'?', u' - %s'),
			),
			gmTools.coalesce(v['comment'], u'')
		] for v in vaccines ]
		lctrl.set_string_items(items)
		lctrl.set_data(vaccines)
	#------------------------------------------------------------
	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = _('\nThe vaccines currently known to GNUmed.\n'),
		caption = _('Showing vaccines.'),
		columns = [ u'#', _('Brand'), _('Preparation'), _(u'Route'), _('Live'), _('ATC'), _('Age range'), _('Comment') ],
		single_selection = True,
		refresh_callback = refresh,
		edit_callback = edit,
		new_callback = edit,
		delete_callback = delete
	)
#----------------------------------------------------------------------
class cBatchNoPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)

		context = {
			u'ctxt_vaccine': {
				u'where_part': u'AND pk_vaccine = %(pk_vaccine)s',
				u'placeholder': u'pk_vaccine'
			}
		}

		query = u"""
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
				clin.v_pat_vaccinations
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
				clin.v_pat_vaccinations
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

		self.unset_context(context = u'pk_vaccine')
		self.SetToolTipString(_('Enter or select the batch/lot number of the vaccine used.'))
		self.selection_only = False
#----------------------------------------------------------------------
class cVaccinePhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)

		# consider ATCs in ref.branded_drug and vacc_indication
		query = u"""
SELECT data, list_label, field_label FROM (

	SELECT DISTINCT ON (data)
		data,
		list_label,
		field_label
	FROM ((
			-- fragment -> vaccine
			SELECT
				pk_vaccine AS data,
				vaccine || ' (' || array_to_string(l10n_indications, ', ') || ')' AS list_label,
				vaccine AS field_label
			FROM
				clin.v_vaccines
			WHERE
				vaccine %(fragment_condition)s

		) union all (

			-- fragment -> localized indication -> vaccines
			SELECT
				pk_vaccine AS data,
				vaccine || ' (' || array_to_string(l10n_indications, ', ') || ')' AS list_label,
				vaccine AS field_label
			FROM
				clin.v_indications4vaccine
			WHERE
				l10n_indication %(fragment_condition)s

		) union all (

			-- fragment -> indication -> vaccines
			SELECT
				pk_vaccine AS data,
				vaccine || ' (' || array_to_string(indications, ', ') || ')' AS list_label,
				vaccine AS field_label
			FROM
				clin.v_indications4vaccine
			WHERE
				indication %(fragment_condition)s
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

		self.__init_ui()
	#----------------------------------------------------------------
	def __init_ui(self):

		# route
		query = u"""
			SELECT DISTINCT ON (abbreviation)
				id,
				abbreviation || ' (' || _(description) || ')'
			FROM
				clin.vacc_route
			WHERE
				abbreviation %(fragment_condition)s
					OR
				description %(fragment_condition)s
			ORDER BY
				abbreviation
		"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query)
		mp.setThresholds(1, 2, 3)
		self._PRW_route.matcher = mp
		self._PRW_route.selection_only = True

		#self._PRW_age_min = gmPhraseWheel.cPhraseWheel(self, -1, "", style=wx.NO_BORDER)
		#self._PRW_age_max = gmPhraseWheel.cPhraseWheel(self, -1, "", style=wx.NO_BORDER)

		self.Layout()
		self.Fit()
	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):

		has_errors = False

		if self._PRW_brand.GetValue().strip() == u'':
			has_errors = True
			self._PRW_brand.display_as_valid(False)
		else:
			self._PRW_brand.display_as_valid(True)

		if self._PRW_route.GetData() is None:
			has_errors = True
			self._PRW_route.display_as_valid(False)
		else:
			self._PRW_route.display_as_valid(True)

		if not self._PNL_indications.has_selection:
			has_errors = True

		if self._PRW_atc.GetValue().strip() in [u'', u'J07']:
			self._PRW_atc.display_as_valid(True)
		else:
			if self._PRW_atc.GetData() is None:
				self._PRW_atc.display_as_valid(True)
			else:
				has_errors = True
				self._PRW_atc.display_as_valid(False)

		val = self._PRW_age_min.GetValue().strip()
		if val == u'':
			self._PRW_age_min.display_as_valid(True)
		else:
			if gmDateTime.str2interval(val) is None:
				has_errors = True
				self._PRW_age_min.display_as_valid(False)
			else:
				self._PRW_age_min.display_as_valid(True)

		val = self._PRW_age_max.GetValue().strip()
		if val == u'':
			self._PRW_age_max.display_as_valid(True)
		else:
			if gmDateTime.str2interval(val) is None:
				has_errors = True
				self._PRW_age_max.display_as_valid(False)
			else:
				self._PRW_age_max.display_as_valid(True)

		# are we editing ?
		ask_user = (self.mode == 'edit')
		# is this vaccine in use ?
		ask_user = (ask_user and self.data.is_in_use)
		# a change ...
		ask_user = ask_user and (
			# ... of brand ...
			(self.data['pk_brand'] != self._PRW_route.GetData())
				or
			# ... or indications ?
			(self.data['indications'] != self._PNL_indications.selected_indications)
		)

		if ask_user:
			do_it = gmGuiHelpers.gm_show_question (
				aTitle = _('Saving vaccine'),
				aMessage = _(
					u'This vaccine is already in use:\n'
					u'\n'
					u' "%s"\n'
					u' (%s)\n'
					u'\n'
					u'Are you absolutely positively sure that\n'
					u'you really want to edit this vaccine ?\n'
					'\n'
					u'This will change the vaccine name and/or target\n'
					u'conditions in each patient this vaccine was\n'
					u'used in to document a vaccination with.\n'
				) % (
					self._PRW_brand.GetValue().strip(),
					u', '.join(self.data['l10n_indications'])
				)
			)
			if not do_it:
				has_errors = True

		return (has_errors is False)
	#----------------------------------------------------------------
	def _save_as_new(self):
		# save the data as a new instance
		data = gmVaccination.create_vaccine (
			pk_brand = self._PRW_brand.GetData(),
			brand_name = self._PRW_brand.GetValue(),
			indications = self._PNL_indications.selected_indications
		)

		data['pk_route'] = self._PRW_route.GetData()
#		data['is_live'] = self._CHBOX_live.GetValue()
		val = self._PRW_age_min.GetValue().strip()
		if val != u'':
			data['min_age'] = gmDateTime.str2interval(val)
		val = self._PRW_age_max.GetValue().strip()
		if val != u'':
			data['max_age'] = gmDateTime.str2interval(val)
		val = self._TCTRL_comment.GetValue().strip()
		if val != u'':
			data['comment'] = val

		data.save()

		drug = data.brand
		drug['is_fake'] = self._CHBOX_fake.GetValue()
		val = self._PRW_atc.GetData()
		if val is not None:
			if val != u'J07':
				drug['atc_code'] = val.strip()
		drug.save()

		# must be done very late or else the property access
		# will refresh the display such that later field
		# access will return empty values
		self.data = data

		return True
	#----------------------------------------------------------------
	def _save_as_update(self):

		drug = self.data.brand
		drug['description'] = self._PRW_brand.GetValue().strip()
		drug['is_fake'] = self._CHBOX_fake.GetValue()
		val = self._PRW_atc.GetData()
		if val is not None:
			if val != u'J07':
				drug['atc_code'] = val.strip()
		drug.save()

		# the validator already asked for changes so just do it
		self.data.set_indications(indications = self._PNL_indications.selected_indications)

		self.data['pk_route'] = self._PRW_route.GetData()
#		self.data['is_live'] = self._CHBOX_live.GetValue()
		val = self._PRW_age_min.GetValue().strip()
		if val != u'':
			self.data['min_age'] = gmDateTime.str2interval(val)
		if val != u'':
			self.data['max_age'] = gmDateTime.str2interval(val)
		val = self._TCTRL_comment.GetValue().strip()
		if val != u'':
			self.data['comment'] = val

		self.data.save()
		return True
	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._PRW_brand.SetText(value = u'', data = None, suppress_smarts = True)
		self._PRW_route.SetText(value = u'intramuscular')
		self._CHBOX_live.SetValue(True)
		self._CHBOX_fake.SetValue(False)
		self._PNL_indications.clear_all()
		self._PRW_atc.SetText(value = u'', data = None, suppress_smarts = True)
		self._PRW_age_min.SetText(value = u'', data = None, suppress_smarts = True)
		self._PRW_age_max.SetText(value = u'', data = None, suppress_smarts = True)
		self._TCTRL_comment.SetValue(u'')

		self._PRW_brand.SetFocus()
	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		self._PRW_brand.SetText(value = self.data['vaccine'], data = self.data['pk_brand'])
		self._PRW_route.SetText(value = self.data['route_description'], data = self.data['pk_route'])
		self._CHBOX_live.SetValue(self.data['is_live'])
		self._CHBOX_fake.SetValue(self.data['is_fake_vaccine'])
		self._PNL_indications.select(self.data['indications'])
		self._PRW_atc.SetText(value = self.data['atc_code'], data = self.data['atc_code'])
		if self.data['min_age'] is None:
			self._PRW_age_min.SetText(value = u'', data = None, suppress_smarts = True)
		else:
			self._PRW_age_min.SetText (
				value = gmDateTime.format_interval(self.data['min_age'], gmDateTime.acc_years),
				data = self.data['min_age']
			)
		if self.data['max_age'] is None:
			self._PRW_age_max.SetText(value = u'', data = None, suppress_smarts = True)
		else:
			self._PRW_age_max.SetText (
				value = gmDateTime.format_interval(self.data['max_age'], gmDateTime.acc_years),
				data = self.data['max_age']
			)
		self._TCTRL_comment.SetValue(gmTools.coalesce(self.data['comment'], u''))

		self._PRW_brand.SetFocus()
	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._refresh_as_new()
#======================================================================
# vaccination related widgets
#----------------------------------------------------------------------
def edit_vaccination(parent=None, vaccination=None, single_entry=True):
	ea = cVaccinationEAPnl(parent = parent, id = -1)
	ea.data = vaccination
	ea.mode = gmTools.coalesce(vaccination, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2(parent = parent, id = -1, edit_area = ea, single_entry = single_entry)
	dlg.SetTitle(gmTools.coalesce(vaccination, _('Adding new vaccinations'), _('Editing vaccination')))
	if dlg.ShowModal() == wx.ID_OK:
		dlg.Destroy()
		return True
	dlg.Destroy()
	if not single_entry:
		return True
	return False
#----------------------------------------------------------------------
def manage_vaccinations(parent=None):

	pat = gmPerson.gmCurrentPatient()
	emr = pat.get_emr()

	if parent is None:
		parent = wx.GetApp().GetTopWindow()
	#------------------------------------------------------------
	def browse2schedules(vaccination=None):
		dbcfg = gmCfg.cCfgSQL()
		url = dbcfg.get2 (
			option = 'external.urls.vaccination_plans',
			workplace = gmSurgery.gmCurrentPractice().active_workplace,
			bias = 'user',
			default = u'http://www.bundesaerztekammer.de/downloads/ImpfempfehlungenRKI2009.pdf'
		)

		webbrowser.open (
			url = url,
			new = False,
			autoraise = True
		)
		return False
	#------------------------------------------------------------
	def edit(vaccination=None):
		return edit_vaccination(parent = parent, vaccination = vaccination, single_entry = (vaccination is not None))
	#------------------------------------------------------------
	def delete(vaccination=None):
		gmVaccination.delete_vaccination(vaccination = vaccination['pk_vaccination'])
		return True
	#------------------------------------------------------------
	def refresh(lctrl):

		vaccs = emr.get_vaccinations(order_by = 'date_given DESC, pk_vaccination')

		items = [ [
			v['date_given'].strftime('%Y %B %d').decode(gmI18N.get_encoding()),
			v['vaccine'],
			u', '.join(v['l10n_indications']),
			v['batch_no'],
			gmTools.coalesce(v['site'], u''),
			gmTools.coalesce(v['reaction'], u''),
			gmTools.coalesce(v['comment'], u'')
		] for v in vaccs ]

		lctrl.set_string_items(items)
		lctrl.set_data(vaccs)
	#------------------------------------------------------------
	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = _('\nComplete vaccination history for this patient.\n'),
		caption = _('Showing vaccinations.'),
		columns = [ _('Date'), _('Vaccine'), _(u'Intended to protect from'), _('Batch'), _('Site'), _('Reaction'), _('Comment') ],
		single_selection = True,
		refresh_callback = refresh,
		new_callback = edit,
		edit_callback = edit,
		delete_callback = delete,
		left_extra_button = (_('Vaccination Plans'), _('Open a browser showing vaccination schedules.'), browse2schedules)
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
#		self._PRW_batch.unset_context(context = 'pk_vaccine')		# done in PRW init()
		self._PRW_reaction.add_callback_on_lose_focus(self._on_PRW_reaction_lost_focus)
	#----------------------------------------------------------------
	def _on_PRW_vaccine_lost_focus(self):

		vaccine = self._PRW_vaccine.GetData(as_instance=True)

		# if we are editing we do not allow using indications rather than a vaccine
		if self.mode == u'edit':
			self._PNL_indications.clear_all()
			if vaccine is None:
				self._PRW_batch.unset_context(context = 'pk_vaccine')
			else:
				self._PRW_batch.set_context(context = 'pk_vaccine', val = vaccine['pk_vaccine'])
				self._PNL_indications.select(indications = vaccine['indications'])
			self._PNL_indications.disable_all()

		# we are entering a new vaccination
		else:
			if vaccine is None:
				self._PRW_batch.unset_context(context = 'pk_vaccine')
				self._PNL_indications.enable_all()
			else:
				self._PRW_batch.set_context(context = 'pk_vaccine', val = vaccine['pk_vaccine'])
				self._PNL_indications.clear_all()
				self._PNL_indications.select(indications = vaccine['indications'])
				self._PNL_indications.disable_all()
	#----------------------------------------------------------------
	def _on_PRW_reaction_lost_focus(self):
		if self._PRW_reaction.GetValue().strip() == u'':
			self._BTN_report.Enable(False)
		else:
			self._BTN_report.Enable(True)
	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):

		has_errors = False

		if not self._PRW_date_given.is_valid_timestamp(allow_empty = False):
			has_errors = True

		vaccine = self._PRW_vaccine.GetData(as_instance = True)

		# we are editing, require vaccine rather than indications
		if self.mode == u'edit':
			if vaccine is None:
				has_errors = True
				self._PRW_vaccine.display_as_valid(False)
			else:
				self._PRW_vaccine.display_as_valid(True)
				self._PNL_indications.clear_all()
				self._PNL_indications.select(indications = vaccine['indications'])
				self._PNL_indications.disable_all()
		# we are creating, allow either vaccine or indications
		else:
			if vaccine is None:
				if self._PNL_indications.has_selection:
					self._PRW_vaccine.display_as_valid(True)
				else:
					has_errors = True
					self._PRW_vaccine.display_as_valid(False)
			else:
				self._PRW_vaccine.display_as_valid(True)

		if self._PRW_batch.GetValue().strip() == u'':
			has_errors = True
			self._PRW_batch.display_as_valid(False)
		else:
			self._PRW_batch.display_as_valid(True)

		if self._PRW_episode.GetValue().strip() == u'':
			self._PRW_episode.SetText(value = _('prevention'))

		return (has_errors is False)
	#----------------------------------------------------------------
	def _save_as_new(self):

		vaccine = self._PRW_vaccine.GetData()
		if vaccine is None:
			data = self.__save_new_from_indications()
		else:
			data = self.__save_new_from_vaccine(vaccine = vaccine)

		# must be done very late or else the property access
		# will refresh the display such that later field
		# access will return empty values
		self.data = data

		return True
	#----------------------------------------------------------------
	def __save_new_from_indications(self):

		inds = self._PNL_indications.selected_indications
		vaccine = gmVaccination.map_indications2generic_vaccine(indications = inds)

		if vaccine is None:
			for ind in inds:
				vaccine = gmVaccination.map_indications2generic_vaccine(indications = [ind])
				data = self.__save_new_from_vaccine(vaccine = vaccine['pk_vaccine'])
		else:
			data = self.__save_new_from_vaccine(vaccine = vaccine['pk_vaccine'])

		return data
	#----------------------------------------------------------------
	def __save_new_from_vaccine(self, vaccine=None):

		emr = gmPerson.gmCurrentPatient().get_emr()

		data = emr.add_vaccination (
			episode = self._PRW_episode.GetData(can_create = True, is_open = False),
			vaccine = vaccine,
			batch_no = self._PRW_batch.GetValue().strip()
		)

		if self._CHBOX_anamnestic.GetValue() is True:
			data['soap_cat'] = u's'
		else:
			data['soap_cat'] = u'p'

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
			self.data['soap_cat'] = u's'
		else:
			self.data['soap_cat'] = u'p'

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
		self._PRW_vaccine.SetText(value = u'', data = None, suppress_smarts = True)

		self._PNL_indications.clear_all()
		self._PRW_batch.unset_context(context = 'pk_vaccine')
		self._PRW_batch.SetValue(u'')

		self._PRW_episode.SetText(value = u'', data = None, suppress_smarts = True)
		self._PRW_site.SetValue(u'')
		self._PRW_provider.SetData(data = None)
		self._PRW_reaction.SetText(value = u'', data = None, suppress_smarts = True)
		self._BTN_report.Enable(False)
		self._TCTRL_comment.SetValue(u'')

		self._PRW_date_given.SetFocus()
	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		self._PRW_date_given.SetText(data = self.data['date_given'])
		if self.data['soap_cat'] == u's':
			self._CHBOX_anamnestic.SetValue(True)
		else:
			self._CHBOX_anamnestic.SetValue(False)
		self._PRW_vaccine.SetText(value = self.data['vaccine'], data = self.data['pk_vaccine'])

		self._PNL_indications.clear_all()
		self._PNL_indications.select(indications = self.data['indications'])
		self._PNL_indications.disable_all()

		self._PRW_batch.SetValue(self.data['batch_no'])
		self._PRW_episode.SetData(data = self.data['pk_episode'])
		self._PRW_site.SetValue(gmTools.coalesce(self.data['site'], u''))
		self._PRW_provider.SetData(self.data['pk_provider'])
		self._PRW_reaction.SetValue(gmTools.coalesce(self.data['reaction'], u''))
		if self.data['reaction'] is None:
			self._BTN_report.Enable(False)
		else:
			self._BTN_report.Enable(True)
		self._TCTRL_comment.SetValue(gmTools.coalesce(self.data['comment'], u''))

		self._PRW_date_given.SetFocus()
	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._PRW_date_given.SetText(data = self.data['date_given'])
		#self._CHBOX_anamnestic.SetValue(False)
		self._PRW_vaccine.SetText(value = self.data['vaccine'], data = self.data['pk_vaccine'])

		self._PNL_indications.clear_all()
		self._PNL_indications.select(indications = self.data['indications'])
		self._PNL_indications.disable_all()

		self._PRW_batch.set_context(context = 'pk_vaccine', val = self.data['pk_vaccine'])
		self._PRW_batch.SetValue(u'')

		self._PRW_episode.SetData(data = self.data['pk_episode'])
		self._PRW_site.SetValue(gmTools.coalesce(self.data['site'], u''))
		self._PRW_provider.SetData(self.data['pk_provider'])
		self._PRW_reaction.SetValue(u'')
		self._BTN_report.Enable(False)
		self._TCTRL_comment.SetValue(u'')

		self._PRW_date_given.SetFocus()
	#----------------------------------------------------------------
	# event handlers
	#----------------------------------------------------------------
	def _on_report_button_pressed(self, event):

		event.Skip()

		dbcfg = gmCfg.cCfgSQL()

		url = dbcfg.get2 (
			option = u'external.urls.report_vaccine_ADR',
			workplace = gmSurgery.gmCurrentPractice().active_workplace,
			bias = u'user',
			default = u'http://www.pei.de/cln_042/SharedDocs/Downloads/fachkreise/uaw/meldeboegen/b-ifsg-meldebogen,templateId=raw,property=publicationFile.pdf/b-ifsg-meldebogen.pdf'
		)

		if url.strip() == u'':
			url = dbcfg.get2 (
				option = u'external.urls.report_ADR',
				workplace = gmSurgery.gmCurrentPractice().active_workplace,
				bias = u'user'
			)

		webbrowser.open(url = url, new = False, autoraise = True)
	#----------------------------------------------------------------
	def _on_add_vaccine_button_pressed(self, event):
		edit_vaccine(parent = self, vaccine = None, single_entry = False)
		# FIXME: could set newly generated vaccine here
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
		gmDispatcher.connect(signal= u'post_patient_selection', receiver=self._schedule_data_reget)
		gmDispatcher.connect(signal= u'vaccinations_updated', receiver=self._schedule_data_reget)
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
		emr = self.__pat.get_emr()
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

		emr = self.__pat.get_emr()

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
		print "vaccinated indications took", time.time()-t1, "seconds"

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
		print "active schedules took", time.time()-t1, "seconds"

		t1 = time.time()
		# populate missing-shots list
		missing_shots = emr.get_missing_vaccinations()
		print "getting missing shots took", time.time()-t1, "seconds"
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
		print "displaying missing shots took", time.time()-t1, "seconds"

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

	if sys.argv[1] != u'test':
		sys.exit()

	app = wx.PyWidgetTester(size = (600, 600))
	app.SetWidget(cATCPhraseWheel, -1)
	app.MainLoop()
#======================================================================

