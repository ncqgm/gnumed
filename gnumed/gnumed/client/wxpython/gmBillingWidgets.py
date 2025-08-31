# -*- coding: utf-8 -*-
"""GNUmed billing handling widgets."""

#================================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"

import logging
import sys


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmMatchProvider
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmCfgDB
from Gnumed.pycommon import gmCfgINI
from Gnumed.pycommon import gmPrinting
from Gnumed.pycommon import gmNetworkTools

from Gnumed.business import gmBilling
from Gnumed.business import gmPerson
from Gnumed.business import gmStaff
from Gnumed.business import gmDocuments
from Gnumed.business import gmPraxis
from Gnumed.business import gmForms

from Gnumed.wxpython import gmListWidgets
from Gnumed.wxpython import gmRegetMixin
from Gnumed.wxpython import gmPhraseWheel
from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmEditArea
from Gnumed.wxpython import gmPersonContactWidgets
from Gnumed.wxpython import gmPatSearchWidgets
from Gnumed.wxpython import gmMacro
from Gnumed.wxpython import gmFormWidgets
from Gnumed.wxpython import gmDocumentWidgets
from Gnumed.wxpython import gmDataPackWidgets


_log = logging.getLogger('gm.ui')

#================================================================
def edit_billable(parent=None, billable=None) -> bool:
	ea = cBillableEAPnl(parent, -1)
	ea.data = billable
	ea.mode = gmTools.coalesce(billable, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2 (
		parent = parent,
		id = -1,
		edit_area = ea,
		single_entry = gmTools.bool2subst((billable is None), False, True)
	)
	dlg.SetTitle(gmTools.coalesce(billable, _('Adding new billable'), _('Editing billable')))
	if dlg.ShowModal() == wx.ID_OK:
		dlg.DestroyLater()
		return True

	dlg.DestroyLater()
	return False

#----------------------------------------------------------------
def manage_billables(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#------------------------------------------------------------
	def edit(billable=None):
		return edit_billable(parent = parent, billable = billable)
	#------------------------------------------------------------
	def delete(billable):
		if billable.is_in_use:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot delete this billable item. It is in use.'), beep = True)
			return False
		return gmBilling.delete_billable(pk_billable = billable['pk_billable'])
	#------------------------------------------------------------
	def get_tooltip(item):
		if item is None:
			return None
		return item.format()
	#------------------------------------------------------------
	def refresh(lctrl):
		billables = gmBilling.get_billables()
		items = [ [
			b['billable_code'],
			b['billable_description'],
			'%(currency)s%(raw_amount)s' % b,
			'%s (%s)' % (b['catalog_short'], b['catalog_version']),
			gmTools.coalesce(b['comment'], ''),
			b['pk_billable']
		] for b in billables ]
		lctrl.set_string_items(items)
		lctrl.set_data(billables)
	#------------------------------------------------------------
	def manage_data_packs(billable):
		gmDataPackWidgets.manage_data_packs(parent = parent)
		return True
	#------------------------------------------------------------
	def browse_catalogs(billable):
		url = gmCfgDB.get4user (
			option = 'external.urls.schedules_of_fees',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
			default = 'http://www.e-bis.de/goae/defaultFrame.htm'
		)
		gmNetworkTools.open_url_in_browser(url = url)
		return False
	#------------------------------------------------------------
	msg = _('\nThese are the items for billing registered with GNUmed.\n')

	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = msg,
		caption = _('Showing billable items.'),
		columns = [_('Code'), _('Description'), _('Value'), _('Catalog'), _('Comment'), '#'],
		single_selection = True,
		new_callback = edit,
		edit_callback = edit,
		delete_callback = delete,
		refresh_callback = refresh,
		middle_extra_button = (
			_('Data packs'),
			_('Browse and install billing catalog (schedule of fees) data packs'),
			manage_data_packs
		),
		right_extra_button = (
			_('Catalogs (WWW)'),
			_('Browse billing catalogs (schedules of fees) on the web'),
			browse_catalogs
		),
		list_tooltip_callback = get_tooltip
	)

#----------------------------------------------------------------
class cBillablePhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		query = """
			SELECT -- DISTINCT ON (label)
				r_vb.pk_billable
					AS data,
				r_vb.billable_code || ': ' || r_vb.billable_description || ' (' || r_vb.catalog_short || ' - ' || r_vb.catalog_version || ')'
					AS list_label,
				r_vb.billable_code || ' (' || r_vb.catalog_short || ' - ' || r_vb.catalog_version || ')'
					AS field_label
			FROM
				ref.v_billables r_vb
			WHERE
				r_vb.active
					AND (
						r_vb.billable_code %(fragment_condition)s
							OR
						r_vb.billable_description %(fragment_condition)s
					)
			ORDER BY list_label
			LIMIT 20
		"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries = query)
		mp.setThresholds(1, 2, 4)
		self.matcher = mp
	#------------------------------------------------------------
	def _data2instance(self, link_obj=None):
		return gmBilling.cBillable(aPK_obj = list(self._data.values())[0]['data'])
	#------------------------------------------------------------
	def _get_data_tooltip(self):
		if self.GetData() is None:
			return None
		billable = gmBilling.cBillable(aPK_obj = list(self._data.values())[0]['data'])
		return billable.format()
	#------------------------------------------------------------
	def set_from_instance(self, instance):
		val = '%s (%s - %s)' % (
			instance['billable_code'],
			instance['catalog_short'],
			instance['catalog_version']
		)
		self.SetText(value = val, data = instance['pk_billable'])
	#------------------------------------------------------------
	def set_from_pk(self, pk):
		self.set_from_instance(gmBilling.cBillable(aPK_obj = pk))

#----------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgBillableEAPnl

class cBillableEAPnl(wxgBillableEAPnl.wxgBillableEAPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwargs):

		try:
			data = kwargs['billable']
			del kwargs['billable']
		except KeyError:
			data = None

		wxgBillableEAPnl.wxgBillableEAPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		self.mode = 'new'
		self.data = data
		if data is not None:
			self.mode = 'edit'

		#self.__init_ui()
	#----------------------------------------------------------------
#	def __init_ui(self):
#		# adjust phrasewheels etc
	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):

		validity = True

		vat = self._TCTRL_vat.GetValue().strip()
		if vat == '':
			self.display_tctrl_as_valid(tctrl = self._TCTRL_vat, valid = True)
		else:
			success, vat = gmTools.input2decimal(initial = vat)
			if success:
				self.display_tctrl_as_valid(tctrl = self._TCTRL_vat, valid = True)
			else:
				validity = False
				self.display_tctrl_as_valid(tctrl = self._TCTRL_vat, valid = False)
				self.StatusText = _('VAT must be empty or a number.')
				self._TCTRL_vat.SetFocus()

		currency = self._TCTRL_currency.GetValue().strip()
		if currency == '':
			validity = False
			self.display_tctrl_as_valid(tctrl = self._TCTRL_currency, valid = False)
			self.StatusText = _('Currency is missing.')
			self._TCTRL_currency.SetFocus()
		else:
			self.display_tctrl_as_valid(tctrl = self._TCTRL_currency, valid = True)

		success, val = gmTools.input2decimal(initial = self._TCTRL_amount.GetValue())
		if success:
			self.display_tctrl_as_valid(tctrl = self._TCTRL_amount, valid = True)
		else:
			validity = False
			self.display_tctrl_as_valid(tctrl = self._TCTRL_amount, valid = False)
			self.StatusText = _('Value is missing.')
			self._TCTRL_amount.SetFocus()

		if self._TCTRL_description.GetValue().strip() == '':
			validity = False
			self.display_tctrl_as_valid(tctrl = self._TCTRL_description, valid = False)
			self.StatusText = _('Description is missing.')
			self._TCTRL_description.SetFocus()
		else:
			self.display_tctrl_as_valid(tctrl = self._TCTRL_description, valid = True)

		if self._PRW_coding_system.GetData() is None:
			validity = False
			self._PRW_coding_system.display_as_valid(False)
			self.StatusText = _('Coding system is missing.')
			self._PRW_coding_system.SetFocus()
		else:
			self._PRW_coding_system.display_as_valid(True)

		if self._TCTRL_code.GetValue().strip() == '':
			validity = False
			self.display_tctrl_as_valid(tctrl = self._TCTRL_code, valid = False)
			self.StatusText = _('Code is missing.')
			self._TCTRL_code.SetFocus()
		else:
			self.display_tctrl_as_valid(tctrl = self._TCTRL_code, valid = True)

		return validity
	#----------------------------------------------------------------
	def _save_as_new(self):
		data = gmBilling.create_billable (
			code = self._TCTRL_code.GetValue().strip(),
			term = self._TCTRL_description.GetValue().strip(),
			data_source = self._PRW_coding_system.GetData(),
			return_existing = False
		)
		if data is None:
			self.StatusText = _('Billable already exists.')
			return False

		val = self._TCTRL_amount.GetValue().strip()
		if val != '':
			tmp, val = gmTools.input2decimal(val)
			data['raw_amount'] = val
		val = self._TCTRL_currency.GetValue().strip()
		if val != '':
			data['currency'] = val
		vat = self._TCTRL_vat.GetValue().strip()
		if vat != '':
			tmp, vat = gmTools.input2decimal(vat)
			data['vat_multiplier'] = vat / 100
		data['comment'] = self._TCTRL_comment.GetValue().strip()
		data['active'] = self._CHBOX_active.GetValue()

		data.save()

		self.data = data

		return True
	#----------------------------------------------------------------
	def _save_as_update(self):
		self.data['billable_description'] = self._TCTRL_description.GetValue().strip()
		tmp, self.data['raw_amount'] = gmTools.input2decimal(self._TCTRL_amount.GetValue())
		self.data['currency'] = self._TCTRL_currency.GetValue().strip()
		vat = self._TCTRL_vat.GetValue().strip()
		if vat == '':
			vat = 0
		else:
			tmp, vat = gmTools.input2decimal(vat)
		self.data['vat_multiplier'] = vat / 100
		self.data['comment'] = self._TCTRL_comment.GetValue().strip()
		self.data['active'] = self._CHBOX_active.GetValue()
		self.data.save()
		return True
	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._TCTRL_code.SetValue('')
		self._PRW_coding_system.SetText('', None)
		self._TCTRL_description.SetValue('')
		self._TCTRL_amount.SetValue('')
		self._TCTRL_currency.SetValue('')
		self._TCTRL_vat.SetValue('')
		self._TCTRL_comment.SetValue('')
		self._CHBOX_active.SetValue(True)

		self._TCTRL_code.SetFocus()
	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._refresh_as_new()
	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		self._TCTRL_code.SetValue(self.data['billable_code'])
		self._TCTRL_code.Enable(False)
		self._PRW_coding_system.SetText('%s (%s)' % (self.data['catalog_short'], self.data['catalog_version']), self.data['pk_data_source'])
		self._PRW_coding_system.Enable(False)
		self._TCTRL_description.SetValue(self.data['billable_description'])
		self._TCTRL_amount.SetValue('%s' % self.data['raw_amount'])
		self._TCTRL_currency.SetValue(self.data['currency'])
		self._TCTRL_vat.SetValue('%s' % (self.data['vat_multiplier'] * 100))
		self._TCTRL_comment.SetValue(gmTools.coalesce(self.data['comment'], ''))
		self._CHBOX_active.SetValue(self.data['active'])

		self._TCTRL_description.SetFocus()
	#----------------------------------------------------------------

#================================================================
# invoice related widgets
#----------------------------------------------------------------
def configure_invoice_template(parent=None, with_vat=True):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	template = gmFormWidgets.manage_form_templates (
		parent = parent,
		template_types = ['invoice']
	)

	if template is None:
		gmDispatcher.send(signal = 'statustext', msg = _('No invoice template configured.'), beep = True)
		return None

	if template['engine'] not in ['L', 'X']:
		gmDispatcher.send(signal = 'statustext', msg = _('No invoice template configured.'), beep = True)
		return None

	if with_vat:
		option = 'form_templates.invoice_with_vat'
	else:
		option = 'form_templates.invoice_no_vat'

	gmCfgDB.set (
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
		option = option,
		value = '%s - %s' % (template['name_long'], template['external_version'])
	)

	return template
#----------------------------------------------------------------
def get_invoice_template(parent=None, with_vat=True):

	if with_vat:
		option = 'form_templates.invoice_with_vat'
	else:
		option = 'form_templates.invoice_no_vat'

	template = gmCfgDB.get4user (
		option = option,
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace
	)

	if template is None:
		template = configure_invoice_template(parent = parent, with_vat = with_vat)
		if template is None:
			gmGuiHelpers.gm_show_error (
				error = _('There is no invoice template configured.'),
				title = _('Getting invoice template')
			)
			return None
	else:
		try:
			name, ver = template.split(' - ')
		except Exception:
			_log.exception('problem splitting invoice template name [%s]', template)
			gmDispatcher.send(signal = 'statustext', msg = _('Problem loading invoice template.'), beep = True)
			return None
		template = gmForms.get_form_template(name_long = name, external_version = ver)
		if template is None:
			gmGuiHelpers.gm_show_error (
				error = _('Cannot load invoice template [%s - %s]') % (name, ver),
				title = _('Getting invoice template')
			)
			return None

	return template

#================================================================
# per-patient bill related widgets
#----------------------------------------------------------------
def edit_bill(parent=None, bill=None, single_entry=False):

	if bill is None:
		# manually creating bills is not yet supported
		return

	ea = cBillEAPnl(parent, -1)
	ea.data = bill
	ea.mode = gmTools.coalesce(bill, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2(parent, -1, edit_area = ea, single_entry = single_entry)
	dlg.SetTitle(gmTools.coalesce(bill, _('Adding new bill'), _('Editing bill')))
	if dlg.ShowModal() == wx.ID_OK:
		dlg.DestroyLater()
		return True
	dlg.DestroyLater()
	return False

#----------------------------------------------------------------
def create_bill_from_items(bill_items=None):

	if len(bill_items) == 0:
		return None

	item = bill_items[0]
	currency = item['currency']
	vat = item['vat_multiplier']
	pk_pat = item['pk_patient']

	# check item consistency
	has_errors = False
	for item in bill_items:
		if item['pk_bill'] is not None:
			msg = _(
				'This item is already invoiced:\n'
				'\n'
				'%s\n'
				'\n'
				'Cannot put it on a second bill.'
			) % item.format()
			has_errors = True
			break
		if	(item['currency'] != currency) or (
			 item['vat_multiplier'] != vat) or (
			 item['pk_patient'] != pk_pat
			):
			msg = _(
				'All items to be included with a bill must\n'
				'coincide on currency, VAT, and patient.\n'
				'\n'
				'This item does not:\n'
				'\n'
				'%s\n'
			) % item.format()
			has_errors = True
			break
	if has_errors:
		gmGuiHelpers.gm_show_warning(title = _('Checking invoice items'), warning = msg)
		return None

	# create bill
	person = gmPerson.cPerson(pk_pat)
	invoice_id_template = gmCfgDB.get4user (
		option = u'billing.invoice_id_template',
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace
	)
	invoice_id = None
	max_attempts = 3
	attempt = 0
	while (invoice_id is None) and (attempt < max_attempts+1):
		attempt += 1
		invoice_id = gmBilling.generate_invoice_id(template = invoice_id_template, person = person)
		if invoice_id is None:
			continue
		if gmBilling.lock_invoice_id(invoice_id):
			break
		invoice_id = None
	if invoice_id is None:
		gmGuiHelpers.gm_show_warning (
			title = _('Generating bill'),
			warning = _('Could not generate invoice ID.\n\nTry again later.')
		)
		return None

	bill = gmBilling.create_bill(invoice_id = invoice_id)
	gmBilling.unlock_invoice_id(invoice_id)
	_log.info('created bill [%s]', bill['invoice_id'])
	bill.add_items(items = bill_items)
	bill.set_missing_address_from_default()

	return bill

#----------------------------------------------------------------
def create_invoice_from_bill(parent = None, bill=None, print_it=False, keep_a_copy=True) -> bool:

	bill_patient_not_active = False
	# do we have a current patient ?
	curr_pat = gmPerson.gmCurrentPatient()
	if curr_pat.connected:
		# is the bill about the current patient, too ?
		# (because that's what the new invoice would get
		#  created for and attached to)
		if curr_pat.ID != bill['pk_patient']:
			bill_patient_not_active = True
	else:
		bill_patient_not_active = True
	# FIXME: could ask whether to set fk_receiver_identity
	# FIXME: but this would need enabling the bill EA to edit same
	if bill_patient_not_active:
		activate_patient = gmGuiHelpers.gm_show_question (
			title = _('Creating invoice'),
			question = _(
				'Patient on bill is not the active patient.\n'
				'\n'
				'Active patient: %s\n'
				'Patient on bill: #%s\n'
				'\n'
				'Activate patient on bill so invoice PDF can be created ?'
			) % (
				gmTools.coalesce(curr_pat.ID, '', '#%s'),
				bill['pk_patient']
			)
		)
		if not activate_patient:
			return False

		if not gmPatSearchWidgets.set_active_patient(patient = bill['pk_patient']):
			gmGuiHelpers.gm_show_error (
				title = _('Creating invoice'),
				error = _('Cannot activate patient #%s.') % bill['pk_patient']
			)
			return False

	if None in [ bill['close_date'], bill['pk_receiver_address'], bill['apply_vat'] ]:
		edit_bill(parent = parent, bill = bill, single_entry = True)
		# cannot invoice open bills
		if bill['close_date'] is None:
			_log.error('cannot create invoice from bill, bill not closed')
			gmGuiHelpers.gm_show_warning (
				title = _('Creating invoice'),
				warning = _(
					'Cannot create invoice from bill.\n'
					'\n'
					'The bill does not have a closing date set.'
				)
			)
			return False

		# cannot create invoice if no receiver address
		if bill['pk_receiver_address'] is None:
			_log.error('cannot create invoice from bill, lacking receiver address')
			gmGuiHelpers.gm_show_warning (
				title = _('Creating invoice'),
				warning = _(
					'Cannot create invoice from bill.\n'
					'\n'
					'There is no receiver address.'
				)
			)
			return False

		# cannot create invoice if applying VAT is undecided
		if bill['apply_vat'] is None:
			_log.error('cannot create invoice from bill, apply_vat undecided')
			gmGuiHelpers.gm_show_warning (
				title = _('Creating invoice'),
				warning = _(
					'Cannot create invoice from bill.\n'
					'\n'
					'You must decide on whether to apply VAT.'
				)
			)
			return False

	# find template
	template = get_invoice_template(parent = parent, with_vat = bill['apply_vat'])
	if template is None:
		gmGuiHelpers.gm_show_warning (
			title = _('Creating invoice'),
			warning = _(
				'Cannot create invoice from bill\n'
				'without an invoice template.'
			)
		)
		return False

	# process template
	try:
		invoice = template.instantiate()
	except KeyError:
		_log.exception('cannot instantiate invoice template [%s]', template)
		gmGuiHelpers.gm_show_error (
			error = _('Invalid invoice template [%s - %s (%s - Gmd:%s)]') % (
				template['name_long'],
				template['external_version'],
				template['engine'],
				template['gnumed_revision']
			),
			title = _('Creating invoice')
		)
		return False

	if not invoice:
		_log.error('cannot instantiate invoice template [%s]', template)
		gmGuiHelpers.gm_show_error (
			error = _('Invalid invoice template [%s - %s (%s - Gmd:%s)]') % (
				template['name_long'],
				template['external_version'],
				template['engine'],
				template['gnumed_revision']
			),
			title = _('Creating invoice')
		)
		return False

	ph = gmMacro.gmPlaceholderHandler()
	#ph.debug = True
	ph.set_cache_value('bill', bill)
	invoice.substitute_placeholders(data_source = ph)
	ph.unset_cache_value('bill')
	pdf_name = invoice.generate_output()
	if pdf_name is None:
		gmGuiHelpers.gm_show_error (
			error = _('Error generating invoice PDF.'),
			title = _('Creating invoice')
		)
		return False

	if keep_a_copy:
		files2import = []
		files2import.extend(invoice.final_output_filenames)
		files2import.extend(invoice.re_editable_filenames)
		doc = gmDocumentWidgets.save_files_as_new_document (
			parent = parent,
			filenames = files2import,
			document_type = template['instance_type'],
			review_as_normal = True,
			reference = bill['invoice_id'],
			pk_org_unit = gmPraxis.gmCurrentPraxisBranch()['pk_org_unit'],
			date_generated = gmDateTime.pydt_now_here()
		)
		if doc:
			bill['pk_doc'] = doc['pk_doc']
			bill.save()
		else:
			gmGuiHelpers.gm_show_warning (
				title = _('Saving invoice'),
				warning = ('Cannot save invoice into document archive.')
			)
	if not print_it:
		return True

	_cfg = gmCfgINI.gmCfgData()
	printed = gmPrinting.print_files(filenames = [pdf_name], jobtype = 'invoice', verbose = _cfg.get(option = 'debug'))
	if not printed:
		gmGuiHelpers.gm_show_error (
			error = _('Error printing the invoice.'),
			title = _('Printing invoice')
		)
		return True	# anyway

	return True

#----------------------------------------------------------------
def delete_bill(parent=None, bill=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	dlg = gmGuiHelpers.c3ButtonQuestionDlg (
		parent,	-1,
		caption = _('Deleting bill'),
		question = _(
			'When deleting the bill [%s]\n'
			'do you want to keep its items (effectively \"unbilling\" them)\n'
			'or do you want to also delete the bill items from the patient ?\n'
		) % bill['invoice_id'],
		button_defs = [
			{'label': _('Delete + keep'), 'tooltip': _('Delete the bill but keep ("unbill") its items.'), 'default': True},
			{'label': _('Delete all'), 'tooltip': _('Delete both the bill and its items from the patient.')}
		],
		show_checkbox = True,
		checkbox_msg = _('Also remove invoice PDF'),
		checkbox_tooltip = _('Also remove the invoice PDF from the document archive (because it will not correspond to the bill anymore).')
	)
	button_pressed = dlg.ShowModal()
	delete_invoice = dlg.checkbox_is_checked()
	dlg.DestroyLater()

	if button_pressed == wx.ID_CANCEL:
		return False

	delete_items = (button_pressed == wx.ID_NO)

	if delete_invoice:
		if bill['pk_doc'] is not None:
			gmDocuments.delete_document (
				document_id = bill['pk_doc'],
				encounter_id = gmPerson.cPatient(aPK_obj = bill['pk_patient']).emr.active_encounter['pk_encounter']
			)

	items = bill['pk_bill_items']
	success = gmBilling.delete_bill(pk_bill = bill['pk_bill'])
	if delete_items:
		for item in items:
			gmBilling.delete_bill_item(pk_bill_item = item)

	return success

#----------------------------------------------------------------
def remove_items_from_bill(parent=None, bill=None):

	if bill is None:
		return False

	list_data = bill.bill_items
	if len(list_data) == 0:
		return False

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	list_items = [ [
		b['date_to_bill'].strftime('%Y %b %d'),
		b['unit_count'],
		'%s: %s%s' % (b['billable_code'], b['billable_description'], gmTools.coalesce(b['item_detail'], '', ' - %s')),
		'%(curr)s %(total_val)s (%(count)s %(x)s %(unit_val)s%(x)s%(val_multiplier)s)' % {
			'curr': b['currency'],
			'total_val': b['total_amount'],
			'count': b['unit_count'],
			'x': gmTools.u_multiply,
			'unit_val': b['net_amount_per_unit'],
			'val_multiplier': b['amount_multiplier']
		},
		'%(curr)s%(vat)s (%(perc_vat)s%%)' % {
			'vat': b['vat'],
			'curr': b['currency'],
			'perc_vat': b['vat_multiplier'] * 100
		},
		'%s (%s)' % (b['catalog_short'], b['catalog_version']),
		b['pk_bill_item']
	] for b in list_data ]

	msg = _('Select the items you want to remove from bill [%s]:\n') % bill['invoice_id']
	items2remove = gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = msg,
		caption = _('Removing items from bill'),
		columns = [_('Date'), _('Count'), _('Description'), _('Value'), _('VAT'), _('Catalog'), '#'],
		single_selection = False,
		choices = list_items,
		data = list_data
	)

	if items2remove is None:
		return False

	if len(items2remove) == len(list_items):
		gmGuiHelpers.gm_show_info (
			title = _('Removing items from bill'),
			info = _(
				'Cannot remove all items from a bill because\n'
				'GNUmed does not support empty bills.\n'
				'\n'
				'You must delete the bill itself if you want to\n'
				'remove all items (at which point you can opt to\n'
				'keep the items and only delete the bill).'
			)
		)
		return False

	dlg = gmGuiHelpers.c3ButtonQuestionDlg (
		parent,	-1,
		caption = _('Removing items from bill'),
		question = _(
			'%s items selected from bill [%s]\n'
			'\n'
			'Do you want to only remove the selected items\n'
			'from the bill ("unbill" them) or do you want\n'
			'to delete them entirely from the patient ?\n'
			'\n'
			'Note that neither action is reversible.'
		) % (
			len(items2remove),
			bill['invoice_id']
		),
		button_defs = [
			{'label': _('"Unbill"'), 'tooltip': _('Only "unbill" items (remove from bill but do not delete from patient).'), 'default': True},
			{'label': _('Delete'), 'tooltip': _('Completely delete items from the patient.')}
		],
		show_checkbox = True,
		checkbox_msg = _('Also remove invoice PDF'),
		checkbox_tooltip = _('Also remove the invoice PDF from the document archive (because it will not correspond to the bill anymore).')
	)
	button_pressed = dlg.ShowModal()
	delete_invoice = dlg.checkbox_is_checked()
	dlg.DestroyLater()

	if button_pressed == wx.ID_CANCEL:
		return False

	# remember this because unlinking/deleting the items
	# will remove the patient PK from the bill
	pk_patient = bill['pk_patient']

	for item in items2remove:
		item['pk_bill'] = None
		item.save()
		if button_pressed == wx.ID_NO:
			gmBilling.delete_bill_item(pk_bill_item = item['pk_bill_item'])

	if delete_invoice:
		if bill['pk_doc'] is not None:
			gmDocuments.delete_document (
				document_id = bill['pk_doc'],
				encounter_id = gmPerson.cPatient(aPK_obj = pk_patient).emr.active_encounter['pk_encounter']
			)

	# delete bill, too, if empty
	if len(bill.bill_items) == 0:
		gmBilling.delete_bill(pk_bill = bill['pk_bill'])

	return True

#----------------------------------------------------------------
def manage_bills(parent=None, patient=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#------------------------------------------------------------
	def show_pdf(bill):
		if bill is None:
			return False

		# find invoice
		invoice = bill.invoice
		if invoice is not None:
			success, msg = invoice.parts[-1].display_via_mime()
			if not success:
				gmGuiHelpers.gm_show_error(error = msg, title = _('Displaying invoice'))
			return False

		# create it ?
		create_it = gmGuiHelpers.gm_show_question (
			title = _('Displaying invoice'),
			question = _(
				'Cannot find an existing\n'
				'invoice PDF for this bill.\n'
				'\n'
				'Do you want to create one ?'
			),
		)
		if not create_it:
			return False

		# prepare invoicing
		if not bill.set_missing_address_from_default():
			gmGuiHelpers.gm_show_warning (
				title = _('Creating invoice'),
				warning = _(
					'There is no pre-configured billing address.\n'
					'\n'
					'Select the address you want to send the bill to.'
				)
			)
			edit_bill(parent = parent, bill = bill, single_entry = True)
			if bill['pk_receiver_address'] is None:
				return False

		if bill['close_date'] is None:
			bill['close_date'] = gmDateTime.pydt_now_here()
			bill.save()
		return create_invoice_from_bill(parent = parent, bill = bill, print_it = True, keep_a_copy = True)

	#------------------------------------------------------------
	def edit(bill):
		return edit_bill(parent = parent, bill = bill, single_entry = True)

	#------------------------------------------------------------
	def delete(bill):
		return delete_bill(parent = parent, bill = bill)
	#------------------------------------------------------------
	def remove_items(bill):
		return remove_items_from_bill(parent = parent, bill = bill)
	#------------------------------------------------------------
	def get_tooltip(item):
		if item is None:
			return None
		return item.format()
	#------------------------------------------------------------
	def refresh(lctrl):
		if patient is None:
			bills = gmBilling.get_bills()
		else:
			bills = gmBilling.get_bills(pk_patient = patient.ID)
		items = []
		for b in bills:
			if b['close_date'] is None:
				close_date = _('<open>')
			else:
				close_date = b['close_date'].strftime('%Y %b %d')
			if b['total_amount'] is None:
				amount = _('no items on bill')
			else:
				amount = gmTools.bool2subst (
					b['apply_vat'],
					_('%(currency)s%(total_amount_with_vat)s (with %(percent_vat)s%% VAT)') % b,
					'%(currency)s%(total_amount)s' % b,
					_('without VAT: %(currency)s%(total_amount)s / with %(percent_vat)s%% VAT: %(currency)s%(total_amount_with_vat)s') % b
				)
			items.append ([
				close_date,
				b['invoice_id'],
				amount,
				gmTools.coalesce(b['comment'], '')
			])
		lctrl.set_string_items(items)
		lctrl.set_data(bills)
	#------------------------------------------------------------
	return gmListWidgets.get_choices_from_list (
		parent = parent,
		caption = _('Showing bills.'),
		columns = [_('Close date'), _('Invoice ID'), _('Value'), _('Comment')],
		single_selection = True,
		edit_callback = edit,
		delete_callback = delete,
		refresh_callback = refresh,
		middle_extra_button = (
			'PDF',
			_('Create if necessary, and show the corresponding invoice PDF'),
			show_pdf
		),
		right_extra_button = (
			_('Unbill'),
			_('Select and remove items from a bill.'),
			remove_items
		),
		list_tooltip_callback = get_tooltip
	)

#----------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgBillEAPnl

class cBillEAPnl(wxgBillEAPnl.wxgBillEAPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwargs):

		try:
			data = kwargs['bill']
			del kwargs['bill']
		except KeyError:
			data = None

		wxgBillEAPnl.wxgBillEAPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		self.mode = 'new'
		self.data = data
		if data is not None:
			self.mode = 'edit'

		self._3state2bool = {
			wx.CHK_UNCHECKED: False,
			wx.CHK_CHECKED: True,
			wx.CHK_UNDETERMINED: None
		}
		self.bool_to_3state = {
			False: wx.CHK_UNCHECKED,
			True: wx.CHK_CHECKED,
			None: wx.CHK_UNDETERMINED
		}

#		self.__init_ui()
	#----------------------------------------------------------------
#	def __init_ui(self):
	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):
		validity = True

		# flag but do not count as wrong
		if not self._PRW_close_date.is_valid_timestamp(empty_is_valid = False):
			self._PRW_close_date.SetFocus()

		# flag but do not count as wrong
		if self._CHBOX_vat_applies.ThreeStateValue == wx.CHK_UNDETERMINED:
			self._CHBOX_vat_applies.SetFocus()
			self._CHBOX_vat_applies.SetBackgroundColour('yellow')

		# "bill_bill_sane_recv_adr" CHECK (fk_receiver_address IS NOT NULL OR close_date IS NULL)
		if self._PRW_close_date.GetData():
			if not self.data['pk_receiver_address']:
				validity = False
				self.StatusText = _('Must select address (perhaps first add to patient) if closing bill.')
				self._TCTRL_address.SetValue(_('<missing>'))
		return validity

	#----------------------------------------------------------------
	def _save_as_new(self):
		# not intended to be used
		return False

	#----------------------------------------------------------------
	def _save_as_update(self):
		self.data['close_date'] = self._PRW_close_date.GetData()
		self.data['apply_vat'] = self._3state2bool[self._CHBOX_vat_applies.ThreeStateValue]
		self.data['comment'] = self._TCTRL_comment.GetValue()
		self.data.save()
		return True

	#----------------------------------------------------------------
	def _refresh_as_new(self):
		pass # not used

	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._refresh_as_new()

	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		self._TCTRL_invoice_id.SetValue(self.data['invoice_id'])
		self._PRW_close_date.SetText(data = self.data['close_date'])
		self.data.set_missing_address_from_default()
		if self.data['pk_receiver_address'] is None:
			self._TCTRL_address.SetValue('')
		else:
			adr = self.data.address
			self._TCTRL_address.SetValue(adr.format(single_line = True, show_type = False))
		self._TCTRL_value.SetValue('%(currency)s%(total_amount)s' % self.data)
		self._CHBOX_vat_applies.ThreeStateValue = self.bool_to_3state[self.data['apply_vat']]
		self._CHBOX_vat_applies.SetLabel(_('&VAT applies (%s%%)') % self.data['percent_vat'])
		if self.data['apply_vat'] is True:
			tmp = '%s %%(currency)s%%(total_vat)s %s %s %%(currency)s%%(total_amount_with_vat)s' % (
				gmTools.u_corresponds_to,
				gmTools.u_arrow2right,
				gmTools.u_sum,
			)
			self._TCTRL_value_with_vat.SetValue(tmp % self.data)
		elif self.data['apply_vat'] is None:
			self._TCTRL_value_with_vat.SetValue('?')
		else:
			self._TCTRL_value_with_vat.SetValue('')
		self._TCTRL_comment.SetValue(gmTools.coalesce(self.data['comment'], ''))
		self._PRW_close_date.SetFocus()

	#----------------------------------------------------------------
	# event handling
	#----------------------------------------------------------------
	def _on_vat_applies_box_checked(self, event):
		if self._CHBOX_vat_applies.ThreeStateValue == wx.CHK_CHECKED:
			tmp = '%s %%(currency)s%%(total_vat)s %s %s %%(currency)s%%(total_amount_with_vat)s' % (
				gmTools.u_corresponds_to,
				gmTools.u_arrow2right,
				gmTools.u_sum,
			)
			self._TCTRL_value_with_vat.SetValue(tmp % self.data)
			return

		if self._CHBOX_vat_applies.ThreeStateValue == wx.CHK_UNDETERMINED:
			self._TCTRL_value_with_vat.SetValue('?')
			return

		self._TCTRL_value_with_vat.SetValue('')

	#----------------------------------------------------------------
	def _on_select_address_button_pressed(self, event):
		adr = gmPersonContactWidgets.select_address (
			missing = _('billing'),
			person = gmPerson.cPerson(aPK_obj = self.data['pk_patient'])
		)
		if adr is None:
			gmGuiHelpers.gm_show_info (
				title = _('Selecting address'),
				info = _('GNUmed does not know any addresses for this patient.')
			)
			return

		self.data['pk_receiver_address'] = adr['pk_lnk_person_org_address']
		self.data.save()
		self._TCTRL_address.SetValue(adr.format(single_line = True, show_type = False))

#================================================================
# per-patient bill items related widgets
#----------------------------------------------------------------
def edit_bill_item(parent=None, bill_item=None, single_entry=False):

	if bill_item is not None:
		if bill_item.is_in_use:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot edit already invoiced bill item.'), beep = True)
			return False

	ea = cBillItemEAPnl(parent, -1)
	ea.data = bill_item
	ea.mode = gmTools.coalesce(bill_item, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2(parent, -1, edit_area = ea, single_entry = single_entry)
	dlg.SetTitle(gmTools.coalesce(bill_item, _('Adding new bill item'), _('Editing bill item')))
	if dlg.ShowModal() == wx.ID_OK:
		dlg.DestroyLater()
		return True
	dlg.DestroyLater()
	return False
#----------------------------------------------------------------
def manage_bill_items(parent=None, pk_patient=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()
	#------------------------------------------------------------
	def edit(item=None):
		return edit_bill_item(parent = parent, bill_item = item, single_entry = (item is not None))
	#------------------------------------------------------------
	def delete(item):
		if item.is_in_use is not None:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot delete already invoiced bill items.'), beep = True)
			return False
		gmBilling.delete_bill_item(pk_bill_item = item['pk_bill_item'])
		return True
	#------------------------------------------------------------
	def get_tooltip(item):
		if item is None:
			return None
		return item.format()
	#------------------------------------------------------------
	def refresh(lctrl):
		b_items = gmBilling.get_bill_items(pk_patient = pk_patient)
		items = [ [
			b['date_to_bill'].strftime('%Y %b %d'),
			b['unit_count'],
			'%s: %s%s' % (b['billable_code'], b['billable_description'], gmTools.coalesce(b['item_detail'], '', ' - %s')),
			b['currency'],
			'%s (%s %s %s%s%s)' % (
				b['total_amount'],
				b['unit_count'],
				gmTools.u_multiply,
				b['net_amount_per_unit'],
				gmTools.u_multiply,
				b['amount_multiplier']
			),
			'%s (%s%%)' % (
				b['vat'],
				b['vat_multiplier'] * 100
			),
			'%s (%s)' % (b['catalog_short'], b['catalog_version']),
			b['pk_bill_item']
		] for b in b_items ]
		lctrl.set_string_items(items)
		lctrl.set_data(b_items)
	#------------------------------------------------------------
	gmListWidgets.get_choices_from_list (
		parent = parent,
		#msg = msg,
		caption = _('Showing bill items.'),
		columns = [_('Date'), _('Count'), _('Description'), _('$__replace_by_your_currency_symbol')[:-len('__replace_by_your_currency_symbol')], _('Value'), _('VAT'), _('Catalog'), '#'],
		single_selection = True,
		new_callback = edit,
		edit_callback = edit,
		delete_callback = delete,
		refresh_callback = refresh,
		list_tooltip_callback = get_tooltip
	)

#------------------------------------------------------------
class cPersonBillItemsManagerPnl(gmListWidgets.cGenericListManagerPnl):
	"""A list for managing a patient's bill items.

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
		self.new_callback = self._add_item
		self.edit_callback = self._edit_item
		self.delete_callback = self._del_item

		self.__show_non_invoiced_only = True

		self.__init_ui()
		self.refresh()
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def refresh(self, *args, **kwargs):
		if self.__identity is None:
			self._LCTRL_items.set_string_items()
			return

		b_items = gmBilling.get_bill_items(pk_patient = self.__identity.ID, non_invoiced_only = self.__show_non_invoiced_only)
		items = [ [
			b['date_to_bill'].strftime('%Y %b %d'),
			b['unit_count'],
			'%s: %s%s' % (b['billable_code'], b['billable_description'], gmTools.coalesce(b['item_detail'], '', ' - %s')),
			b['currency'],
			b['total_amount'],
			'%s (%s%%)' % (
				b['vat'],
				b['vat_multiplier'] * 100
			),
			'%s (%s)' % (b['catalog_short'], b['catalog_version']),
			'%s %s %s %s %s' % (
				b['unit_count'],
				gmTools.u_multiply,
				b['net_amount_per_unit'],
				gmTools.u_multiply,
				b['amount_multiplier']
			),
			gmTools.coalesce(b['pk_bill'], gmTools.u_diameter),
			b['pk_encounter_to_bill'],
			b['pk_bill_item']
		] for b in b_items ]

		self._LCTRL_items.set_string_items(items = items)
		self._LCTRL_items.set_column_widths()
		self._LCTRL_items.set_data(data = b_items)
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __init_ui(self):
		self._LCTRL_items.set_columns(columns = [
			_('Charge date'),
			_('Count'),
			_('Description'),
			_('$__replace_by_your_currency_symbol')[:-len('__replace_by_your_currency_symbol')],
			_('Value'),
			_('VAT'),
			_('Catalog'),
			_('Count %s Value %s Factor') % (gmTools.u_multiply, gmTools.u_multiply),
			_('Invoice'),
			_('Encounter'),
			'#'
		])
		self._LCTRL_items.item_tooltip_callback = self._get_item_tooltip
#		self.left_extra_button = (
#			_('Select pending'),
#			_('Select non-invoiced (pending) items.'),
#			self._select_pending_items
#		)
		self.left_extra_button = (
			_('Invoice selected items'),
			_('Create invoice from selected items.'),
			self._invoice_selected_items
		)
		self.middle_extra_button = (
			_('Bills'),
			_('Browse bills of this patient.'),
			self._browse_bills
		)
		self.right_extra_button = (
			_('Billables'),
			_('Browse list of billables.'),
			self._browse_billables
		)
	#--------------------------------------------------------
	def _add_item(self):
		return edit_bill_item(parent = self, bill_item = None, single_entry = False)
	#--------------------------------------------------------
	def _edit_item(self, bill_item):
		return edit_bill_item(parent = self, bill_item = bill_item, single_entry = True)
	#--------------------------------------------------------
	def _del_item(self, item):
		if item['pk_bill'] is not None:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot delete already invoiced bill items.'), beep = True)
			return False
		go_ahead = gmGuiHelpers.gm_show_question (
			_(	'Do you really want to delete this\n'
				'bill item from the patient ?'),
			_('Deleting bill item')
		)
		if not go_ahead:
			return False
		gmBilling.delete_bill_item(pk_bill_item = item['pk_bill_item'])
		return True
	#--------------------------------------------------------
	def _get_item_tooltip(self, item):
		if item is None:
			return None
		return item.format()
	#--------------------------------------------------------
	def _select_pending_items(self, item):
		pass
	#--------------------------------------------------------
	def _invoice_selected_items(self, item):
		bill_items = self._LCTRL_items.get_selected_item_data()
		bill = create_bill_from_items(bill_items)
		if bill is None:
			return
		if bill['pk_receiver_address'] is None:
			gmGuiHelpers.gm_show_error (
				error = _(
					'Cannot create invoice.\n'
					'\n'
					'No receiver address selected.'
				),
				title = _('Creating invoice')
			)
			return
		if bill['close_date'] is None:
			bill['close_date'] = gmDateTime.pydt_now_here()
			bill.save()
		create_invoice_from_bill(parent = self, bill = bill, print_it = True, keep_a_copy = True)
	#--------------------------------------------------------
	def _browse_billables(self, item):
		manage_billables(parent = self)
		return False
	#--------------------------------------------------------
	def _browse_bills(self, item):
		manage_bills(parent = self, patient = self.__identity)
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
	def _get_show_non_invoiced_only(self):
		return self.__show_non_invoiced_only

	def _set_show_non_invoiced_only(self, value):
		self.__show_non_invoiced_only = value
		self.refresh()

	show_non_invoiced_only = property(_get_show_non_invoiced_only, _set_show_non_invoiced_only)

#------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgBillItemEAPnl

class cBillItemEAPnl(wxgBillItemEAPnl.wxgBillItemEAPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwargs):

		try:
			data = kwargs['bill_item']
			del kwargs['bill_item']
		except KeyError:
			data = None

		wxgBillItemEAPnl.wxgBillItemEAPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		self.mode = 'new'
		self.data = data
		if data is not None:
			self.mode = 'edit'

		self.__init_ui()
	#----------------------------------------------------------------
	def __init_ui(self):
		self._PRW_encounter.set_context(context = 'patient', val = gmPerson.gmCurrentPatient().ID)
		self._PRW_billable.add_callback_on_selection(self._on_billable_selected)
		self._PRW_billable.add_callback_on_modified(self._on_billable_modified)
	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):

		validity = True

		if self._TCTRL_factor.GetValue().strip() == '':
			validity = False
			self.display_tctrl_as_valid(tctrl = self._TCTRL_factor, valid = False)
			self._TCTRL_factor.SetFocus()
		else:
			converted, factor = gmTools.input2decimal(self._TCTRL_factor.GetValue())
			if not converted:
				validity = False
				self.display_tctrl_as_valid(tctrl = self._TCTRL_factor, valid = False)
				self._TCTRL_factor.SetFocus()
			else:
				self.display_tctrl_as_valid(tctrl = self._TCTRL_factor, valid = True)

		if self._TCTRL_amount.GetValue().strip() == '':
			validity = False
			self.display_tctrl_as_valid(tctrl = self._TCTRL_amount, valid = False)
			self._TCTRL_amount.SetFocus()
		else:
			converted, factor = gmTools.input2decimal(self._TCTRL_amount.GetValue())
			if not converted:
				validity = False
				self.display_tctrl_as_valid(tctrl = self._TCTRL_amount, valid = False)
				self._TCTRL_amount.SetFocus()
			else:
				self.display_tctrl_as_valid(tctrl = self._TCTRL_amount, valid = True)

		if self._TCTRL_count.GetValue().strip() == '':
			validity = False
			self.display_tctrl_as_valid(tctrl = self._TCTRL_count, valid = False)
			self._TCTRL_count.SetFocus()
		else:
			converted, factor = gmTools.input2decimal(self._TCTRL_count.GetValue())
			if not converted:
				validity = False
				self.display_tctrl_as_valid(tctrl = self._TCTRL_count, valid = False)
				self._TCTRL_count.SetFocus()
			else:
				self.display_tctrl_as_valid(tctrl = self._TCTRL_count, valid = True)

		if self._PRW_date.is_valid_timestamp(empty_is_valid = True):
			self._PRW_date.display_as_valid(True)
		else:
			validity = False
			self._PRW_date.display_as_valid(False)
			self._PRW_date.SetFocus()

		if self._PRW_encounter.GetData() is None:
			validity = False
			self._PRW_encounter.display_as_valid(False)
			self._PRW_encounter.SetFocus()
		else:
			self._PRW_encounter.display_as_valid(True)

		if self._PRW_billable.GetData() is None:
			validity = False
			self._PRW_billable.display_as_valid(False)
			self._PRW_billable.SetFocus()
		else:
			self._PRW_billable.display_as_valid(True)

		return validity
	#----------------------------------------------------------------
	def _save_as_new(self):
		data = gmBilling.create_bill_item (
			pk_encounter = self._PRW_encounter.GetData(),
			pk_billable = self._PRW_billable.GetData(),
			pk_staff = gmStaff.gmCurrentProvider()['pk_staff']		# should be settable !
		)
		data['raw_date_to_bill'] = self._PRW_date.GetData()
		converted, data['unit_count'] = gmTools.input2decimal(self._TCTRL_count.GetValue())
		converted, data['net_amount_per_unit'] = gmTools.input2decimal(self._TCTRL_amount.GetValue())
		converted, data['amount_multiplier'] = gmTools.input2decimal(self._TCTRL_factor.GetValue())
		data['item_detail'] = self._TCTRL_comment.GetValue().strip()
		data.save()

		self.data = data
		return True
	#----------------------------------------------------------------
	def _save_as_update(self):
		self.data['pk_encounter_to_bill'] = self._PRW_encounter.GetData()
		self.data['raw_date_to_bill'] = self._PRW_date.GetData()
		converted, self.data['unit_count'] = gmTools.input2decimal(self._TCTRL_count.GetValue())
		converted, self.data['net_amount_per_unit'] = gmTools.input2decimal(self._TCTRL_amount.GetValue())
		converted, self.data['amount_multiplier'] = gmTools.input2decimal(self._TCTRL_factor.GetValue())
		self.data['item_detail'] = self._TCTRL_comment.GetValue().strip()
		return self.data.save()
	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._PRW_billable.SetText()
		self._PRW_encounter.set_from_instance(gmPerson.gmCurrentPatient().emr.active_encounter)
		self._PRW_date.SetData()
		self._TCTRL_count.SetValue('1')
		self._TCTRL_amount.SetValue('')
		self._LBL_currency.SetLabel(gmTools.u_euro)
		self._TCTRL_factor.SetValue('1')
		self._TCTRL_comment.SetValue('')

		self._PRW_billable.Enable()
		self._PRW_billable.SetFocus()
	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._PRW_billable.SetText()
		self._TCTRL_count.SetValue('1')
		self._TCTRL_amount.SetValue('')
		self._TCTRL_comment.SetValue('')

		self._PRW_billable.Enable()
		self._PRW_billable.SetFocus()
	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		self._PRW_billable.set_from_pk(self.data['pk_billable'])
		self._PRW_encounter.SetData(self.data['pk_encounter_to_bill'])
		self._PRW_date.SetData(data = self.data['raw_date_to_bill'])
		self._TCTRL_count.SetValue('%s' % self.data['unit_count'])
		self._TCTRL_amount.SetValue('%s' % self.data['net_amount_per_unit'])
		self._LBL_currency.SetLabel(self.data['currency'])
		self._TCTRL_factor.SetValue('%s' % self.data['amount_multiplier'])
		self._TCTRL_comment.SetValue(gmTools.coalesce(self.data['item_detail'], ''))

		self._PRW_billable.Disable()
		self._PRW_date.SetFocus()
	#----------------------------------------------------------------
	def _on_billable_selected(self, item):
		if item is None:
			return
		if self._TCTRL_amount.GetValue().strip() != '':
			return
		val = '%s' % self._PRW_billable.GetData(as_instance = True)['raw_amount']
		wx.CallAfter(self._TCTRL_amount.SetValue, val)
	#----------------------------------------------------------------
	def _on_billable_modified(self):
		if self._PRW_billable.GetData() is None:
			wx.CallAfter(self._TCTRL_amount.SetValue, '')

#============================================================
# a plugin for billing
#------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgBillingPluginPnl

class cBillingPluginPnl(wxgBillingPluginPnl.wxgBillingPluginPnl, gmRegetMixin.cRegetOnPaintMixin):
	def __init__(self, *args, **kwargs):

		wxgBillingPluginPnl.wxgBillingPluginPnl.__init__(self, *args, **kwargs)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)
		self.__register_interests()
	#-----------------------------------------------------
	def __reset_ui(self):
		self._PNL_bill_items.identity = None
		self._CHBOX_show_non_invoiced_only.SetValue(1)
		self._PRW_billable.SetText('', None)
		self._TCTRL_factor.SetValue('1.0')
		self._TCTRL_factor.Disable()
		self._TCTRL_details.SetValue('')
		self._TCTRL_details.Disable()
	#-----------------------------------------------------
	# event handling
	#-----------------------------------------------------
	def __register_interests(self):
		gmDispatcher.connect(signal = 'pre_patient_unselection', receiver = self._on_pre_patient_unselection)
		gmDispatcher.connect(signal = 'post_patient_selection', receiver = self._on_post_patient_selection)

		gmDispatcher.connect(signal = 'bill.bill_item_mod_db', receiver = self._on_bill_item_modified)

		self._PRW_billable.add_callback_on_selection(self._on_billable_selected_in_prw)
	#-----------------------------------------------------
	def _on_pre_patient_unselection(self):
		self.__reset_ui()
	#-----------------------------------------------------
	def _on_post_patient_selection(self):
		self._schedule_data_reget()
	#-----------------------------------------------------
	def _on_bill_item_modified(self):
		self._schedule_data_reget()
	#-----------------------------------------------------
	def _on_non_invoiced_only_checkbox_toggled(self, event):
		self._PNL_bill_items.show_non_invoiced_only = self._CHBOX_show_non_invoiced_only.GetValue()
	#--------------------------------------------------------
	def _on_insert_bill_item_button_pressed(self, event):
		if self._PRW_billable.GetData() is None:
			gmGuiHelpers.gm_show_warning (
				_('No billable item selected.\n\nCannot insert bill item.'),
				_('Inserting bill item')
			)
			return False
		val = self._TCTRL_factor.GetValue().strip()
		if val == '':
			factor = 1.0
		else:
			converted, factor = gmTools.input2decimal(val)
			if not converted:
				gmGuiHelpers.gm_show_warning (
					_('"Factor" must be a number\n\nCannot insert bill item.'),
					_('Inserting bill item')
				)
				return False
		bill_item = gmBilling.create_bill_item (
			pk_encounter = gmPerson.gmCurrentPatient().emr.active_encounter['pk_encounter'],
			pk_billable = self._PRW_billable.GetData(),
			pk_staff = gmStaff.gmCurrentProvider()['pk_staff']
		)
		bill_item['amount_multiplier'] = factor
		bill_item['item_detail'] = self._TCTRL_details.GetValue()
		bill_item.save()

		self._TCTRL_details.SetValue('')

		return True
	#--------------------------------------------------------
	def _on_billable_selected_in_prw(self, billable):
		if billable is None:
			self._TCTRL_factor.Disable()
			self._TCTRL_details.Disable()
			self._BTN_insert_item.Disable()
		else:
			self._TCTRL_factor.Enable()
			self._TCTRL_details.Enable()
			self._BTN_insert_item.Enable()
	#-----------------------------------------------------
	# reget-on-paint mixin API
	#-----------------------------------------------------
	def _populate_with_data(self):
		self._PNL_bill_items.identity = gmPerson.gmCurrentPatient()
		return True

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
	#app.SetWidget(cXxxPhraseWheel, -1)
	app.MainLoop()
