# -*- coding: utf8 -*-
"""GNUmed Praxis related middleware."""
#============================================================
__license__ = "GPL"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"


import sys
import logging
import urllib.parse


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmBorg
from Gnumed.pycommon import gmCfgINI
from Gnumed.pycommon import gmHooks
from Gnumed.pycommon import gmBusinessDBObject

from Gnumed.business import gmOrganization


_log = logging.getLogger('gm.praxis')
_cfg = gmCfgINI.gmCfgData()

#============================================================
def delete_workplace(workplace=None, delete_config=False, conn=None):

	args = {'wp': workplace}

	# delete workplace itself (plugin load list, that is)
	queries = [
		{'sql': """
delete from cfg.cfg_item
where
	fk_template = (
		select pk
		from cfg.cfg_template
		where name = 'horstspace.notebook.plugin_load_order'
	)
		and
	workplace = %(wp)s""",
		'args': args
		}
	]

	# delete other config items associated with this workplace
	if delete_config:
		queries.append ({
			'sql': """
delete from cfg.cfg_item
where
	workplace = %(wp)s""",
			'args': args
		})

	gmPG2.run_rw_queries(link_obj = conn, queries = queries, end_tx = True)

#============================================================
# short description
#------------------------------------------------------------
_SQL_get_praxis_branches = "SELECT * FROM dem.v_praxis_branches WHERE %s"

class cPraxisBranch(gmBusinessDBObject.cBusinessDBObject):
	"""Represents a praxis branch"""

	_cmd_fetch_payload = _SQL_get_praxis_branches % "pk_praxis_branch = %s"
	_cmds_store_payload = [
		"""UPDATE dem.praxis_branch SET
				fk_org_unit = %(pk_org_unit)s
			WHERE
				pk = %(pk_praxis_branch)s
					AND
				xmin = %(xmin_praxis_branch)s
			RETURNING
				xmin as xmin_praxis_branch
		"""
	]
	_updatable_fields = [
		'pk_org_unit'
	]
	#--------------------------------------------------------
	def format(self, one_line=False):
		if one_line:
			unit = self.org_unit
			return '%s@%s' % (unit['unit'], unit['organization'])

		txt = _('Praxis branch                   #%s\n') % self._payload['pk_praxis_branch']
		txt += ' '
		txt += '\n '.join(self.org_unit.format(with_address = True, with_org = True, with_comms = True))
		return txt

	#--------------------------------------------------------
	def format_for_failsafe_output(self, max_width:int=80) -> list[str]:
		lines = []
		lines.append(_('%s of %s') % (self['branch'], self['praxis']))
		adr = self.address
		if adr:
			lines.extend(adr.format_for_failsafe_output(max_width = max_width))
		for ch in self.get_comm_channels():
			if ch['is_confidential']:
				continue
			lines.append('%s: %s' % (ch['l10n_comm_type'], ch['url']))
		return lines

	#--------------------------------------------------------
	def lock(self, exclusive=False):
		return lock_praxis_branch(pk_praxis_branch = self._payload['pk_praxis_branch'], exclusive = exclusive)

	#--------------------------------------------------------
	def unlock(self, exclusive=False):
		return unlock_praxis_branch(pk_praxis_branch = self._payload['pk_praxis_branch'], exclusive = exclusive)

	#--------------------------------------------------------
	def get_comm_channels(self, comm_medium=None):
		return self.org_unit.get_comm_channels(comm_medium = comm_medium)

	#--------------------------------------------------------
	def get_external_ids(self, id_type=None, issuer=None):
		return self.org_unit.get_external_ids(id_type = id_type, issuer = issuer)

	#--------------------------------------------------------
	def get_distance2address_url(self, address):
		self_adr = self.address
		url = 'https://www.luftlinie.org/%s-%s-%s-%s-%s/%s-%s-%s-%s-%s' % (
			urllib.parse.quote(self_adr['street'].encode('utf8')),
			urllib.parse.quote(self_adr['number'].encode('utf8')),
			urllib.parse.quote(self_adr['urb'].encode('utf8')),
			urllib.parse.quote(self_adr['postcode'].encode('utf8')),
			urllib.parse.quote(self_adr['country'].encode('utf8')),
			urllib.parse.quote(address['street'].encode('utf8')),
			urllib.parse.quote(address['number'].encode('utf8')),
			urllib.parse.quote(address['urb'].encode('utf8')),
			urllib.parse.quote(address['postcode'].encode('utf8')),
			urllib.parse.quote(address['country'].encode('utf8'))
		)
		return url

	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_org_unit(self):
		return gmOrganization.cOrgUnit(aPK_obj = self._payload['pk_org_unit'])

	org_unit = property(_get_org_unit)

	#--------------------------------------------------------
	def _get_org(self):
		return gmOrganization.cOrg(aPK_obj = self._payload['pk_org'])

	organization = property(_get_org)

	#--------------------------------------------------------
	def _get_address(self):
		return self.org_unit.address

	address = property(_get_address)

#	def _set_address(self, address):
#		self['pk_address'] = address['pk_address']
#		self.save()
#	address = property(_get_address, _set_address)

	#--------------------------------------------------------
	def _get_vcf(self):
		vcf_fields = [
			'BEGIN:VCARD',
			'VERSION:4.0',
			'KIND:org',
			'ORG:%(l10n_organization_category)s %(praxis)s;%(l10n_unit_category)s %(branch)s' % self,
			_('FN:%(l10n_unit_category)s %(branch)s of %(l10n_organization_category)s %(praxis)s') % self,
			'N:%(praxis)s;%(branch)s' % self
		]
		adr = self.address
		if adr is not None:
			vcf_fields.append('ADR:;%(subunit)s;%(street)s %(number)s;%(urb)s;%(l10n_region)s;%(postcode)s;%(l10n_country)s' % adr)
		comms = self.get_comm_channels(comm_medium = 'workphone')
		if len(comms) > 0:
			vcf_fields.append('TEL;VALUE=uri;TYPE=work:tel:%(url)s' % comms[0])
		comms = self.get_comm_channels(comm_medium = 'email')
		if len(comms) > 0:
			vcf_fields.append('EMAIL:%(url)s' % comms[0])
		if adr is not None:
			vcf_fields.append('URL:%s' % adr.as_map_url)
		vcf_fields.append('END:VCARD')
		vcf_fname = gmTools.get_unique_filename (
			prefix = 'gm-praxis-',
			suffix = '.vcf'
		)
		vcf_file = open(vcf_fname, mode = 'wt', encoding = 'utf8')
		vcf_file.write('\n'.join(vcf_fields))
		vcf_file.write('\n')
		vcf_file.close()
		return vcf_fname

	vcf = property(_get_vcf)

	#--------------------------------------------------------
	def export_as_mecard(self, filename=None):
		if filename is None:
			filename = gmTools.get_unique_filename (
				prefix = 'gm-praxis-',
				suffix = '.mcf'
			)
		with open(filename, mode = 'wt', encoding = 'utf8') as mecard_file:
			mecard_file.write(self.MECARD)
		return filename

	#--------------------------------------------------------
	def _get_mecard(self):
		"""
		http://blog.thenetimpact.com/2011/07/decoding-qr-codes-how-to-format-data-for-qr-code-generators/
		https://www.nttdocomo.co.jp/english/service/developer/make/content/barcode/function/application/addressbook/index.html

		MECARD:N:NAME;ADR:pobox,subunit,unit,street,ort,region,zip,country;TEL:111111111;FAX:22222222;EMAIL:mail@praxis.org;

		MECARD:N:$<praxis::%(praxis)s, %(branch)s::>$;ADR:$<praxis_address::,%(subunit)s,%(number)s,%(street)s,%(urb)s,,%(postcode)s,%(l10n_country)s::>$;TEL:$<praxis_comm::workphone::>$;FAX:$<praxis_comm::fax::>$;EMAIL:$<praxis_comm::email::60>$;
		"""
		MECARD = 'MECARD:N:%(praxis)s,%(branch)s;' % self
		adr = self.address
		if adr is not None:
			MECARD += 'ADR:,%(subunit)s,%(number)s,%(street)s,%(urb)s,,%(postcode)s,%(l10n_country)s;' % adr
		comms = self.get_comm_channels(comm_medium = 'workphone')
		if len(comms) > 0:
			MECARD += 'TEL:%(url)s;' % comms[0]
		comms = self.get_comm_channels(comm_medium = 'fax')
		if len(comms) > 0:
			MECARD += 'FAX:%(url)s;' % comms[0]
		comms = self.get_comm_channels(comm_medium = 'email')
		if len(comms) > 0:
			MECARD += 'EMAIL:%(url)s;' % comms[0]
		if adr is not None:
			MECARD += 'URL:%s;' % adr.as_map_url
		MECARD += ';'
		return MECARD

	MECARD = property(_get_mecard)

	#--------------------------------------------------------
	def _get_scan2pay_data(self):
		IBANs = self.get_external_ids(id_type = 'IBAN', issuer = 'Bank')
		if len(IBANs) == 0:
			_log.debug('no IBAN found, cannot create scan2pay data')
			return None
		data = {
			'IBAN': IBANs[0]['value'][:34],
			'beneficiary': self['praxis'][:70]
		}
		BICs = self.get_external_ids(id_type = 'BIC', issuer = 'Bank')
		if len(BICs) == 0:
			data['BIC'] = ''
		else:
			data['BIC'] = BICs[0]['value'][:11]
		return 'BCD\n002\n1\nSCT\n%(BIC)s\n%(beneficiary)s\n%(IBAN)s' % data

	scan2pay_data = property(_get_scan2pay_data)

#------------------------------------------------------------
def lock_praxis_branch(pk_praxis_branch=None, exclusive=False):
	return gmPG2.lock_row(table = 'dem.praxis_branch', pk = pk_praxis_branch, exclusive = exclusive)

#------------------------------------------------------------
def unlock_praxis_branch(pk_praxis_branch=None, exclusive=False):
	unlocked = gmPG2.unlock_row(table = 'dem.praxis_branch', pk = pk_praxis_branch, exclusive = exclusive)
	if not unlocked:
		_log.warning('cannot unlock praxis branch [#%s]', pk_praxis_branch)
	return unlocked

#------------------------------------------------------------
def get_praxis_branches(order_by=None, return_pks=False):
	if order_by is None:
		order_by = 'true'
	else:
		order_by = 'true ORDER BY %s' % order_by

	cmd = _SQL_get_praxis_branches % order_by
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd}])
	if return_pks:
		return [ r['pk_praxis_branch'] for r in rows ]
	return [ cPraxisBranch(row = {'data': r, 'pk_field': 'pk_praxis_branch'}) for r in rows ]

#------------------------------------------------------------
def get_praxis_branch_by_org_unit(pk_org_unit=None):
	cmd = _SQL_get_praxis_branches % 'pk_org_unit = %(pk_ou)s'
	args = {'pk_ou': pk_org_unit}
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	if len(rows) == 0:
		return None
	return cPraxisBranch(row = {'data': rows[0], 'pk_field': 'pk_praxis_branch'})

#------------------------------------------------------------
def create_praxis_branch(pk_org_unit=None):

	args = {'fk_unit': pk_org_unit}
	cmd1 = """
		INSERT INTO dem.praxis_branch (fk_org_unit)
		SELECT %(fk_unit)s WHERE NOT EXISTS (
			SELECT 1 FROM dem.praxis_branch WHERE fk_org_unit = %(fk_unit)s
		)
	"""
	cmd2 = """SELECT * from dem.v_praxis_branches WHERE pk_org_unit = %(fk_unit)s"""
	queries = [
		{'sql': cmd1, 'args': args},
		{'sql': cmd2, 'args': args}
	]
	rows = gmPG2.run_rw_queries(queries = queries, return_data = True)
	return cPraxisBranch(row = {'data': rows[0], 'pk_field': 'pk_praxis_branch'})

#------------------------------------------------------------
def create_praxis_branches(pk_org_units=None):
	queries = []
	for pk in pk_org_units:
		args = {'fk_unit': pk}
		cmd = """
			INSERT INTO dem.praxis_branch (fk_org_unit)
			SELECT %(fk_unit)s WHERE NOT EXISTS (
				SELECT 1 FROM dem.praxis_branch WHERE fk_org_unit = %(fk_unit)s
			)
		"""
		queries.append({'sql': cmd, 'args': args})

	args = {'fk_units': pk_org_units}
	cmd = """SELECT * from dem.v_praxis_branches WHERE pk_org_unit = ANY(%(fk_units)s)"""
	queries.append({'sql': cmd, 'args': args})
	rows = gmPG2.run_rw_queries(queries = queries, return_data = True)
	return [ cPraxisBranch(row = {'data': r, 'pk_field': 'pk_praxis_branch'}) for r in rows ]

#------------------------------------------------------------
def delete_praxis_branch(pk_praxis_branch=None):
	if not lock_praxis_branch(pk_praxis_branch = pk_praxis_branch, exclusive = True):
		return False
	args = {'pk': pk_praxis_branch}
	cmd = "DELETE FROM dem.praxis_branch WHERE pk = %(pk)s"
	gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])
	unlock_praxis_branch(pk_praxis_branch = pk_praxis_branch, exclusive = True)
	return True

#------------------------------------------------------------
def delete_praxis_branches(pk_praxis_branches=None, except_pk_praxis_branches=None):
	if pk_praxis_branches is None:
		cmd = 'SELECT pk from dem.praxis_branch'
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd}])
		pks_to_lock = [ r[0] for r in rows ]
	else:
		pks_to_lock = pk_praxis_branches[:]
	if except_pk_praxis_branches is not None:
		for pk in except_pk_praxis_branches:
			try: pks_to_lock.remove(pk)
			except ValueError: pass

	for pk in pks_to_lock:
		if not lock_praxis_branch(pk_praxis_branch = pk, exclusive = True):
			return False

	args = {}
	where_parts = []
	if pk_praxis_branches is not None:
		args['pks'] = pk_praxis_branches
		where_parts.append('pk = ANY(%(pks)s)')
	if except_pk_praxis_branches is not None:
		args['except'] = except_pk_praxis_branches
		where_parts.append('pk <> ALL(%(except)s)')
	if len(where_parts) == 0:
		cmd = "DELETE FROM dem.praxis_branch"
	else:
		cmd = "DELETE FROM dem.praxis_branch WHERE %s" % ' AND '.join(where_parts)
	gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])
	for pk in pks_to_lock:
		unlock_praxis_branch(pk_praxis_branch = pk, exclusive = True)
	return True

#============================================================
class gmCurrentPraxisBranch(gmBorg.cBorg):

	#--------------------------------------------------------
	def __init__(self, branch=None):
		try:
			self.has_been_initialized
		except AttributeError:
			self.branch = None
			self.has_been_initialized = True
			self.__helpdesk = None
			self.__active_workplace = None

		# user wants copy of current branch
		if branch is None:
			return None

		# must be cPraxisBranch instance, then
		if not isinstance(branch, cPraxisBranch):
			_log.error('cannot set current praxis branch to [%s], must be a cPraxisBranch instance' % str(branch))
			raise TypeError('gmPraxis.gmCurrentPraxisBranch.__init__(): <branch> must be a cPraxisBranch instance but is: %s' % str(branch))

		if self.branch is not None:
			self.branch.unlock()

		branch.lock()
		self.branch = branch
		_log.debug('current praxis branch now: %s', self.branch)

		return None

	#--------------------------------------------------------
	@classmethod
	def from_first_branch(cls) -> 'gmCurrentPraxisBranch':
		"""Initialize from 'first' branch of praxis."""
		_log.debug('activating first praxis branch as current branch')
		branches = get_praxis_branches()
		if branches:
			return cls(branch = branches[0])

		raise ValueError('no praxis branches found')

	#--------------------------------------------------------
	# __getattr__ handling
	#--------------------------------------------------------
	def __getattr__(self, attribute):
		if attribute == 'has_been_initialized':
			raise AttributeError
		if attribute in ['branch', 'waiting_list_patients', 'help_desk', 'db_logon_banner', 'active_workplace', 'workplaces', 'user_email']:
			return getattr(self, attribute)
		return getattr(self.branch, attribute)

	#--------------------------------------------------------
	# __get/setitem__ handling
	#--------------------------------------------------------
	def __getitem__(self, attribute = None):
		"""Return any attribute if known how to retrieve it by proxy."""
		return self.branch[attribute]

	#--------------------------------------------------------
	def __setitem__(self, attribute, value):
		self.branch[attribute] = value

	#--------------------------------------------------------
	# waiting list handling
	#--------------------------------------------------------
	def remove_from_waiting_list(self, pk=None):
		cmd = 'DELETE FROM clin.waiting_list WHERE pk = %(pk)s'
		args = {'pk': pk}
		gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])
		gmHooks.run_hook_script(hook = 'after_waiting_list_modified')

	#--------------------------------------------------------
	def update_in_waiting_list(self, pk = None, urgency = 0, comment = None, zone = None):
		cmd = """
update clin.waiting_list
set
	urgency = %(urg)s,
	comment = %(cmt)s,
	area = %(zone)s
where
	pk = %(pk)s"""
		args = {
			'pk': pk,
			'urg': urgency,
			'cmt': gmTools.none_if(comment, ''),
			'zone': gmTools.none_if(zone, '')
		}

		gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])
		gmHooks.run_hook_script(hook = 'after_waiting_list_modified')

	#--------------------------------------------------------
	def raise_in_waiting_list(self, current_position=None):
		if current_position == 1:
			return

		cmd = 'select clin.move_waiting_list_entry(%(pos)s, (%(pos)s - 1))'
		args = {'pos': current_position}

		gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])

	#--------------------------------------------------------
	def lower_in_waiting_list(self, current_position=None):
		cmd = 'select clin.move_waiting_list_entry(%(pos)s, (%(pos)s+1))'
		args = {'pos': current_position}

		gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])

	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_waiting_list_patients(self):
		cmd = """
			SELECT * FROM clin.v_waiting_list
			ORDER BY
				list_position
		"""
		rows = gmPG2.run_ro_queries (
			queries = [{'sql': cmd}]
		)
		return rows

	waiting_list_patients = property (_get_waiting_list_patients)

	#--------------------------------------------------------
	def _set_helpdesk(self, helpdesk):
		return

	def _get_helpdesk(self):

		if self.__helpdesk is not None:
			return self.__helpdesk

		self.__helpdesk = gmTools.coalesce (
			_cfg.get (
				group = 'workplace',
				option = 'help desk',
				source_order = [
					('explicit', 'return'),
					('workbase', 'return'),
					('local', 'return'),
					('user', 'return'),
					('system', 'return')
				]
			),
			'https://www.gnumed.de/documentation/'
		)

		return self.__helpdesk

	helpdesk = property(_get_helpdesk, _set_helpdesk)

	#--------------------------------------------------------
	def _get_db_logon_banner(self):
		rows = gmPG2.run_ro_queries(queries = [{'sql': 'select _(message) from cfg.db_logon_banner'}])
		if len(rows) == 0:
			return ''
		return gmTools.coalesce(rows[0][0], '').strip()

	def _set_db_logon_banner(self, banner):
		queries = [
			{'sql': 'delete from cfg.db_logon_banner'}
		]
		if banner.strip() != '':
			queries.append ({
				'sql': 'insert into cfg.db_logon_banner (message) values (%(msg)s)',
				'args': {'msg': banner.strip()}
			})
		gmPG2.run_rw_queries(queries = queries, end_tx = True)

	db_logon_banner = property(_get_db_logon_banner, _set_db_logon_banner)

	#--------------------------------------------------------
	def _set_workplace(self, workplace):
		# maybe later allow switching workplaces on the fly
		return True

	def _get_workplace(self):
		"""Return the current workplace (client profile) definition.

		The first occurrence counts.
		"""
		if self.__active_workplace is not None:
			return self.__active_workplace

		self.__active_workplace = gmTools.coalesce (
			_cfg.get (
				group = 'workplace',
				option = 'name',
				source_order = [
					('explicit', 'return'),
					('workbase', 'return'),
					('local', 'return'),
					('user', 'return'),
					('system', 'return'),
				]
			),
			'Local Default'
		)

		return self.__active_workplace

	active_workplace = property(_get_workplace, _set_workplace)

	#--------------------------------------------------------
	def _set_workplaces(self, val):
		pass

	def _get_workplaces(self):
		cmd = 'SELECT DISTINCT workplace FROM cfg.cfg_item WHERE workplace IS NOT NULL ORDER BY workplace'
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd}])
		return [ r['workplace'] for r in rows ]

	workplaces = property(_get_workplaces, _set_workplaces)

	#--------------------------------------------------------
	def _get_user_email(self):
		# FIXME: get this from the current users staff record in the database
		return _cfg.get (
			group = 'preferences',
			option = 'user email',
			source_order = [
				('explicit', 'return'),
				('user', 'return'),
				('local', 'return'),
				('workbase', 'return'),
				('system', 'return')
			]
		)

	def _set_user_email(self, val):
		prefs_file = _cfg.get(option = 'user_preferences_file')
		gmCfgINI.set_option_in_INI_file (
			filename = prefs_file,
			group = 'preferences',
			option = 'user email',
			value = val
		)
		_cfg.reload_file_source(filename = prefs_file)

	user_email = property(_get_user_email, _set_user_email)

#============================================================
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.pycommon import gmI18N
	gmI18N.install_domain()

	def run_tests():
		prac = gmCurrentPraxisBranch()
#		print "help desk:", prac.helpdesk
#		print "active workplace:", prac.active_workplace

		old_banner = prac.db_logon_banner
		test_banner = 'a test banner'
		prac.db_logon_banner = test_banner
		if prac.db_logon_banner != test_banner:
			print(('Cannot set logon banner to', test_banner))
			return False
		prac.db_logon_banner = ''
		if prac.db_logon_banner != '':
			print('Cannot set logon banner to ""')
			return False
		prac.db_logon_banner = old_banner

		return True

#	if not run_tests():
#		print "regression tests failed"
#	print "regression tests succeeded"

	gmPG2.request_login_params(setup_pool = True)

	for b in get_praxis_branches():
		print((b.format()))
		#print(b.vcf)
#		print(b.scan2pay_data)

	#--------------------------------------------------------
	def test_mecard():
		for b in get_praxis_branches():
			print(gmTools.create_qrcode(text = b.MECARD, qr_filename = None, verbose = True))
			print(b.MECARD)
			mcf = b.export_as_mecard()
			print(mcf)
			print(gmTools.create_qrcode(filename = mcf, qr_filename = None, verbose = True))
			input()

	#--------------------------------------------------------
	def test_from_first_branch():
		print(gmCurrentPraxisBranch.from_first_branch())

	#--------------------------------------------------------
	#test_mecard()
	test_from_first_branch()
