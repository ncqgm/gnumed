# -*- coding: utf8 -*-
"""Billing code.

license: GPL v2 or later
"""
#============================================================
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

import sys
import logging
#import codecs


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmBusinessDBObject
from Gnumed.pycommon import gmTools


_log = logging.getLogger('gm.bill')

#============================================================
#class cChargeItemGroup(gmBusinessDBObject.cBusinessDBObject):
#	"""An Charge Item Group
#	"""
#	_cmd_fetch_payload = u"select *, xmin from bill.ci_category where pk=%s"
#	_cmds_store_payload = [
#		u"""update bill.ci_category set
#				description=%(description)s
#			where
#				pk=%(pk)s and
#				xmin=%(xmin)s""",
#		]
#
#	_updatable_fields = [
#		'description',
#	]
#
#============================================================
_SQL_get_billable_fields = u"""SELECT * FROM ref.v_billables WHERE %s"""

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
				xmin = %(xmin_billable)s"""
		]

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
#def create_charge_item_group(description=None):
#	"""Creates a new charge_item_group
#
#		description
#	"""
#	queries = [
#		{'cmd': u"insert into bill.ci_category (description) values (%s) returning pk",
#		 'args': [description or u'' ]
#		},
#	]
#	rows, idx = gmPG2.run_rw_queries(queries = queries, return_data=True)
#
#	new = cChargeItemGroup(aPK_obj = rows[0][0])
#	return (True, new)
#
#
#def create_charge_item(description=None):
#	"""Creates a new charge_item
#
#		description
#		category - category
#	"""
#	queries = [
#		{'cmd': u"insert into ref.billable (description) values (%s) returning pk",
#		 'args': [description or u'' ]
#		},
#	]
#	rows, idx = gmPG2.run_rw_queries(queries = queries, return_data=True)
#
#	new = cBillable(aPK_obj = rows[0][0])
#	return (True, new)

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
		print "\test"
		print	"--------------"
		me = cBillable(aPK_obj=1)
		fields = me.get_fields()
		for field in fields:
			print field, ':', me[field]
		print "updatable:", me.get_updatable_fields()
		#me['vat']=4; me.store_payload()

	test_me()
