"""Widgets dealing with address/contact information."""
#============================================================
__version__ = "$Revision: 1.175 $"
__author__ = "R.Terry, SJ Tan, I Haywood, Carlos Moro <cfmoro1976@yahoo.es>"
__license__ = 'GPL v2 or later (details at http://www.gnu.org)'

# standard library
import sys, logging


import wx


# GNUmed specific
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmDispatcher, gmMatchProvider, gmPG2, gmTools
from Gnumed.business import gmDemographicRecord
from Gnumed.wxpython import gmPhraseWheel, gmGuiHelpers, gmCfgWidgets
from Gnumed.wxpython import gmListWidgets, gmEditArea


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
# province/state related widgets / functions
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
# address phrasewheels and widgets
#============================================================
def manage_addresses(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()
	#------------------------------------------------------------
	def refresh(lctrl):
		adrs = gmDemographicRecord.get_addresses(order_by = u'l10n_country, urb, street, number, subunit')
		items = [ [
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
		lctrl.set_string_items(items)
		lctrl.set_data(adrs)

	#------------------------------------------------------------
	cols = [
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
	]
	gmListWidgets.get_choices_from_list (
		parent = parent,
		caption = _('Showing addresses registered in GNUmed.'),
		columns = cols,
		single_selection = True,
		refresh_callback = refresh
	)
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
		ea.address_holder = self.__identity
		dlg = gmEditArea.cGenericEditAreaDlg(self, -1, edit_area = ea)
		dlg.SetTitle(_('Adding new address'))
		if dlg.ShowModal() == wx.ID_OK:
			return True
		return False
	#--------------------------------------------------------
	def _edit_address(self, address):
		ea = cAddressEditAreaPnl(self, -1, address = address)
		ea.address_holder = self.__identity
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
from Gnumed.wxGladeWidgets import wxgGenericAddressEditAreaPnl

class cAddressEditAreaPnl(wxgGenericAddressEditAreaPnl.wxgGenericAddressEditAreaPnl):
	"""An edit area for editing/creating an address."""

	def __init__(self, *args, **kwargs):
		try:
			self.__address = kwargs['address']
			del kwargs['address']
		except KeyError:
			self.__address = None

		wxgGenericAddressEditAreaPnl.wxgGenericAddressEditAreaPnl.__init__(self, *args, **kwargs)

		self.address_holder = None
		self.type_is_editable = True

		self.__register_interests()
		self.refresh()
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def refresh(self, address = None):
		if address is not None:
			self.__address = address

		if self.__address is None:
			self._PRW_type.SetText(u'', None)
			self._PRW_zip.SetText(u'', None)
			self._PRW_street.SetText(u'', None)
			self._TCTRL_notes_street.SetValue(u'')
			self._TCTRL_number.SetValue(u'')
			self._TCTRL_subunit.SetValue(u'')
			self._PRW_suburb.SetText(u'', None)
			self._PRW_urb.SetText(u'', None)
			self._PRW_state.SetText(u'', None)
			self._PRW_country.SetText(u'', None)
			self._TCTRL_notes_subunit.SetValue(u'')
			return

		if self.__type_is_editable:
			self._PRW_type.SetText(self.address['l10n_address_type'])
		else:
			self._PRW_type.SetText(u'', None)
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
	#--------------------------------------------------------
	def save(self):
		"""Links address to patient, creating new address if necessary"""

		if not self.__valid_for_save():
			return False

		try:
			address = gmDemographicRecord.create_address (
				country = self._PRW_country.GetData(),
				state = self._PRW_state.GetData(),
				urb = self._PRW_urb.GetValue().strip(),
				suburb = gmTools.none_if(self._PRW_suburb.GetValue().strip(), u''),
				postcode = self._PRW_zip.GetValue().strip(),
				street = self._PRW_street.GetValue().strip(),
				number = self._TCTRL_number.GetValue().strip(),
				subunit = gmTools.none_if(self._TCTRL_subunit.GetValue().strip(), u'')
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

		# link address to owner
		a = self.address_holder.link_address(id_type = self._PRW_type.GetData(), address = address)
		if a['pk_address'] != address['pk_address']:
			raise ValueError('problem linking address to person or org')

		notes = self._TCTRL_notes_street.GetValue().strip()
		if notes != u'':
			address['notes_street'] = notes
		notes = self._TCTRL_notes_subunit.GetValue().strip()
		if notes != u'':
			address['notes_subunit'] = notes
		address.save_payload()

		self.__address = address

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

		required_fields = [
			self._PRW_zip,
			self._PRW_street,
			self._TCTRL_number,
			self._PRW_urb
		]
		if self.__type_is_editable:
			required_fields.insert(0, self._PRW_type)

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
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_type_is_editable(self):
		return self.__type_is_editable

	def _set_type_is_editable(self, type_is_editable):
		self.__type_is_editable = type_is_editable
		self._PRW_type.Enable(type_is_editable)
		self._PRW_type.Show(type_is_editable)
		self._LBL_type.Show(type_is_editable)

	type_is_editable = property(_get_type_is_editable, _set_type_is_editable)
	#--------------------------------------------------------
	def _get_address(self):
		return self.__address

	def _set_address(self, address):
		self.__address = address
		self.refresh()

	address = property(_get_address, _set_address)
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
# communication channels related widgets
#============================================================
def manage_comm_channel_types(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#------------------------------------------------------------
	def delete(channel=None):
		return gmDemographicRecord.delete_comm_channel_type(pk_channel_type = channel['pk'])
	#------------------------------------------------------------
	def refresh(lctrl):
		wx.BeginBusyCursor()
		channel_types = gmDemographicRecord.get_comm_channel_types()
		lctrl.set_string_items([ (ct['l10n_description'], ct['description'], ct['pk']) for ct in channel_types ])
		lctrl.set_data(channel_types)
		wx.EndBusyCursor()
	#------------------------------------------------------------
	msg = _('\nThis lists the communication channel types known to GNUmed.\n')

	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = msg,
		caption = _('Managing communication types ...'),
		columns = [_('Channel'), _('System type'), '#'],
		single_selection = True,
		#new_callback = edit,
		#edit_callback = edit,
		delete_callback = delete,
		refresh_callback = refresh
	)

#------------------------------------------------------------
class cCommChannelTypePhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		query = u"""
SELECT
	data,
	field_label,
	list_label
FROM (
	SELECT DISTINCT ON (field_label)
		pk
			AS data,
		_(description)
			AS field_label,
		(_(description) || ' (' || description || ')')
			AS list_label
	FROM dem.enum_comm_types
	WHERE
		_(description) %(fragment_condition)s
			OR
		description %(fragment_condition)s
) AS ur
ORDER BY
	ur.list_label
"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query)
		mp.setThresholds(1, 2, 4)
		mp.word_separators = u'[ \t]+'
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.matcher = mp
		self.SetToolTipString(_('Select the type of communications channel.'))
		self.selection_only = True

#------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgCommChannelEditAreaPnl

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
#			self._PRW_address.SetText(value = u'', data = None)
			self._CHBOX_confidential.SetValue(False)
		else:
			self._PRW_type.SetText(self.channel['l10n_comm_type'])
			self._TCTRL_url.SetValue(self.channel['url'])
#			self._PRW_address.SetData(data = self.channel['pk_address'])
			self._CHBOX_confidential.SetValue(self.channel['is_confidential'])

		self._PRW_address.Disable()
	#--------------------------------------------------------
	def save(self):
		"""Links comm channel to patient."""
		if self.channel is None:
			return self.__save_new()
		return self.__save_udpate()
#		self.channel['pk_address'] = self._PRW_address.GetData()
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __save_new(self):
		if not self.__valid_for_save():
			return False
		try:
			self.channel = self.identity.link_comm_channel (
				comm_medium = self._PRW_type.GetValue().strip(),
				pk_channel_type = self._PRW_type.GetData(),
				url = self._TCTRL_url.GetValue().strip(),
				is_confidential = self._CHBOX_confidential.GetValue(),
			)
		except gmPG2.dbapi.IntegrityError:
			_log.exception('error saving comm channel')
			gmDispatcher.send(signal = u'statustext', msg = _('Cannot save communications channel.'), beep = True)
			return False
		return True
	#--------------------------------------------------------
	def __save_update(self):
		comm_type = self._PRW_type.GetValue().strip()
		if comm_type != u'':
			self.channel['comm_type'] = comm_type
		url = self._TCTRL_url.GetValue().strip()
		if url != u'':
			self.channel['url'] = url
		self.channel['is_confidential'] = self._CHBOX_confidential.GetValue()
		self.channel.save_payload()

		return True
	#--------------------------------------------------------
	def __valid_for_save(self):

		no_errors = True

#		if self._PRW_type.GetData() is None:
		if self._PRW_type.GetValue().strip() == u'':
			no_errors = False
			self._PRW_type.display_as_valid(False)
			self._PRW_type.SetFocus()
		else:
			self._PRW_type.display_as_valid(True)

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

#------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgPersonContactsManagerPnl

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
if __name__ == "__main__":

	#--------------------------------------------------------
	def test_state_prw():
		app = wx.PyWidgetTester(size = (200, 50))
		pw = cStateSelectionPhraseWheel(app.frame, -1)
#		pw.set_context(context = u'zip', val = u'04318')
#		pw.set_context(context = u'country', val = u'Deutschland')
		app.frame.Show(True)
		app.MainLoop()
	#--------------------------------------------------------
	def test_person_adrs_pnl():
		app = wx.PyWidgetTester(size = (600, 400))
		widget = cPersonAddressesManagerPnl(app.frame, -1)
		widget.identity = activate_patient()
		app.frame.Show(True)
		app.MainLoop()
	#--------------------------------------------------------
	def test_address_ea_pnl():
		app = wx.PyWidgetTester(size = (600, 400))
		app.SetWidget(cAddressEditAreaPnl, address = gmDemographicRecord.cAddress(aPK_obj = 1))
		app.MainLoop()
	#--------------------------------------------------------
	def test_address_prw():
		app = wx.PyWidgetTester(size = (200, 50))
		pw = cAddressPhraseWheel(app.frame, -1)
		app.frame.Show(True)
		app.MainLoop()
	#--------------------------------------------------------
	def test_address_type_prw():
		app = wx.PyWidgetTester(size = (200, 50))
		pw = cAddressTypePhraseWheel(app.frame, -1)
		app.frame.Show(True)
		app.MainLoop()
	#--------------------------------------------------------
	def test_zipcode_prw():
		app = wx.PyWidgetTester(size = (200, 50))
		pw = cZipcodePhraseWheel(app.frame, -1)
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
	def test_suburb_prw():
		app = wx.PyWidgetTester(size = (200, 50))
		pw = cSuburbPhraseWheel(app.frame, -1)
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
	def test_person_comms_pnl():
		app = wx.PyWidgetTester(size = (600, 400))
		widget = cPersonCommsManagerPnl(app.frame, -1)
		widget.identity = activate_patient()
		app.frame.Show(True)
		app.MainLoop()

#============================================================
