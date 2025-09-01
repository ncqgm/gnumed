"""GNUmed generic address related widgets."""
#================================================================
__author__ = 'karsten.hilbert@gmx.net'
__license__ = 'GPL v2 or later (details at https://www.gnu.org)'

# stdlib
import logging, sys


# 3rd party
import wx


# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x

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
			'ctxt_zip': {
				'where_part': 'and zip ilike %(zip)s',
				'placeholder': 'zip'
			}
		}
		query = """
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
		mp._SQL_data2match = """
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

		self.unset_context(context = 'zip')
		self.SetToolTip(_('Type or select a country.'))
		self.capitalisation_mode = gmTools.CAPS_FIRST
		self.selection_only = True

#============================================================
# region related widgets / functions
#============================================================
def configure_default_region(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	regs = gmDemographicRecord.get_regions()

	gmCfgWidgets.configure_string_from_list_option (
		parent = parent,
		message = _('Select the default region (state/province/county/territory/arrondissement/prefecture/department/kanton/...) for new persons.\n'),
		option = 'person.create.default_region',
		bias = 'user',
		choices = [ (r['l10n_country'], r['l10n_region'], r['code_region']) for r in regs ],
		columns = [_('Country'), _('Region'), _('Code')],
		data = [ r['region'] for r in regs ]
	)
#============================================================
def edit_region(parent=None, region=None):
	ea = cProvinceEAPnl(parent, -1, region = region)
	dlg = gmEditArea.cGenericEditAreaDlg2(parent, -1, edit_area = ea, single_entry = (region is not None))
	dlg.SetTitle(gmTools.coalesce(region, _('Adding region'), _('Editing region')))
	result = dlg.ShowModal()
	dlg.DestroyLater()
	return (result == wx.ID_OK)
#============================================================
def delete_region(parent=None, region=None):

	msg = _(
		'Are you sure you want to delete this region ?\n'
		'\n'
		'Deletion will only work if this region is not\n'
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
		caption = _('Deleting region'),
		question = msg,
		show_checkbox = True,
		checkbox_msg = _('delete related townships'),
		checkbox_tooltip = tt,
		button_defs = [
			{'label': _('Yes, delete'), 'tooltip': _('Delete region and possibly related townships.'), 'default': False},
			{'label': _('No'), 'tooltip': _('No, do NOT delete anything.'), 'default': True}
		]
	)

	decision = dlg.ShowModal()
	if decision != wx.ID_YES:
		dlg.DestroyLater()
		return False

	include_urbs = dlg.checkbox_is_checked()
	dlg.DestroyLater()

	return gmDemographicRecord.delete_region(region = region, delete_urbs = include_urbs)
#============================================================
def manage_regions(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#------------------------------------------------------------
	def delete(region=None):
		return delete_region(parent = parent, region = region['pk_region'])
	#------------------------------------------------------------
	def edit(region=None):
		return edit_region(parent = parent, region = region)
	#------------------------------------------------------------
	def refresh(lctrl):
		wx.BeginBusyCursor()
		provinces = gmDemographicRecord.get_regions()
		lctrl.set_string_items([ (p['l10n_country'], p['l10n_region']) for p in provinces ])
		lctrl.set_data(provinces)
		wx.EndBusyCursor()
	#------------------------------------------------------------
	msg = _(
		'This list shows the regions known to GNUmed.\n'
		'\n'
		'In your jurisdiction "region" may correspond to either of "state",\n'
		'"county", "province", "territory", "arrondissement", "department,"\n'
		'"prefecture", "kanton", or some such term.\n'
	)

	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = msg,
		caption = _('Editing regions ...'),
		columns = [_('Country'), _('Region')],
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
			'ctxt_country_name': {
				'where_part': 'AND l10n_country ILIKE %(country_name)s OR country ILIKE %(country_name)s',
				'placeholder': 'country_name'
			},
			'ctxt_zip': {
				'where_part': 'AND zip ilike %(zip)s',
				'placeholder': 'zip'
			},
			'ctxt_country_code': {
				'where_part': 'AND country IN (SELECT code FROM dem.country WHERE _(name) ILIKE %(country_name)s OR name ILIKE %(country_name)s)',
				'placeholder': 'country_name'
			}
		}

		query = """
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
			-- 1: find regions based on name, context: zip and country name
			SELECT
				code_region AS data,
				region AS field_label,
				region || ' (' || code_region || '), ' || l10n_country || ' (' || code_country || ')' AS list_label,
				1 AS rank
			FROM dem.v_zip2data
			WHERE
				region %(fragment_condition)s
				%(ctxt_country_name)s
				%(ctxt_zip)s

		UNION ALL

			-- 2: find regions based on code, context: zip and country name
			SELECT
				code_region AS data,
				region AS field_label,
				code_region || ': ' || region || ' (' || l10n_country || ', ' || code_country || ')' AS list_label,
				2 AS rank
			FROM dem.v_zip2data
			WHERE
				code_region %(fragment_condition)s
				%(ctxt_country_name)s
				%(ctxt_zip)s

		UNION ALL

			-- 3: find regions based on name, context: country
			SELECT
				code AS data,
				name AS field_label,
				name || ' (' || code || '), ' || country AS list_label,
				3 AS rank
			FROM dem.region
			WHERE
				name %(fragment_condition)s
				%(ctxt_country_code)s

		UNION ALL

			-- 4: find regions based on code, context: country
			SELECT
				code AS data,
				name AS field_label,
				code || ': ' || name || ', ' || country AS list_label,
				3 AS rank
			FROM dem.region
			WHERE
				code %(fragment_condition)s
				%(ctxt_country_code)s

	) AS candidate_regions
) AS distinct_matches
ORDER BY rank, list_label
LIMIT 50"""

		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query, context=context)
		mp.setThresholds(2, 5, 6)
		mp.word_separators = '[ \t]+'
		self.matcher = mp

		self.unset_context(context = 'zip')
		self.unset_context(context = 'country_name')
		self.SetToolTip(_('Type or select a region (state/province/county/territory/arrondissement/prefecture/department/kanton/...).'))
		self.capitalisation_mode = gmTools.CAPS_FIRST
		self.selection_only = True
#====================================================================
from Gnumed.wxGladeWidgets import wxgProvinceEAPnl

class cProvinceEAPnl(wxgProvinceEAPnl.wxgProvinceEAPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwargs):

		try:
			data = kwargs['region']
			del kwargs['region']
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
		self._PRW_region.selection_only = False
	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):

		validity = True

		if self._PRW_region.GetData() is None:
			if self._PRW_region.GetValue().strip() == '':
				validity = False
				self._PRW_region.display_as_valid(False)
			else:
				self._PRW_region.display_as_valid(True)
		else:
			self._PRW_region.display_as_valid(True)

		if self._PRW_region.GetData() is None:
			if self._TCTRL_code.GetValue().strip() == '':
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
		gmDemographicRecord.create_region (
			name = self._PRW_region.GetValue().strip(),
			code = self._TCTRL_code.GetValue().strip(),
			country = self._PRW_country.GetData()
		)

		# EA is refreshed automatically after save, so need this ...
		self.data = {
			'l10n_region' : self._PRW_region.GetValue().strip(),
			'code_region' : self._TCTRL_code.GetValue().strip(),
			'l10n_country' : self._PRW_country.GetValue().strip(),
			'code_country' : self._PRW_country.GetData().strip()
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
		self._PRW_region.SetText()
		self._TCTRL_code.SetValue('')
		self._PRW_country.SetText()

		self._PRW_region.SetFocus()
	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		self._PRW_region.SetText(self.data['l10n_region'], self.data['code_region'])
		self._TCTRL_code.SetValue(self.data['code_region'])
		self._PRW_country.SetText(self.data['l10n_country'], self.data['code_country'])

		self._PRW_region.SetFocus()
	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._PRW_region.SetText()
		self._TCTRL_code.SetValue('')
		self._PRW_country.SetText(self.data['l10n_country'], self.data['code_country'])

		self._PRW_region.SetFocus()

#============================================================
# other address parts phrasewheels and widgets
#============================================================
class cZipcodePhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):
		# FIXME: add possible context
		query = """(
			SELECT DISTINCT ON (list_label)
				postcode AS data,
				postcode || ' (' || name || ')' AS list_label,
				postcode AS field_label
			FROM dem.street
			WHERE
				postcode %(fragment_condition)s
			ORDER BY list_label
			LIMIT 20

		) UNION (

			SELECT DISTINCT ON (list_label)
				postcode AS data,
				postcode || ' (' || name || ')' AS list_label,
				postcode AS field_label
			FROM dem.urb
			WHERE
				postcode %(fragment_condition)s
			ORDER BY list_label
			LIMIT 20
		)"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query)
		mp.setThresholds(2, 3, 15)
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.SetToolTip(_("Type or select a zip code (postcode).\n\nUse e.g. '?' if unknown."))
		self.matcher = mp
#============================================================
class cStreetPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):
		context = {
			'ctxt_zip': {
				'where_part': 'AND zip ILIKE %(zip)s',
				'placeholder': 'zip'
			}
		}
		query = """
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
				name || ' (' || coalesce(postcode, '') || coalesce(', ' || suburb, '') || ')' AS list_label,
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
		self.unset_context(context = 'zip')

		self.SetToolTip(_('Type or select a street.'))
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

		self.SetToolTip(_('Type or select the suburb.'))
		self.capitalisation_mode = gmTools.CAPS_FIRST
		self.matcher = mp
#============================================================
class cUrbPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):
		context = {
			'ctxt_zip': {
				'where_part': 'and zip ilike %(zip)s',
				'placeholder': 'zip'
			}
		}
		query = """
	SELECT DISTINCT ON (rank, data)
		data,
		field_label,
		list_label
	FROM (

			SELECT
				urb AS data,
				urb AS field_label,
				urb || ' (' || zip || ', ' || region || ', ' || l10n_country || ')' AS list_label,
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
		self.unset_context(context = 'zip')

		self.SetToolTip(_('Type or select a city/town/village/dwelling.'))
		self.capitalisation_mode = gmTools.CAPS_FIRST
		self.matcher = mp
#============================================================
# address type related widgets
#============================================================
class cAddressTypePhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		query = """
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
		mp.word_separators = '[ \t]+'
		gmPhraseWheel.cPhraseWheel.__init__ (
			self,
			*args,
			**kwargs
		)
		self.matcher = mp
		self.SetToolTip(_('Select the type of address.'))
#		self.capitalisation_mode = gmTools.CAPS_FIRST
		self.selection_only = True
	#--------------------------------------------------------
#	def GetData(self, can_create=False):
#		if self.data is None:
#			if can_create:
#				self.data = gmDocuments.create_document_type(self.GetValue().strip())['pk_doc_type']	# FIXME: error handling
#		return self.data

#============================================================
# address phrasewheels and widgets
#============================================================
def manage_addresses(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#------------------------------------------------------------
	def calculate_tooltip(address):
		return '\n'.join(address.format())
	#------------------------------------------------------------
	def delete(address):
		return gmDemographicRecord.delete_address(pk_address = address['pk_address'])
	#------------------------------------------------------------
	def refresh(lctrl):
		adrs = gmDemographicRecord.get_addresses(order_by = 'l10n_country, urb, street, number, subunit')
		items = [ [
				a['street'],
				gmTools.coalesce(a['notes_street'], ''),
				a['number'],
				gmTools.coalesce(a['subunit'], ''),
				a['postcode'],
				a['urb'],
				gmTools.coalesce(a['suburb'], ''),
				a['l10n_region'],
				a['l10n_country'],
				gmTools.coalesce(a['notes_subunit'], '')
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
		_('Community'),
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
		delete_callback = delete,
		list_tooltip_callback = calculate_tooltip
	)

#============================================================
from Gnumed.wxGladeWidgets import wxgGenericAddressEditAreaPnl

class cAddressEAPnl(wxgGenericAddressEditAreaPnl.wxgGenericAddressEditAreaPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwargs):

		try:
			data = kwargs['address']
			del kwargs['address']
		except KeyError:
			data = None

		self.address_holder = None
		self.__type_is_editable = True
		self.__address_is_searchable = False

		wxgGenericAddressEditAreaPnl.wxgGenericAddressEditAreaPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		self.type_is_editable = True
		self.address_is_searchable = False

		# Code using this mixin should set mode and data
		# after instantiating the class:
		self.mode = 'new'
		self.data = data
		if data is not None:
			self.mode = 'edit'

		self.__init_ui()
	#----------------------------------------------------------------
	def __init_ui(self):
		self._PRW_zip.add_callback_on_lose_focus(self._on_zip_set)
		self._PRW_country.add_callback_on_lose_focus(self._on_country_set)
	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):

		validity = True

		# if any field is filled, all must be filled, so track that
		is_any_field_filled = False

		# check by string
		required_fields = [
			self._PRW_urb,
			self._TCTRL_number,
			self._PRW_street,
			self._PRW_zip
		]
		if self.__type_is_editable:
			required_fields.insert(0, self._PRW_type)
		for field in required_fields:
			if len(field.GetValue().strip()) == 0:
				if is_any_field_filled:
					self.display_ctrl_as_valid(field, False)
					field.SetFocus()
					gmGuiHelpers.gm_show_error (
						_('Address details must be filled in completely or not at all.'),
						_('Saving contact data')
					)
					validity = False
			else:
				is_any_field_filled = True
				self.display_ctrl_as_valid(field, True)

		# check by data
		required_fields = (
			self._PRW_country,
			self._PRW_state
		)
		for field in required_fields:
			if field.GetData() is None:
				if is_any_field_filled:
					self.display_ctrl_as_valid(field, False)
					field.SetFocus()
					gmGuiHelpers.gm_show_error (
						_('Address details must be filled in completely or not at all.'),
						_('Saving contact data')
					)
					validity = False
			else:
				is_any_field_filled = True
				self.display_ctrl_as_valid(field, True)

		return validity
	#----------------------------------------------------------------
	def _save_as_new(self):
		try:
			# will create or return address
			address = gmDemographicRecord.create_address (
				country_code = self._PRW_country.GetData(),
				region_code = self._PRW_state.GetData(),
				urb = self._PRW_urb.GetValue().strip(),
				suburb = gmTools.none_if(self._PRW_suburb.GetValue().strip(), ''),
				postcode = self._PRW_zip.GetValue().strip(),
				street = self._PRW_street.GetValue().strip(),
				number = self._TCTRL_number.GetValue().strip(),
				subunit = gmTools.none_if(self._TCTRL_subunit.GetValue().strip(), '')
			)
		except Exception:
			_log.exception('cannot save address')
			gmGuiHelpers.gm_show_error (
				_('Cannot save address.\n\n'
				  'Does the region [%s]\n'
				  'exist in country [%s] ?'
				) % (
					self._PRW_state.GetValue().strip(),
					self._PRW_country.GetValue().strip()
				),
				_('Saving address')
			)
			return False

		# link address to holder (there better be one)
		linked_address = self.address_holder.link_address(id_type = self._PRW_type.GetData(), address = address)
		if linked_address['pk_address'] != address['pk_address']:
			raise ValueError('problem linking address to person or org')

		address['notes_street'] = gmTools.none_if(self._TCTRL_notes_street.GetValue().strip(), '')
		address['notes_subunit'] = gmTools.none_if(self._TCTRL_notes_subunit.GetValue().strip(), '')
		address.save()

		linked_address.refetch_payload()
		self.data = linked_address

		return True
	#----------------------------------------------------------------
	def _save_as_update(self):
		# do not update existing address, rather
		# create new one or get corresponding
		# address should it exist
		try:
			created_or_loaded_address = gmDemographicRecord.create_address (
				country_code = self._PRW_country.GetData(),
				region_code = self._PRW_state.GetData(),
				urb = self._PRW_urb.GetValue().strip(),
				suburb = gmTools.none_if(self._PRW_suburb.GetValue().strip(), ''),
				postcode = self._PRW_zip.GetValue().strip(),
				street = self._PRW_street.GetValue().strip(),
				number = self._TCTRL_number.GetValue().strip(),
				subunit = gmTools.none_if(self._TCTRL_subunit.GetValue().strip(), '')
			)
		except Exception:
			_log.exception('cannot save address')
			gmGuiHelpers.gm_show_error (
				_('Cannot save address.\n\n'
				  'Does the region [%s]\n'
				  'exist in country [%s] ?'
				) % (
					self._PRW_state.GetValue().strip(),
					self._PRW_country.GetValue().strip()
				),
				_('Saving address')
			)
			return False

		# link address to holder (there better be one)
		linked_address = self.address_holder.link_address(id_type = self._PRW_type.GetData(), address = created_or_loaded_address)
		if linked_address['pk_address'] != created_or_loaded_address['pk_address']:
			raise ValueError('problem linking address to person or org')

		created_or_loaded_address['notes_street'] = gmTools.none_if(self._TCTRL_notes_street.GetValue().strip(), '')
		created_or_loaded_address['notes_subunit'] = gmTools.none_if(self._TCTRL_notes_subunit.GetValue().strip(), '')
		created_or_loaded_address.save_payload()
		linked_address.refetch_payload()
		self.data = linked_address

		return True
	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._PRW_type.SetText('', None)
		self._PRW_zip.SetText('', None)
		self._PRW_street.SetText('', None)
		self._TCTRL_notes_street.SetValue('')
		self._TCTRL_number.SetValue('')
		self._TCTRL_subunit.SetValue('')
		self._PRW_suburb.SetText('', None)
		self._PRW_urb.SetText('', None)
		self._PRW_state.SetText('', None)
		self._PRW_country.SetText('', None)
		self._TCTRL_notes_subunit.SetValue('')

		if self.__type_is_editable:
			self._PRW_type.SetFocus()
		else:
			self._PRW_zip.SetFocus()
	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._refresh_as_new()

		self._PRW_zip.SetText(self.data['postcode'])
		self._PRW_street.SetText(self.data['street'], data = self.data['street'])
		self._PRW_suburb.SetText(gmTools.coalesce(self.data['suburb'], ''))
		self._PRW_urb.SetText(self.data['urb'], data = self.data['urb'])
		self._PRW_state.SetText(self.data['l10n_region'], data = self.data['code_region'])
		self._PRW_country.SetText(self.data['l10n_country'], data = self.data['code_country'])

		if self.__type_is_editable:
			self._PRW_type.SetFocus()
		else:
			self._TCTRL_number.SetFocus()
	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		if self.__type_is_editable:
			self._PRW_type.SetText(self.data['l10n_address_type'])
		else:
			self._PRW_type.SetText('', None)
		self._PRW_zip.SetText(self.data['postcode'])
		self._PRW_street.SetText(self.data['street'], data = self.data['street'])
		self._TCTRL_notes_street.SetValue(gmTools.coalesce(self.data['notes_street'], ''))
		self._TCTRL_number.SetValue(self.data['number'])
		self._TCTRL_subunit.SetValue(gmTools.coalesce(self.data['subunit'], ''))
		self._PRW_suburb.SetText(gmTools.coalesce(self.data['suburb'], ''))
		self._PRW_urb.SetText(self.data['urb'], data = self.data['urb'])
		self._PRW_state.SetText(self.data['l10n_region'], data = self.data['code_region'])
		self._PRW_country.SetText(self.data['l10n_country'], data = self.data['code_country'])
		self._TCTRL_notes_subunit.SetValue(gmTools.coalesce(self.data['notes_subunit'], ''))

		if self.__type_is_editable:
			self._PRW_type.SetFocus()
		else:
			self._PRW_zip.SetFocus()
	#----------------------------------------------------------------
	# event handling
	#----------------------------------------------------------------
	def _on_zip_set(self):
		"""Set the street, town, region and country according to entered zip code."""
		zip_code = self._PRW_zip.GetValue()
		if zip_code.strip() == '':
			self._PRW_street.unset_context(context = 'zip')
			self._PRW_urb.unset_context(context = 'zip')
			self._PRW_state.unset_context(context = 'zip')
			self._PRW_country.unset_context(context = 'zip')
		else:
			self._PRW_street.set_context(context = 'zip', val = zip_code)
			self._PRW_urb.set_context(context = 'zip', val = zip_code)
			self._PRW_state.set_context(context = 'zip', val = zip_code)
			self._PRW_country.set_context(context = 'zip', val = zip_code)
	#----------------------------------------------------------------
	def _on_country_set(self):
		"""Set the regions according to entered country."""
		country = self._PRW_country.GetData()
		if country is None:
			self._PRW_state.unset_context(context = 'country')
		else:
			self._PRW_state.set_context(context = 'country', val = country)
	#----------------------------------------------------------------
	# properties
	#----------------------------------------------------------------
	def _get_type_is_editable(self):
		return self.__type_is_editable

	def _set_type_is_editable(self, type_is_editable):
		self.__type_is_editable = type_is_editable
		self._PRW_type.Enable(type_is_editable)
		self._PRW_type.Show(type_is_editable)
		self._LBL_type.Show(type_is_editable)

	type_is_editable = property(_get_type_is_editable, _set_type_is_editable)
	#----------------------------------------------------------------
	def _get_address_is_searchable(self):
		return self.__address_is_searchable

	def _set_address_is_searchable(self, address_is_searchable):
		# FIXME: always set to FALSE when self.mode == 'new' ?
		self.__address_is_searchable = address_is_searchable
		self._PRW_address_searcher.Enable(address_is_searchable)
		self._PRW_address_searcher.Show(address_is_searchable)
		self._LBL_search.Show(address_is_searchable)

	address_is_searchable = property(_get_address_is_searchable, _set_address_is_searchable)
	#----------------------------------------------------------------
	def _get_address(self):
		return self.data

	def _set_address(self, address):
		self.data = address

	address = property(_get_address, _set_address)

#============================================================
class cAddressMatchProvider(gmMatchProvider.cMatchProvider_SQL2):

	def __init__(self):

		query = """
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
				|| l10n_region || ', '
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
				|| l10n_region || ', '
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
				|| l10n_region || ', '
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

		self._SQL_data2match = """
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
				|| l10n_region || ', '
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
		self.SetToolTip(_('Select an address by postcode or street name.'))
		self.selection_only = True
		self.__address = None
		self.__old_pk = None
	#--------------------------------------------------------
	def _get_data_tooltip(self):
		adr = self.address
		if adr is None:
			return None
		return '\n'.join(adr.format())
	#--------------------------------------------------------
	def _data2instance(self, link_obj=None):
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
			self.SetText('', None)
			return
		if isinstance(address, (gmDemographicRecord.cAddress, gmDemographicRecord.cPatientAddress)):
			self.__old_pk = address['pk_address']
			self.__address = address
			pk = self.__old_pk
		else:
			self.__old_pk = None
			self.__address = None
			pk = address
		match = self.matcher.get_match_by_data(data = pk)
		if match is None:
			raise ValueError('[%s]: cannot match address [#%s]' % (self.__class__.__name__, pk))
		self.SetText(match['field_label'], pk)

	address = property(__get_address, __set_address)

	#--------------------------------------------------------
#	def __get_person_address(self):
#		pk = self.GetData()
#		if pk is None:
#			self.__address = None
#			return None
#		if self.__address is None:
#			self.__old_pk = pk
#			self.__address = gmDemographicRecord.cPatientAddress(aPK_obj = pk xxxxxxxxx)
#		else:
#			if pk != self.__old_pk:
#				self.__old_pk = pk
#				self.__address = gmDemographicRecord.cPatientAddress(aPK_obj = pk xxxxxxxxxxx)
#		return self.__address
#
#	xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
#	must have access to pk_identity
#	person_address = property(__get_person_address)

#============================================================
from Gnumed.wxGladeWidgets import wxgAddressSelectionDlg

class cAddressSelectionDlg(wxgAddressSelectionDlg.wxgAddressSelectionDlg):

	def __init__(self, *args, **kwargs):
		wxgAddressSelectionDlg.wxgAddressSelectionDlg.__init__(self, *args, **kwargs)
		self._PRW_address_searcher.SetFocus()
	#--------------------------------------------------------
	def _get_address(self):
		return self._PRW_address_searcher.address

	address = property(_get_address)
	#--------------------------------------------------------
	def _set_message(self, msg):
		self._LBL_msg.SetLabel(msg)

	message = property(lambda x:x, _set_message)
	#--------------------------------------------------------
	def _on_manage_addresses_button_pressed(self, event):
		event.Skip()
		manage_addresses(parent = self)

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
	#from Gnumed.business import gmPersonSearch

	#--------------------------------------------------------
#	def test_country_prw():
#		app = wx.PyWidgetTester(size = (200, 50))
#		cCountryPhraseWheel(app.frame, -1)
#		app.frame.Show(True)
#		app.MainLoop()
	#--------------------------------------------------------
#	def test_region_prw():
#		app = wx.PyWidgetTester(size = (200, 50))
#		pw = cStateSelectionPhraseWheel(app.frame, -1)
#		pw.set_context(context = 'zip', val = '04318')
#		pw.set_context(context = 'country', val = 'Deutschland')
#		app.frame.Show(True)
#		app.MainLoop()
	#--------------------------------------------------------
#	def test_zipcode_prw():
#		app = wx.PyWidgetTester(size = (200, 50))
#		cZipcodePhraseWheel(app.frame, -1)
#		app.frame.Show(True)
#		app.MainLoop()
	#--------------------------------------------------------
#	def test_street_prw():
#		app = wx.PyWidgetTester(size = (200, 50))
#		cStreetPhraseWheel(app.frame, -1)
##		pw.set_context(context = u'zip', val = u'04318')
#		app.frame.Show(True)
#		app.MainLoop()
	#--------------------------------------------------------
#	def test_suburb_prw():
#		app = wx.PyWidgetTester(size = (200, 50))
#		cSuburbPhraseWheel(app.frame, -1)
#		app.frame.Show(True)
#		app.MainLoop()
	#--------------------------------------------------------
#	def test_urb_prw():
#		app = wx.PyWidgetTester(size = (200, 50))
#		pw = cUrbPhraseWheel(app.frame, -1)
#		app.frame.Show(True)
#		pw.set_context(context = 'zip', val = '04317')
#		app.MainLoop()
	#--------------------------------------------------------
#	def test_address_type_prw():
#		app = wx.PyWidgetTester(size = (200, 50))
#		cAddressTypePhraseWheel(app.frame, -1)
#		app.frame.Show(True)
#		app.MainLoop()
	#--------------------------------------------------------
#	def test_address_prw():
#		app = wx.PyWidgetTester(size = (200, 50))
#		cAddressPhraseWheel(app.frame, -1)
#		app.frame.Show(True)
#		app.MainLoop()
	#--------------------------------------------------------
#	def test_address_ea_pnl():
#		app = wx.PyWidgetTester(size = (600, 400))
#		app.SetWidget(cAddressEAPnl, address = gmDemographicRecord.cAddress(aPK_obj = 1))
#		app.MainLoop()
	#--------------------------------------------------------
	#test_address_type_prw()
	#test_zipcode_prw()
	#test_region_prw()
	#test_street_prw()
	#test_suburb_prw()
	#test_country_prw()
	#test_urb_prw()
	#test_address_ea_pnl()
#	test_address_prw()

#================================================================
