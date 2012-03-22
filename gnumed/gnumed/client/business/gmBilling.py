# -*- coding: utf8 -*-
"""Billing code.

Copyright: authors
"""
#============================================================
__author__ = "Nico Latzer <nl@mnet-online.de>, Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL v2 or later (details at http://www.gnu.org)'

import sys
import logging


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmBusinessDBObject
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDateTime
from Gnumed.business import gmDemographicRecord
from Gnumed.business import gmDocuments

_log = logging.getLogger('gm.bill')

INVOICE_DOCUMENT_TYPE = u'invoice'
#============================================================
# billables
#------------------------------------------------------------

_SQL_get_billable_fields = u"SELECT * FROM ref.v_billables WHERE %s"

class cBillable(gmBusinessDBObject.cBusinessDBObject):
	"""Items which can be billed to patients."""

	_cmd_fetch_payload = _SQL_get_billable_fields % u"""pk_billable = %s"""
	_cmds_store_payload = [
		u"""UPDATE ref.billable SET
				code = %(billable_code)s,
				term = %(billable_description)s,
				amount = %(raw_amount)s,
				currency = %(currency)s,
				vat_multiplier = %(vat_multiplier)s
			WHERE
				pk = %(pk_billabs)s
					AND
				xmin = %(xmin_billable)s
			RETURNING
				xmin AS xmin_billable
		"""]

	_updatable_fields = [
		'billable_description',
		'raw_amount',
		'vat_multiplier',
	]
	#--------------------------------------------------------
	def format(self):
		txt = u'%s                                    [#%s]\n\n' % (
			gmTools.bool2subst (
				self._payload[self._idx['active']],
				_('Active billable item'),
				_('Inactive billable item')
			),
			self._payload[self._idx['pk_billable']]
		)
		txt += u' %s: %s\n' % (
			self._payload[self._idx['billable_code']],
			self._payload[self._idx['billable_description']]
		)
		txt += _(' %s %s + %s%% VAT = %s %s\n') % (
			self._payload[self._idx['raw_amount']],
			self._payload[self._idx['currency']],
			self._payload[self._idx['vat_multiplier']] * 100,
			self._payload[self._idx['amount_with_vat']],
			self._payload[self._idx['currency']]
		)
		txt += u' %s %s%s (%s)' % (
			self._payload[self._idx['catalog_short']],
			self._payload[self._idx['catalog_version']],
			gmTools.coalesce(self._payload[self._idx['catalog_language']], u'', ' - %s'),
			self._payload[self._idx['catalog_long']]
		)
		txt += gmTools.coalesce(self._payload[self._idx['comment']], u'', u'\n %s')

		return txt
	#--------------------------------------------------------
	def _get_is_in_use(self):
		cmd = u'SELECT EXISTS(SELECT 1 FROM bill.bill_item WHERE fk_billable = %(pk)s LIMIT 1)'
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': {'pk': self._payload[self._idx['pk_billable']]}}])
		return rows[0][0]

	is_in_use = property(_get_is_in_use, lambda x:x)
#------------------------------------------------------------
def get_billables(active_only=True, order_by=None):

	if order_by is None:
		order_by = u' ORDER BY catalog_long, catalog_version, billable_code'
	else:
		order_by = u' ORDER BY %s' % order_by

	if active_only:
		where = u'active IS true'
	else:
		where = u'true'

	cmd = (_SQL_get_billable_fields % where) + order_by
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = True)
	return [ cBillable(row = {'data': r, 'idx': idx, 'pk_field': 'pk_billable'}) for r in rows ]
#------------------------------------------------------------
def delete_billable(pk_billable=None):
	cmd = u"""
		DELETE FROM ref.billable
		WHERE
			pk = %(pk)s
				AND
			NOT EXISTS (
				SELECT 1 FROM bill.bill_item WHERE fk_billable = %(pk)s
			)
	"""
	args = {'pk': pk_billable}
	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
#============================================================
# bill items
#------------------------------------------------------------
_SQL_fetch_bill_item_fields = u"SELECT * FROM bill.v_bill_items WHERE %s"

class cBillItem(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = _SQL_fetch_bill_item_fields % u"pk_bill_item = %s"
	_cmds_store_payload = [
		u"""UPDATE bill.bill_item SET
				fk_provider = %(pk_provider)s,
				fk_encounter = %(pk_encounter_to_bill)s,
				date_to_bill = %(raw_date_to_bill)s,
				description = gm.nullify_empty_string(%(item_detail)s),
				net_amount_per_unit = %(net_amount_per_unit)s,
				currency = gm.nullify_empty_string(%(currency)s),
				fk_bill = %(pk_bill)s,
				unit_count = %(unit_count)s,
				amount_multiplier = %(amount_multiplier)s
			WHERE
				pk = %(pk_bill_item)s
					AND
				xmin = %(xmin_bill_item)s
			RETURNING
				xmin AS xmin_bill_item
		"""]

	_updatable_fields = [
		'pk_provider',
		'pk_encounter_to_bill',
		'raw_date_to_bill',
		'item_detail',
		'net_amount_per_unit',
		'currency',
		'pk_bill',
		'unit_count',
		'amount_multiplier'
	]
	#--------------------------------------------------------
	def format(self):
		return u'%s' % self
	#--------------------------------------------------------
	def _get_is_in_use(self):
		return self._payload[self._idx['pk_bill']] is not None

	is_in_use = property(_get_is_in_use, lambda x:x)
#------------------------------------------------------------
def get_bill_items(pk_patient=None, non_invoiced_only=False):
	if non_invoiced_only:
		cmd = _SQL_fetch_bill_item_fields % u"pk_patient = %(pat)s AND pk_bill IS NULL"
	else:
		cmd = _SQL_fetch_bill_item_fields % u"pk_patient = %(pat)s"
	args = {'pat': pk_patient}
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
	return [ cBillItem(row = {'data': r, 'idx': idx, 'pk_field': 'pk_bill_item'}) for r in rows ]
#------------------------------------------------------------
def create_bill_item(pk_encounter=None, pk_billable=None, pk_staff=None):

	billable = cBillable(aPK_obj = pk_billable)
	cmd = u"""
		INSERT INTO bill.bill_item (
			fk_provider,
			fk_encounter,
			net_amount_per_unit,
			currency,
			fk_billable
		) VALUES (
			%(staff)s,
			%(enc)s,
			%(val)s,
			%(curr)s,
			%(billable)s
		)
		RETURNING pk"""
	args = {
		'staff': pk_staff,
		'enc': pk_encounter,
		'val': billable['raw_amount'],
		'curr': billable['currency'],
		'billable': pk_billable
	}
	rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True)
	return cBillItem(aPK_obj = rows[0][0])
#------------------------------------------------------------
def delete_bill_item(pk_bill_item=None):
	cmd = u'DELETE FROM bill.bill_item WHERE pk = %(pk)s AND fk_bill IS NULL'
	args = {'pk': pk_bill_item}
	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])

#============================================================
# bills
#------------------------------------------------------------
_SQL_get_bill_fields = u"""SELECT * FROM bill.v_bills WHERE %s"""

class cBill(gmBusinessDBObject.cBusinessDBObject):
	"""Represents a bill"""

	_cmd_fetch_payload = _SQL_get_bill_fields % u"pk_bill = %s"
	_cmds_store_payload = [
		u"""UPDATE bill.bill SET
				invoice_id = gm.nullify_empty_string(%(invoice_id)s),
				close_date = %(close_date)s,
				apply_vat = %(apply_vat)s,
				fk_receiver_identity = %(pk_receiver_identity)s,
				fk_receiver_address = %(pk_receiver_address)s
			WHERE
				pk = %(pk_bill)s
					AND
				xmin = %(xmin_bill)s
			RETURNING
				pk as pk_bill,
				xmin as xmin_bill
		"""
	]
	_updatable_fields = [
		u'invoice_id',
		u'pk_receiver_identity',
		u'close_date',
		u'apply_vat',
		u'pk_receiver_address'
	]
	#--------------------------------------------------------
	def format(self):
		txt = u'%s                       [#%s]\n' % (
			gmTools.bool2subst (
				(self._payload[self._idx['close_date']] is None),
				_('Open bill'),
				_('Closed bill')
			),
			self._payload[self._idx['pk_bill']]
		)
		txt += _(' Invoice ID: %s\n') % self._payload[self._idx['invoice_id']]
		if self._payload[self._idx['close_date']] is not None:
			txt += _(' Closed: %s\n') % gmDateTime.pydt_strftime (
				self._payload[self._idx['close_date']],
				'%Y %b %d',
				accuracy = gmDateTime.acc_days
			)
		txt += _(' Bill value: %s %s\n') % (
			self._payload[self._idx['total_amount']],
			self._payload[self._idx['currency']]
		)
		if self._payload[self._idx['apply_vat']]:
			txt += _(' VAT: %s%% %s %s %s\n') % (
				self._payload[self._idx['percent_vat']],
				gmTools.u_corresponds_to,
				self._payload[self._idx['total_vat']],
				self._payload[self._idx['currency']]
			)
			txt += _(' Value + VAT: %s %s\n') % (
				self._payload[self._idx['total_amount_with_vat']],
				self._payload[self._idx['currency']]
			)
		else:
			txt += _(' VAT: does not apply\n')
		txt += _(' Items billed: %s\n') % len(self._payload[self._idx['pk_bill_items']])
		txt += _(' Patient: #%s\n') % self._payload[self._idx['pk_patient']]
		txt += gmTools.coalesce (
			self._payload[self._idx['pk_receiver_identity']],
			u'',
			_(' Receiver: %s\n')
		)
		if self._payload[self._idx['pk_receiver_address']] is not None:
			txt += u'\n '.join(gmDemographicRecord.get_patient_address(pk_patient_address = self._payload[self._idx['pk_receiver_address']]).format())

		return txt
	#--------------------------------------------------------
	def add_items(self, items=None):
		"""Requires no pending changes within the bill itself."""
		# should check for item consistency first
		conn = gmPG2.get_connection(readonly = False)
		for item in items:
			item['pk_bill'] = self._payload[self._idx['pk_bill']]
			item.save(conn = conn)
		conn.commit()
		self.refetch_payload()		# make sure aggregates are re-filled from view
	#--------------------------------------------------------
	def _get_bill_items(self):
		return [ cBillItem(aPK_obj = pk) for pk in self._payload[self._idx['pk_bill_items']] ]

	bill_items = property(_get_bill_items, lambda x:x)
	#--------------------------------------------------------
	def _get_invoice(self):
		invoices = gmDocuments.search_for_documents (
			patient_id = self._payload[self._idx['pk_patient']],
			type_id = gmDocuments.get_document_type_pk(document_type = INVOICE_DOCUMENT_TYPE),
			# this *should* make it unique:
			external_reference = self._payload[self._idx['invoice_id']]
		)
		if len(invoices) == 0:
			return None
		if len(invoices) == 1:
			return invoices[0]
		raise EnvironmentError('there is more than one invoice PDF for this bill')

	invoice = property(_get_invoice, lambda x:x)
#------------------------------------------------------------
def get_bills(order_by=None, pk_patient=None):

	args = {'pat': pk_patient}
	where_parts = [u'true']

	if pk_patient is not None:
		where_parts.append(u'pk_patient = %(pat)s')

	if order_by is None:
		order_by = u''
	else:
		order_by = u' ORDER BY %s' % order_by

	cmd = (_SQL_get_bill_fields % u' AND '.join(where_parts)) + order_by
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
	return [ cBill(row = {'data': r, 'idx': idx, 'pk_field': 'pk_bill'}) for r in rows ]
#------------------------------------------------------------
def create_bill(conn=None, invoice_id=None):

	args = {u'inv_id': invoice_id}
	cmd = u"""
		INSERT INTO bill.bill (invoice_id)
		VALUES (gm.nullify_empty_string(%(inv_id)s))
		RETURNING pk
	"""
	rows, idx = gmPG2.run_rw_queries(link_obj = conn, queries = [{'cmd': cmd, 'args': args}], return_data = True, get_col_idx = False)

	return cBill(aPK_obj = rows[0]['pk'])
#------------------------------------------------------------
def delete_bill(pk_bill=None):
	args = {'pk': pk_bill}
	cmd = u"DELETE FROM bill.bill WHERE pk = %(pk)s"
	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
	return True
#------------------------------------------------------------
def get_bill_receiver(pk_patient=None):
	pass
#------------------------------------------------------------
def get_invoice_id(pk_patient=None):
	return u'GM%s / %s' % (
		pk_patient,
		gmDateTime.pydt_strftime (
			gmDateTime.pydt_now_here(),
			'%Y-%m-%d / %H%M%S'
		)
	)
#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

#	from Gnumed.pycommon import gmLog2
#	from Gnumed.pycommon import gmI18N
#	from Gnumed.business import gmPerson

#	gmI18N.activate_locale()
##	gmDateTime.init()

	def test_me():
		print "--------------"
		me = cBillable(aPK_obj=1)
		fields = me.get_fields()
		for field in fields:
			print field, ':', me[field]
		print "updatable:", me.get_updatable_fields()
		#me['vat']=4; me.store_payload()

	test_me()
