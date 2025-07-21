"""GNUmed patient creation widgets.

copyright: authors
"""
#============================================================
__author__ = "K.Hilbert"
__license__ = "GPL v2 or later (details at https://www.gnu.org)"

import logging
import sys
import datetime as pydt


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.pycommon import gmCfgDB
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmDispatcher

from Gnumed.business import gmPraxis
from Gnumed.business import gmPerson
from Gnumed.business import gmGender
from Gnumed.business import gmStaff
from Gnumed.business import gmDemographicRecord

from Gnumed.wxpython import gmEditArea
from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmEncounterWidgets
from Gnumed.wxpython.gmDemographicsWidgets import _validate_dob_field, _validate_tob_field, _empty_dob_allowed


_log = logging.getLogger('gm.patient')

#============================================================
def create_new_person(parent=None, activate=False):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	if activate:			# meaning we will switch away from the current patient if any
		msg = _(
			'Before creating a new person review the encounter details\n'
			'of the patient you just worked on:\n'
		)
		gmEncounterWidgets.sanity_check_encounter_of_active_patient(parent = parent, msg = msg)

		msg = _('Edit the current encounter of the patient you are ABOUT TO LEAVE:')

	def_region = gmCfgDB.get4user (
		option = 'person.create.default_region',
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace
	)
	def_country = None

	if def_region is None:
		def_country = gmCfgDB.get4user (
			option = 'person.create.default_country',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace
		)
	else:
		countries = gmDemographicRecord.get_country_for_region(region = def_region)
		if len(countries) == 1:
			def_country = countries[0]['code_country']

	ea = cNewPatientEAPnl(parent, -1, country = def_country, region = def_region)
	dlg = gmEditArea.cGenericEditAreaDlg2(parent, -1, edit_area = ea, single_entry = True)
	dlg.SetTitle(_('Adding new person'))
	ea._PRW_lastname.SetFocus()
	result = dlg.ShowModal()
	pat = ea.data
	dlg.DestroyLater()

	if result != wx.ID_OK:
		return False

	_log.debug('created new person [%s]', pat.ID)

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

		# only if we would support None on selection_only's:
#		self._PRW_external_id_type.selection_only = True

		if self.default_country is not None:
			match = self._PRW_country._data2match(data = self.default_country)
			if match is not None:
				self._PRW_country.SetText(value = match['field_label'], data = match['data'])

		if self.default_region is not None:
			self._PRW_region.SetText(value = self.default_region)

		self._PRW_type.SetText(value = 'home')
		# FIXME: only use this if member of gm-doctors,
		# FIXME: other than that check fallback_primary_provider
		self._PRW_primary_provider.SetData(data = gmStaff.gmCurrentProvider()['pk_staff'])

		self._PRW_lastname.SetFocus()
	#----------------------------------------------------------------
	def _refresh_ext_id_warning(self):
		id_type = self._PRW_external_id_type.GetData()
		if id_type is None:
			self._LBL_id_exists.SetLabel('')
			return
		val = self._TCTRL_external_id_value.GetValue().strip()
		if val == '':
			self._LBL_id_exists.SetLabel('')
			return
		if gmPerson.external_id_exists(pk_issuer = id_type, value = val) > 0:
			self._LBL_id_exists.SetLabel(_('ID exists !'))
		else:
			self._LBL_id_exists.SetLabel('')
	#----------------------------------------------------------------
	def _refresh_dupe_warning(self):
		lname = self._PRW_lastname.GetValue().strip()
		if lname == '':
			self._LBL_person_exists.SetLabel('')
			return

		dob = self._PRW_dob.GetData()
		if dob is None:
			self._LBL_person_exists.SetLabel('')
			return

		#fname = gmTools.none_if(self._PRW_firstnames.GetValue().strip()[:1], '')
		fname = gmTools.none_if(self._PRW_firstnames.GetValue().strip(), '')
		no_of_dupes = gmPerson.get_potential_person_dupes(lastnames = lname, firstnames = fname, dob = dob)
		if no_of_dupes == 0:
			lbl = ''
		elif no_of_dupes == 1:
			lbl = _('A (one) "%s, %s (%s)" already exists.') % (
				lname,
				gmTools.coalesce(fname, '?', '%s %%s%s %s' % (gmTools.u_ellipsis, gmTools.u_ellipsis, gmTools.u_ellipsis)),
				gmDateTime.format_dob(dob, format = '%Y %b %d', none_string = _('unknown DOB'))
			)
		else:
			lbl = _('%s "%s, %s (%s)" already exist.') % (
				no_of_dupes,
				lname,
				gmTools.coalesce(fname, '?', '%s %%s%s %s' % (gmTools.u_ellipsis, gmTools.u_ellipsis, gmTools.u_ellipsis)),
				gmDateTime.format_dob(dob, format = '%Y %b %d', none_string = _('unknown DOB'))
			)
		self._LBL_person_exists.SetLabel(lbl)

	#----------------------------------------------------------------
	def __perhaps_invalidate_address_searcher(self, ctrl=None, field=None):

		adr = self._PRW_address_searcher.address
		if adr is None:
			return True

		if ctrl.GetValue().strip() != adr[field]:
			wx.CallAfter(self._PRW_address_searcher.SetText, value = '', data = None)
			return True

		return False
	#----------------------------------------------------------------
	def __set_fields_from_address_searcher(self):
		adr = self._PRW_address_searcher.address
		if adr is None:
			return True

		self._PRW_zip.SetText(value = adr['postcode'], data = adr['postcode'])

		self._PRW_street.SetText(value = adr['street'], data = adr['street'])
		self._PRW_street.set_context(context = 'zip', val = adr['postcode'])

		self._PRW_urb.SetText(value = adr['urb'], data = adr['urb'])
		self._PRW_urb.set_context(context = 'zip', val = adr['postcode'])

		self._PRW_region.SetText(value = adr['l10n_region'], data = adr['code_region'])
		self._PRW_region.set_context(context = 'zip', val = adr['postcode'])

		self._PRW_country.SetText(value = adr['l10n_country'], data = adr['code_country'])
		self._PRW_country.set_context(context = 'zip', val = adr['postcode'])

	#----------------------------------------------------------------
	def __identity_valid_for_save(self):
		validity = True

		# name fields
		if self._PRW_lastname.GetValue().strip() == '':
			validity = False
			gmDispatcher.send(signal = 'statustext', msg = _('Must enter lastname.'))
			self._PRW_lastname.display_as_valid(False)
		else:
			self._PRW_lastname.display_as_valid(True)

		if self._PRW_firstnames.GetValue().strip() == '':
			validity = False
			gmDispatcher.send(signal = 'statustext', msg = _('Must enter first name.'))
			self._PRW_firstnames.display_as_valid(False)
		else:
			self._PRW_firstnames.display_as_valid(True)

		# gender
		if self._PRW_gender.GetData() is None:
			validity = False
			gmDispatcher.send(signal = 'statustext', msg = _('Must select gender.'))
			self._PRW_gender.display_as_valid(False)
		else:
			self._PRW_gender.display_as_valid(True)

		# dob validation
		if not _validate_dob_field(self._PRW_dob):
			validity = False

		# TOB validation
		if _validate_tob_field(self._TCTRL_tob):
			self.display_ctrl_as_valid(ctrl = self._TCTRL_tob, valid = True)
		else:
			validity = False
			self.display_ctrl_as_valid(ctrl = self._TCTRL_tob, valid = False)

		# uniqueness
		if len(gmPerson.get_person_duplicates (
			lastnames = self._PRW_lastname.GetValue(),
			firstnames = self._PRW_firstnames.GetValue(),
			dob = self._PRW_dob.GetData(),
			gender = self._PRW_gender.GetData(),
			comment = self._TCTRL_comment.Value
		)) > 0:
			validity = False
			self.StatusText = _('Duplicate person. Modify name and/or DOB or use comment to make unique.')

		return validity

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
			self._PRW_type
		)
		no_of_filled_fields = 0

		for field in fields_to_fill:
			if field.GetValue().strip() != '':
				no_of_filled_fields += 1
				field.display_as_valid(True)

		# empty address ?
		if no_of_filled_fields == 0:
			if empty_address_is_valid:
				return True
			else:
				return None

		# incompletely filled address ?
		if no_of_filled_fields != len(fields_to_fill):
			for field in fields_to_fill:
				if field.GetValue().strip() == '':
					field.display_as_valid(False)
					field.SetFocus()
			msg = _('To properly create an address, all the related fields must be filled in.')
			gmGuiHelpers.gm_show_error(msg, _('Required fields'))
			return False

		# fields which must contain a selected item
		# FIXME: they must also contain an *acceptable combination* which
		# FIXME: can only be tested against the database itself ...
		strict_fields = (
			self._PRW_type,
			self._PRW_region,
			self._PRW_country
		)
		error = False
		for field in strict_fields:
			if field.GetData() is None:
				error = True
				field.display_as_valid(False)
				field.SetFocus()
			else:
				field.display_as_valid(True)

		if error:
			msg = _('This field must contain an item selected from the dropdown list.')
			gmGuiHelpers.gm_show_error(msg, _('Required fields'))
			return False

		return True
	#----------------------------------------------------------------
	def __register_interests(self):

		# identity
		self._PRW_lastname.add_callback_on_lose_focus(self._on_leaving_lastname)
		self._PRW_firstnames.add_callback_on_lose_focus(self._on_leaving_firstname)
		self._PRW_dob.add_callback_on_lose_focus(self._on_leaving_dob)

		# address
		self._PRW_address_searcher.add_callback_on_lose_focus(self._on_leaving_adress_searcher)

		# invalidate address searcher when any field edited
		self._PRW_street.add_callback_on_lose_focus(self._invalidate_address_searcher)
		self._TCTRL_number.Bind(wx.EVT_KILL_FOCUS, self._on_leaving_number)
		self._TCTRL_unit.Bind(wx.EVT_KILL_FOCUS, self._on_leaving_unit)
		self._PRW_urb.add_callback_on_lose_focus(self._invalidate_address_searcher)
		self._PRW_region.add_callback_on_lose_focus(self._invalidate_address_searcher)

		self._PRW_zip.add_callback_on_lose_focus(self._on_leaving_zip)
		self._PRW_country.add_callback_on_lose_focus(self._on_leaving_country)

		self._PRW_external_id_type.add_callback_on_lose_focus(callback = self._on_leaving_ext_id_type)
		self._TCTRL_external_id_value.add_callback_on_lose_focus(callback = self._on_leaving_ext_id_val)

	#----------------------------------------------------------------
	# event handlers
	#----------------------------------------------------------------
	def _on_leaving_ext_id_type(self):
		wx.CallAfter(self._refresh_ext_id_warning)
	#----------------------------------------------------------------
	def _on_leaving_ext_id_val(self):
		wx.CallAfter(self._refresh_ext_id_warning)
	#----------------------------------------------------------------
	def _on_leaving_lastname(self):
		wx.CallAfter(self._refresh_dupe_warning)
	#----------------------------------------------------------------
	def _on_leaving_firstname(self):
		"""Set the gender according to entered firstname.

		Matches are fetched from existing records in backend.
		"""
		wx.CallAfter(self._refresh_dupe_warning)

		# only set if not already set so as to not
		# overwrite a change by the user
		if self._PRW_gender.GetData() is not None:
			return True

		firstname = self._PRW_firstnames.GetValue().strip()
		if firstname == '':
			return True

		gender = gmGender.map_firstnames2gender(firstnames = firstname)
		if gender is None:
			return True

		wx.CallAfter(self._PRW_gender.SetData, gender)

		return True
	#----------------------------------------------------------------
	def _on_leaving_dob(self):
		_validate_dob_field(self._PRW_dob)
		wx.CallAfter(self._refresh_dupe_warning)
	#----------------------------------------------------------------
	def _on_leaving_zip(self):
		self.__perhaps_invalidate_address_searcher(self._PRW_zip, 'postcode')

		zip_code = gmTools.none_if(self._PRW_zip.GetValue().strip(), '')
		self._PRW_street.set_context(context = 'zip', val = zip_code)
		self._PRW_urb.set_context(context = 'zip', val = zip_code)
		self._PRW_region.set_context(context = 'zip', val = zip_code)
		self._PRW_country.set_context(context = 'zip', val = zip_code)

		return True
	#----------------------------------------------------------------
	def _on_leaving_country(self):
		self.__perhaps_invalidate_address_searcher(self._PRW_country, 'l10n_country')

		country = gmTools.none_if(self._PRW_country.GetValue().strip(), '')
		self._PRW_region.set_context(context = 'country', val = country)

		return True
	#----------------------------------------------------------------
	def _on_leaving_number(self, evt):
		if self._TCTRL_number.GetValue().strip() == '':
			adr = self._PRW_address_searcher.address
			if adr is None:
				return True
			self._TCTRL_number.SetValue(adr['number'])
			return True

		self.__perhaps_invalidate_address_searcher(self._TCTRL_number, 'number')
		return True
	#----------------------------------------------------------------
	def _on_leaving_unit(self, evt):
		if self._TCTRL_unit.GetValue().strip() == '':
			adr = self._PRW_address_searcher.address
			if adr is None:
				return True
			self._TCTRL_unit.SetValue(gmTools.coalesce(adr['subunit'], ''))
			return True

		self.__perhaps_invalidate_address_searcher(self._TCTRL_unit, 'subunit')
		return True
	#----------------------------------------------------------------
	def _invalidate_address_searcher(self, *args, **kwargs):
		mapping = [
			(self._PRW_street, 'street'),
			(self._PRW_urb, 'urb'),
			(self._PRW_region, 'l10n_region')
		]
		# loop through fields and invalidate address searcher if different
		for ctrl, field in mapping:
			if self.__perhaps_invalidate_address_searcher(ctrl, field):
				return True

		return True
	#----------------------------------------------------------------
	def _on_leaving_adress_searcher(self):
		if self._PRW_address_searcher.address is None:
			return True

		wx.CallAfter(self.__set_fields_from_address_searcher)
		return True
	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):
		if self._PRW_primary_provider.GetValue().strip() == '':
			self._PRW_primary_provider.display_as_valid(True)
		else:
			if self._PRW_primary_provider.GetData() is None:
				self._PRW_primary_provider.display_as_valid(False)
			else:
				self._PRW_primary_provider.display_as_valid(True)
		return (self.__identity_valid_for_save() and self.__address_valid_for_save(empty_address_is_valid = True))
	#----------------------------------------------------------------
	def _save_as_new(self):

		if self._PRW_dob.GetValue().strip() == '':
			if not _empty_dob_allowed():
				self._PRW_dob.display_as_valid(False)
				self._PRW_dob.SetFocus()
				return False

		# identity
		new_identity = gmPerson.create_identity (
			gender = self._PRW_gender.GetData(),
			dob = self._PRW_dob.GetData(),
			lastnames = self._PRW_lastname.GetValue().strip(),
			firstnames = self._PRW_firstnames.GetValue().strip(),
			comment = gmTools.none_if(self._TCTRL_comment.GetValue().strip(), '')
		)
		if new_identity is None:
			gmGuiHelpers.gm_show_error (
				title = _('Creating person.'),
				error = _(
					'Failed to create person. Does it already exist ?\n'
					'\n'
					'If so you need to add a unique comment.'
				)
			)
			return False
		_log.info('identity created: %s' % new_identity)

		new_identity['dob_is_estimated'] = self._CHBOX_estimated_dob.GetValue()
		val = self._TCTRL_tob.GetValue().strip()
		if val != '':
			new_identity['tob'] = pydt.time(int(val[:2]), int(val[3:5]))
		new_identity['title'] = gmTools.none_if(self._PRW_title.GetValue().strip())

		prov = self._PRW_primary_provider.GetData()
		if prov is not None:
			new_identity['pk_primary_provider'] = prov
		#new_identity['comment'] = gmTools.none_if(self._TCTRL_comment.GetValue().strip(), '')
		new_identity.save()
		_log.info('new identity updated: %s' % new_identity)

		new_identity.set_nickname(nickname = gmTools.none_if(self._PRW_nickname.GetValue().strip(), ''))
		_log.info('nickname set on new identity: %s' % new_identity)

		# address
		# if we reach this the address cannot be completely empty
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
					region_code = self._PRW_region.GetData(),
					country_code = self._PRW_country.GetData(),
					subunit = gmTools.none_if(self._TCTRL_unit.GetValue().strip(), ''),
					id_type = self._PRW_type.GetData()
				)
			except gmPG2.dbapi.InternalError:
				_log.debug('number: >>%s<<', self._TCTRL_number.GetValue().strip())
				_log.debug('(sub)unit: >>%s<<', self._TCTRL_unit.GetValue().strip())
				_log.debug('street: >>%s<<', self._PRW_street.GetValue().strip())
				_log.debug('postcode: >>%s<<', self._PRW_zip.GetValue().strip())
				_log.debug('urb: >>%s<<', self._PRW_urb.GetValue().strip())
				_log.debug('region: >>%s<<', self._PRW_region.GetData())
				_log.debug('country: >>%s<<', self._PRW_country.GetData())
				_log.exception('cannot link address')
				gmGuiHelpers.gm_show_error (
					title = _('Saving address'),
					error = _(
						'Cannot save this address.\n'
						'\n'
						'You will have to add it via the Demographics plugin.\n'
					)
				)
		elif is_valid is False:
			gmGuiHelpers.gm_show_error (
				title = _('Saving address'),
				error = _(
					'Address not saved.\n'
					'\n'
					'You will have to add it via the Demographics plugin.\n'
				)
			)
		# else it is None which means empty address which we ignore

		# phone
		channel_name = self._PRW_channel_type.GetValue().strip()
		pk_channel_type = self._PRW_channel_type.GetData()
		if pk_channel_type is None:
			if channel_name == '':
				channel_name = 'homephone'
		new_identity.link_comm_channel (
			comm_medium = channel_name,
			pk_channel_type = pk_channel_type,
			url = gmTools.none_if(self._TCTRL_phone.GetValue().strip(), ''),
			is_confidential = False
		)

		# external ID
		pk_type = self._PRW_external_id_type.GetData()
		id_value = self._TCTRL_external_id_value.GetValue().strip()
		if (pk_type is not None) and (id_value != ''):
			new_identity.add_external_id(value = id_value, pk_type = pk_type)

		# occupation
		new_identity.link_occupation (
			occupation = gmTools.none_if(self._PRW_occupation.GetValue().strip(), '')
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
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

#	from Gnumed.pycommon import gmPG2
#	from Gnumed.pycommon import gmI18N
#	gmI18N.activate_locale()
#	gmI18N.install_domain()

	#--------------------------------------------------------
	#test_org_unit_prw()
