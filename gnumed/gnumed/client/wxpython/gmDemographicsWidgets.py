"""Widgets dealing with patient demographics."""
#============================================================
__version__ = "$Revision: 1.175 $"
__author__ = "R.Terry, SJ Tan, I Haywood, Carlos Moro <cfmoro1976@yahoo.es>"
__license__ = 'GPL (details at http://www.gnu.org)'

# standard library
import time, string, sys, os, datetime as pyDT, csv, codecs, re as regex, psycopg2, logging


import wx
import wx.wizard


# GNUmed specific
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmDispatcher, gmI18N, gmMatchProvider, gmPG2, gmTools, gmCfg
from Gnumed.pycommon import gmDateTime, gmShellAPI
from Gnumed.business import gmDemographicRecord, gmPerson, gmSurgery
from Gnumed.wxpython import gmPlugin, gmPhraseWheel, gmGuiHelpers, gmDateTimeInput
from Gnumed.wxpython import gmRegetMixin, gmDataMiningWidgets, gmListWidgets, gmEditArea
from Gnumed.wxpython import gmAuthWidgets, gmCfgWidgets
from Gnumed.wxGladeWidgets import wxgGenericAddressEditAreaPnl, wxgPersonContactsManagerPnl, wxgPersonIdentityManagerPnl
from Gnumed.wxGladeWidgets import wxgCommChannelEditAreaPnl, wxgExternalIDEditAreaPnl


# constant defs
_log = logging.getLogger('gm.ui')


try:
	_('dummy-no-need-to-translate-but-make-epydoc-happy')
except NameError:
	_ = lambda x:x

#============================================================
# country related widgets / functions
#============================================================
def configure_default_country(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	countries = gmDemographicRecord.get_countries()

	gmCfgWidgets.configure_string_from_list_option (
		parent = parent,
		message = _('Select the default country for new persons.\n'),
		option = 'person.create.default_country',
		bias = 'user',
		choices = [ (c['l10n_country'], c['code']) for c in countries ],
		columns = [_('Country'), _('Code')],
		data = [ c['name'] for c in countries ]
	)
#============================================================
class cCountryPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)

		context = {
			u'ctxt_zip': {
				u'where_part': u'and zip ilike %(zip)s',
				u'placeholder': u'zip'
			}
		}
		query = u"""
select code, name from (
	select distinct on (code, name) code, (name || ' (' || code || ')') as name, rank from (

-- localized to user

			select
				code_country as code, l10n_country as name, 1 as rank
			from dem.v_zip2data
			where
				l10n_country %(fragment_condition)s
				%(ctxt_zip)s

		union all

			select
				code as code, _(name) as name, 2 as rank
			from dem.country
			where
				_(name) %(fragment_condition)s

		union all

-- non-localized

			select
				code_country as code, country as name, 3 as rank
			from dem.v_zip2data
			where
				country %(fragment_condition)s
				%(ctxt_zip)s

		union all

			select
				code as code, name as name, 4 as rank
			from dem.country
			where
				name %(fragment_condition)s

		union all

-- abbreviation

			select
				code as code, name as name, 5 as rank
			from dem.country
			where
				code %(fragment_condition)s

	) as q2
) as q1 order by rank, name limit 25"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query, context=context)
		mp.setThresholds(2, 5, 9)
		self.matcher = mp

		self.unset_context(context = u'zip')
		self.SetToolTipString(_('Type or select a country.'))
		self.capitalisation_mode = gmTools.CAPS_FIRST
		self.selection_only = True

#============================================================
# province related widgets / functions
#============================================================
def configure_default_region(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	provs = gmDemographicRecord.get_provinces()

	gmCfgWidgets.configure_string_from_list_option (
		parent = parent,
		message = _('Select the default region/province/state/territory for new persons.\n'),
		option = 'person.create.default_region',
		bias = 'user',
		choices = [ (p['l10n_country'], p['l10n_state'], p['code_state']) for p in provs ],
		columns = [_('Country'), _('Region'), _('Code')],
		data = [ p['state'] for p in provs ]
	)
#============================================================
def edit_province(parent=None, province=None):
	ea = cProvinceEAPnl(parent = parent, id = -1, province = province)
	dlg = gmEditArea.cGenericEditAreaDlg2(parent = parent, id = -1, edit_area = ea, single_entry = (province is not None))
	dlg.SetTitle(gmTools.coalesce(province, _('Adding province'), _('Editing province')))
	result = dlg.ShowModal()
	dlg.Destroy()
	return (result == wx.ID_OK)
#============================================================
def delete_province(parent=None, province=None):

	msg = _(
		'Are you sure you want to delete this province ?\n'
		'\n'
		'Deletion will only work if this province is not\n'
		'yet in use in any patient addresses.'
	)

	tt = _(
		'Also delete any towns/cities/villages known\n'
		'to be situated in this state as long as\n'
		'no patients are recorded to live there.'
	)

	dlg = gmGuiHelpers.c2ButtonQuestionDlg (
		parent,
		-1,
		caption = _('Deleting province'),
		question = msg,
		show_checkbox = True,
		checkbox_msg = _('delete related townships'),
		checkbox_tooltip = tt,
		button_defs = [
			{'label': _('Yes, delete'), 'tooltip': _('Delete province and possibly related townships.'), 'default': False},
			{'label': _('No'), 'tooltip': _('No, do NOT delete anything.'), 'default': True}
		]
	)

	decision = dlg.ShowModal()
	if decision != wx.ID_YES:
		dlg.Destroy()
		return False

	include_urbs = dlg.checkbox_is_checked()
	dlg.Destroy()

	return gmDemographicRecord.delete_province(province = province, delete_urbs = include_urbs)
#============================================================
def manage_provinces(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#------------------------------------------------------------
	def delete(province=None):
		return delete_province(parent = parent, province = province['pk_state'])
	#------------------------------------------------------------
	def edit(province=None):
		return edit_province(parent = parent, province = province)
	#------------------------------------------------------------
	def refresh(lctrl):
		wx.BeginBusyCursor()
		provinces = gmDemographicRecord.get_provinces()
		lctrl.set_string_items([ (p['l10n_country'], p['l10n_state']) for p in provinces ])
		lctrl.set_data(provinces)
		wx.EndBusyCursor()
	#------------------------------------------------------------
	msg = _(
		'\n'
		'This list shows the provinces known to GNUmed.\n'
		'\n'
		'In your jurisdiction "province" may correspond to either of "state",\n'
		'"county", "region", "territory", or some such term.\n'
		'\n'
		'Select the province you want to edit !\n'
	)

	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = msg,
		caption = _('Editing provinces ...'),
		columns = [_('Country'), _('Province')],
		single_selection = True,
		new_callback = edit,
		#edit_callback = edit,
		delete_callback = delete,
		refresh_callback = refresh
	)
#============================================================
class cStateSelectionPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)

		context = {
			u'ctxt_country_name': {
				u'where_part': u'and l10n_country ilike %(country_name)s or country ilike %(country_name)s',
				u'placeholder': u'country_name'
			},
			u'ctxt_zip': {
				u'where_part': u'and zip ilike %(zip)s',
				u'placeholder': u'zip'
			},
			u'ctxt_country_code': {
				u'where_part': u'and country in (select code from dem.country where _(name) ilike %(country_name)s or name ilike %(country_name)s)',
				u'placeholder': u'country_name'
			}
		}

		query = u"""
select code, name from (
	select distinct on (name) code, name, rank from (
			-- 1: find states based on name, context: zip and country name
			select
				code_state as code, state as name, 1 as rank
			from dem.v_zip2data
			where
				state %(fragment_condition)s
				%(ctxt_country_name)s
				%(ctxt_zip)s

		union all

			-- 2: find states based on code, context: zip and country name
			select
				code_state as code, state as name, 2 as rank
			from dem.v_zip2data
			where
				code_state %(fragment_condition)s
				%(ctxt_country_name)s
				%(ctxt_zip)s

		union all

			-- 3: find states based on name, context: country
			select
				code as code, name as name, 3 as rank
			from dem.state
			where
				name %(fragment_condition)s
				%(ctxt_country_code)s

		union all

			-- 4: find states based on code, context: country
			select
				code as code, name as name, 3 as rank
			from dem.state
			where
				code %(fragment_condition)s
				%(ctxt_country_code)s

	) as q2
) as q1 order by rank, name limit 50"""

		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query, context=context)
		mp.setThresholds(2, 5, 6)
		mp.word_separators = u'[ \t]+'
		self.matcher = mp

		self.unset_context(context = u'zip')
		self.unset_context(context = u'country_name')
		self.SetToolTipString(_('Type or select a state/region/province/territory.'))
		self.capitalisation_mode = gmTools.CAPS_FIRST
		self.selection_only = True
#====================================================================
from Gnumed.wxGladeWidgets import wxgProvinceEAPnl

class cProvinceEAPnl(wxgProvinceEAPnl.wxgProvinceEAPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwargs):

		try:
			data = kwargs['province']
			del kwargs['province']
		except KeyError:
			data = None

		wxgProvinceEAPnl.wxgProvinceEAPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		self.mode = 'new'
		self.data = data
		if data is not None:
			self.mode = 'edit'

		self.__init_ui()
	#----------------------------------------------------------------
	def __init_ui(self):
		self._PRW_province.selection_only = False
	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):

		validity = True

		if self._PRW_province.GetData() is None:
			if self._PRW_province.GetValue().strip() == u'':
				validity = False
				self._PRW_province.display_as_valid(False)
			else:
				self._PRW_province.display_as_valid(True)
		else:
			self._PRW_province.display_as_valid(True)

		if self._PRW_province.GetData() is None:
			if self._TCTRL_code.GetValue().strip() == u'':
				validity = False
				self._TCTRL_code.SetBackgroundColour(gmPhraseWheel.color_prw_invalid)
			else:
				self._TCTRL_code.SetBackgroundColour(gmPhraseWheel.color_prw_valid)

		if self._PRW_country.GetData() is None:
			validity = False
			self._PRW_country.display_as_valid(False)
		else:
			self._PRW_country.display_as_valid(True)

		return validity
	#----------------------------------------------------------------
	def _save_as_new(self):
		gmDemographicRecord.create_province (
			name = self._PRW_province.GetValue().strip(),
			code = self._TCTRL_code.GetValue().strip(),
			country = self._PRW_country.GetData()
		)

		# EA is refreshed automatically after save, so need this ...
		self.data = {
			'l10n_state' : self._PRW_province.GetValue().strip(),
			'code_state' : self._TCTRL_code.GetValue().strip(),
			'l10n_country' : self._PRW_country.GetValue().strip()
		}

		return True
	#----------------------------------------------------------------
	def _save_as_update(self):
		# update self.data and save the changes
		#self.data[''] = 
		#self.data[''] = 
		#self.data[''] = 
		#self.data.save()

		# do nothing for now (IOW, don't support updates)
		return True
	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._PRW_province.SetText()
		self._TCTRL_code.SetValue(u'')
		self._PRW_country.SetText()

		self._PRW_province.SetFocus()
	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		self._PRW_province.SetText(self.data['l10n_state'], self.data['code_state'])
		self._TCTRL_code.SetValue(self.data['code_state'])
		self._PRW_country.SetText(self.data['l10n_country'], self.data['code_country'])

		self._PRW_province.SetFocus()
	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._PRW_province.SetText()
		self._TCTRL_code.SetValue(u'')
		self._PRW_country.SetText(self.data['l10n_country'], self.data['code_country'])

		self._PRW_province.SetFocus()
#============================================================
#============================================================
class cKOrganizerSchedulePnl(gmDataMiningWidgets.cPatientListingPnl):

	def __init__(self, *args, **kwargs):

		kwargs['message'] = _("Today's KOrganizer appointments ...")
		kwargs['button_defs'] = [
			{'label': _('Reload'), 'tooltip': _('Reload appointments from KOrganizer')},
			{'label': u''},
			{'label': u''},
			{'label': u''},
			{'label': u'KOrganizer', 'tooltip': _('Launch KOrganizer')}
		]
		gmDataMiningWidgets.cPatientListingPnl.__init__(self, *args, **kwargs)

		self.fname = os.path.expanduser(os.path.join('~', '.gnumed', 'tmp', 'korganizer2gnumed.csv'))
		self.reload_cmd = 'konsolekalendar --view --export-type csv --export-file %s' % self.fname

	#--------------------------------------------------------
	def _on_BTN_1_pressed(self, event):
		"""Reload appointments from KOrganizer."""
		self.reload_appointments()
	#--------------------------------------------------------
	def _on_BTN_5_pressed(self, event):
		"""Reload appointments from KOrganizer."""
		found, cmd = gmShellAPI.detect_external_binary(binary = 'korganizer')

		if not found:
			gmDispatcher.send(signal = 'statustext', msg = _('KOrganizer is not installed.'), beep = True)
			return

		gmShellAPI.run_command_in_shell(command = cmd, blocking = False)
	#--------------------------------------------------------
	def reload_appointments(self):
		try: os.remove(self.fname)
		except OSError: pass
		gmShellAPI.run_command_in_shell(command=self.reload_cmd, blocking=True)
		try:
			csv_file = codecs.open(self.fname , mode = 'rU', encoding = 'utf8', errors = 'replace')
		except IOError:
			gmDispatcher.send(signal = u'statustext', msg = _('Cannot access KOrganizer transfer file [%s]') % self.fname, beep = True)
			return

		csv_lines = gmTools.unicode_csv_reader (
			csv_file,
			delimiter = ','
		)
		# start_date, start_time, end_date, end_time, title (patient), ort, comment, UID
		self._LCTRL_items.set_columns ([
			_('Place'),
			_('Start'),
			u'',
			u'',
			_('Patient'),
			_('Comment')
		])
		items = []
		data = []
		for line in csv_lines:
			items.append([line[5], line[0], line[1], line[3], line[4], line[6]])
			data.append([line[4], line[7]])

		self._LCTRL_items.set_string_items(items = items)
		self._LCTRL_items.set_column_widths()
		self._LCTRL_items.set_data(data = data)
		self._LCTRL_items.patient_key = 0
	#--------------------------------------------------------
	# notebook plugins API
	#--------------------------------------------------------
	def repopulate_ui(self):
		self.reload_appointments()
#============================================================
def edit_occupation():

	pat = gmPerson.gmCurrentPatient()
	curr_jobs = pat.get_occupations()
	if len(curr_jobs) > 0:
		old_job = curr_jobs[0]['l10n_occupation']
		update = curr_jobs[0]['modified_when'].strftime('%m/%Y')
	else:
		old_job = u''
		update = u''

	msg = _(
		'Please enter the primary occupation of the patient.\n'
		'\n'
		'Currently recorded:\n'
		'\n'
		' %s (last updated %s)'
	) % (old_job, update)

	new_job = wx.GetTextFromUser (
		message = msg,
		caption = _('Editing primary occupation'),
		default_value = old_job,
		parent = None
	)
	if new_job.strip() == u'':
		return

	for job in curr_jobs:
		# unlink all but the new job
		if job['l10n_occupation'] != new_job:
			pat.unlink_occupation(occupation = job['l10n_occupation'])
	# and link the new one
	pat.link_occupation(occupation = new_job)
#============================================================
def disable_identity(identity=None):
	# ask user for assurance
	go_ahead = gmGuiHelpers.gm_show_question (
		_('Are you sure you really, positively want\n'
		  'to disable the following person ?\n'
		  '\n'
		  ' %s %s %s\n'
		  ' born %s\n'
		  '\n'
		  '%s\n'
		) % (
			identity['firstnames'],
			identity['lastnames'],
			identity['gender'],
			identity['dob'],
			gmTools.bool2subst (
				identity.is_patient,
				_('This patient DID receive care.'),
				_('This person did NOT receive care.')
			)
		),
		_('Disabling person')
	)
	if not go_ahead:
		return True

	# get admin connection
	conn = gmAuthWidgets.get_dbowner_connection (
		procedure = _('Disabling patient')
	)
	# - user cancelled
	if conn is False:
		return True
	# - error
	if conn is None:
		return False

	# now disable patient
	gmPG2.run_rw_queries(queries = [{'cmd': u"update dem.identity set deleted=True where pk=%s", 'args': [identity['pk_identity']]}])

	return True
#============================================================
# address phrasewheels and widgets
#============================================================
class cPersonAddressesManagerPnl(gmListWidgets.cGenericListManagerPnl):
	"""A list for managing a person's addresses.

	Does NOT act on/listen to the current patient.
	"""
	def __init__(self, *args, **kwargs):

		try:
			self.__identity = kwargs['identity']
			del kwargs['identity']
		except KeyError:
			self.__identity = None

		gmListWidgets.cGenericListManagerPnl.__init__(self, *args, **kwargs)

		self.new_callback = self._add_address
		self.edit_callback = self._edit_address
		self.delete_callback = self._del_address
		self.refresh_callback = self.refresh

		self.__init_ui()
		self.refresh()
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def refresh(self, *args, **kwargs):
		if self.__identity is None:
			self._LCTRL_items.set_string_items()
			return

		adrs = self.__identity.get_addresses()
		self._LCTRL_items.set_string_items (
			items = [ [
					a['l10n_address_type'],
					a['street'],
					gmTools.coalesce(a['notes_street'], u''),
					a['number'],
					gmTools.coalesce(a['subunit'], u''),
					a['postcode'],
					a['urb'],
					gmTools.coalesce(a['suburb'], u''),
					a['l10n_state'],
					a['l10n_country'],
					gmTools.coalesce(a['notes_subunit'], u'')
				] for a in adrs
			]
		)
		self._LCTRL_items.set_column_widths()
		self._LCTRL_items.set_data(data = adrs)
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __init_ui(self):
		self._LCTRL_items.SetToolTipString(_('List of known addresses.'))
		self._LCTRL_items.set_columns(columns = [
			_('Type'),
			_('Street'),
			_('Street info'),
			_('Number'),
			_('Subunit'),
			_('Postal code'),
			_('Place'),
			_('Suburb'),
			_('Region'),
			_('Country'),
			_('Comment')
		])
	#--------------------------------------------------------
	def _add_address(self):
		ea = cAddressEditAreaPnl(self, -1)
		ea.identity = self.__identity
		dlg = gmEditArea.cGenericEditAreaDlg(self, -1, edit_area = ea)
		dlg.SetTitle(_('Adding new address'))
		if dlg.ShowModal() == wx.ID_OK:
			return True
		return False
	#--------------------------------------------------------
	def _edit_address(self, address):
		ea = cAddressEditAreaPnl(self, -1, address = address)
		ea.identity = self.__identity
		dlg = gmEditArea.cGenericEditAreaDlg(self, -1, edit_area = ea)
		dlg.SetTitle(_('Editing address'))
		if dlg.ShowModal() == wx.ID_OK:
			# did we add an entirely new address ?
			# if so then unlink the old one as implied by "edit"
			if ea.address['pk_address'] != address['pk_address']:
				self.__identity.unlink_address(address = address)
			return True
		return False
	#--------------------------------------------------------
	def _del_address(self, address):
		go_ahead = gmGuiHelpers.gm_show_question (
			_(	'Are you sure you want to remove this\n'
				"address from the patient's addresses ?\n"
				'\n'
				'The address itself will not be deleted\n'
				'but it will no longer be associated with\n'
				'this patient.'
			),
			_('Removing address')
		)
		if not go_ahead:
			return False
		self.__identity.unlink_address(address = address)
		return True
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_identity(self):
		return self.__identity

	def _set_identity(self, identity):
		self.__identity = identity
		self.refresh()

	identity = property(_get_identity, _set_identity)
#============================================================
class cPersonContactsManagerPnl(wxgPersonContactsManagerPnl.wxgPersonContactsManagerPnl):
	"""A panel for editing contact data for a person.

	- provides access to:
	  - addresses
	  - communication paths

	Does NOT act on/listen to the current patient.
	"""
	def __init__(self, *args, **kwargs):

		wxgPersonContactsManagerPnl.wxgPersonContactsManagerPnl.__init__(self, *args, **kwargs)

		self.__identity = None
		self.refresh()
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def refresh(self):
		self._PNL_addresses.identity = self.__identity
		self._PNL_comms.identity = self.__identity
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_identity(self):
		return self.__identity

	def _set_identity(self, identity):
		self.__identity = identity
		self.refresh()

	identity = property(_get_identity, _set_identity)
#============================================================
class cAddressEditAreaPnl(wxgGenericAddressEditAreaPnl.wxgGenericAddressEditAreaPnl):
	"""An edit area for editing/creating an address.

	Does NOT act on/listen to the current patient.
	"""
	def __init__(self, *args, **kwargs):
		try:
			self.address = kwargs['address']
			del kwargs['address']
		except KeyError:
			self.address = None

		wxgGenericAddressEditAreaPnl.wxgGenericAddressEditAreaPnl.__init__(self, *args, **kwargs)

		self.identity = None

		self.__register_interests()
		self.refresh()
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def refresh(self, address = None):
		if address is not None:
			self.address = address

		if self.address is not None:
			self._PRW_type.SetText(self.address['l10n_address_type'])
			self._PRW_zip.SetText(self.address['postcode'])
			self._PRW_street.SetText(self.address['street'], data = self.address['street'])
			self._TCTRL_notes_street.SetValue(gmTools.coalesce(self.address['notes_street'], ''))
			self._TCTRL_number.SetValue(self.address['number'])
			self._TCTRL_subunit.SetValue(gmTools.coalesce(self.address['subunit'], ''))
			self._PRW_suburb.SetText(gmTools.coalesce(self.address['suburb'], ''))
			self._PRW_urb.SetText(self.address['urb'], data = self.address['urb'])
			self._PRW_state.SetText(self.address['l10n_state'], data = self.address['code_state'])
			self._PRW_country.SetText(self.address['l10n_country'], data = self.address['code_country'])
			self._TCTRL_notes_subunit.SetValue(gmTools.coalesce(self.address['notes_subunit'], ''))
		# FIXME: clear fields
#		else:
#			pass
	#--------------------------------------------------------
	def save(self):
		"""Links address to patient, creating new address if necessary"""

		if not self.__valid_for_save():
			return False

		# link address to patient
		try:
			adr = self.identity.link_address (
				number = self._TCTRL_number.GetValue().strip(),
				street = self._PRW_street.GetValue().strip(),
				postcode = self._PRW_zip.GetValue().strip(),
				urb = self._PRW_urb.GetValue().strip(),
				state = self._PRW_state.GetData(),
				country = self._PRW_country.GetData(),
				subunit = gmTools.none_if(self._TCTRL_subunit.GetValue().strip(), u''),
				suburb = gmTools.none_if(self._PRW_suburb.GetValue().strip(), u''),
				id_type = self._PRW_type.GetData()
			)
		except:
			_log.exception('cannot save address')
			gmGuiHelpers.gm_show_error (
				_('Cannot save address.\n\n'
				  'Does the state [%s]\n'
				  'exist in country [%s] ?'
				) % (
					self._PRW_state.GetValue().strip(),
					self._PRW_country.GetValue().strip()
				),
				_('Saving address')
			)
			return False

		notes = self._TCTRL_notes_street.GetValue().strip()
		if notes != u'':
			adr['notes_street'] = notes
		notes = self._TCTRL_notes_subunit.GetValue().strip()
		if notes != u'':
			adr['notes_subunit'] = notes
		adr.save_payload()

		self.address = adr

		return True
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		self._PRW_zip.add_callback_on_lose_focus(self._on_zip_set)
		self._PRW_country.add_callback_on_lose_focus(self._on_country_set)
	#--------------------------------------------------------
	def _on_zip_set(self):
		"""Set the street, town, state and country according to entered zip code."""
		zip_code = self._PRW_zip.GetValue()
		if zip_code.strip() == u'':
			self._PRW_street.unset_context(context = u'zip')
			self._PRW_urb.unset_context(context = u'zip')
			self._PRW_state.unset_context(context = u'zip')
			self._PRW_country.unset_context(context = u'zip')
		else:
			self._PRW_street.set_context(context = u'zip', val = zip_code)
			self._PRW_urb.set_context(context = u'zip', val = zip_code)
			self._PRW_state.set_context(context = u'zip', val = zip_code)
			self._PRW_country.set_context(context = u'zip', val = zip_code)
	#--------------------------------------------------------
	def _on_country_set(self):
		"""Set the states according to entered country."""
		country = self._PRW_country.GetData()
		if country is None:
			self._PRW_state.unset_context(context = 'country')
		else:
			self._PRW_state.set_context(context = 'country', val = country)
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __valid_for_save(self):

		# validate required fields
		is_any_field_filled = False

		required_fields = (
			self._PRW_type,
			self._PRW_zip,
			self._PRW_street,
			self._TCTRL_number,
			self._PRW_urb
		)
		for field in required_fields:
			if len(field.GetValue().strip()) == 0:
				if is_any_field_filled:
					field.SetBackgroundColour('pink')
					field.SetFocus()
					field.Refresh()
					gmGuiHelpers.gm_show_error (
						_('Address details must be filled in completely or not at all.'),
						_('Saving contact data')
					)
					return False
			else:
				is_any_field_filled = True
				field.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
				field.Refresh()

		required_fields = (
			self._PRW_state,
			self._PRW_country
		)
		for field in required_fields:
			if field.GetData() is None:
				if is_any_field_filled:
					field.SetBackgroundColour('pink')
					field.SetFocus()
					field.Refresh()
					gmGuiHelpers.gm_show_error (
						_('Address details must be filled in completely or not at all.'),
						_('Saving contact data')
					)
					return False
			else:
				is_any_field_filled = True
				field.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
				field.Refresh()

		return True
#============================================================
class cAddressMatchProvider(gmMatchProvider.cMatchProvider_SQL2):

	def __init__(self):

		query = u"""
select * from (
	(select
		pk_address,
		(street || ' ' || number || coalesce(' (' || subunit || ')', '') || ', '
		|| urb || coalesce(' (' || suburb || ')', '') || ', '
		|| postcode
		|| coalesce(', ' || notes_street, '')
		|| coalesce(', ' || notes_subunit, '')
		) as address
	from
		dem.v_address
	where
		street %(fragment_condition)s

	) union (

	select
		pk_address,
		(street || ' ' || number || coalesce(' (' || subunit || ')', '') || ', '
		|| urb || coalesce(' (' || suburb || ')', '') || ', '
		|| postcode
		|| coalesce(', ' || notes_street, '')
		|| coalesce(', ' || notes_subunit, '')
		) as address
	from
		dem.v_address
	where
		postcode_street %(fragment_condition)s

	) union (

	select
		pk_address,
		(street || ' ' || number || coalesce(' (' || subunit || ')', '') || ', '
		|| urb || coalesce(' (' || suburb || ')', '') || ', '
		|| postcode
		|| coalesce(', ' || notes_street, '')
		|| coalesce(', ' || notes_subunit, '')
		) as address
	from
		dem.v_address
	where
		postcode_urb %(fragment_condition)s
	)
) as union_result
order by union_result.address limit 50"""

		gmMatchProvider.cMatchProvider_SQL2.__init__(self, queries = query)

		self.setThresholds(2, 4, 6)
#		self.word_separators = u'[ \t]+'

#============================================================
class cAddressPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		mp = cAddressMatchProvider()
		gmPhraseWheel.cPhraseWheel.__init__ (
			self,
			*args,
			**kwargs
		)
		self.matcher = cAddressMatchProvider()
		self.SetToolTipString(_('Select an address by postcode or street name.'))
		self.selection_only = True
		self.__address = None
		self.__old_pk = None
	#--------------------------------------------------------
	def get_address(self):

		pk = self.GetData()

		if pk is None:
			self.__address = None
			return None

		if self.__address is None:
			self.__old_pk = pk
			self.__address = gmDemographicRecord.cAddress(aPK_obj = pk)
		else:
			if pk != self.__old_pk:
				self.__old_pk = pk
				self.__address = gmDemographicRecord.cAddress(aPK_obj = pk)

		return self.__address
#============================================================
class cAddressTypePhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		query = u"""
select id, type from ((
	select id, _(name) as type, 1 as rank
	from dem.address_type
	where _(name) %(fragment_condition)s
) union (
	select id, name as type, 2 as rank
	from dem.address_type
	where name %(fragment_condition)s
)) as ur
order by
	ur.rank, ur.type
"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query)
		mp.setThresholds(1, 2, 4)
		mp.word_separators = u'[ \t]+'
		gmPhraseWheel.cPhraseWheel.__init__ (
			self,
			*args,
			**kwargs
		)
		self.matcher = mp
		self.SetToolTipString(_('Select the type of address.'))
#		self.capitalisation_mode = gmTools.CAPS_FIRST
		self.selection_only = True
	#--------------------------------------------------------
#	def GetData(self, can_create=False):
#		if self.data is None:
#			if can_create:
#				self.data = gmDocuments.create_document_type(self.GetValue().strip())['pk_doc_type']	# FIXME: error handling
#		return self.data
#============================================================
class cZipcodePhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):
		# FIXME: add possible context
		query = u"""
			(select distinct postcode, postcode from dem.street where postcode %(fragment_condition)s limit 20)
				union
			(select distinct postcode, postcode from dem.urb where postcode %(fragment_condition)s limit 20)"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query)
		mp.setThresholds(2, 3, 15)
		gmPhraseWheel.cPhraseWheel.__init__ (
			self,
			*args,
			**kwargs
		)
		self.SetToolTipString(_("Type or select a zip code (postcode)."))
		self.matcher = mp
#============================================================
class cStreetPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):
		context = {
			u'ctxt_zip': {
				u'where_part': u'and zip ilike %(zip)s',
				u'placeholder': u'zip'
			}
		}
		query = u"""
select s1, s2 from (
	select s1, s2, rank from (
			select distinct on (street)
				street as s1, street as s2, 1 as rank
			from dem.v_zip2data
			where
				street %(fragment_condition)s
				%(ctxt_zip)s

		union all

			select distinct on (name)
				name as s1, name as s2, 2 as rank
			from dem.street
			where
				name %(fragment_condition)s

	) as q2
) as q1 order by rank, s2 limit 50"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query, context=context)
		mp.setThresholds(3, 5, 8)
		gmPhraseWheel.cPhraseWheel.__init__ (
			self,
			*args,
			**kwargs
		)
		self.unset_context(context = u'zip')

		self.SetToolTipString(_('Type or select a street.'))
		self.capitalisation_mode = gmTools.CAPS_FIRST
		self.matcher = mp
#============================================================
class cSuburbPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		query = """
select distinct on (suburb) suburb, suburb
from dem.street
where suburb %(fragment_condition)s
order by suburb
limit 50
"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query)
		mp.setThresholds(2, 3, 6)
		gmPhraseWheel.cPhraseWheel.__init__ (
			self,
			*args,
			**kwargs
		)

		self.SetToolTipString(_('Type or select the suburb.'))
		self.capitalisation_mode = gmTools.CAPS_FIRST
		self.matcher = mp
#============================================================
class cUrbPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):
		context = {
			u'ctxt_zip': {
				u'where_part': u'and zip ilike %(zip)s',
				u'placeholder': u'zip'
			}
		}
		query = u"""
select u1, u2 from (
	select distinct on (rank, u1)
		u1, u2, rank
	from (
			select
				urb as u1, urb as u2, 1 as rank
			from dem.v_zip2data
			where
				urb %(fragment_condition)s
				%(ctxt_zip)s

		union all

			select
				name as u1, name as u2, 2 as rank
			from dem.urb
			where
				name %(fragment_condition)s
	) as union_result
	order by rank, u1
) as distincted_union
limit 50
"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query, context=context)
		mp.setThresholds(3, 5, 7)
		gmPhraseWheel.cPhraseWheel.__init__ (
			self,
			*args,
			**kwargs
		)
		self.unset_context(context = u'zip')

		self.SetToolTipString(_('Type or select a city/town/village/dwelling.'))
		self.capitalisation_mode = gmTools.CAPS_FIRST
		self.matcher = mp
#============================================================
# communications channel related widgets
#============================================================
class cCommChannelTypePhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		query = u"""
select pk, type from ((
	select pk, _(description) as type, 1 as rank
	from dem.enum_comm_types
	where _(description) %(fragment_condition)s
) union (
	select pk, description as type, 2 as rank
	from dem.enum_comm_types
	where description %(fragment_condition)s
)) as ur
order by
	ur.rank, ur.type
"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query)
		mp.setThresholds(1, 2, 4)
		mp.word_separators = u'[ \t]+'
		gmPhraseWheel.cPhraseWheel.__init__ (
			self,
			*args,
			**kwargs
		)
		self.matcher = mp
		self.SetToolTipString(_('Select the type of communications channel.'))
		self.selection_only = True
#------------------------------------------------------------
class cCommChannelEditAreaPnl(wxgCommChannelEditAreaPnl.wxgCommChannelEditAreaPnl):
	"""An edit area for editing/creating a comms channel.

	Does NOT act on/listen to the current patient.
	"""
	def __init__(self, *args, **kwargs):
		try:
			self.channel = kwargs['comm_channel']
			del kwargs['comm_channel']
		except KeyError:
			self.channel = None

		wxgCommChannelEditAreaPnl.wxgCommChannelEditAreaPnl.__init__(self, *args, **kwargs)

		self.identity = None

		self.refresh()
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def refresh(self, comm_channel = None):
		if comm_channel is not None:
			self.channel = comm_channel

		if self.channel is None:
			self._PRW_type.SetText(u'')
			self._TCTRL_url.SetValue(u'')
			self._PRW_address.SetText(value = u'', data = None)
			self._CHBOX_confidential.SetValue(False)
		else:
			self._PRW_type.SetText(self.channel['l10n_comm_type'])
			self._TCTRL_url.SetValue(self.channel['url'])
			self._PRW_address.SetData(data = self.channel['pk_address'])
			self._CHBOX_confidential.SetValue(self.channel['is_confidential'])
	#--------------------------------------------------------
	def save(self):
		"""Links comm channel to patient."""
		if self.channel is None:
			if not self.__valid_for_save():
				return False
			try:
				self.channel = self.identity.link_comm_channel (
					pk_channel_type = self._PRW_type.GetData(),
					url = self._TCTRL_url.GetValue().strip(),
					is_confidential = self._CHBOX_confidential.GetValue(),
				)
			except psycopg2.IntegrityError:
				_log.exception('error saving comm channel')
				gmDispatcher.send(signal = u'statustext', msg = _('Cannot save communications channel.'), beep = True)
				return False
		else:
			comm_type = self._PRW_type.GetValue().strip()
			if comm_type != u'':
				self.channel['comm_type'] = comm_type
			url = self._TCTRL_url.GetValue().strip()
			if url != u'':
				self.channel['url'] = url
			self.channel['is_confidential'] = self._CHBOX_confidential.GetValue()

		self.channel['pk_address'] = self._PRW_address.GetData()
		self.channel.save_payload()

		return True
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __valid_for_save(self):

		no_errors = True

		if self._PRW_type.GetData() is None:
			self._PRW_type.SetBackgroundColour('pink')
			self._PRW_type.SetFocus()
			self._PRW_type.Refresh()
			no_errors = False
		else:
			self._PRW_type.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
			self._PRW_type.Refresh()

		if self._TCTRL_url.GetValue().strip() == u'':
			self._TCTRL_url.SetBackgroundColour('pink')
			self._TCTRL_url.SetFocus()
			self._TCTRL_url.Refresh()
			no_errors = False
		else:
			self._TCTRL_url.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
			self._TCTRL_url.Refresh()

		return no_errors
#------------------------------------------------------------
class cPersonCommsManagerPnl(gmListWidgets.cGenericListManagerPnl):
	"""A list for managing a person's comm channels.

	Does NOT act on/listen to the current patient.
	"""
	def __init__(self, *args, **kwargs):

		try:
			self.__identity = kwargs['identity']
			del kwargs['identity']
		except KeyError:
			self.__identity = None

		gmListWidgets.cGenericListManagerPnl.__init__(self, *args, **kwargs)

		self.new_callback = self._add_comm
		self.edit_callback = self._edit_comm
		self.delete_callback = self._del_comm
		self.refresh_callback = self.refresh

		self.__init_ui()
		self.refresh()
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def refresh(self, *args, **kwargs):
		if self.__identity is None:
			self._LCTRL_items.set_string_items()
			return

		comms = self.__identity.get_comm_channels()
		self._LCTRL_items.set_string_items (
			items = [ [ gmTools.bool2str(c['is_confidential'], u'X', u''), c['l10n_comm_type'], c['url'] ] for c in comms ]
		)
		self._LCTRL_items.set_column_widths()
		self._LCTRL_items.set_data(data = comms)
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __init_ui(self):
		self._LCTRL_items.SetToolTipString(_('List of known communication channels.'))
		self._LCTRL_items.set_columns(columns = [
			_('confidential'),
			_('Type'),
			_('Value')
		])
	#--------------------------------------------------------
	def _add_comm(self):
		ea = cCommChannelEditAreaPnl(self, -1)
		ea.identity = self.__identity
		dlg = gmEditArea.cGenericEditAreaDlg(self, -1, edit_area = ea)
		dlg.SetTitle(_('Adding new communications channel'))
		if dlg.ShowModal() == wx.ID_OK:
			return True
		return False
	#--------------------------------------------------------
	def _edit_comm(self, comm_channel):
		ea = cCommChannelEditAreaPnl(self, -1, comm_channel = comm_channel)
		ea.identity = self.__identity
		dlg = gmEditArea.cGenericEditAreaDlg(self, -1, edit_area = ea)
		dlg.SetTitle(_('Editing communications channel'))
		if dlg.ShowModal() == wx.ID_OK:
			return True
		return False
	#--------------------------------------------------------
	def _del_comm(self, comm):
		go_ahead = gmGuiHelpers.gm_show_question (
			_(	'Are you sure this patient can no longer\n'
				"be contacted via this channel ?"
			),
			_('Removing communication channel')
		)
		if not go_ahead:
			return False
		self.__identity.unlink_comm_channel(comm_channel = comm)
		return True
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_identity(self):
		return self.__identity

	def _set_identity(self, identity):
		self.__identity = identity
		self.refresh()

	identity = property(_get_identity, _set_identity)
#============================================================
# identity widgets
#============================================================
# phrasewheels
#------------------------------------------------------------
class cLastnamePhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):
		query = u"select distinct lastnames, lastnames from dem.names where lastnames %(fragment_condition)s order by lastnames limit 25"
		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query)
		mp.setThresholds(3, 5, 9)
		gmPhraseWheel.cPhraseWheel.__init__ (
			self,
			*args,
			**kwargs
		)
		self.SetToolTipString(_("Type or select a last name (family name/surname)."))
		self.capitalisation_mode = gmTools.CAPS_NAMES
		self.matcher = mp
#------------------------------------------------------------
class cFirstnamePhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):
		query = u"""
			(select distinct firstnames, firstnames from dem.names where firstnames %(fragment_condition)s order by firstnames limit 20)
				union
			(select distinct name, name from dem.name_gender_map where name %(fragment_condition)s order by name limit 20)"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query)
		mp.setThresholds(3, 5, 9)
		gmPhraseWheel.cPhraseWheel.__init__ (
			self,
			*args,
			**kwargs
		)
		self.SetToolTipString(_("Type or select a first name (forename/Christian name/given name)."))
		self.capitalisation_mode = gmTools.CAPS_NAMES
		self.matcher = mp
#------------------------------------------------------------
class cNicknamePhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):
		query = u"""
			(select distinct preferred, preferred from dem.names where preferred %(fragment_condition)s order by preferred limit 20)
				union
			(select distinct firstnames, firstnames from dem.names where firstnames %(fragment_condition)s order by firstnames limit 20)
				union
			(select distinct name, name from dem.name_gender_map where name %(fragment_condition)s order by name limit 20)"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query)
		mp.setThresholds(3, 5, 9)
		gmPhraseWheel.cPhraseWheel.__init__ (
			self,
			*args,
			**kwargs
		)
		self.SetToolTipString(_("Type or select an alias (nick name, preferred name, call name, warrior name, artist name)."))
		# nicknames CAN start with lower case !
		#self.capitalisation_mode = gmTools.CAPS_NAMES
		self.matcher = mp
#------------------------------------------------------------
class cTitlePhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):
		query = u"select distinct title, title from dem.identity where title %(fragment_condition)s"
		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query)
		mp.setThresholds(1, 3, 9)
		gmPhraseWheel.cPhraseWheel.__init__ (
			self,
			*args,
			**kwargs
		)
		self.SetToolTipString(_("Type or select a title. Note that the title applies to the person, not to a particular name !"))
		self.matcher = mp
#------------------------------------------------------------
class cGenderSelectionPhraseWheel(gmPhraseWheel.cPhraseWheel):
	"""Let user select a gender."""

	_gender_map = None

	def __init__(self, *args, **kwargs):

		if cGenderSelectionPhraseWheel._gender_map is None:
			cmd = u"""
				select tag, l10n_label, sort_weight
				from dem.v_gender_labels
				order by sort_weight desc"""
			rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx=True)
			cGenderSelectionPhraseWheel._gender_map = {}
			for gender in rows:
				cGenderSelectionPhraseWheel._gender_map[gender[idx['tag']]] = {
					'data': gender[idx['tag']],
					'label': gender[idx['l10n_label']],
					'weight': gender[idx['sort_weight']]
				}

		mp = gmMatchProvider.cMatchProvider_FixedList(aSeq = cGenderSelectionPhraseWheel._gender_map.values())
		mp.setThresholds(1, 1, 3)

		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.selection_only = True
		self.matcher = mp
		self.picklist_delay = 50
#------------------------------------------------------------
class cOccupationPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):
		query = u"select distinct name, _(name) from dem.occupation where _(name) %(fragment_condition)s"
		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query)
		mp.setThresholds(1, 3, 5)
		gmPhraseWheel.cPhraseWheel.__init__ (
			self,
			*args,
			**kwargs
		)
		self.SetToolTipString(_("Type or select an occupation."))
		self.capitalisation_mode = gmTools.CAPS_FIRST
		self.matcher = mp
#------------------------------------------------------------
class cExternalIDTypePhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):
		query = u"""
select distinct pk, (name || coalesce(' (%s ' || issuer || ')', '')) as label
from dem.enum_ext_id_types
where name %%(fragment_condition)s
order by label limit 25""" % _('issued by')
		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query)
		mp.setThresholds(1, 3, 5)
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.SetToolTipString(_("Enter or select a type for the external ID."))
		self.matcher = mp
#------------------------------------------------------------
class cExternalIDIssuerPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):
		query = u"""
select distinct issuer, issuer
from dem.enum_ext_id_types
where issuer %(fragment_condition)s
order by issuer limit 25"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query)
		mp.setThresholds(1, 3, 5)
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.SetToolTipString(_("Type or select an occupation."))
		self.capitalisation_mode = gmTools.CAPS_FIRST
		self.matcher = mp
#------------------------------------------------------------
# edit areas
#------------------------------------------------------------
class cExternalIDEditAreaPnl(wxgExternalIDEditAreaPnl.wxgExternalIDEditAreaPnl):
	"""An edit area for editing/creating external IDs.

	Does NOT act on/listen to the current patient.
	"""
	def __init__(self, *args, **kwargs):
	
		try:
			self.ext_id = kwargs['external_id']
			del kwargs['external_id']
		except:
			self.ext_id = None

		wxgExternalIDEditAreaPnl.wxgExternalIDEditAreaPnl.__init__(self, *args, **kwargs)

		self.identity = None

		self.__register_events()

		self.refresh()
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def refresh(self, ext_id=None):
		if ext_id is not None:
			self.ext_id = ext_id

		if self.ext_id is not None:
			self._PRW_type.SetText(value = self.ext_id['name'], data = self.ext_id['pk_type'])
			self._TCTRL_value.SetValue(self.ext_id['value'])
			self._PRW_issuer.SetText(self.ext_id['issuer'])
			self._TCTRL_comment.SetValue(gmTools.coalesce(self.ext_id['comment'], u''))
		# FIXME: clear fields
#		else:
#			pass
	#--------------------------------------------------------
	def save(self):

		if not self.__valid_for_save():
			return False

		# strip out " (issued by ...)" added by phrasewheel
		type = regex.split(' \(%s .+\)$' % _('issued by'), self._PRW_type.GetValue().strip(), 1)[0]

		# add new external ID
		if self.ext_id is None:
			self.identity.add_external_id (
				type_name = type,
				value = self._TCTRL_value.GetValue().strip(),
				issuer = gmTools.none_if(self._PRW_issuer.GetValue().strip(), u''),
				comment = gmTools.none_if(self._TCTRL_comment.GetValue().strip(), u'')
			)
		# edit old external ID
		else:
			self.identity.update_external_id (
				pk_id = self.ext_id['pk_id'],
				type = type,
				value = self._TCTRL_value.GetValue().strip(),
				issuer = gmTools.none_if(self._PRW_issuer.GetValue().strip(), u''),
				comment = gmTools.none_if(self._TCTRL_comment.GetValue().strip(), u'')
			)

		return True
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __register_events(self):
		self._PRW_type.add_callback_on_lose_focus(self._on_type_set)
	#--------------------------------------------------------
	def _on_type_set(self):
		"""Set the issuer according to the selected type.

		Matches are fetched from existing records in backend.
		"""
		pk_curr_type = self._PRW_type.GetData()
		if pk_curr_type is None:
			return True
		rows, idx = gmPG2.run_ro_queries(queries = [{
			'cmd': u"select issuer from dem.enum_ext_id_types where pk = %s",
			'args': [pk_curr_type]
		}])
		if len(rows) == 0:
			return True
		wx.CallAfter(self._PRW_issuer.SetText, rows[0][0])
		return True
	#--------------------------------------------------------
	def __valid_for_save(self):

		no_errors = True

		# do not test .GetData() because adding external IDs
		# will create types if necessary
#		if self._PRW_type.GetData() is None:
		if self._PRW_type.GetValue().strip() == u'':
			self._PRW_type.SetBackgroundColour('pink')
			self._PRW_type.SetFocus()
			self._PRW_type.Refresh()
		else:
			self._PRW_type.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
			self._PRW_type.Refresh()

		if self._TCTRL_value.GetValue().strip() == u'':
			self._TCTRL_value.SetBackgroundColour('pink')
			self._TCTRL_value.SetFocus()
			self._TCTRL_value.Refresh()
			no_errors = False
		else:
			self._TCTRL_value.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
			self._TCTRL_value.Refresh()

		return no_errors
#------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgIdentityEAPnl

class cIdentityEAPnl(wxgIdentityEAPnl.wxgIdentityEAPnl, gmEditArea.cGenericEditAreaMixin):
	"""An edit area for editing/creating title/gender/dob/dod etc."""

	def __init__(self, *args, **kwargs):

		try:
			data = kwargs['identity']
			del kwargs['identity']
		except KeyError:
			data = None

		wxgIdentityEAPnl.wxgIdentityEAPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		self.mode = 'new'
		self.data = data
		if data is not None:
			self.mode = 'edit'

#		self.__init_ui()
	#----------------------------------------------------------------
#	def __init_ui(self):
#		# adjust phrasewheels etc
	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):

		has_error = False

		if self._PRW_gender.GetData() is None:
			self._PRW_gender.SetFocus()
			has_error = True

		if not self._PRW_dob.is_valid_timestamp():
			val = self._PRW_dob.GetValue().strip()
			gmDispatcher.send(signal = u'statustext', msg = _('Cannot parse <%s> into proper timestamp.') % val)
			self._PRW_dob.SetBackgroundColour('pink')
			self._PRW_dob.Refresh()
			self._PRW_dob.SetFocus()
			has_error = True
		else:
			self._PRW_dob.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
			self._PRW_dob.Refresh()

		if not self._DP_dod.is_valid_timestamp(allow_none=True):
			gmDispatcher.send(signal = u'statustext', msg = _('Invalid date of death.'))
			self._DP_dod.SetFocus()
			has_error = True

		return (has_error is False)
	#----------------------------------------------------------------
	def _save_as_new(self):
		# save the data as a new instance
#		data = 1

#		data[''] = 1
#		data[''] = 1

#		data.save()

		# must be done very late or else the property access
		# will refresh the display such that later field
		# access will return empty values
#		self.data = data
		return False
		return True
	#----------------------------------------------------------------
	def _save_as_update(self):

		self.data['gender'] = self._PRW_gender.GetData()

		if self._PRW_dob.GetValue().strip() == u'':
			self.data['dob'] = None
		else:
			self.data['dob'] = self._PRW_dob.GetData().get_pydt()

		self.data['title'] = gmTools.none_if(self._PRW_title.GetValue().strip(), u'')
		self.data['deceased'] = self._DP_dod.GetValue(as_pydt = True)
		self.data['comment'] = gmTools.none_if(self._TCTRL_comment.GetValue().strip(), u'')

		self.data.save()
		return True
	#----------------------------------------------------------------
	def _refresh_as_new(self):
		pass
	#----------------------------------------------------------------
	def _refresh_from_existing(self):

		self._LBL_info.SetLabel(u'ID: #%s' % (
			self.data.ID
			# FIXME: add 'deleted' status
		))
		self._PRW_dob.SetText (
			value = self.data.get_formatted_dob(format = '%Y-%m-%d %H:%M', encoding = gmI18N.get_encoding()),
			data = self.data['dob']
		)
		self._DP_dod.SetValue(self.data['deceased'])
		self._PRW_gender.SetData(self.data['gender'])
		#self._PRW_ethnicity.SetValue()
		self._PRW_title.SetText(gmTools.coalesce(self.data['title'], u''))
		self._TCTRL_comment.SetValue(gmTools.coalesce(self.data['comment'], u''))
	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		pass
	#----------------------------------------------------------------

#------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgNameGenderDOBEditAreaPnl

class cNameGenderDOBEditAreaPnl(wxgNameGenderDOBEditAreaPnl.wxgNameGenderDOBEditAreaPnl):
	"""An edit area for editing/creating name/gender/dob.

	Does NOT act on/listen to the current patient.
	"""
	def __init__(self, *args, **kwargs):

		self.__name = kwargs['name']
		del kwargs['name']
		self.__identity = gmPerson.cIdentity(aPK_obj = self.__name['pk_identity'])

		wxgNameGenderDOBEditAreaPnl.wxgNameGenderDOBEditAreaPnl.__init__(self, *args, **kwargs)

		self.__register_interests()
		self.refresh()
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def refresh(self):
		if self.__name is None:
			return

		self._PRW_title.SetText(gmTools.coalesce(self.__name['title'], u''))
		self._PRW_firstname.SetText(self.__name['firstnames'])
		self._PRW_lastname.SetText(self.__name['lastnames'])
		self._PRW_nick.SetText(gmTools.coalesce(self.__name['preferred'], u''))
		self._PRW_dob.SetText (
			value = self.__identity.get_formatted_dob(format = '%Y-%m-%d %H:%M', encoding = gmI18N.get_encoding()),
			data = self.__identity['dob']
		)
		self._PRW_gender.SetData(self.__name['gender'])
		self._CHBOX_active.SetValue(self.__name['active_name'])
		self._DP_dod.SetValue(self.__identity['deceased'])
		self._TCTRL_comment.SetValue(gmTools.coalesce(self.__name['comment'], u''))
		# FIXME: clear fields
#		else:
#			pass
	#--------------------------------------------------------
	def save(self):

		if not self.__valid_for_save():
			return False

		self.__identity['gender'] = self._PRW_gender.GetData()
		if self._PRW_dob.GetValue().strip() == u'':
			self.__identity['dob'] = None
		else:
			self.__identity['dob'] = self._PRW_dob.GetData().get_pydt()
		self.__identity['title'] = gmTools.none_if(self._PRW_title.GetValue().strip(), u'')
		self.__identity['deceased'] = self._DP_dod.GetValue(as_pydt = True)
		self.__identity.save_payload()

		active = self._CHBOX_active.GetValue()
		first = self._PRW_firstname.GetValue().strip()
		last = self._PRW_lastname.GetValue().strip()
		old_nick = self.__name['preferred']

		# is it a new name ?
		old_name = self.__name['firstnames'] + self.__name['lastnames']
		if (first + last) != old_name:
			self.__name = self.__identity.add_name(first, last, active)

		self.__name['active_name'] = active
		self.__name['preferred'] = gmTools.none_if(self._PRW_nick.GetValue().strip(), u'')
		self.__name['comment'] = gmTools.none_if(self._TCTRL_comment.GetValue().strip(), u'')

		self.__name.save_payload()

		return True
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		self._PRW_firstname.add_callback_on_lose_focus(self._on_name_set)
	#--------------------------------------------------------
	def _on_name_set(self):
		"""Set the gender according to entered firstname.

		Matches are fetched from existing records in backend.
		"""
		firstname = self._PRW_firstname.GetValue().strip()
		if firstname == u'':
			return True
		rows, idx = gmPG2.run_ro_queries(queries = [{
			'cmd': u"select gender from dem.name_gender_map where name ilike %s",
			'args': [firstname]
		}])
		if len(rows) == 0:
			return True
		wx.CallAfter(self._PRW_gender.SetData, rows[0][0])
		return True
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __valid_for_save(self):

		has_error = False

		if self._PRW_gender.GetData() is None:
			self._PRW_gender.SetBackgroundColour('pink')
			self._PRW_gender.Refresh()
			self._PRW_gender.SetFocus()
			has_error = True
		else:
			self._PRW_gender.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
			self._PRW_gender.Refresh()

		if not self._PRW_dob.is_valid_timestamp():
			val = self._PRW_dob.GetValue().strip()
			gmDispatcher.send(signal = u'statustext', msg = _('Cannot parse <%s> into proper timestamp.') % val)
			self._PRW_dob.SetBackgroundColour('pink')
			self._PRW_dob.Refresh()
			self._PRW_dob.SetFocus()
			has_error = True
		else:
			self._PRW_dob.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
			self._PRW_dob.Refresh()

		if not self._DP_dod.is_valid_timestamp():
			gmDispatcher.send(signal = u'statustext', msg = _('Invalid date of death.'))
			self._DP_dod.SetBackgroundColour('pink')
			self._DP_dod.Refresh()
			self._DP_dod.SetFocus()
			has_error = True
		else:
			self._DP_dod.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
			self._DP_dod.Refresh()

		if self._PRW_lastname.GetValue().strip() == u'':
			self._PRW_lastname.SetBackgroundColour('pink')
			self._PRW_lastname.Refresh()
			self._PRW_lastname.SetFocus()
			has_error = True
		else:
			self._PRW_lastname.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
			self._PRW_lastname.Refresh()

		if self._PRW_firstname.GetValue().strip() == u'':
			self._PRW_firstname.SetBackgroundColour('pink')
			self._PRW_firstname.Refresh()
			self._PRW_firstname.SetFocus()
			has_error = True
		else:
			self._PRW_firstname.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
			self._PRW_firstname.Refresh()

		return (has_error is False)
#------------------------------------------------------------
# list manager
#------------------------------------------------------------
class cPersonNamesManagerPnl(gmListWidgets.cGenericListManagerPnl):
	"""A list for managing a person's names.

	Does NOT act on/listen to the current patient.
	"""
	def __init__(self, *args, **kwargs):

		try:
			self.__identity = kwargs['identity']
			del kwargs['identity']
		except KeyError:
			self.__identity = None

		gmListWidgets.cGenericListManagerPnl.__init__(self, *args, **kwargs)

		self.new_callback = self._add_name
		self.edit_callback = self._edit_name
		self.delete_callback = self._del_name
		self.refresh_callback = self.refresh

		self.__init_ui()
		self.refresh()
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def refresh(self, *args, **kwargs):
		if self.__identity is None:
			self._LCTRL_items.set_string_items()
			return

		names = self.__identity.get_names()
		self._LCTRL_items.set_string_items (
			items = [ [
					gmTools.bool2str(n['active_name'], 'X', ''),
					n['lastnames'],
					n['firstnames'],
					gmTools.coalesce(n['preferred'], u''),
					gmTools.coalesce(n['comment'], u'')
				] for n in names ]
		)
		self._LCTRL_items.set_column_widths()
		self._LCTRL_items.set_data(data = names)
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __init_ui(self):
		self._LCTRL_items.set_columns(columns = [
			_('Active'),
			_('Lastname'),
			_('Firstname(s)'),
			_('Preferred Name'),
			_('Comment')
		])
	#--------------------------------------------------------
	def _add_name(self):
		ea = cNameGenderDOBEditAreaPnl(self, -1, name = self.__identity.get_active_name())
		dlg = gmEditArea.cGenericEditAreaDlg(self, -1, edit_area = ea)
		dlg.SetTitle(_('Adding new name'))
		if dlg.ShowModal() == wx.ID_OK:
			dlg.Destroy()
			return True
		dlg.Destroy()
		return False
	#--------------------------------------------------------
	def _edit_name(self, name):
		ea = cNameGenderDOBEditAreaPnl(self, -1, name = name)
		dlg = gmEditArea.cGenericEditAreaDlg(self, -1, edit_area = ea)
		dlg.SetTitle(_('Editing name'))
		if dlg.ShowModal() == wx.ID_OK:
			dlg.Destroy()
			return True
		dlg.Destroy()
		return False
	#--------------------------------------------------------
	def _del_name(self, name):

		if len(self.__identity.get_names()) == 1:
			gmDispatcher.send(signal = u'statustext', msg = _('Cannot delete the only name of a person.'), beep = True)
			return False

		go_ahead = gmGuiHelpers.gm_show_question (
			_(	'It is often advisable to keep old names around and\n'
				'just create a new "currently active" name.\n'
				'\n'
				'This allows finding the patient by both the old\n'
				'and the new name (think before/after marriage).\n'
				'\n'
				'Do you still want to really delete\n'
				"this name from the patient ?"
			),
			_('Deleting name')
		)
		if not go_ahead:
			return False

		self.__identity.delete_name(name = name)
		return True
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_identity(self):
		return self.__identity

	def _set_identity(self, identity):
		self.__identity = identity
		self.refresh()

	identity = property(_get_identity, _set_identity)
#------------------------------------------------------------
class cPersonIDsManagerPnl(gmListWidgets.cGenericListManagerPnl):
	"""A list for managing a person's external IDs.

	Does NOT act on/listen to the current patient.
	"""
	def __init__(self, *args, **kwargs):

		try:
			self.__identity = kwargs['identity']
			del kwargs['identity']
		except KeyError:
			self.__identity = None

		gmListWidgets.cGenericListManagerPnl.__init__(self, *args, **kwargs)

		self.new_callback = self._add_id
		self.edit_callback = self._edit_id
		self.delete_callback = self._del_id
		self.refresh_callback = self.refresh

		self.__init_ui()
		self.refresh()
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def refresh(self, *args, **kwargs):
		if self.__identity is None:
			self._LCTRL_items.set_string_items()
			return

		ids = self.__identity.get_external_ids()
		self._LCTRL_items.set_string_items (
			items = [ [
					i['name'],
					i['value'],
					gmTools.coalesce(i['issuer'], u''),
					i['context'],
					gmTools.coalesce(i['comment'], u'')
				] for i in ids
			]
		)
		self._LCTRL_items.set_column_widths()
		self._LCTRL_items.set_data(data = ids)
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __init_ui(self):
		self._LCTRL_items.set_columns(columns = [
			_('ID type'),
			_('Value'),
			_('Issuer'),
			_('Context'),
			_('Comment')
		])
	#--------------------------------------------------------
	def _add_id(self):
		ea = cExternalIDEditAreaPnl(self, -1)
		ea.identity = self.__identity
		dlg = gmEditArea.cGenericEditAreaDlg(self, -1, edit_area = ea)
		dlg.SetTitle(_('Adding new external ID'))
		if dlg.ShowModal() == wx.ID_OK:
			dlg.Destroy()
			return True
		dlg.Destroy()
		return False
	#--------------------------------------------------------
	def _edit_id(self, ext_id):
		ea = cExternalIDEditAreaPnl(self, -1, external_id = ext_id)
		ea.identity = self.__identity
		dlg = gmEditArea.cGenericEditAreaDlg(self, -1, edit_area = ea)
		dlg.SetTitle(_('Editing external ID'))
		if dlg.ShowModal() == wx.ID_OK:
			dlg.Destroy()
			return True
		dlg.Destroy()
		return False
	#--------------------------------------------------------
	def _del_id(self, ext_id):
		go_ahead = gmGuiHelpers.gm_show_question (
			_(	'Do you really want to delete this\n'
				'external ID from the patient ?'),
			_('Deleting external ID')
		)
		if not go_ahead:
			return False
		self.__identity.delete_external_id(pk_ext_id = ext_id['pk_id'])
		return True
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_identity(self):
		return self.__identity

	def _set_identity(self, identity):
		self.__identity = identity
		self.refresh()

	identity = property(_get_identity, _set_identity)
#------------------------------------------------------------
# integrated panels
#------------------------------------------------------------
class cPersonIdentityManagerPnl(wxgPersonIdentityManagerPnl.wxgPersonIdentityManagerPnl):
	"""A panel for editing identity data for a person.

	- provides access to:
	  - name
	  - external IDs

	Does NOT act on/listen to the current patient.
	"""
	def __init__(self, *args, **kwargs):

		wxgPersonIdentityManagerPnl.wxgPersonIdentityManagerPnl.__init__(self, *args, **kwargs)

		self.__identity = None
		self.refresh()
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def refresh(self):
		self._PNL_names.identity = self.__identity
		self._PNL_ids.identity = self.__identity
		# this is an Edit Area:
		self._PNL_identity.mode = 'new'
		self._PNL_identity.data = self.__identity
		if self.__identity is not None:
			self._PNL_identity.mode = 'edit'
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_identity(self):
		return self.__identity

	def _set_identity(self, identity):
		self.__identity = identity
		self.refresh()

	identity = property(_get_identity, _set_identity)
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_save_identity_details_button_pressed(self, event):
		if not self._PNL_identity.save():
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot save identity. Incomplete information.'), beep = True)
	#--------------------------------------------------------
	def _on_reload_identity_button_pressed(self, event):
		self._PNL_identity.refresh()

#============================================================
from Gnumed.wxGladeWidgets import wxgPersonSocialNetworkManagerPnl

class cPersonSocialNetworkManagerPnl(wxgPersonSocialNetworkManagerPnl.wxgPersonSocialNetworkManagerPnl):
	def __init__(self, *args, **kwargs):

		wxgPersonSocialNetworkManagerPnl.wxgPersonSocialNetworkManagerPnl.__init__(self, *args, **kwargs)

		self.__identity = None
		self.refresh()
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def refresh(self):

		tt = _("Link another person in this database as the emergency contact.")

		if self.__identity is None:
			self._TCTRL_er_contact.SetValue(u'')
			self._TCTRL_person.person = None
			self._TCTRL_person.SetToolTipString(tt)
			return

		self._TCTRL_er_contact.SetValue(gmTools.coalesce(self.__identity['emergency_contact'], u''))
		if self.__identity['pk_emergency_contact'] is not None:
			ident = gmPerson.cIdentity(aPK_obj = self.__identity['pk_emergency_contact'])
			self._TCTRL_person.person = ident
			tt = u'%s\n\n%s\n\n%s' % (
				tt,
				ident['description_gender'],
				u'\n'.join([
					u'%s: %s%s' % (
						c['l10n_comm_type'],
						c['url'],
						gmTools.bool2subst(c['is_confidential'], _(' (confidential !)'), u'', u'')
					)
					for c in ident.get_comm_channels()
				])
			)
		else:
			self._TCTRL_person.person = None

		self._TCTRL_person.SetToolTipString(tt)
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_identity(self):
		return self.__identity

	def _set_identity(self, identity):
		self.__identity = identity
		self.refresh()

	identity = property(_get_identity, _set_identity)
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_save_button_pressed(self, event):
		if self.__identity is not None:
			self.__identity['emergency_contact'] = self._TCTRL_er_contact.GetValue().strip()
			if self._TCTRL_person.person is not None:
				self.__identity['pk_emergency_contact'] = self._TCTRL_person.person.ID
			self.__identity.save()

		event.Skip()
	#--------------------------------------------------------
	def _on_remove_contact_button_pressed(self, event):
		event.Skip()

		if self.__identity is None:
			return

		self._TCTRL_person.person = None

		self.__identity['pk_emergency_contact'] = None
		self.__identity.save()
	#--------------------------------------------------------
	def _on_button_activate_contact_pressed(self, event):
		ident = self._TCTRL_person.person
		if ident is not None:
			from Gnumed.wxpython import gmPatSearchWidgets
			gmPatSearchWidgets.set_active_patient(patient = ident, forced_reload = False)

		event.Skip()
#============================================================
# new-patient widgets
#============================================================
def create_new_person(parent=None, activate=False):

	dbcfg = gmCfg.cCfgSQL()

	def_region = dbcfg.get2 (
		option = u'person.create.default_region',
		workplace = gmSurgery.gmCurrentPractice().active_workplace,
		bias = u'user'
	)

	if def_region is None:
		def_country = dbcfg.get2 (
			option = u'person.create.default_country',
			workplace = gmSurgery.gmCurrentPractice().active_workplace,
			bias = u'user'
		)
	else:
		countries = gmDemographicRecord.get_country_for_region(region = def_region)
		if len(countries) == 1:
			def_country = countries[0]['l10n_country']

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	ea = cNewPatientEAPnl(parent = parent, id = -1, country = def_country, region = def_region)
	dlg = gmEditArea.cGenericEditAreaDlg2(parent = parent, id = -1, edit_area = ea, single_entry = True)
	dlg.SetTitle(_('Adding new person'))
	ea._PRW_lastname.SetFocus()
	result = dlg.ShowModal()
	pat = ea.data
	dlg.Destroy()

	if result != wx.ID_OK:
		return False

	if activate:
		from Gnumed.wxpython import gmPatSearchWidgets
		gmPatSearchWidgets.set_active_patient(patient = pat)

	gmDispatcher.send(signal = 'display_widget', name = 'gmNotebookedPatientEditionPlugin')

	return True
#============================================================
from Gnumed.wxGladeWidgets import wxgNewPatientEAPnl

class cNewPatientEAPnl(wxgNewPatientEAPnl.wxgNewPatientEAPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwargs):

		try:
			self.default_region = kwargs['region']
			del kwargs['region']
		except KeyError:
			self.default_region = None

		try:
			self.default_country = kwargs['country']
			del kwargs['country']
		except KeyError:
			self.default_country = None

		wxgNewPatientEAPnl.wxgNewPatientEAPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		self.mode = 'new'
		self.data = None
		self._address = None

		self.__init_ui()
		self.__register_interests()
	#----------------------------------------------------------------
	# internal helpers
	#----------------------------------------------------------------
	def __init_ui(self):
		self._PRW_lastname.final_regex = '.+'
		self._PRW_firstnames.final_regex = '.+'
		self._PRW_address_searcher.selection_only = False
		low = wx.DateTimeFromDMY(1,0,1900)
		hi = wx.DateTime()
		self._DP_dob.SetRange(low, hi.SetToCurrent())
		# only if we would support None on selection_only's
		#self._PRW_external_id_type.selection_only = True

		if self.default_country is not None:
			self._PRW_country.SetText(value = self.default_country)

		if self.default_region is not None:
			self._PRW_region.SetText(value = self.default_region)
	#----------------------------------------------------------------
	def __perhaps_invalidate_address_searcher(self, ctrl=None, field=None):

		adr = self._PRW_address_searcher.get_address()
		if adr is None:
			return True

		if ctrl.GetValue().strip() != adr[field]:
			wx.CallAfter(self._PRW_address_searcher.SetText, value = u'', data = None)
			return True

		return False
	#----------------------------------------------------------------
	def __set_fields_from_address_searcher(self):
		adr = self._PRW_address_searcher.get_address()
		if adr is None:
			return True

		self._PRW_zip.SetText(value = adr['postcode'], data = adr['postcode'])

		self._PRW_street.SetText(value = adr['street'], data = adr['street'])
		self._PRW_street.set_context(context = u'zip', val = adr['postcode'])

		self._TCTRL_number.SetValue(adr['number'])

		self._PRW_urb.SetText(value = adr['urb'], data = adr['urb'])
		self._PRW_urb.set_context(context = u'zip', val = adr['postcode'])

		self._PRW_region.SetText(value = adr['l10n_state'], data = adr['code_state'])
		self._PRW_region.set_context(context = u'zip', val = adr['postcode'])

		self._PRW_country.SetText(value = adr['l10n_country'], data = adr['code_country'])
		self._PRW_country.set_context(context = u'zip', val = adr['postcode'])
	#----------------------------------------------------------------
	def __identity_valid_for_save(self):
		error = False

		# name fields
		if self._PRW_lastname.GetValue().strip() == u'':
			error = True
			gmDispatcher.send(signal = 'statustext', msg = _('Must enter lastname.'))
			self._PRW_lastname.display_as_valid(False)
		else:
			self._PRW_lastname.display_as_valid(True)

		if self._PRW_firstnames.GetValue().strip() == '':
			error = True
			gmDispatcher.send(signal = 'statustext', msg = _('Must enter first name.'))
			self._PRW_firstnames.display_as_valid(False)
		else:
			self._PRW_firstnames.display_as_valid(True)

		# gender
		if self._PRW_gender.GetData() is None:
			error = True
			gmDispatcher.send(signal = 'statustext', msg = _('Must select gender.'))
			self._PRW_gender.display_as_valid(False)
		else:
			self._PRW_gender.display_as_valid(True)

		# dob validation
		if not self._DP_dob.is_valid_timestamp():

			gmDispatcher.send(signal = 'statustext', msg = _('Cannot use this date of birth. Does it lie before 1900 ?'))

			do_it_anyway = gmGuiHelpers.gm_show_question (
				_(
					'Are you sure you want to register this person\n'
					'without a valid date of birth ?\n'
					'\n'
					'This can be useful for temporary staff members\n'
					'but will provoke nag screens if this person\n'
					'becomes a patient.\n'
					'\n'
					'Note that the date of birth cannot technically\n'
					'be before 1900, either :-(\n'
				),
				_('Registering new person')
			)

			if not do_it_anyway:
				error = True

		if self._DP_dob.GetValue() is None:
			self._DP_dob.SetBackgroundColour(gmPhraseWheel.color_prw_valid)
		elif self._DP_dob.GetValue().GetYear() < 1900:
			error = True
			gmDispatcher.send(signal = 'statustext', msg = _('The year of birth must lie after 1900.'), beep = True)
			self._DP_dob.SetBackgroundColour(gmPhraseWheel.color_prw_invalid)
			self._DP_dob.SetFocus()
		else:
			self._DP_dob.SetBackgroundColour(gmPhraseWheel.color_prw_valid)
		self._DP_dob.Refresh()

		# TOB validation if non-empty
#		if self._TCTRL_tob.GetValue().strip() != u'':

		return (not error)
	#----------------------------------------------------------------
	def __address_valid_for_save(self, empty_address_is_valid=False):

		# existing address ? if so set other fields
		if self._PRW_address_searcher.GetData() is not None:
			wx.CallAfter(self.__set_fields_from_address_searcher)
			return True

		# must either all contain something or none of them
		fields_to_fill = (
			self._TCTRL_number,
			self._PRW_zip,
			self._PRW_street,
			self._PRW_urb,
			self._PRW_region,
			self._PRW_country
		)
		no_of_filled_fields = 0

		for field in fields_to_fill:
			if field.GetValue().strip() != u'':
				no_of_filled_fields += 1
				field.SetBackgroundColour(gmPhraseWheel.color_prw_valid)
				field.Refresh()

		# empty address ?
		if no_of_filled_fields == 0:
			if empty_address_is_valid:
				return True
			else:
				return None

		# incompletely filled address ?
		if no_of_filled_fields != len(fields_to_fill):
			for field in fields_to_fill:
				if field.GetValue().strip() == u'':
					field.SetBackgroundColour(gmPhraseWheel.color_prw_invalid)
					field.SetFocus()
					field.Refresh()
			msg = _('To properly create an address, all the related fields must be filled in.')
			gmGuiHelpers.gm_show_error(msg, _('Required fields'))
			return False

		# fields which must contain a selected item
		# FIXME: they must also contain an *acceptable combination* which
		# FIXME: can only be tested against the database itself ...
		strict_fields = (
			self._PRW_region,
			self._PRW_country
		)
		error = False
		for field in strict_fields:
			if field.GetData() is None:
				error = True
				field.SetBackgroundColour(gmPhraseWheel.color_prw_invalid)
				field.SetFocus()
			else:
				field.SetBackgroundColour(gmPhraseWheel.color_prw_valid)
			field.Refresh()

		if error:
			msg = _('This field must contain an item selected from the dropdown list.')
			gmGuiHelpers.gm_show_error(msg, _('Required fields'))
			return False

		return True
	#----------------------------------------------------------------
	def __register_interests(self):

		# identity
		self._PRW_firstnames.add_callback_on_lose_focus(self._on_leaving_firstname)

		# address
		self._PRW_address_searcher.add_callback_on_lose_focus(self._on_leaving_adress_searcher)

		# invalidate address searcher when any field edited
		self._PRW_street.add_callback_on_lose_focus(self._invalidate_address_searcher)
		wx.EVT_KILL_FOCUS(self._TCTRL_number, self._invalidate_address_searcher)
		self._PRW_urb.add_callback_on_lose_focus(self._invalidate_address_searcher)
		self._PRW_region.add_callback_on_lose_focus(self._invalidate_address_searcher)

		self._PRW_zip.add_callback_on_lose_focus(self._on_leaving_zip)
		self._PRW_country.add_callback_on_lose_focus(self._on_leaving_country)
	#----------------------------------------------------------------
	# event handlers
	#----------------------------------------------------------------
	def _on_leaving_firstname(self):
		"""Set the gender according to entered firstname.

		Matches are fetched from existing records in backend.
		"""
		# only set if not already set so as to not
		# overwrite a change by the user
		if self._PRW_gender.GetData() is not None:
			return True

		firstname = self._PRW_firstnames.GetValue().strip()
		if firstname == u'':
			return True

		gender = gmPerson.map_firstnames2gender(firstnames = firstname)
		if gender is None:
			return True

		wx.CallAfter(self._PRW_gender.SetData, gender)
		return True
	#----------------------------------------------------------------
	def _on_leaving_zip(self):
		self.__perhaps_invalidate_address_searcher(self._PRW_zip, 'postcode')

		zip_code = gmTools.none_if(self._PRW_zip.GetValue().strip(), u'')
		self._PRW_street.set_context(context = u'zip', val = zip_code)
		self._PRW_urb.set_context(context = u'zip', val = zip_code)
		self._PRW_region.set_context(context = u'zip', val = zip_code)
		self._PRW_country.set_context(context = u'zip', val = zip_code)

		return True
	#----------------------------------------------------------------
	def _on_leaving_country(self):
		self.__perhaps_invalidate_address_searcher(self._PRW_country, 'l10n_country')

		country = gmTools.none_if(self._PRW_country.GetValue().strip(), u'')
		self._PRW_region.set_context(context = u'country', val = country)

		return True
	#----------------------------------------------------------------
	def _invalidate_address_searcher(self, *args, **kwargs):
		mapping = [
			(self._PRW_street, 'street'),
			(self._TCTRL_number, 'number'),
			(self._PRW_urb, 'urb'),
			(self._PRW_region, 'l10n_state')
		]

		# loop through fields and invalidate address searcher if different
		for ctrl, field in mapping:
			if self.__perhaps_invalidate_address_searcher(ctrl, field):
				return True

		return True
	#----------------------------------------------------------------
	def _on_leaving_adress_searcher(self):
		adr = self._PRW_address_searcher.get_address()
		if adr is None:
			return True

		wx.CallAfter(self.__set_fields_from_address_searcher)
		return True
	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):
		return (self.__identity_valid_for_save() and self.__address_valid_for_save(empty_address_is_valid = True))
	#----------------------------------------------------------------
	def _save_as_new(self):

		# identity
		new_identity = gmPerson.create_identity (
			gender = self._PRW_gender.GetData(),
			dob = self._DP_dob.get_pydt(),
			lastnames = self._PRW_lastname.GetValue().strip(),
			firstnames = self._PRW_firstnames.GetValue().strip()
		)
		_log.debug('identity created: %s' % new_identity)

		new_identity['title'] = gmTools.none_if(self._PRW_title.GetValue().strip())
		new_identity.set_nickname(nickname = gmTools.none_if(self._PRW_nickname.GetValue().strip(), u''))
		#TOB
		new_identity.save()

		name = new_identity.get_active_name()
		name['comment'] = gmTools.none_if(self._TCTRL_comment.GetValue().strip(), u'')
		name.save()

		# address
		is_valid = self.__address_valid_for_save(empty_address_is_valid = False)
		if is_valid is True:
			# because we currently only check for non-emptiness
			# we must still deal with database errors
			try:
				new_identity.link_address (
					number = self._TCTRL_number.GetValue().strip(),
					street = self._PRW_street.GetValue().strip(),
					postcode = self._PRW_zip.GetValue().strip(),
					urb = self._PRW_urb.GetValue().strip(),
					state = self._PRW_region.GetData(),
					country = self._PRW_country.GetData()
				)
			except psycopg2.InternalError:
			#except StandardError:
				_log.debug('number: >>%s<<', self._TCTRL_number.GetValue().strip())
				_log.debug('street: >>%s<<', self._PRW_street.GetValue().strip())
				_log.debug('postcode: >>%s<<', self._PRW_zip.GetValue().strip())
				_log.debug('urb: >>%s<<', self._PRW_urb.GetValue().strip())
				_log.debug('state: >>%s<<', self._PRW_region.GetData().strip())
				_log.debug('country: >>%s<<', self._PRW_country.GetData().strip())
				_log.exception('cannot link address')
				gmGuiHelpers.gm_show_error (
					aTitle = _('Saving address'),
					aMessage = _(
						'Cannot save this address.\n'
						'\n'
						'You will have to add it via the Demographics plugin.\n'
					)
				)
		elif is_valid is False:
			gmGuiHelpers.gm_show_error (
				aTitle = _('Saving address'),
				aMessage = _(
					'Address not saved.\n'
					'\n'
					'You will have to add it via the Demographics plugin.\n'
				)
			)
		# else it is None which means empty address which we ignore

		# phone
		new_identity.link_comm_channel (
			comm_medium = u'homephone',
			url = gmTools.none_if(self._TCTRL_phone.GetValue().strip(), u''),
			is_confidential = False
		)

		# external ID
		pk_type = self._PRW_external_id_type.GetData()
		id_value = self._TCTRL_external_id_value.GetValue().strip()
		if (pk_type is not None) and (id_value != u''):
			new_identity.add_external_id(value = id_value, pk_type = pk_type)

		# occupation
		new_identity.link_occupation (
			occupation = gmTools.none_if(self._PRW_occupation.GetValue().strip(), u'')
		)

		self.data = new_identity
		return True
	#----------------------------------------------------------------
	def _save_as_update(self):
		raise NotImplementedError('[%s]: not expected to be used' % self.__class__.__name__)
	#----------------------------------------------------------------
	def _refresh_as_new(self):
		# FIXME: button "empty out"
		return
	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		return		# there is no forward button so nothing to do here
	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		raise NotImplementedError('[%s]: not expected to be used' % self.__class__.__name__)
#============================================================
# new-patient wizard classes
#============================================================
class cBasicPatDetailsPage(wx.wizard.WizardPageSimple):
	"""
	Wizard page for entering patient's basic demographic information
	"""

	form_fields = (
			'firstnames', 'lastnames', 'nick', 'dob', 'gender', 'title', 'occupation',
			'address_number', 'zip_code', 'street', 'town', 'state', 'country', 'phone', 'comment'
	)

	def __init__(self, parent, title):
		"""
		Creates a new instance of BasicPatDetailsPage
		@param parent - The parent widget
		@type parent - A wx.Window instance
		@param tile - The title of the page
		@type title - A StringType instance
		"""
		wx.wizard.WizardPageSimple.__init__(self, parent) #, bitmap = gmGuiHelpers.gm_icon(_('oneperson'))
		self.__title = title
		self.__do_layout()
		self.__register_interests()
	#--------------------------------------------------------
	def __do_layout(self):
		PNL_form = wx.Panel(self, -1)

		# last name
		STT_lastname = wx.StaticText(PNL_form, -1, _('Last name'))
		STT_lastname.SetForegroundColour('red')
		self.PRW_lastname = cLastnamePhraseWheel(parent = PNL_form, id = -1)
		self.PRW_lastname.SetToolTipString(_('Required: lastname (family name)'))

		# first name
		STT_firstname = wx.StaticText(PNL_form, -1, _('First name(s)'))
		STT_firstname.SetForegroundColour('red')
		self.PRW_firstname = cFirstnamePhraseWheel(parent = PNL_form, id = -1)
		self.PRW_firstname.SetToolTipString(_('Required: surname/given name/first name'))

		# nickname
		STT_nick = wx.StaticText(PNL_form, -1, _('Nick name'))
		self.PRW_nick = cNicknamePhraseWheel(parent = PNL_form, id = -1)

		# DOB
		STT_dob = wx.StaticText(PNL_form, -1, _('Date of birth'))
		STT_dob.SetForegroundColour('red')
		self.PRW_dob = gmDateTimeInput.cFuzzyTimestampInput(parent = PNL_form, id = -1)
		self.PRW_dob.SetToolTipString(_("Required: date of birth, if unknown or aliasing wanted then invent one"))

		# gender
		STT_gender = wx.StaticText(PNL_form, -1, _('Gender'))
		STT_gender.SetForegroundColour('red')
		self.PRW_gender = cGenderSelectionPhraseWheel(parent = PNL_form, id=-1)
		self.PRW_gender.SetToolTipString(_("Required: gender of patient"))

		# title
		STT_title = wx.StaticText(PNL_form, -1, _('Title'))
		self.PRW_title = cTitlePhraseWheel(parent = PNL_form, id = -1)

		# zip code
		STT_zip_code = wx.StaticText(PNL_form, -1, _('Postal code'))
		STT_zip_code.SetForegroundColour('orange')
		self.PRW_zip_code = cZipcodePhraseWheel(parent = PNL_form, id = -1)
		self.PRW_zip_code.SetToolTipString(_("primary/home address: zip/postal code"))

		# street
		STT_street = wx.StaticText(PNL_form, -1, _('Street'))
		STT_street.SetForegroundColour('orange')
		self.PRW_street = cStreetPhraseWheel(parent = PNL_form, id = -1)
		self.PRW_street.SetToolTipString(_("primary/home address: name of street"))

		# address number
		STT_address_number = wx.StaticText(PNL_form, -1, _('Number'))
		STT_address_number.SetForegroundColour('orange')
		self.TTC_address_number = wx.TextCtrl(PNL_form, -1)
		self.TTC_address_number.SetToolTipString(_("primary/home address: address number"))

		# town
		STT_town = wx.StaticText(PNL_form, -1, _('Place'))
		STT_town.SetForegroundColour('orange')
		self.PRW_town = cUrbPhraseWheel(parent = PNL_form, id = -1)
		self.PRW_town.SetToolTipString(_("primary/home address: city/town/village/dwelling/..."))

		# state
		STT_state = wx.StaticText(PNL_form, -1, _('Region'))
		STT_state.SetForegroundColour('orange')
		self.PRW_state = cStateSelectionPhraseWheel(parent=PNL_form, id=-1)
		self.PRW_state.SetToolTipString(_("primary/home address: state/province/county/..."))

		# country
		STT_country = wx.StaticText(PNL_form, -1, _('Country'))
		STT_country.SetForegroundColour('orange')
		self.PRW_country = cCountryPhraseWheel(parent = PNL_form, id = -1)
		self.PRW_country.SetToolTipString(_("primary/home address: country"))

		# phone
		STT_phone = wx.StaticText(PNL_form, -1, _('Phone'))
		self.TTC_phone = wx.TextCtrl(PNL_form, -1)
		self.TTC_phone.SetToolTipString(_("phone number at home"))

		# occupation
		STT_occupation = wx.StaticText(PNL_form, -1, _('Occupation'))
		self.PRW_occupation = cOccupationPhraseWheel(parent = PNL_form,	id = -1)

		# comment
		STT_comment = wx.StaticText(PNL_form, -1, _('Comment'))
		self.TCTRL_comment = wx.TextCtrl(PNL_form, -1)
		self.TCTRL_comment.SetToolTipString(_('A comment on this patient.'))

		# form main validator
		self.form_DTD = cFormDTD(fields = self.__class__.form_fields)
		PNL_form.SetValidator(cBasicPatDetailsPageValidator(dtd = self.form_DTD))

		# layout input widgets
		SZR_input = wx.FlexGridSizer(cols = 2, rows = 16, vgap = 4, hgap = 4)
		SZR_input.AddGrowableCol(1)
		SZR_input.Add(STT_lastname, 0, wx.SHAPED)
		SZR_input.Add(self.PRW_lastname, 1, wx.EXPAND)
		SZR_input.Add(STT_firstname, 0, wx.SHAPED)
		SZR_input.Add(self.PRW_firstname, 1, wx.EXPAND)
		SZR_input.Add(STT_nick, 0, wx.SHAPED)
		SZR_input.Add(self.PRW_nick, 1, wx.EXPAND)
		SZR_input.Add(STT_dob, 0, wx.SHAPED)
		SZR_input.Add(self.PRW_dob, 1, wx.EXPAND)
		SZR_input.Add(STT_gender, 0, wx.SHAPED)
		SZR_input.Add(self.PRW_gender, 1, wx.EXPAND)
		SZR_input.Add(STT_title, 0, wx.SHAPED)
		SZR_input.Add(self.PRW_title, 1, wx.EXPAND)
		SZR_input.Add(STT_zip_code, 0, wx.SHAPED)
		SZR_input.Add(self.PRW_zip_code, 1, wx.EXPAND)
		SZR_input.Add(STT_street, 0, wx.SHAPED)
		SZR_input.Add(self.PRW_street, 1, wx.EXPAND)
		SZR_input.Add(STT_address_number, 0, wx.SHAPED)
		SZR_input.Add(self.TTC_address_number, 1, wx.EXPAND)
		SZR_input.Add(STT_town, 0, wx.SHAPED)
		SZR_input.Add(self.PRW_town, 1, wx.EXPAND)
		SZR_input.Add(STT_state, 0, wx.SHAPED)
		SZR_input.Add(self.PRW_state, 1, wx.EXPAND)
		SZR_input.Add(STT_country, 0, wx.SHAPED)
		SZR_input.Add(self.PRW_country, 1, wx.EXPAND)
		SZR_input.Add(STT_phone, 0, wx.SHAPED)
		SZR_input.Add(self.TTC_phone, 1, wx.EXPAND)
		SZR_input.Add(STT_occupation, 0, wx.SHAPED)
		SZR_input.Add(self.PRW_occupation, 1, wx.EXPAND)
		SZR_input.Add(STT_comment, 0, wx.SHAPED)
		SZR_input.Add(self.TCTRL_comment, 1, wx.EXPAND)

		PNL_form.SetSizerAndFit(SZR_input)

		# layout page
		SZR_main = gmGuiHelpers.makePageTitle(self, self.__title)
		SZR_main.Add(PNL_form, 1, wx.EXPAND)
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		self.PRW_firstname.add_callback_on_lose_focus(self.on_name_set)
		self.PRW_country.add_callback_on_selection(self.on_country_selected)
		self.PRW_zip_code.add_callback_on_lose_focus(self.on_zip_set)
	#--------------------------------------------------------
	def on_country_selected(self, data):
		"""Set the states according to entered country."""
		self.PRW_state.set_context(context=u'country', val=data)
		return True
	#--------------------------------------------------------
	def on_name_set(self):
		"""Set the gender according to entered firstname.

		Matches are fetched from existing records in backend.
		"""
		firstname = self.PRW_firstname.GetValue().strip()
		rows, idx = gmPG2.run_ro_queries(queries = [{
			'cmd': u"select gender from dem.name_gender_map where name ilike %s",
			'args': [firstname]
		}])
		if len(rows) == 0:
			return True
		wx.CallAfter(self.PRW_gender.SetData, rows[0][0])
		return True
	#--------------------------------------------------------
	def on_zip_set(self):
		"""Set the street, town, state and country according to entered zip code."""
		zip_code = self.PRW_zip_code.GetValue().strip()
		self.PRW_street.set_context(context=u'zip', val=zip_code)
		self.PRW_town.set_context(context=u'zip', val=zip_code)
		self.PRW_state.set_context(context=u'zip', val=zip_code)
		self.PRW_country.set_context(context=u'zip', val=zip_code)
		return True
#============================================================
class cNewPatientWizard(wx.wizard.Wizard):
	"""
	Wizard to create a new patient.

	TODO:
	- write pages for different "themes" of patient creation
	- make it configurable which pages are loaded
	- make available sets of pages that apply to a country
	- make loading of some pages depend upon values in earlier pages, eg
	  when the patient is female and older than 13 include a page about
	  "female" data (number of kids etc)

	FIXME: use: wizard.FindWindowById(wx.ID_FORWARD).Disable()
	"""
	#--------------------------------------------------------
	def __init__(self, parent, title = _('Register new person'), subtitle = _('Basic demographic details') ):
		"""
		Creates a new instance of NewPatientWizard
		@param parent - The parent widget
		@type parent - A wx.Window instance
		"""
		id_wiz = wx.NewId()
		wx.wizard.Wizard.__init__(self, parent, id_wiz, title) #images.getWizTest1Bitmap()
		self.SetExtraStyle(wx.WS_EX_VALIDATE_RECURSIVELY)
		self.__subtitle = subtitle
		self.__do_layout()
	#--------------------------------------------------------
	def RunWizard(self, activate=False):
		"""Create new patient.

		activate, too, if told to do so (and patient successfully created)
		"""
		while True:

			if not wx.wizard.Wizard.RunWizard(self, self.basic_pat_details):
				return False

			try:
				# retrieve DTD and create patient
				ident = create_identity_from_dtd(dtd = self.basic_pat_details.form_DTD)
			except:
				_log.exception('cannot add new patient - missing identity fields')
				gmGuiHelpers.gm_show_error (
					_('Cannot create new patient.\n'
					  'Missing parts of the identity.'
					),
					_('Adding new patient')
				)
				continue

			update_identity_from_dtd(identity = ident, dtd = self.basic_pat_details.form_DTD)

			try:
				link_contacts_from_dtd(identity = ident, dtd = self.basic_pat_details.form_DTD)
			except:
				_log.exception('cannot finalize new patient - missing address fields')
				gmGuiHelpers.gm_show_error (
					_('Cannot add address for the new patient.\n'
					  'You must either enter all of the address fields or\n'
					  'none at all. The relevant fields are marked in yellow.\n'
					  '\n'
					  'You will need to add the address details in the\n'
					  'demographics module.'
					),
					_('Adding new patient')
				)
				break

			link_occupation_from_dtd(identity = ident, dtd = self.basic_pat_details.form_DTD)

			break

		if activate:
			from Gnumed.wxpython import gmPatSearchWidgets
			gmPatSearchWidgets.set_active_patient(patient = ident)

		return ident
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __do_layout(self):
		"""Arrange widgets.
		"""
		# Create the wizard pages
		self.basic_pat_details = cBasicPatDetailsPage(self, self.__subtitle )
		self.FitToPage(self.basic_pat_details)
#============================================================
#============================================================
class cBasicPatDetailsPageValidator(wx.PyValidator):
	"""
	This validator is used to ensure that the user has entered all
	the required conditional values in the page (eg., to properly
	create an address, all the related fields must be filled).
	"""
	#--------------------------------------------------------
	def __init__(self, dtd):
		"""
		Validator initialization.
		@param dtd The object containing the data model.
		@type dtd A cFormDTD instance
		"""
		# initialize parent class
		wx.PyValidator.__init__(self)
		# validator's storage object
		self.form_DTD = dtd
	#--------------------------------------------------------
	def Clone(self):
		"""
		Standard cloner.
		Note that every validator must implement the Clone() method.
		"""
		return cBasicPatDetailsPageValidator(dtd = self.form_DTD)		# FIXME: probably need new instance of DTD ?
	#--------------------------------------------------------
	def Validate(self, parent = None):
		"""
		Validate the contents of the given text control.
		"""
		_pnl_form = self.GetWindow().GetParent()

		error = False

		# name fields
		if _pnl_form.PRW_lastname.GetValue().strip() == '':
			error = True
			gmDispatcher.send(signal = 'statustext', msg = _('Must enter lastname.'))
			_pnl_form.PRW_lastname.SetBackgroundColour('pink')
			_pnl_form.PRW_lastname.Refresh()
		else:
			_pnl_form.PRW_lastname.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
			_pnl_form.PRW_lastname.Refresh()

		if _pnl_form.PRW_firstname.GetValue().strip() == '':
			error = True
			gmDispatcher.send(signal = 'statustext', msg = _('Must enter first name.'))
			_pnl_form.PRW_firstname.SetBackgroundColour('pink')
			_pnl_form.PRW_firstname.Refresh()
		else:
			_pnl_form.PRW_firstname.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
			_pnl_form.PRW_firstname.Refresh()

		# gender
		if _pnl_form.PRW_gender.GetData() is None:
			error = True
			gmDispatcher.send(signal = 'statustext', msg = _('Must select gender.'))
			_pnl_form.PRW_gender.SetBackgroundColour('pink')
			_pnl_form.PRW_gender.Refresh()
		else:
			_pnl_form.PRW_gender.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
			_pnl_form.PRW_gender.Refresh()

		# dob validation
		if (
				(_pnl_form.PRW_dob.GetValue().strip() == u'')
				or (not _pnl_form.PRW_dob.is_valid_timestamp())
				or (_pnl_form.PRW_dob.GetData().timestamp.year < 1900)
		):
			error = True
			msg = _('Cannot parse <%s> into proper timestamp.') % _pnl_form.PRW_dob.GetValue()
			gmDispatcher.send(signal = 'statustext', msg = msg)
			_pnl_form.PRW_dob.SetBackgroundColour('pink')
			_pnl_form.PRW_dob.Refresh()
		else:
			_pnl_form.PRW_dob.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
			_pnl_form.PRW_dob.Refresh()

		# address
		is_any_field_filled = False
		address_fields = (
			_pnl_form.TTC_address_number,
			_pnl_form.PRW_zip_code,
			_pnl_form.PRW_street,
			_pnl_form.PRW_town
		)
		for field in address_fields:
			if field.GetValue().strip() == u'':
				if is_any_field_filled:
					error = True
					msg = _('To properly create an address, all the related fields must be filled in.')
					gmGuiHelpers.gm_show_error(msg, _('Required fields'))
					field.SetBackgroundColour('pink')
					field.SetFocus()
					field.Refresh()
			else:
				is_any_field_filled = True
				field.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
				field.Refresh()

		address_fields = (
			_pnl_form.PRW_state,
			_pnl_form.PRW_country
		)
		for field in address_fields:
			if field.GetData() is None:
				if is_any_field_filled:
					error = True
					msg = _('To properly create an address, all the related fields must be filled in.')
					gmGuiHelpers.gm_show_error(msg, _('Required fields'))
					field.SetBackgroundColour('pink')
					field.SetFocus()
					field.Refresh()
			else:
				is_any_field_filled = True
				field.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
				field.Refresh()

		return (not error)
	#--------------------------------------------------------
	def TransferToWindow(self):
		"""
		Transfer data from validator to window.
		The default implementation returns False, indicating that an error
		occurred.  We simply return True, as we don't do any data transfer.
		"""
		_pnl_form = self.GetWindow().GetParent()
		# fill in controls with values from self.form_DTD
		_pnl_form.PRW_gender.SetData(self.form_DTD['gender'])
		_pnl_form.PRW_dob.SetText(self.form_DTD['dob'])
		_pnl_form.PRW_lastname.SetText(self.form_DTD['lastnames'])
		_pnl_form.PRW_firstname.SetText(self.form_DTD['firstnames'])
		_pnl_form.PRW_title.SetText(self.form_DTD['title'])
		_pnl_form.PRW_nick.SetText(self.form_DTD['nick'])
		_pnl_form.PRW_occupation.SetText(self.form_DTD['occupation'])
		_pnl_form.TTC_address_number.SetValue(self.form_DTD['address_number'])
		_pnl_form.PRW_street.SetText(self.form_DTD['street'])
		_pnl_form.PRW_zip_code.SetText(self.form_DTD['zip_code'])
		_pnl_form.PRW_town.SetText(self.form_DTD['town'])
		_pnl_form.PRW_state.SetData(self.form_DTD['state'])
		_pnl_form.PRW_country.SetData(self.form_DTD['country'])
		_pnl_form.TTC_phone.SetValue(self.form_DTD['phone'])
		_pnl_form.TCTRL_comment.SetValue(self.form_DTD['comment'])
		return True # Prevent wxDialog from complaining
	#--------------------------------------------------------
	def TransferFromWindow(self):
		"""
		Transfer data from window to validator.
		The default implementation returns False, indicating that an error
		occurred.  We simply return True, as we don't do any data transfer.
		"""
		# FIXME: should be called automatically
		if not self.GetWindow().GetParent().Validate():
			return False
		try:
			_pnl_form = self.GetWindow().GetParent()
			# fill in self.form_DTD with values from controls
			self.form_DTD['gender'] = _pnl_form.PRW_gender.GetData()
			self.form_DTD['dob'] = _pnl_form.PRW_dob.GetData()

			self.form_DTD['lastnames'] = _pnl_form.PRW_lastname.GetValue()
			self.form_DTD['firstnames'] = _pnl_form.PRW_firstname.GetValue()
			self.form_DTD['title'] = _pnl_form.PRW_title.GetValue()
			self.form_DTD['nick'] = _pnl_form.PRW_nick.GetValue()

			self.form_DTD['occupation'] = _pnl_form.PRW_occupation.GetValue()

			self.form_DTD['address_number'] = _pnl_form.TTC_address_number.GetValue()
			self.form_DTD['street'] = _pnl_form.PRW_street.GetValue()
			self.form_DTD['zip_code'] = _pnl_form.PRW_zip_code.GetValue()
			self.form_DTD['town'] = _pnl_form.PRW_town.GetValue()
			self.form_DTD['state'] = _pnl_form.PRW_state.GetData()
			self.form_DTD['country'] = _pnl_form.PRW_country.GetData()

			self.form_DTD['phone'] = _pnl_form.TTC_phone.GetValue()

			self.form_DTD['comment'] = _pnl_form.TCTRL_comment.GetValue()
		except:
			return False
		return True
#============================================================
#class cFormDTD:
#	"""
#	Simple Data Transfer Dictionary class to make easy the trasfer of
#	data between the form (view) and the business logic.
#
#	Maybe later consider turning this into a standard dict by
#	{}.fromkeys([key, key, ...], default) when it becomes clear that
#	we really don't need the added potential of a full-fledged class.
#	"""
#	def __init__(self, fields):
#		"""
#		Initialize the DTD with the supplied field names.
#		@param fields The names of the fields.
#		@type fields A TupleType instance.
#		"""
#		self.data = {}
#		for a_field in fields:
#			self.data[a_field] = ''
#
#	def __getitem__(self, attribute):
#		"""
#		Retrieve the value of the given attribute (key)
#		@param attribute The attribute (key) to retrieve its value for.
#		@type attribute a StringType instance.
#		"""
#		if not self.data[attribute]:
#			return ''
#		return self.data[attribute]
#
#	def __setitem__(self, attribute, value):
#		"""
#		Set the value of a given attribute (key).
#		@param attribute The attribute (key) to set its value for.
#		@type attribute a StringType instance.		
#		@param avaluee The value to set.
#		@rtpe attribute a StringType instance.
#		"""
#		self.data[attribute] = value
#
#	def __str__(self):
#		"""
#		Print string representation of the DTD object.
#		"""
#		return str(self.data)
#============================================================
# patient demographics editing classes
#============================================================
class cPersonDemographicsEditorNb(wx.Notebook):
	"""Notebook displaying demographics editing pages:

		- Identity
		- Contacts (addresses, phone numbers, etc)
		- Social Network (significant others, GP, etc)

	Does NOT act on/listen to the current patient.
	"""
	#--------------------------------------------------------
	def __init__(self, parent, id):

		wx.Notebook.__init__ (
			self,
			parent = parent,
			id = id,
			style = wx.NB_TOP | wx.NB_MULTILINE | wx.NO_BORDER,
			name = self.__class__.__name__
		)

		self.__identity = None
		self.__do_layout()
		self.SetSelection(0)
	#--------------------------------------------------------
	# public API
	#--------------------------------------------------------
	def refresh(self):
		"""Populate fields in pages with data from model."""
		for page_idx in range(self.GetPageCount()):
			page = self.GetPage(page_idx)
			page.identity = self.__identity

		return True
	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __do_layout(self):
		"""Build patient edition notebook pages."""

		# contacts page
		new_page = cPersonContactsManagerPnl(self, -1)
		new_page.identity = self.__identity
		self.AddPage (
			page = new_page,
			text = _('Contacts'),
			select = True
		)

		# identity page
		new_page = cPersonIdentityManagerPnl(self, -1)
		new_page.identity = self.__identity
		self.AddPage (
			page = new_page,
			text = _('Identity'),
			select = False
		)

		# social network page
		new_page = cPersonSocialNetworkManagerPnl(self, -1)
		new_page.identity = self.__identity
		self.AddPage (
			page = new_page,
			text = _('Social Network'),
			select = False
		)
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_identity(self):
		return self.__identity

	def _set_identity(self, identity):
		self.__identity = identity

	identity = property(_get_identity, _set_identity)
#============================================================
#============================================================
# FIXME: support multiple occupations
# FIXME: redo with wxGlade

class cPatOccupationsPanel(wx.Panel):
	"""Page containing patient occupations edition fields.
	"""
	def __init__(self, parent, id, ident=None):
		"""
		Creates a new instance of BasicPatDetailsPage
		@param parent - The parent widget
		@type parent - A wx.Window instance
		@param id - The widget id
		@type id - An integer
		"""
		wx.Panel.__init__(self, parent, id)
		self.__ident = ident
		self.__do_layout()
	#--------------------------------------------------------
	def __do_layout(self):
		PNL_form = wx.Panel(self, -1)
		# occupation
		STT_occupation = wx.StaticText(PNL_form, -1, _('Occupation'))
		self.PRW_occupation = cOccupationPhraseWheel(parent = PNL_form,	id = -1)
		self.PRW_occupation.SetToolTipString(_("primary occupation of the patient"))
		# known since
		STT_occupation_updated = wx.StaticText(PNL_form, -1, _('Last updated'))
		self.TTC_occupation_updated = wx.TextCtrl(PNL_form, -1, style = wx.TE_READONLY)

		# layout input widgets
		SZR_input = wx.FlexGridSizer(cols = 2, rows = 5, vgap = 4, hgap = 4)
		SZR_input.AddGrowableCol(1)				
		SZR_input.Add(STT_occupation, 0, wx.SHAPED)
		SZR_input.Add(self.PRW_occupation, 1, wx.EXPAND)
		SZR_input.Add(STT_occupation_updated, 0, wx.SHAPED)
		SZR_input.Add(self.TTC_occupation_updated, 1, wx.EXPAND)
		PNL_form.SetSizerAndFit(SZR_input)

		# layout page
		SZR_main = wx.BoxSizer(wx.VERTICAL)
		SZR_main.Add(PNL_form, 1, wx.EXPAND)
		self.SetSizer(SZR_main)
	#--------------------------------------------------------
	def set_identity(self, identity):
		return self.refresh(identity=identity)
	#--------------------------------------------------------
	def refresh(self, identity=None):
		if identity is not None:
			self.__ident = identity
		jobs = self.__ident.get_occupations()
		if len(jobs) > 0:
			self.PRW_occupation.SetText(jobs[0]['l10n_occupation'])
			self.TTC_occupation_updated.SetValue(jobs[0]['modified_when'].strftime('%m/%Y'))
		return True
	#--------------------------------------------------------
	def save(self):
		if self.PRW_occupation.IsModified():
			new_job = self.PRW_occupation.GetValue().strip()
			jobs = self.__ident.get_occupations()
			for job in jobs:
				if job['l10n_occupation'] == new_job:
					continue
				self.__ident.unlink_occupation(occupation = job['l10n_occupation'])
			self.__ident.link_occupation(occupation = new_job)
		return True
#============================================================
class cNotebookedPatEditionPanel(wx.Panel, gmRegetMixin.cRegetOnPaintMixin):
	"""Patient demographics plugin for main notebook.

	Hosts another notebook with pages for Identity, Contacts, etc.

	Acts on/listens to the currently active patient.
	"""
	#--------------------------------------------------------
	def __init__(self, parent, id):
		wx.Panel.__init__ (self, parent = parent, id = id, style = wx.NO_BORDER)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)
		self.__do_layout()
		self.__register_interests()
	#--------------------------------------------------------
	# public API
	#--------------------------------------------------------
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __do_layout(self):
		"""Arrange widgets."""
		self.__patient_notebook = cPersonDemographicsEditorNb(self, -1)

		szr_main = wx.BoxSizer(wx.VERTICAL)
		szr_main.Add(self.__patient_notebook, 1, wx.EXPAND)
		self.SetSizerAndFit(szr_main)
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		gmDispatcher.connect(signal = u'pre_patient_selection', receiver = self._on_pre_patient_selection)
		gmDispatcher.connect(signal = u'post_patient_selection', receiver = self._on_post_patient_selection)
	#--------------------------------------------------------
	def _on_pre_patient_selection(self):
		self._schedule_data_reget()
	#--------------------------------------------------------
	def _on_post_patient_selection(self):
		self._schedule_data_reget()
	#--------------------------------------------------------
	# reget mixin API
	#--------------------------------------------------------
	def _populate_with_data(self):
		"""Populate fields in pages with data from model."""
		pat = gmPerson.gmCurrentPatient()
		if pat.connected:
			self.__patient_notebook.identity = pat
		else:
			self.__patient_notebook.identity = None
		self.__patient_notebook.refresh()
		return True
#============================================================
#def create_identity_from_dtd(dtd=None):
#	"""
#	Register a new patient, given the data supplied in the 
#	Data Transfer Dictionary object.
#
#	@param basic_details_DTD Data Transfer Dictionary encapsulating all the
#	supplied data.
#	@type basic_details_DTD A cFormDTD instance.
#	"""
#	new_identity = gmPerson.create_identity (
#		gender = dtd['gender'],
#		dob = dtd['dob'].get_pydt(),
#		lastnames = dtd['lastnames'],
#		firstnames = dtd['firstnames']
#	)
#	if new_identity is None:
#		_log.error('cannot create identity from %s' % str(dtd))
#		return None
#	_log.debug('identity created: %s' % new_identity)
#
#	if dtd['comment'] is not None:
#		if dtd['comment'].strip() != u'':
#			name = new_identity.get_active_name()
#			name['comment'] = dtd['comment']
#			name.save_payload()
#
#	return new_identity
#============================================================
#def update_identity_from_dtd(identity, dtd=None):
#	"""
#	Update patient details with data supplied by
#	Data Transfer Dictionary object.
#
#	@param basic_details_DTD Data Transfer Dictionary encapsulating all the
#	supplied data.
#	@type basic_details_DTD A cFormDTD instance.
#	"""
#	# identity
#	if identity['gender'] != dtd['gender']:
#		identity['gender'] = dtd['gender']
#	if identity['dob'] != dtd['dob'].get_pydt():
#		identity['dob'] = dtd['dob'].get_pydt()
#	if len(dtd['title']) > 0 and identity['title'] != dtd['title']:
#		identity['title'] = dtd['title']
#	# FIXME: error checking
#	# FIXME: we need a trigger to update the values of the
#	# view, identity['keys'], eg. lastnames and firstnames
#	# are not refreshed.
#	identity.save_payload()
#
#	# names
#	# FIXME: proper handling of "active"
#	if identity['firstnames'] != dtd['firstnames'] or identity['lastnames'] != dtd['lastnames']:
#		new_name = identity.add_name(firstnames = dtd['firstnames'], lastnames = dtd['lastnames'], active = True)
#	# nickname
#	if len(dtd['nick']) > 0 and identity['preferred'] != dtd['nick']:
#		identity.set_nickname(nickname = dtd['nick'])
#
#	return True
#============================================================
#def link_contacts_from_dtd(identity, dtd=None):
#	"""
#	Update patient details with data supplied by
#	Data Transfer Dictionary object.
#
#	@param basic_details_DTD Data Transfer Dictionary encapsulating all the
#	supplied data.
#	@type basic_details_DTD A cFormDTD instance.
#	"""
#	lng = len (
#		dtd['address_number'].strip() +
#		dtd['street'].strip() +
#		dtd['zip_code'].strip() +
#		dtd['town'].strip() +
#		dtd['state'].strip() +
#		dtd['country'].strip()
#	)
#	# FIXME: improve error checking
#	if lng > 5:
#		# FIXME: support address type
#		success = identity.link_address (
#			number = dtd['address_number'].strip(),
#			street = dtd['street'].strip(),
#			postcode = dtd['zip_code'].strip(),
#			urb = dtd['town'].strip(),
#			state = dtd['state'].strip(),
#			country = dtd['country'].strip()
#		)
#		if not success:
#			gmDispatcher.send(signal='statustext', msg = _('Cannot add patient address.'))
#	else:
#		gmDispatcher.send(signal='statustext', msg = _('Cannot add patient address. Missing fields.'))
#
#	if len(dtd['phone']) > 0:
#		identity.link_comm_channel (
#			comm_medium = 'homephone',
#			url = dtd['phone'],
#			is_confidential = False
#		)
#
#	# FIXME: error checking
##	identity.save_payload()
#	return True
#============================================================				
#def link_occupation_from_dtd(identity, dtd=None):
#	"""
#	Update patient details with data supplied by
#	Data Transfer Dictionary object.
#
#	@param basic_details_DTD Data Transfer Dictionary encapsulating all the
#	supplied data.
#	@type basic_details_DTD A cFormDTD instance.
#	"""
#	identity.link_occupation(occupation = dtd['occupation'])
#
#	return True
#============================================================
class TestWizardPanel(wx.Panel):   
	"""
	Utility class to test the new patient wizard.
	"""
	#--------------------------------------------------------
	def __init__(self, parent, id):
		"""
		Create a new instance of TestPanel.
		@param parent The parent widget
		@type parent A wx.Window instance
		"""
		wx.Panel.__init__(self, parent, id)
		wizard = cNewPatientWizard(self)
		print wizard.RunWizard()
#============================================================
if __name__ == "__main__":

	#--------------------------------------------------------
	def test_zipcode_prw():
		app = wx.PyWidgetTester(size = (200, 50))
		pw = cZipcodePhraseWheel(app.frame, -1)
		app.frame.Show(True)
		app.MainLoop()
	#--------------------------------------------------------
	def test_state_prw():
		app = wx.PyWidgetTester(size = (200, 50))
		pw = cStateSelectionPhraseWheel(app.frame, -1)
#		pw.set_context(context = u'zip', val = u'04318')
#		pw.set_context(context = u'country', val = u'Deutschland')
		app.frame.Show(True)
		app.MainLoop()
	#--------------------------------------------------------
	def test_urb_prw():
		app = wx.PyWidgetTester(size = (200, 50))
		pw = cUrbPhraseWheel(app.frame, -1)
		app.frame.Show(True)
		pw.set_context(context = u'zip', val = u'04317')
		app.MainLoop()
	#--------------------------------------------------------
	def test_suburb_prw():
		app = wx.PyWidgetTester(size = (200, 50))
		pw = cSuburbPhraseWheel(app.frame, -1)
		app.frame.Show(True)
		app.MainLoop()
	#--------------------------------------------------------
	def test_address_type_prw():
		app = wx.PyWidgetTester(size = (200, 50))
		pw = cAddressTypePhraseWheel(app.frame, -1)
		app.frame.Show(True)
		app.MainLoop()
	#--------------------------------------------------------
	def test_address_prw():
		app = wx.PyWidgetTester(size = (200, 50))
		pw = cAddressPhraseWheel(app.frame, -1)
		app.frame.Show(True)
		app.MainLoop()
	#--------------------------------------------------------
	def test_street_prw():
		app = wx.PyWidgetTester(size = (200, 50))
		pw = cStreetPhraseWheel(app.frame, -1)
#		pw.set_context(context = u'zip', val = u'04318')
		app.frame.Show(True)
		app.MainLoop()
	#--------------------------------------------------------
	def test_organizer_pnl():
		app = wx.PyWidgetTester(size = (600, 400))
		app.SetWidget(cKOrganizerSchedulePnl)
		app.MainLoop()
	#--------------------------------------------------------
	def test_person_names_pnl():
		app = wx.PyWidgetTester(size = (600, 400))
		widget = cPersonNamesManagerPnl(app.frame, -1)
		widget.identity = activate_patient()
		app.frame.Show(True)
		app.MainLoop()
	#--------------------------------------------------------
	def test_person_ids_pnl():
		app = wx.PyWidgetTester(size = (600, 400))
		widget = cPersonIDsManagerPnl(app.frame, -1)
		widget.identity = activate_patient()
		app.frame.Show(True)
		app.MainLoop()
	#--------------------------------------------------------
	def test_pat_ids_pnl():
		app = wx.PyWidgetTester(size = (600, 400))
		widget = cPersonIdentityManagerPnl(app.frame, -1)
		widget.identity = activate_patient()
		app.frame.Show(True)
		app.MainLoop()
	#--------------------------------------------------------
	def test_name_ea_pnl():
		app = wx.PyWidgetTester(size = (600, 400))
		app.SetWidget(cNameGenderDOBEditAreaPnl, name = activate_patient().get_active_name())
		app.MainLoop()
	#--------------------------------------------------------
	def test_address_ea_pnl():
		app = wx.PyWidgetTester(size = (600, 400))
		app.SetWidget(cAddressEditAreaPnl, address = gmDemographicRecord.cAddress(aPK_obj = 1))
		app.MainLoop()
	#--------------------------------------------------------
	def test_person_adrs_pnl():
		app = wx.PyWidgetTester(size = (600, 400))
		widget = cPersonAddressesManagerPnl(app.frame, -1)
		widget.identity = activate_patient()
		app.frame.Show(True)
		app.MainLoop()
	#--------------------------------------------------------
	def test_person_comms_pnl():
		app = wx.PyWidgetTester(size = (600, 400))
		widget = cPersonCommsManagerPnl(app.frame, -1)
		widget.identity = activate_patient()
		app.frame.Show(True)
		app.MainLoop()
	#--------------------------------------------------------
	def test_pat_contacts_pnl():
		app = wx.PyWidgetTester(size = (600, 400))
		widget = cPersonContactsManagerPnl(app.frame, -1)
		widget.identity = activate_patient()
		app.frame.Show(True)
		app.MainLoop()
	#--------------------------------------------------------
	def test_cPersonDemographicsEditorNb():
		app = wx.PyWidgetTester(size = (600, 400))
		widget = cPersonDemographicsEditorNb(app.frame, -1)
		widget.identity = activate_patient()
		widget.refresh()
		app.frame.Show(True)
		app.MainLoop()
	#--------------------------------------------------------
	def activate_patient():
		patient = gmPerson.ask_for_patient()
		if patient is None:
			print "No patient. Exiting gracefully..."
			sys.exit(0)
		from Gnumed.wxpython import gmPatSearchWidgets
		gmPatSearchWidgets.set_active_patient(patient=patient)
		return patient
	#--------------------------------------------------------
	if len(sys.argv) > 1 and sys.argv[1] == 'test':

		gmI18N.activate_locale()
		gmI18N.install_domain(domain='gnumed')
		gmPG2.get_connection()

#		a = cFormDTD(fields = cBasicPatDetailsPage.form_fields)

#		app = wx.PyWidgetTester(size = (400, 300))
#		app.SetWidget(cNotebookedPatEditionPanel, -1)
#		app.SetWidget(TestWizardPanel, -1)
#		app.frame.Show(True)
#		app.MainLoop()

		# phrasewheels
#		test_zipcode_prw()
#		test_state_prw()
#		test_street_prw()
#		test_organizer_pnl()
		#test_address_type_prw()
		#test_suburb_prw()
		test_urb_prw()
		#test_address_prw()

		# contacts related widgets
		#test_address_ea_pnl()
		#test_person_adrs_pnl()
		#test_person_comms_pnl()
		#test_pat_contacts_pnl()

		# identity related widgets
		#test_person_names_pnl()
		#test_person_ids_pnl()
		#test_pat_ids_pnl()
		#test_name_ea_pnl()

		#test_cPersonDemographicsEditorNb()

#============================================================
