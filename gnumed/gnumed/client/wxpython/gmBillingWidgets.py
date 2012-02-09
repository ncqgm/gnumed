"""GNUmed billing handling widgets.
"""
#================================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"

import logging
import sys
#os.path


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDateTime
#from Gnumed.pycommon import gmDispatcher, gmCfg
#from Gnumed.pycommon import gmMatchProvider, gmI18N, gmPrinting, gmCfg2, gmNetworkTools

from Gnumed.business import gmBilling
#from Gnumed.business import gmPerson, gmATC, gmSurgery, gmMedication, gmForms, gmStaff

from Gnumed.wxpython import gmListWidgets
#from Gnumed.wxpython import gmGuiHelpers, gmRegetMixin, gmAuthWidgets, gmEditArea, gmMacro
#from Gnumed.wxpython import gmCfgWidgets, gmListWidgets, gmPhraseWheel, gmFormWidgets


_log = logging.getLogger('gm.ui')

#================================================================
def manage_billables(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()
	#------------------------------------------------------------
#	def edit(substance=None):
#		return edit_consumable_substance(parent = parent, substance = substance, single_entry = (substance is not None))
	#------------------------------------------------------------
#	def delete(substance):
#		if substance.is_in_use_by_patients:
#			gmDispatcher.send(signal = 'statustext', msg = _('Cannot delete this substance. It is in use.'), beep = True)
#			return False
#
#		return gmMedication.delete_consumable_substance(substance = substance['pk'])
	#------------------------------------------------------------
	def refresh(lctrl):
		billables = gmBilling.get_billables()
		items = [ [
			b['billable_code'],
			b['billable_description'],
			u'%s %s' % (b['raw_amount'], b['currency']),
			u'%s (%s)' % (b['catalog_short'], b['catalog_version']),
			gmTools.coalesce(b['comment'], u''),
			b['pk_billable']
		] for b in billables ]
		lctrl.set_string_items(items)
		lctrl.set_data(billables)
	#------------------------------------------------------------
	msg = _('\nThese are the items for billing registered with GNUmed.\n')

	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = msg,
		caption = _('Showing billable items.'),
		columns = [_('Code'), _('Description'), _('Value'), _('Catalog'), _('Comment'), u'#'],
		single_selection = True,
		#new_callback = edit,
		#edit_callback = edit,
		#delete_callback = delete,
		refresh_callback = refresh
	)

#================================================================
def manage_bill_items(parent=None, pk_patient=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()
	#------------------------------------------------------------
#	def edit(substance=None):
#		return edit_consumable_substance(parent = parent, substance = substance, single_entry = (substance is not None))
	#------------------------------------------------------------
#	def delete(substance):
#		if substance.is_in_use_by_patients:
#			gmDispatcher.send(signal = 'statustext', msg = _('Cannot delete this substance. It is in use.'), beep = True)
#			return False
#
#		return gmMedication.delete_consumable_substance(substance = substance['pk'])
	#------------------------------------------------------------
	def refresh(lctrl):
		b_items = gmBilling.get_bill_items(pk_patient = pk_patient)
		items = [ [
			gmDateTime.pydt_strftime(b['date_to_bill'], '%x', accuracy = gmDateTime.acc_days),
			b['unit_count'],
			u'%s: %s%s' % (b['billable_code'], b['billable_description'], gmTools.coalesce(b['item_detail'], u'', u' - %s')),
			u'%s %s (%sx%s x %s + (%s%%=%s))' % (
				b['final_amount'],
				b['currency'],
				b['unit_count'],
				b['net_amount_per_unit'],
				b['amount_multiplier'],
				b['vat_multiplier'] * 100,
				b['vat']
			),
			u'%s (%s)' % (b['catalog_short'], b['catalog_version']),
			b['status'],
			b['pk_bill_item']
		] for b in b_items ]
		lctrl.set_string_items(items)
		lctrl.set_data(b_items)
	#------------------------------------------------------------
	gmListWidgets.get_choices_from_list (
		parent = parent,
		#msg = msg,
		caption = _('Showing bill items.'),
		columns = [_('Date'), _('Count'), _('Description'), _('Value'), _('Catalog'), _('Status'), u'#'],
		single_selection = True,
		#new_callback = edit,
		#edit_callback = edit,
		#delete_callback = delete,
		refresh_callback = refresh
	)
#============================================================
# main
#------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.pycommon import gmI18N

	gmI18N.activate_locale()
	gmI18N.install_domain(domain = 'gnumed')

	#----------------------------------------
	app = wx.PyWidgetTester(size = (600, 600))
	#app.SetWidget(cATCPhraseWheel, -1)
	app.SetWidget(cSubstancePhraseWheel, -1)
	app.MainLoop()
