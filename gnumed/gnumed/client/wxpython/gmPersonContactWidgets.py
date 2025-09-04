"""Widgets dealing with address/contact information."""
#============================================================
__author__ = "R.Terry, SJ Tan, I Haywood, Carlos Moro <cfmoro1976@yahoo.es>"
__license__ = 'GPL v2 or later (details at https://www.gnu.org)'

# standard library
import sys
import logging


import wx


# GNUmed specific
if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmNetworkTools

from Gnumed.business import gmPraxis

from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmListWidgets
from Gnumed.wxpython import gmEditArea
from Gnumed.wxpython import gmAddressWidgets


# constant defs
_log = logging.getLogger('gm.ui')

#============================================================
def select_address(missing=None, person=None):

	#--------------------------
	def calculate_tooltip(adr):
		return '\n'.join(adr.format())
	#--------------------------
	addresses = person.get_addresses()
	if len(addresses) == 0:
		return None

	msg = _(
		'There is no [%s] address registered with this patient.\n\n'
		'Please select the address you would like to use instead:'
	) % missing
	choices = [
		[
			a['l10n_address_type'],
			'%s %s%s, %s %s, %s' % (
				a['street'],
				a['number'],
				gmTools.coalesce(a['subunit'], '', '/%s'),
				a['postcode'],
				a['urb'],
				a['l10n_country']
			)
		]
	for a in addresses ]

	return gmListWidgets.get_choices_from_list (
		msg = msg,
		caption = _('Selecting address by type'),
		columns = [_('Type'), _('Address')],
		choices = choices,
		data = addresses,
		single_selection = True,
		list_tooltip_callback = calculate_tooltip
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

		self.refresh_callback = self.refresh
		self.new_callback = self._add_address
		self.edit_callback = self._edit_address
		self.delete_callback = self._del_address

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
		)
		self._LCTRL_items.set_column_widths()
		self._LCTRL_items.set_data(data = adrs)
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __init_ui(self):
		self.__static_tooltip_part = _('List of addresses related to this person.')
		self._LCTRL_items.item_tooltip_callback = self._calculate_tooltip
		self._LCTRL_items.set_columns(columns = [
			_('Type'),
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
		])

		self.left_extra_button = (
			_('Map'),
			_('Show selected address on map'),
			self._show_address_on_map
		)
		self.middle_extra_button = (
			_('Distance'),
			_('Show distance from your praxis'),
			self._show_distance_on_map
		)

	#--------------------------------------------------------
	def _add_address(self):
		ea = gmAddressWidgets.cAddressEAPnl(self, -1)
		ea.address_holder = self.__identity
		dlg = gmEditArea.cGenericEditAreaDlg2(self, -1, edit_area = ea)
		dlg.SetTitle(_('Adding new address'))
		if dlg.ShowModal() == wx.ID_OK:
			return True
		return False
	#--------------------------------------------------------
	def _edit_address(self, address):
		ea = gmAddressWidgets.cAddressEAPnl(self, -1, address = address)
		ea.address_holder = self.__identity
		dlg = gmEditArea.cGenericEditAreaDlg2(self, -1, edit_area = ea)
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
	def _show_address_on_map(self, address):
		if address is None:
			return False
		gmNetworkTools.open_url_in_browser(address.as_map_url, new = 2, autoraise = True)

	#--------------------------------------------------------
	def _show_distance_on_map(self, address):
		if address is None:
			return False
		praxis_branch = gmPraxis.gmCurrentPraxisBranch()
		gmNetworkTools.open_url_in_browser(praxis_branch.get_distance2address_url(address), new = 2, autoraise = True)

	#--------------------------------------------------------
	def _calculate_tooltip(self, address):
		tt = '\n'.join(address.format())
		tt += '\n'
		tt += '%s\n' % (gmTools.u_box_horiz_single * 40)
		tt += self.__static_tooltip_part
		return tt

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
		self._PNL_comms.channel_owner = self.__identity
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

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.pycommon import gmPG2
	gmPG2.get_connection()

	#--------------------------------------------------------
#	def test_person_adrs_pnl():
#		app = wx.PyWidgetTester(size = (600, 400))
		#widget = 
#		cPersonAddressesManagerPnl(app.frame, -1)
		#widget.identity = activate_patient()
#		app.frame.Show(True)
#		app.MainLoop()
	#--------------------------------------------------------
#	def test_pat_contacts_pnl():
#		app = wx.PyWidgetTester(size = (600, 400))
		#widget = 
#		cPersonContactsManagerPnl(app.frame, -1)
		#widget.identity = activate_patient()
#		app.frame.Show(True)
#		app.MainLoop()
	#--------------------------------------------------------
	#test_pat_contacts_pnl()
	#test_person_adrs_pnl()

#============================================================
