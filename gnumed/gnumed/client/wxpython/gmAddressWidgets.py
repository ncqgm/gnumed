"""GNUmed generic address related widgets."""
#================================================================
__author__ = 'karsten.hilbert@gmx.net'
__license__ = 'GPL v2 or later (details at http://www.gnu.org)'

# stdlib
import logging, sys


# 3rd party
import wx


# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')

from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmMatchProvider
from Gnumed.business import gmDemographicRecord

from Gnumed.wxpython import gmCfgWidgets
from Gnumed.wxpython import gmPhraseWheel
from Gnumed.wxpython import gmListWidgets
from Gnumed.wxpython import gmEditArea
from Gnumed.wxpython import gmGuiHelpers


_log = logging.getLogger('gm.ui')
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
		data = [ c['code'] for c in countries ]
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
SELECT
	data,
	field_label,
	list_label
FROM (
	SELECT DISTINCT ON (data)
		data,
		field_label,
		list_label,
		rank
	FROM (

	-- localized to user
			SELECT
				code_country AS data,
				l10n_country AS field_label,
				l10n_country || ' (' || code_country || '): ' || country AS list_label,
				1 AS rank
			FROM dem.v_zip2data
			WHERE
				l10n_country %(fragment_condition)s
				%(ctxt_zip)s
		UNION ALL
			SELECT
				code AS data,
				_(name) AS field_label,
				_(name) || ' (' || code || '): ' || name AS list_label,
				2 AS rank
			FROM dem.country
			WHERE
				_(name) %(fragment_condition)s

		UNION ALL

	-- non-localized
			SELECT
				code_country AS data,
				l10n_country AS field_label,
				country || ' (' || code_country || '): ' || l10n_country AS list_label,
				3 AS rank
			FROM dem.v_zip2data
			WHERE
				country %(fragment_condition)s
				%(ctxt_zip)s
		UNION ALL
			SELECT
				code AS data,
				_(name) AS field_label,
				name || ' (' || code || '): ' || _(name) AS list_label,
				4 AS rank
			FROM dem.country
			WHERE
				name %(fragment_condition)s

		UNION ALL

	-- abbreviation
			SELECT
				code AS data,
				_(name) AS field_label,
				code || ': ' || _(name) || ' (' || name || ')' AS list_label,
				5 AS rank
			FROM dem.country
			WHERE
				code %(fragment_condition)s

	) AS candidates
) AS distint_candidates
ORDER BY rank, list_label
LIMIT 25"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query, context=context)
		mp._SQL_data2match = u"""
			SELECT
				code AS data,
				_(name) AS field_label,
				code || ': ' || _(name) || ' (' || name || ')' AS list_label,
				5 AS rank
			FROM dem.country
			WHERE
				code = %(pk)s
		"""
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
				u'where_part': u'AND l10n_country ILIKE %(country_name)s OR country ILIKE %(country_name)s',
				u'placeholder': u'country_name'
			},
			u'ctxt_zip': {
				u'where_part': u'AND zip ilike %(zip)s',
				u'placeholder': u'zip'
			},
			u'ctxt_country_code': {
				u'where_part': u'AND country IN (SELECT code FROM dem.country WHERE _(name) ILIKE %(country_name)s OR name ILIKE %(country_name)s)',
				u'placeholder': u'country_name'
			}
		}

		query = u"""
SELECT
	data,
	field_label,
	list_label
FROM (
	SELECT DISTINCT ON (field_label)
		data,
		field_label,
		list_label,
		rank
	FROM (
			-- 1: find states based on name, context: zip and country name
			SELECT
				code_state AS data,
				state AS field_label,
				state || ' (' || code_state || '), ' || l10n_country || ' (' || code_country || ')' AS list_label,
				1 AS rank
			FROM dem.v_zip2data
			WHERE
				state %(fragment_condition)s
				%(ctxt_country_name)s
				%(ctxt_zip)s

		UNION ALL

			-- 2: find states based on code, context: zip and country name
			SELECT
				code_state AS data,
				state AS field_label,
				code_state || ': ' || state || ' (' || l10n_country || ', ' || code_country || ')' AS list_label,
				2 AS rank
			FROM dem.v_zip2data
			WHERE
				code_state %(fragment_condition)s
				%(ctxt_country_name)s
				%(ctxt_zip)s

		UNION ALL

			-- 3: find states based on name, context: country
			SELECT
				code AS data,
				name AS field_label,
				name || ' (' || code || '), ' || country AS list_label,
				3 AS rank
			FROM dem.state
			WHERE
				name %(fragment_condition)s
				%(ctxt_country_code)s

		UNION ALL

			-- 4: find states based on code, context: country
			SELECT
				code AS data,
				name AS field_label,
				code || ': ' || name || ', ' || country AS list_label,
				3 AS rank
			FROM dem.state
			WHERE
				code %(fragment_condition)s
				%(ctxt_country_code)s

	) AS candidate_states
) AS distinct_matches
ORDER BY rank, list_label
LIMIT 50"""

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
# other address parts phrasewheels and widgets
#============================================================
class cZipcodePhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):
		# FIXME: add possible context
		query = u"""
			(SELECT distinct postcode, postcode FROM dem.street WHERE postcode %(fragment_condition)s limit 20)
				UNION
			(SELECT distinct postcode, postcode FROM dem.urb WHERE postcode %(fragment_condition)s limit 20)"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query)
		mp.setThresholds(2, 3, 15)
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.SetToolTipString(_("Type or select a zip code (postcode).\n\nUse e.g. '?' if unknown."))
		self.matcher = mp
#============================================================
class cStreetPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):
		context = {
			u'ctxt_zip': {
				u'where_part': u'AND zip ILIKE %(zip)s',
				u'placeholder': u'zip'
			}
		}
		query = u"""
	SELECT
		data,
		field_label,
		list_label
	FROM (

			SELECT DISTINCT ON (data)
				street AS data,
				street AS field_label,
				street || ' (' || zip || ', ' || urb || coalesce(', ' || suburb, '') || ', ' || l10n_country || ')' AS list_label,
				1 AS rank
			FROM dem.v_zip2data
			WHERE
				street %(fragment_condition)s
				%(ctxt_zip)s

		UNION ALL

			SELECT DISTINCT ON (data)
				name AS data,
				name AS field_label,
				name || ' (' || postcode || coalesce(', ' || suburb, '') || ')' AS list_label,
				2 AS rank
			FROM dem.street
			WHERE
				name %(fragment_condition)s

	) AS matching_streets
	ORDER BY rank, field_label
	LIMIT 50"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query, context=context)
		mp.setThresholds(3, 5, 8)
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.unset_context(context = u'zip')

		self.SetToolTipString(_('Type or select a street.'))
		self.capitalisation_mode = gmTools.CAPS_FIRST
		self.matcher = mp
#============================================================
class cSuburbPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		query = """
SELECT DISTINCT ON (suburb) suburb, suburb
FROM dem.street
WHERE suburb %(fragment_condition)s
ORDER BY suburb
LIMIT 50
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
	SELECT DISTINCT ON (rank, data)
		data,
		field_label,
		list_label
	FROM (

			SELECT
				urb AS data,
				urb AS field_label,
				urb || ' (' || zip || ', ' || state || ', ' || l10n_country || ')' AS list_label,
				1 AS rank
			FROM dem.v_zip2data
			WHERE
				urb %(fragment_condition)s
				%(ctxt_zip)s

		UNION ALL

			SELECT
				name AS data,
				name AS field_label,
				name || ' (' || postcode ||')' AS list_label,
				2 AS rank
			FROM dem.urb
			WHERE
				name %(fragment_condition)s

	) AS matching_urbs
	ORDER BY rank, data
	LIMIT 50"""
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
# address phrasewheels and widgets
#============================================================
def manage_addresses(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#------------------------------------------------------------
	def delete(address):
		return gmDemographicRecord.delete_address(pk_address = address['pk_address'])
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
	return gmListWidgets.get_choices_from_list (
		parent = parent,
		caption = _('Showing addresses registered in GNUmed.'),
		columns = cols,
		single_selection = True,
		refresh_callback = refresh,
		delete_callback = delete
	)
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
		self.address_is_searchable = False

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
			if self.__type_is_editable:
				self._PRW_type.SetFocus()
			else:
				self._PRW_zip.SetFocus()
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

		if self.__type_is_editable:
			self._PRW_type.SetFocus()
		else:
			self._PRW_zip.SetFocus()
		return
	#--------------------------------------------------------
	def save(self):
		"""Links address to patient or org, creating new address if necessary"""

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
	def _get_address_is_searchable(self):
		return self.__address_is_searchable

	def _set_address_is_searchable(self, address_is_searchable):
		# always set tot FALSE when self.mode == 'new'
		self.__address_is_searchable = address_is_searchable
		self._PRW_address_searcher.Enable(address_is_searchable)
		self._PRW_address_searcher.Show(address_is_searchable)
		self._LBL_search.Show(address_is_searchable)

	address_is_searchable = property(_get_address_is_searchable, _set_address_is_searchable)
	#--------------------------------------------------------
	def _get_address(self):
		return self.__address

	def _set_address(self, address):
		self.__address = address
		self.refresh()

	address = property(_get_address, _set_address)

#============================================================
class cAddressTypePhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		query = u"""
SELECT id, type FROM ((
	SELECT id, _(name) AS type, 1 AS rank
	FROM dem.address_type
	WHERE _(name) %(fragment_condition)s
) UNION (
	SELECT id, name AS type, 2 AS rank
	FROM dem.address_type
	WHERE name %(fragment_condition)s
)) AS ur
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
class cAddressMatchProvider(gmMatchProvider.cMatchProvider_SQL2):

	def __init__(self):

		query = u"""
SELECT * FROM (
	(SELECT
		pk_address AS data,
		(street || ' ' || number || coalesce(' (' || subunit || ')', '') || ', '
				|| urb || coalesce(' (' || suburb || ')', '') || ', '
				|| postcode || ', '
				|| code_country
		) AS field_label,
		(street || ' ' || number || coalesce(' (' || subunit || ')', '') || ', '
				|| urb || coalesce(' (' || suburb || ')', '') || ', '
				|| postcode || ', '
				|| l10n_state || ', '
				|| l10n_country
				|| coalesce(', ' || notes_street, '')
				|| coalesce(', ' || notes_subunit, '')
		) AS list_label
	FROM
		dem.v_address
	WHERE
		street %(fragment_condition)s

	) UNION (

	SELECT
		pk_address AS data,
		(street || ' ' || number || coalesce(' (' || subunit || ')', '') || ', '
				|| urb || coalesce(' (' || suburb || ')', '') || ', '
				|| postcode || ', '
				|| code_country
		) AS field_label,
		(street || ' ' || number || coalesce(' (' || subunit || ')', '') || ', '
				|| urb || coalesce(' (' || suburb || ')', '') || ', '
				|| postcode || ', '
				|| l10n_state || ', '
				|| l10n_country
				|| coalesce(', ' || notes_street, '')
				|| coalesce(', ' || notes_subunit, '')
		) AS list_label
	FROM
		dem.v_address
	WHERE
		postcode_street %(fragment_condition)s

	) UNION (

	SELECT
		pk_address AS data,
		(street || ' ' || number || coalesce(' (' || subunit || ')', '') || ', '
				|| urb || coalesce(' (' || suburb || ')', '') || ', '
				|| postcode || ', '
				|| code_country
		) AS field_label,
		(street || ' ' || number || coalesce(' (' || subunit || ')', '') || ', '
				|| urb || coalesce(' (' || suburb || ')', '') || ', '
				|| postcode || ', '
				|| l10n_state || ', '
				|| l10n_country
				|| coalesce(', ' || notes_street, '')
				|| coalesce(', ' || notes_subunit, '')
		) AS list_label
	FROM
		dem.v_address
	WHERE
		postcode_urb %(fragment_condition)s
	)
) AS matching_addresses
ORDER BY list_label
LIMIT 50"""

		gmMatchProvider.cMatchProvider_SQL2.__init__(self, queries = query)

		self.setThresholds(2, 4, 6)
#		self.word_separators = u'[ \t]+'

		self._SQL_data2match = u"""
	SELECT
		pk_address AS data,
		(street || ' ' || number || coalesce(' (' || subunit || ')', '') || ', '
				|| urb || coalesce(' (' || suburb || ')', '') || ', '
				|| postcode || ', '
				|| code_country
		) AS field_label,
		(street || ' ' || number || coalesce(' (' || subunit || ')', '') || ', '
				|| urb || coalesce(' (' || suburb || ')', '') || ', '
				|| postcode || ', '
				|| l10n_state || ', '
				|| l10n_country
				|| coalesce(', ' || notes_street, '')
				|| coalesce(', ' || notes_subunit, '')
		) AS list_label
	FROM
		dem.v_address
	WHERE
		pk_address = %(pk)s
	"""

#============================================================
class cAddressPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.matcher = cAddressMatchProvider()
		self.SetToolTipString(_('Select an address by postcode or street name.'))
		self.selection_only = True
		self.__address = None
		self.__old_pk = None
	#--------------------------------------------------------
	def _get_data_tooltip(self):
		adr = self.address
		if adr is None:
			return None
		return u'\n'.join(adr.format())
	#--------------------------------------------------------
	def _data2instance(self):
		return gmDemographicRecord.cAddress(aPK_obj = self.GetData())
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def __get_address(self):
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

	def __set_address(self, address):
		if address is None:
			self.__old_pk = None
			self.__address = None
			self.SetText(u'', None)
			return
		if isinstance(address, gmDemographicRecord.cAddress):
			self.__old_pk = address['pk_address']
			self.__address = address
			pk = self.__old_pk
		else:
			self.__old_pk = None
			self.__address = None
			pk = address
		match = self.matcher.get_match_by_data(data = pk)
		if match is None:
			raise ValueError(u'[%s]: cannot match address [#%s]' % (self.__class__.__name__, pk))
		self.SetText(match['field_label'], pk)

	address = property(__get_address, __set_address)

#================================================================
# main
#----------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()
	from Gnumed.business import gmPersonSearch

	#--------------------------------------------------------
	def test_country_prw():
		app = wx.PyWidgetTester(size = (200, 50))
		pw = cCountryPhraseWheel(app.frame, -1)
		app.frame.Show(True)
		app.MainLoop()
	#--------------------------------------------------------
	def test_state_prw():
		app = wx.PyWidgetTester(size = (200, 50))
		pw = cStateSelectionPhraseWheel(app.frame, -1)
		pw.set_context(context = u'zip', val = u'04318')
		pw.set_context(context = u'country', val = u'Deutschland')
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
	def test_address_ea_pnl():
		app = wx.PyWidgetTester(size = (600, 400))
		app.SetWidget(cAddressEditAreaPnl, address = gmDemographicRecord.cAddress(aPK_obj = 1))
		app.MainLoop()
	#--------------------------------------------------------
	#test_address_type_prw()
	#test_zipcode_prw()
	#test_state_prw()
	#test_street_prw()
	#test_suburb_prw()
	#test_country_prw()
	#test_urb_prw()
	#test_address_ea_pnl()
	test_address_prw()

#================================================================
