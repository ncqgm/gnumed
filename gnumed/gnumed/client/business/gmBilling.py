# -*- coding: utf8 -*-
"""Billing code.

license: GPL v2 or later
"""
#============================================================
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

import sys
import logging


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmBusinessDBObject
from Gnumed.pycommon import gmTools


_log = logging.getLogger('gm.bill')

#============================================================
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

#============================================================
_SQL_fetch_bill_item_fields = u"SELECT * FROM bill.v_bill_items WHERE %s"

class cBillItem(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = _SQL_fetch_bill_item_fields % u"pk_bill_item = %s"
	_cmds_store_payload = [
		u"""UPDATE bill.bill_item SET
				fk_provider = %(pk_provider)s,
				fk_encounter = %(pk_encounter_to_bill)s,
				date_to_bill = %(date_to_bill)s,
				description = gm.nullify_empty_string(%(item_detail)s),
				net_amount_per_unit = %(net_amount_per_unit)s,
				currency = gm.nullify_empty_string(%(currency)s),
				status = %(status)s,
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
		'date_to_bill',
		'item_detail',
		'net_amount_per_unit',
		'currency',
		'status',
		'pk_bill',
		'unit_count',
		'amount_multiplier'
	]

#------------------------------------------------------------
def get_bill_items(pk_patient=None):
	cmd = _SQL_fetch_bill_item_fields % u"pk_patient = %(pat)s"
	args = {'pat': pk_patient}
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
	return [ cBillItem(row = {'data': r, 'idx': idx, 'pk_field': 'pk_bill_item'}) for r in rows ]

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
