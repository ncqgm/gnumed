# -*- coding: utf-8 -*-
"""Billing code.

Copyright: authors
"""
#============================================================
__author__ = "Nico Latzer <nl@mnet-online.de>, Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL v2 or later (details at https://www.gnu.org)'

import sys
import zlib
import decimal
import logging


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmBusinessDBObject

from Gnumed.business import gmDemographicRecord
from Gnumed.business import gmDocuments

_log = logging.getLogger('gm.bill')

INVOICE_DOCUMENT_TYPE = 'invoice'
# default: old style
DEFAULT_INVOICE_ID_TEMPLATE = 'GM%(pk_pat)s / %(date)s / %(time)s'

#============================================================
# billables
#------------------------------------------------------------
_SQL_get_billable_fields = "SELECT * FROM ref.v_billables WHERE %s"

class cBillable(gmBusinessDBObject.cBusinessDBObject):
	"""Items which can be billed to patients."""

	_cmd_fetch_payload = _SQL_get_billable_fields % "pk_billable = %s"
	_cmds_store_payload = [
		"""UPDATE ref.billable SET
				fk_data_source = %(pk_data_source)s,
				code = %(billable_code)s,
				term = %(billable_description)s,
				comment = gm.nullify_empty_string(%(comment)s),
				amount = %(raw_amount)s,
				currency = %(currency)s,
				vat_multiplier = %(vat_multiplier)s,
				active = %(active)s
				--, discountable = %(discountable)s
			WHERE
				pk = %(pk_billable)s
					AND
				xmin = %(xmin_billable)s
			RETURNING
				xmin AS xmin_billable
		"""]

	_updatable_fields = [
		'billable_code',
		'billable_description',
		'raw_amount',
		'vat_multiplier',
		'comment',
		'currency',
		'active',
		'pk_data_source'
	]
	#--------------------------------------------------------
	def format(self):
		txt = '%s                                    [#%s]\n\n' % (
			gmTools.bool2subst (
				self._payload['active'],
				_('Active billable item'),
				_('Inactive billable item')
			),
			self._payload['pk_billable']
		)
		txt += ' %s: %s\n' % (
			self._payload['billable_code'],
			self._payload['billable_description']
		)
		txt += _(' %(curr)s%(raw_val)s + %(perc_vat)s%% VAT = %(curr)s%(val_w_vat)s\n') % {
			'curr': self._payload['currency'],
			'raw_val': self._payload['raw_amount'],
			'perc_vat': self._payload['vat_multiplier'] * 100,
			'val_w_vat': self._payload['amount_with_vat']
		}
		txt += ' %s %s%s (%s)' % (
			self._payload['catalog_short'],
			self._payload['catalog_version'],
			gmTools.coalesce(self._payload['catalog_language'], '', ' - %s'),
			self._payload['catalog_long']
		)
		txt += gmTools.coalesce(self._payload['comment'], '', '\n %s')

		return txt
	#--------------------------------------------------------
	def _get_is_in_use(self):
		cmd = 'SELECT EXISTS(SELECT 1 FROM bill.bill_item WHERE fk_billable = %(pk)s LIMIT 1)'
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': {'pk': self._payload['pk_billable']}}])
		return rows[0][0]

	is_in_use = property(_get_is_in_use)

#------------------------------------------------------------
def get_billables(active_only=True, order_by=None, return_pks=False):

	if order_by is None:
		order_by = ' ORDER BY catalog_long, catalog_version, billable_code'
	else:
		order_by = ' ORDER BY %s' % order_by

	if active_only:
		where = 'active IS true'
	else:
		where = 'true'

	cmd = (_SQL_get_billable_fields % where) + order_by
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd}])
	if return_pks:
		return [ r['pk_billable'] for r in rows ]
	return [ cBillable(row = {'data': r, 'pk_field': 'pk_billable'}) for r in rows ]

#------------------------------------------------------------
def create_billable(code=None, term=None, data_source=None, return_existing=False):
	args = {
		'code': code.strip(),
		'term': term.strip(),
		'data_src': data_source
	}
	cmd = """
		INSERT INTO ref.billable (code, term, fk_data_source)
		SELECT
			%(code)s,
			%(term)s,
			%(data_src)s
		WHERE NOT EXISTS (
			SELECT 1 FROM ref.billable
			WHERE
				code = %(code)s
					AND
				term = %(term)s
					AND
				fk_data_source = %(data_src)s
		)
		RETURNING pk"""
	rows = gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}], return_data = True)
	if len(rows) > 0:
		return cBillable(aPK_obj = rows[0]['pk'])

	if not return_existing:
		return None

	cmd = """
		SELECT * FROM ref.v_billables
		WHERE
			code = %(code)s
				AND
			term = %(term)s
				AND
			pk_data_source = %(data_src)s
	"""
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	return cBillable(row = {'data': rows[0], 'pk_field': 'pk_billable'})

#------------------------------------------------------------
def delete_billable(pk_billable=None):
	cmd = """
		DELETE FROM ref.billable
		WHERE
			pk = %(pk)s
				AND
			NOT EXISTS (
				SELECT 1 FROM bill.bill_item WHERE fk_billable = %(pk)s
			)
	"""
	args = {'pk': pk_billable}
	gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])

#============================================================
# bill items
#------------------------------------------------------------
_SQL_get_bill_item_fields = u"SELECT * FROM bill.v_bill_items WHERE %s"

class cBillItem(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = _SQL_get_bill_item_fields % u"pk_bill_item = %s"
	_cmds_store_payload = [
		"""UPDATE bill.bill_item SET
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
		txt = '%s (%s %s%s)         [#%s]\n' % (
			gmTools.bool2subst(
				self._payload['pk_bill'] is None,
				_('Open item'),
				_('Billed item'),
			),
			self._payload['catalog_short'],
			self._payload['catalog_version'],
			gmTools.coalesce(self._payload['catalog_language'], '', ' - %s'),
			self._payload['pk_bill_item']
		)
		txt += ' %s: %s\n' % (
			self._payload['billable_code'],
			self._payload['billable_description']
		)
		txt += gmTools.coalesce (
			self._payload['billable_comment'],
			'',
			'  (%s)\n',
		)
		txt += gmTools.coalesce (
			self._payload['item_detail'],
			'',
			_(' Details: %s\n'),
		)

		txt += '\n'
		txt += _(' %s of units: %s\n') % (
			gmTools.u_numero,
			self._payload['unit_count']
		)
		txt += _(' Amount per unit: %(curr)s%(val_p_unit)s (%(cat_curr)s%(cat_val)s per catalog)\n') % {
			'curr': self._payload['currency'],
			'val_p_unit': self._payload['net_amount_per_unit'],
			'cat_curr': self._payload['billable_currency'],
			'cat_val': self._payload['billable_amount']
		}
		txt += _(' Amount multiplier: %s\n') % self._payload['amount_multiplier']
		txt += _(' VAT would be: %(perc_vat)s%% %(equals)s %(curr)s%(vat)s\n') % {
			'perc_vat': self._payload['vat_multiplier'] * 100,
			'equals': gmTools.u_corresponds_to,
			'curr': self._payload['currency'],
			'vat': self._payload['vat']
		}

		txt += '\n'
		txt += _(' Charge date: %s') % self._payload['date_to_bill'].strftime('%Y %b %d')
		if self._payload['pk_bill']:
			txt += _('\n On bill: %s') % self.bill['invoice_id']

		return txt

	#--------------------------------------------------------
	def _get_billable(self):
		return cBillable(aPK_obj = self._payload['pk_billable'])

	billable = property(_get_billable)
	#--------------------------------------------------------
	def _get_bill(self):
		if self._payload['pk_bill'] is None:
			return None

		return cBill(aPK_obj = self._payload['pk_bill'])

	bill = property(_get_bill)
	#--------------------------------------------------------
	def _get_is_in_use(self):
		return self._payload['pk_bill'] is not None

	is_in_use = property(_get_is_in_use)
#------------------------------------------------------------
def get_bill_items(pk_patient=None, non_invoiced_only=False, return_pks=False):
	if non_invoiced_only:
		cmd = _SQL_get_bill_item_fields % u"pk_patient = %(pat)s AND pk_bill IS NULL"
	else:
		cmd = _SQL_get_bill_item_fields % u"pk_patient = %(pat)s"
	args = {'pat': pk_patient}
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	if return_pks:
		return [ r['pk_bill_item'] for r in rows ]
	return [ cBillItem(row = {'data': r, 'pk_field': 'pk_bill_item'}) for r in rows ]

#------------------------------------------------------------
def create_bill_item(pk_encounter=None, pk_billable=None, pk_staff=None):

	billable = cBillable(aPK_obj = pk_billable)
	cmd = """
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
	rows = gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}], return_data = True)
	return cBillItem(aPK_obj = rows[0][0])

#------------------------------------------------------------
def delete_bill_item(link_obj=None, pk_bill_item=None):
	cmd = 'DELETE FROM bill.bill_item WHERE pk = %(pk)s AND fk_bill IS NULL'
	args = {'pk': pk_bill_item}
	gmPG2.run_rw_queries(link_obj = link_obj, queries = [{'sql': cmd, 'args': args}])

#============================================================
# bills
#------------------------------------------------------------
_SQL_get_bill_fields = """SELECT * FROM bill.v_bills WHERE %s"""

class cBill(gmBusinessDBObject.cBusinessDBObject):
	"""Represents a bill"""

	_cmd_fetch_payload = _SQL_get_bill_fields % "pk_bill = %s"
	_cmds_store_payload = [
		"""UPDATE bill.bill SET
				invoice_id = gm.nullify_empty_string(%(invoice_id)s),
				close_date = %(close_date)s,
				apply_vat = %(apply_vat)s,
				comment = gm.nullify_empty_string(%(comment)s),
				fk_receiver_identity = %(pk_receiver_identity)s,
				fk_receiver_address = %(pk_receiver_address)s,
				fk_doc = %(pk_doc)s
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
		'invoice_id',
		'pk_receiver_identity',
		'close_date',
		'apply_vat',
		'comment',
		'pk_receiver_address',
		'pk_doc'
	]
	#--------------------------------------------------------
	def format(self, include_receiver=True, include_doc=True):
		txt = '%s                       [#%s]\n' % (
			gmTools.bool2subst (
				(self._payload['close_date'] is None),
				_('Open bill'),
				_('Closed bill')
			),
			self._payload['pk_bill']
		)
		txt += _(' Invoice ID: %s\n') % self._payload['invoice_id']
		if self._payload['close_date']:
			txt += _(' Closed: %s\n') % self._payload['close_date'].strftime('%Y %b %d')
		if self._payload['comment']:
			txt += _(' Comment: %s\n') % self._payload['comment']
		txt += _(' Bill value: %(curr)s%(val)s\n') % {
			'curr': self._payload['currency'],
			'val': self._payload['total_amount']
		}

		if self._payload['apply_vat'] is None:
			txt += _(' VAT: undecided\n')
		elif self._payload['apply_vat'] is True:
			txt += _(' VAT: %(perc_vat)s%% %(equals)s %(curr)s%(vat)s\n') % {
				'perc_vat': self._payload['percent_vat'],
				'equals': gmTools.u_corresponds_to,
				'curr': self._payload['currency'],
				'vat': self._payload['total_vat']
			}
			txt += _(' Value + VAT: %(curr)s%(val)s\n') % {
				'curr': self._payload['currency'],
				'val': self._payload['total_amount_with_vat']
			}
		else:
			txt += _(' VAT: does not apply\n')

		if self._payload['pk_bill_items'] is None:
			txt += _(' Items billed: 0\n')
		else:
			txt += _(' Items billed: %s\n') % len(self._payload['pk_bill_items'])
		if include_doc:
			txt += _(' Invoice: %s\n') % (
				gmTools.bool2subst (
					self._payload['pk_doc'] is None,
					_('not available'),
					'#%s' % self._payload['pk_doc']
				)
			)
		txt += _(' Patient: #%s\n') % self._payload['pk_patient']
		if include_receiver:
			txt += gmTools.coalesce (
				self._payload['pk_receiver_identity'],
				'',
				_(' Receiver: #%s\n')
			)
			if self._payload['pk_receiver_address'] is not None:
				txt += '\n '.join(gmDemographicRecord.get_patient_address(pk_patient_address = self._payload['pk_receiver_address']).format())

		return txt

	#--------------------------------------------------------
	def add_items(self, items=None):
		"""Requires no pending changes within the bill itself."""
		# should check for item consistency first
		conn = gmPG2.get_connection(readonly = False)
		for item in items:
			item['pk_bill'] = self._payload['pk_bill']
			item.save(conn = conn)
		conn.commit()
		self.refetch_payload()		# make sure aggregates are re-filled from view
	#--------------------------------------------------------
	def _get_bill_items(self):
		return [ cBillItem(aPK_obj = pk) for pk in self._payload['pk_bill_items'] ]

	bill_items = property(_get_bill_items)
	#--------------------------------------------------------
	def _get_invoice(self):
		if self._payload['pk_doc'] is None:
			return None
		return gmDocuments.cDocument(aPK_obj = self._payload['pk_doc'])

	invoice = property(_get_invoice)
	#--------------------------------------------------------
	def _get_address(self):
		if self._payload['pk_receiver_address'] is None:
			return None
		return gmDemographicRecord.get_address_from_patient_address_pk (
			pk_patient_address = self._payload['pk_receiver_address']
		)

	address = property(_get_address)
	#--------------------------------------------------------
	def _get_default_address(self):
		return gmDemographicRecord.get_patient_address_by_type (
			pk_patient = self._payload['pk_patient'],
			adr_type = 'billing'
		)

	default_address = property(_get_default_address)
	#--------------------------------------------------------
	def _get_home_address(self):
		return gmDemographicRecord.get_patient_address_by_type (
			pk_patient = self._payload['pk_patient'],
			adr_type = 'home'
		)

	home_address = property(_get_home_address)
	#--------------------------------------------------------
	def set_missing_address_from_default(self):
		if self._payload['pk_receiver_address'] is not None:
			return True
		adr = self.default_address
		if adr is None:
			adr = self.home_address
			if adr is None:
				return False
		self['pk_receiver_address'] = adr['pk_lnk_person_org_address']
		return self.save_payload()

#------------------------------------------------------------
def get_bills(order_by=None, pk_patient=None, return_pks=False):

	args = {'pat': pk_patient}
	where_parts = ['true']

	if pk_patient is not None:
		where_parts.append('pk_patient = %(pat)s')

	if order_by is None:
		order_by = ''
	else:
		order_by = ' ORDER BY %s' % order_by

	cmd = (_SQL_get_bill_fields % ' AND '.join(where_parts)) + order_by
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	if return_pks:
		return [ r['pk_bill'] for r in rows ]
	return [ cBill(row = {'data': r, 'pk_field': 'pk_bill'}) for r in rows ]

#------------------------------------------------------------
def get_bills4document(pk_document=None):
	args = {'pk_doc': pk_document}
	cmd = _SQL_get_bill_fields % 'pk_doc = %(pk_doc)s'
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	return [ cBill(row = {'data': r, 'pk_field': 'pk_bill'}) for r in rows ]

#------------------------------------------------------------
def create_bill(conn=None, invoice_id=None):

	args = {'inv_id': invoice_id}
	cmd = """
		INSERT INTO bill.bill (invoice_id)
		VALUES (gm.nullify_empty_string(%(inv_id)s))
		RETURNING pk
	"""
	rows = gmPG2.run_rw_queries(link_obj = conn, queries = [{'sql': cmd, 'args': args}], return_data = True)

	return cBill(aPK_obj = rows[0]['pk'])

#------------------------------------------------------------
def delete_bill(link_obj=None, pk_bill=None):
	args = {'pk': pk_bill}
	cmd = "DELETE FROM bill.bill WHERE pk = %(pk)s"
	gmPG2.run_rw_queries(link_obj = link_obj, queries = [{'sql': cmd, 'args': args}])
	return True

#------------------------------------------------------------
def get_bill_receiver(pk_patient=None):
	pass

#------------------------------------------------------------
def generate_invoice_id(template=None, pk_patient=None, person=None, date_format='%Y-%m-%d', time_format='%H%M%S'):
	"""Generate invoice ID string, based on template.

	No template given -> generate old style fixed format invoice ID.

	Placeholders:
		%(pk_pat)s
		%(date)s
		%(time)s
			if included, $counter$ is not *needed* (but still possible)
		%(firstname)s
		%(lastname)s
		%(dob)s

		#counter#
			will be replaced by a counter, counting up from 1 until the invoice id is unique, max 999999
	"""
	assert (None in [pk_patient, person]), u'either of <pk_patient> or <person> can be defined, but not both'

	if (template is None) or (template.strip() == u''):
		template = DEFAULT_INVOICE_ID_TEMPLATE
		date_format = '%Y-%m-%d'
		time_format = '%H%M%S'
	template = template.strip()
	_log.debug('invoice ID template: %s', template)
	if pk_patient is None:
		if person is not None:
			pk_patient = person.ID
	now = gmDateTime.pydt_now_here()
	data = {}
	data['pk_pat'] = gmTools.coalesce(pk_patient, '?')
	data['date'] = now.strftime(date_format).strip()
	data['time'] = now.strftime(time_format).strip()
	if person is None:
		data['firstname'] = u'?'
		data['lastname'] = u'?'
		data['dob'] = u'?'
	else:
		data['firstname'] = person['firstnames'].replace(' ', gmTools.u_space_as_open_box).strip()
		data['lastname'] = person['lastnames'].replace(' ', gmTools.u_space_as_open_box).strip()
		data['dob'] = person.get_formatted_dob (
			format = date_format,
			none_string = '?',
			honor_estimation = False
		).strip()
	candidate_invoice_id = template % data
	if u'#counter#' not in candidate_invoice_id:
		if u'%(time)s' in template:
			return candidate_invoice_id

		candidate_invoice_id = candidate_invoice_id + u' [##counter#]'

	_log.debug('invoice id candidate: %s', candidate_invoice_id)
	# get existing invoice IDs consistent with candidate
	search_term = u'^\s*%s\s*$' % gmPG2.sanitize_pg_regex(expression = candidate_invoice_id).replace(u'#counter#', '\d+')
	cmd = u'SELECT invoice_id FROM bill.bill WHERE invoice_id ~* %(search_term)s UNION ALL SELECT invoice_id FROM audit.log_bill WHERE invoice_id ~* %(search_term)s'
	args = {'search_term': search_term}
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	if len(rows) == 0:
		return candidate_invoice_id.replace(u'#counter#', u'1')

	existing_invoice_ids = [ r['invoice_id'].strip() for r in rows ]
	counter = None
	counter_max = 999999
	for idx in range(1, counter_max):
		candidate = candidate_invoice_id.replace(u'#counter#', '%s' % idx)
		if candidate not in existing_invoice_ids:
			counter = idx
			break
	if counter is None:
		# exhausted the range, unlikely (1 million bills are possible
		# even w/o any other invoice ID data) but technically possible
		_log.debug('exhausted uniqueness space of [%s] invoice IDs per template', counter_max)
		counter = '>%s[%s]' % (counter_max, data['time'])

	return candidate_invoice_id.replace(u'#counter#', '%s' % counter)

#------------------------------------------------------------
def __generate_invoice_id_lock_token(invoice_id):
	"""Turn invoice ID into integer token for PG level locking.

	CAUTION: This is NOT compatible with any of 1.8 or below.
	Do NOT attempt to run this against a v22 database at the
	risk of duplicate invoice IDs.
	"""
	_log.debug('invoice ID: %s', invoice_id)
	data4adler32 = 'adler32---[%s]---[%s]' % (invoice_id, invoice_id)
	adler32 = zlib.adler32(bytes(data4adler32, 'utf8'))
	_log.debug('adler32: %s', adler32)
	data4crc32 = 'crc32---[%s]---[adler32:%s]' % (invoice_id, adler32)
	_log.debug('data for CRC 32: %s', data4crc32)
	crc32 = zlib.crc32(bytes(data4crc32, 'utf8'), adler32)
	_log.debug('CRC 32: %s', crc32)
	return crc32

#------------------------------------------------------------
def lock_invoice_id(invoice_id):
	"""Lock an invoice ID.

	The lock taken is an exclusive advisory lock in PostgreSQL.

	Because the data is short _and_ crc32/adler32 are fairly
	weak we assume that collisions can be created "easily".
	Therefore we apply both algorithms concurrently.

	NOT compatible with anything 1.8 or below.
	"""
	_log.debug('locking invoice ID: %s', invoice_id)
	token = __generate_invoice_id_lock_token(invoice_id)
	cmd = "SELECT pg_try_advisory_lock(%s)" % token
	try:
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd}])
	except gmPG2.dbapi.ProgrammingError:
		_log.exception('cannot lock invoice ID: [%s] (%s)', invoice_id, token)
		return False

	if rows[0][0]:
		return True

	_log.error('cannot lock invoice ID: [%s] (%s)', invoice_id, token)
	return False

#------------------------------------------------------------
def unlock_invoice_id(invoice_id):
	_log.debug('unlocking invoice ID: %s', invoice_id)
	token = __generate_invoice_id_lock_token(invoice_id)
	cmd = u"SELECT pg_advisory_unlock(%s)" % token
	try:
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd}])
	except gmPG2.dbapi.ProgrammingError:
		_log.exception('cannot unlock invoice ID: [%s] (%s)', invoice_id, token)
		return False

	if rows[0][0]:
		return True

	_log.error('cannot unlock invoice ID: [%s] (%s)', invoice_id, token)
	return False

#------------------------------------------------------------
def generate_scan2pay_qrcode(data:str=None, create_svg:bool=False):
	return gmTools.create_qrcode (
		text = data,
		verbose = False,
		ecc_level = 'M',		# Wikipedia says must be M
		create_svg = create_svg
	)

#------------------------------------------------------------
def generate_scan2pay_string (
	IBAN:str=None,
	beneficiary:str=None,
	BIC:str=None,
	amount:str|int|decimal.Decimal='',
	invoice_id:str=None,
	comment:str=None
) -> str:
	"""Create scan2pay data for generating a QR code.

	https://www.scan2pay.info
	--------------------------------
	BCD														# (3) fixed, barcode tag
	002														# (3) fixed, version
	1														# (1) charset, 1 = utf8
	SCT														# (3) fixed
	$<praxis_id::BIC//Bank//%(value)s::11>$					# (11) <BIC>
	$2<range_of::$<current_provider_name::%(lastnames)s::>$,$<praxis::%(praxis)s::>$::70>2$			# (70) <Name of beneficiary> "Empfänger" - Praxis
	$<praxis_id::IBAN//Bank//%(value)s::34>$				# (34) <IBAN>
	EUR$<bill::%(total_amount_with_vat)s::12>$				# (12) <Amount in EURO> "EUR12.5"
															# (4) <purpose of transfer> - leer
															# (35) <remittance info - struct> - only this XOR the next field - GNUmed: leer
	$2<range_of::InvID=$<bill::%(invoice_id)s::>$/Date=$<today::%d.%B %Y::>$::140$>2$	# (140) <remittance info - text> "Client:Marie Louise La Lune" - "Rg Nr, date"
	<beneficiary-to-payor info>								# (70)	"pay soon :-)" - optional - GNUmed nur wenn bytes verfügbar
	--------------------------------
	total: 331 bytes (not chars ! - cave UTF8)
	EOL: LF or CRLF
	last *used* element not followed by anything, IOW can omit pending non-used elements
	"""
	assert IBAN, '<IBAN> must be given'
	assert beneficiary, '<beneficiary> must be given'
	assert amount, '<amount> must be given'
	assert invoice_id, '<invoice_id> must be given'

	data = {}
	data['IBAN'] = IBAN[:34]
	data['beneficiary'] = beneficiary[:70]
	if not BIC:
		BIC = ''
	data['BIC'] = BIC[:11]
	data['amount'] = str(amount)[:9]
	data['ref'] = invoice_id[:140]
	if not comment:
		comment = gmDateTime.pydt_now_here().strftime('%Y %b %d')
	data['cmt'] = comment[:70]
	data_str = 'BCD\n002\n1\nSCT\n%(BIC)s\n%(beneficiary)s\n%(IBAN)s\nEUR%(amount)s\n\n\n%(ref)s\n%(cmt)s' % data
	data_str_bytes = bytes(data_str, 'utf8')[:331]
	return str(data_str_bytes, 'utf8')

#------------------------------------------------------------
def get_scan2pay_data(branch, bill, provider=None, comment=None):
	"""Format data from bill, branch, and provider for scan2pay QR code generation."""
	assert (branch is not None), '<branch> must not be <None>'
	assert (bill is not None), '<bill> must not be <None>'

	IBANs = branch.get_external_ids(id_type = 'IBAN', issuer = 'Bank')
	if len(IBANs) == 0:
		_log.debug('no IBAN found, cannot create scan2pay data')
		return None

	IBAN = IBANs[0]['value']
	beneficiary = gmTools.coalesce (
		value2test = provider,
		return_instead = branch['praxis'][:70],
		template4value = '%%(lastnames)s, %s' % branch['praxis']
	)
	BICs = branch.get_external_ids(id_type = 'BIC', issuer = 'Bank')
	if BICs:
		BIC = BICs[0]['value']
	else:
		BIC = ''
	amount = bill['total_amount_with_vat']
	invoice_id = (_('Inv: %s, %s') % (
		bill['invoice_id'],
		gmDateTime.pydt_now_here().strftime('%d.%B %Y')
	))
	return generate_scan2pay_string (
		IBAN = IBAN,
		beneficiary = beneficiary,
		BIC = BIC,
		amount = amount,
		invoice_id = invoice_id,
		comment = comment
	)

#------------------------------------------------------------
def __get_scan2pay_data(branch, bill, provider=None, comment=None):
	"""Create scan2pay data for generating a QR code.

	https://www.scan2pay.info
	--------------------------------
	BCD														# (3) fixed, barcode tag
	002														# (3) fixed, version
	1														# (1) charset, 1 = utf8
	SCT														# (3) fixed
	$<praxis_id::BIC//Bank//%(value)s::11>$					# (11) <BIC>
	$2<range_of::$<current_provider_name::%(lastnames)s::>$,$<praxis::%(praxis)s::>$::70>2$			# (70) <Name of beneficiary> "Empfänger" - Praxis
	$<praxis_id::IBAN//Bank//%(value)s::34>$				# (34) <IBAN>
	EUR$<bill::%(total_amount_with_vat)s::12>$				# (12) <Amount in EURO> "EUR12.5"
															# (4) <purpose of transfer> - leer
															# (35) <remittance info - struct> - only this XOR the next field - GNUmed: leer
	$2<range_of::InvID=$<bill::%(invoice_id)s::>$/Date=$<today::%d.%B %Y::>$::140$>2$	# (140) <remittance info - text> "Client:Marie Louise La Lune" - "Rg Nr, date"
	<beneficiary-to-payor info>								# (70)	"pay soon :-)" - optional - GNUmed nur wenn bytes verfügbar
	--------------------------------
	total: 331 bytes (not chars ! - cave UTF8)
	EOL: LF or CRLF
	last *used* element not followed by anything, IOW can omit pending non-used elements
	"""
	assert (branch is not None), '<branch> must not be <None>'
	assert (bill is not None), '<bill> must not be <None>'

	data = {}
	IBANs = branch.get_external_ids(id_type = 'IBAN', issuer = 'Bank')
	if len(IBANs) == 0:
		_log.debug('no IBAN found, cannot create scan2pay data')
		return None
	data['IBAN'] = IBANs[0]['value'][:34]
	data['beneficiary'] = gmTools.coalesce (
		value2test = provider,
		return_instead = branch['praxis'][:70],
		template4value = '%%(lastnames)s, %s' % branch['praxis']
	)[:70]
	BICs = branch.get_external_ids(id_type = 'BIC', issuer = 'Bank')
	if len(BICs) == 0:
		data['BIC'] = ''
	else:
		data['BIC'] = BICs[0]['value'][:11]
	data['amount'] = bill['total_amount_with_vat'][:9]
	data['ref'] = (_('Inv: %s, %s') % (
		bill['invoice_id'],
		gmDateTime.pydt_now_here().strftime('%d.%B %Y')
	))[:140]
	data['cmt'] = gmTools.coalesce(comment, '', '\n%s')[:70]

	data_str = 'BCD\n002\n1\nSCT\n%(BIC)s\n%(beneficiary)s\n%(IBAN)s\nEUR%(amount)s\n\n\n%(ref)s%(cmt)s' % data
	data_str_bytes = bytes(data_str, 'utf8')[:331]
	return str(data_str_bytes, 'utf8')

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
	from Gnumed.business import gmPraxis

#	gmI18N.activate_locale()
	gmDateTime.init()

	#--------------------------------------------------
	def test_default_address():
		bills = get_bills(pk_patient = 12)
		first_bill = bills[0]
		print(first_bill.default_address)

	#--------------------------------------------------
	def test_me():
		print("--------------")
		me = cBillable(aPK_obj=1)
		fields = me.get_fields()
		for field in fields:
			print(field, ':', me[field])
		print("updatable:", me.get_updatable_fields())
		#me['vat']=4; me.store_payload()

	#--------------------------------------------------
	def test_get_scan2pay_data():
		prax = gmPraxis.get_praxis_branches()[0]
		bills = get_bills(pk_patient = 12)
		print(get_scan2pay_data (
			prax,
			bills[0],
			provider=None,
			comment = 'GNUmed test harness' + ('x' * 400)
		))

	#--------------------------------------------------
	def test_generate_invoice_id():
		from Gnumed.pycommon import gmI18N
		gmI18N.activate_locale()
		gmI18N.install_domain()
		from Gnumed.business import gmPerson
		for idx in range(1,15):
			print ('')
			print ('classic:', generate_invoice_id(pk_patient = idx))
			pat = gmPerson.cPerson(idx)
			template = u'%(firstname).4s%(lastname).4s%(date)s'
			print ('new: template = "%s" => %s' % (
				template,
				generate_invoice_id (
					template = template,
					pk_patient = None,
					person = pat,
					date_format='%d%m%Y',
					time_format='%H%M%S'
				)
			))
			template = u'%(firstname).4s%(lastname).4s%(date)s-#counter#'
			new_id = generate_invoice_id (
				template = template,
				pk_patient = None,
				person = pat,
				date_format='%d%m%Y',
				time_format='%H%M%S'
			)
			print('locked: %s' % lock_invoice_id(new_id))
			print ('new: template = "%s" => %s' % (template, new_id))
			print('unlocked: %s' % unlock_invoice_id(new_id))

		#generate_invoice_id(template=None, pk_patient=None, person=None, date_format='%Y-%m-%d', time_format='%H%M%S')

	#--------------------------------------------------
	def test_generate_scan2pay_string():
		print(generate_scan2pay_string (
			IBAN = 'DE014032403423',
			beneficiary = 'GNUmed developers',
			BIC = 'NDOLSD99X',
			amount = '1.99',
			invoice_id = 'GM-01-1234-x034'
			, comment = 'test'
		))

	#--------------------------------------------------
	def test_generate_scan2pay_qrcode():
		scan2pay = generate_scan2pay_string (
			IBAN = 'DE014032403423',
			beneficiary = 'GNUmed developers',
			BIC = 'NDOLSD99X',
			amount = '1.99',
			invoice_id = 'GM-01-1234-x034'
			#, comment = 'test'
		)
		print(scan2pay)
		print(generate_scan2pay_qrcode(data = scan2pay))

	#--------------------------------------------------

	#test_generate_scan2pay_string()
	test_generate_scan2pay_qrcode()
	sys.exit()

	gmPG2.request_login_params(setup_pool = True)

	#test_me()
	#test_default_address()
	#test_get_scan2pay_data()
	#test_generate_invoice_id()
