# -*- coding: utf8 -*-
"""Medication handling code.

license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmMedication.py,v $
# $Id: gmMedication.py,v 1.15 2009-11-29 19:59:31 ncq Exp $
__version__ = "$Revision: 1.15 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

import sys, logging, csv, codecs, os, re as regex


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmBusinessDBObject, gmPG2, gmShellAPI, gmTools, gmDateTime
from Gnumed.business import gmATC


_log = logging.getLogger('gm.meds')
_log.info(__version__)

#============================================================
# wishlist:
# - --conf-file= for glwin.exe
# - wirkstoff: Konzentration auch in Multiprodukten
# - wirkstoff: ATC auch in Multiprodukten
# - Suche nach ATC per CLI

class cGelbeListeCSVFile(object):
	"""Iterator over a Gelbe Liste/MMI v8.2 CSV file."""

	version = u'Gelbe Liste/MMI v8.2 CSV file interface'
	default_transfer_file_windows = r"c:\rezept.txt"
	#default_encoding = 'cp1252'
	default_encoding = 'cp1250'
	csv_fieldnames = [
		u'name',
		u'packungsgroesse',					# obsolete, use "packungsmenge"
		u'darreichungsform',
		u'packungstyp',
		u'festbetrag',
		u'avp',
		u'hersteller',
		u'rezepttext',
		u'pzn',
		u'status_vertrieb',
		u'status_rezeptpflicht',
		u'status_fachinfo',
		u'btm',
		u'atc',
		u'anzahl_packungen',
		u'zuzahlung_pro_packung',
		u'einheit',
		u'schedule_morgens',
		u'schedule_mittags',
		u'schedule_abends',
		u'schedule_nachts',
		u'status_dauermedikament',
		u'status_hausliste',
		u'status_negativliste',
		u'ik_nummer',
		u'status_rabattvertrag',
		u'wirkstoffe',
		u'wirkstoffmenge',
		u'wirkstoffeinheit',
		u'wirkstoffmenge_bezug',
		u'wirkstoffmenge_bezugseinheit',
		u'status_import',
		u'status_lifestyle',
		u'status_ausnahmeliste',
		u'packungsmenge',
		u'apothekenpflicht',
		u'status_billigere_packung',
		u'rezepttyp',
		u'besonderes_arzneimittel',			# Abstimmungsverfahren SGB-V
		u't-rezept-pflicht',				# Thalidomid-Rezept
		u'erstattbares_medizinprodukt',
		u'hilfsmittel'
	]
	boolean_fields = [
		u'status_rezeptpflicht',
		u'status_fachinfo',
		u'btm',
		u'status_dauermedikament',
		u'status_hausliste',
		u'status_negativliste',
		u'status_rabattvertrag',
		u'status_import',
		u'status_lifestyle',
		u'status_ausnahmeliste',
		u'apothekenpflicht',
		u'status_billigere_packung',
		u'besonderes_arzneimittel',			# Abstimmungsverfahren SGB-V
		u't-rezept-pflicht',
		u'erstattbares_medizinprodukt',
		u'hilfsmittel'
	]
	#--------------------------------------------------------
	def __init__(self, filename=None):

		_log.info(cGelbeListeCSVFile.version)

		self.filename = filename
		if filename is None:
			self.filename = cGelbeListeCSVFile.default_transfer_file_windows

		_log.debug('reading Gelbe Liste/MMI drug data from [%s]', self.filename)

		self.csv_file = codecs.open(filename = filename, mode = 'rUb', encoding = cGelbeListeCSVFile.default_encoding)

		self.csv_lines = gmTools.unicode_csv_reader (
			self.csv_file,
			fieldnames = cGelbeListeCSVFile.csv_fieldnames,
			delimiter = ';',
			quotechar = '"',
			dict = True
		)
	#--------------------------------------------------------
	def __iter__(self):
		return self
	#--------------------------------------------------------
	def next(self):
		line = self.csv_lines.next()

		for field in cGelbeListeCSVFile.boolean_fields:
			line[field] = (line[field].strip() == u'T')

		# split field "Wirkstoff" by ";"
		line['wirkstoffe'] = [ wirkstoff.strip() for wirkstoff in line['wirkstoffe'].split(u';') ]

		return line
	#--------------------------------------------------------
	def close(self, truncate=True):
		try: self.csv_file.close()
		except: pass

		if truncate:
			try: os.open(self.filename, 'wb').close
			except: pass
#============================================================
class cDrugDataSourceInterface(object):

	#--------------------------------------------------------
	def get_data_source_version(self):
		raise NotImplementedError
	#--------------------------------------------------------
	def create_data_source_entry(self):
		raise NotImplementedError
	#--------------------------------------------------------
	def switch_to_frontend(self):
		raise NotImplementedError
	#--------------------------------------------------------
	def select_drugs(self):
		raise NotImplementedError
	#--------------------------------------------------------
	def import_drugs(self):
		raise NotImplementedError
	#--------------------------------------------------------
	def check_drug_interactions(self):
		raise NotImplementedError
#============================================================
class cGelbeListeWindowsInterface(cDrugDataSourceInterface):
	"""Support v8.2 CSV file interface only."""

	version = u'Gelbe Liste/MMI v8.2 interface'
	default_encoding = 'cp1250'
	bdt_line_template = u'%03d6210#%s\r\n'		# Medikament verordnet auf Kassenrezept
	bdt_line_base_length = 8
	#--------------------------------------------------------
	def __init__(self):
		_log.info(u'%s (native Windows)', cGelbeListeWindowsInterface.version)

		self.path_to_binary = r'C:\Programme\MMI PHARMINDEX\glwin.exe'
		self.args = r'-KEEPBACKGROUND -PRESCRIPTIONFILE %s -CLOSETOTRAY'

		paths = gmTools.gmPaths()

		self.default_csv_filename = os.path.join(paths.home_dir, '.gnumed', 'tmp', 'rezept.txt')
		self.default_csv_filename_arg = os.path.join(paths.home_dir, '.gnumed', 'tmp')
		self.interactions_filename = os.path.join(paths.home_dir, '.gnumed', 'tmp', 'gm2mmi.bdt')
		self.data_date_filename = r'C:\Programme\MMI PHARMINDEX\datadate.txt'

		self.data_date = None
		self.online_update_date = None

		# use adjusted config.dat
	#--------------------------------------------------------
	def get_data_source_version(self):

		open(self.data_date_filename, 'wb').close()

		cmd = u'%s -DATADATE' % self.path_to_binary
		if not gmShellAPI.run_command_in_shell(command = cmd, blocking = True):
			_log.error('problem querying the MMI drug database for version information')
			return {
				'data': u'?',
				'online_update': u'?'
			}

		version_file = open(self.data_date_filename, 'rU')
		versions = {
			'data': version_file.readline()[:10],
			'online_update': version_file.readline()[:10]
		}
		version_file.close()

		return versions
	#--------------------------------------------------------
	def create_data_source_entry(self):
		versions = self.get_data_source_version()

		args = {
			'lname': u'Medikamentendatenbank "mmi PHARMINDEX" (Gelbe Liste)',
			'sname': u'GL/MMI',
			'ver': u'Daten: %s, Preise (Onlineupdate): %s' % (versions['data'], versions['online_update']),
			'src': u'Medizinische Medien Informations GmbH, Am Forsthaus Gravenbruch 7, 63263 Neu-Isenburg',
			'lang': u'de'
		}

		cmd = u"""select pk from ref.data_source where name_long = %(lname)s and name_short = %(sname)s and version = %(ver)s"""
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])
		if len(rows) > 0:
			return rows[0]['pk']

		cmd = u"""
			INSERT INTO ref.data_source (name_long, name_short, version, source, lang)
			VALUES (
				%(lname)s,
				%(sname)s,
				%(ver)s,
				%(src)s,
				%(lang)s
			)
			returning pk
			"""

		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True)

		return rows[0]['pk']
	#--------------------------------------------------------
	def switch_to_frontend(self, blocking=False):

		# must make sure csv file exists
		open(self.default_csv_filename, 'wb').close()

		cmd = (u'%s %s' % (self.path_to_binary, self.args)) % self.default_csv_filename_arg

		if not gmShellAPI.run_command_in_shell(command = cmd, blocking = blocking):
			_log.error('problem switching to the MMI drug database')
			# apparently on the first call MMI does not
			# consistently return 0 on success
#			return False

		return True
	#--------------------------------------------------------
	def select_drugs(self, filename=None):

		# better to clean up interactions file
		open(self.interactions_filename, 'wb').close()

		if not self.switch_to_frontend(blocking = True):
			return None

		return cGelbeListeCSVFile(filename = self.default_csv_filename)
	#--------------------------------------------------------
	def import_drugs_as_substances(self):

		selected_drugs = self.select_drugs()
		if selected_drugs is None:
			return None

		new_substances = []

		for drug in selected_drugs:
			atc = None							# hopefully MMI eventually supports atc-per-substance in a drug...
			if len(drug['wirkstoffe']) == 1:
				atc = drug['atc']
			for wirkstoff in drug['wirkstoffe']:
				new_substances.append(create_used_substance(substance = wirkstoff, atc = atc))

		selected_drugs.close()

		return new_substances
	#--------------------------------------------------------
	def import_drugs(self):

		selected_drugs = self.select_drugs()
		if selected_drugs is None:
			return None

		data_src_pk = self.create_data_source_entry()

		new_drugs = []
		new_substances = []

		for entry in selected_drugs:

			# create branded drug (or get it if it already exists)
			drug = create_branded_drug(brand_name = entry['name'], preparation = entry['darreichungsform'])
			if drug is None:
				drug = get_drug_by_brand(brand_name = entry['name'], preparation = entry['darreichungsform'])
			new_drugs.append(drug)

			# update fields
			drug['is_fake'] = False
			drug['atc_code'] = entry['atc']
			drug['external_code'] = u'%s::%s' % ('DE-PZN', entry['pzn'])
			drug['fk_data_source'] = data_src_pk
			drug.save()

			# add components to brand
			atc = None							# hopefully MMI eventually supports atc-per-substance in a drug...
			if len(entry['wirkstoffe']) == 1:
				atc = entry['atc']
			for wirkstoff in entry['wirkstoffe']:
				drug.add_component(substance = wirkstoff, atc = atc)

			# create as consumable substances, too
			atc = None							# hopefully MMI eventually supports atc-per-substance in a drug...
			if len(entry['wirkstoffe']) == 1:
				atc = entry['atc']
			for wirkstoff in entry['wirkstoffe']:
				new_substances.append(create_used_substance(substance = wirkstoff, atc = atc))

		return new_drugs, new_substances
	#--------------------------------------------------------
	def check_drug_interactions(self, pzn_list=None, substances=None):
		"""For this to work the BDT interaction check must be configured in the MMI."""

		if pzn_list is None:
			if substances is None:
				return
			if len(substances) < 2:
				return
			pzn_list = [ s.external_code for s in substances ]
			pzn_list = [ pzn for pzn in pzn_list if pzn is not None ]
			pzn_list = [ code_value for code_type, code_value in pzn_list if code_type == u'DE-PZN']

		else:
			if len(pzn_list) < 2:
				return

		if pzn_list < 2:
			return

		bdt_file = codecs.open(filename = self.interactions_filename, mode = 'wb', encoding = cGelbeListeWindowsInterface.default_encoding)

		for pzn in pzn_list:
			pzn = pzn.strip()
			lng = cGelbeListeWindowsInterface.bdt_line_base_length + len(pzn)
			bdt_file.write(cGelbeListeWindowsInterface.bdt_line_template % (lng, pzn))

		bdt_file.close()

		self.switch_to_frontend(blocking = False)
#============================================================
class cGelbeListeWineInterface(cGelbeListeWindowsInterface):

	def __init__(self):
		cGelbeListeWindowsInterface.__init__(self)

		_log.info(u'%s (WINE extension)', cGelbeListeWindowsInterface.version)

		# FIXME: if -CLOSETOTRAY is used GNUmed cannot detect the end of MMI
		self.path_to_binary = r'wine "C:\Programme\MMI PHARMINDEX\glwin.exe"'
		self.args = r'"-PRESCRIPTIONFILE %s -KEEPBACKGROUND"'

		paths = gmTools.gmPaths()

		self.default_csv_filename = os.path.join(paths.home_dir, '.wine', 'drive_c', 'windows', 'temp', 'mmi2gm.csv')
		self.default_csv_filename_arg = r'c:\windows\temp\mmi2gm.csv'
		self.interactions_filename = os.path.join(paths.home_dir, '.wine', 'drive_c', 'windows', 'temp', 'gm2mmi.bdt')
		self.data_date_filename = os.path.join(paths.home_dir, '.wine', 'drive_c', 'Programme', 'MMI PHARMINDEX', 'datadate.txt')
#============================================================
class cIfapInterface(cDrugDataSourceInterface):
	"""empirical CSV interface"""

	def __init__(self):
		pass

	def print_transfer_file(self, filename=None):

		try:
			csv_file = open(filename, 'rb')						# FIXME: encoding ?
		except:
			_log.exception('cannot access [%s]', filename)
			csv_file = None

		field_names = u'PZN Handelsname Form Abpackungsmenge Einheit Preis1 Hersteller Preis2 rezeptpflichtig Festbetrag Packungszahl Packungsgr\xf6\xdfe'.split()

		if csv_file is None:
			return False

		csv_lines = csv.DictReader (
			csv_file,
			fieldnames = field_names,
			delimiter = ';'
		)

		for line in csv_lines:
			print "--------------------------------------------------------------------"[:31]
			for key in field_names:
				tmp = ('%s                                                ' % key)[:30]
				print '%s: %s' % (tmp, line[key])

		csv_file.close()

#				narr = u'%sx %s %s %s (\u2258 %s %s) von %s (%s)' % (
#					line['Packungszahl'].strip(),
#					line['Handelsname'].strip(),
#					line['Form'].strip(),
#					line[u'Packungsgr\xf6\xdfe'].strip(),
#					line['Abpackungsmenge'].strip(),
#					line['Einheit'].strip(),
#					line['Hersteller'].strip(),
#					line['PZN'].strip()
#				)
#============================================================
drug_data_source_interfaces = {
	'Gelbe Liste/MMI (Windows)': cGelbeListeWindowsInterface,
	'Gelbe Liste/MMI (WINE)': cGelbeListeWineInterface
}
#============================================================
# substances in use across all patients
#------------------------------------------------------------
def get_substances_in_use():
	cmd = u'select * from clin.consumed_substance order by description'
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}])
	return rows
#------------------------------------------------------------
def create_used_substance(substance=None, atc=None):

	substance = substance.strip()

	if atc is not None:
		atc = atc.strip()

	args = {'desc': substance, 'atc': atc}

	cmd = u'select pk, atc_code, description from clin.consumed_substance where description = %(desc)s'
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])

	if len(rows) == 0:
		cmd = u'insert into clin.consumed_substance (description, atc_code) values (%(desc)s, gm.nullify_empty_string(%(atc)s)) returning pk, atc_code, description'
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True)

	gmATC.propagate_atc(substance = substance, atc = atc)

	row = rows[0]
	# unfortunately not a real dict so no setting stuff by keyword
	#row['atc_code'] = args['atc']
	row[1] = args['atc']
	return row
#------------------------------------------------------------
def delete_used_substance(substance=None):
	args = {'pk': substance}
	cmd = u"""
delete from clin.consumed_substance
where
	pk = %(pk)s and not exists (
		select 1 from clin.substance_intake
		where fk_substance = %(pk)s
	)"""
	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
#============================================================
class cSubstanceIntakeEntry(gmBusinessDBObject.cBusinessDBObject):
	"""Represents a substance currently taken by a patient."""

	_cmd_fetch_payload = u"select * from clin.v_pat_substance_intake where pk_substance_intake = %s"
	_cmds_store_payload = [
		u"""update clin.substance_intake set
				clin_when = %(started)s,
				strength = gm.nullify_empty_string(%(strength)s),
				preparation = %(preparation)s,
				schedule = gm.nullify_empty_string(%(schedule)s),
				aim = gm.nullify_empty_string(%(aim)s),
				narrative = gm.nullify_empty_string(%(notes)s),
				intake_is_approved_of = %(intake_is_approved_of)s,

				-- is_long_term = %(is_long_term)s,
				is_long_term = (
					case
						when (
							(%(is_long_term)s is False)
								and
							(gm.is_null_or_blank_string(%(duration)s) is True)
						) is True then null
						else %(is_long_term)s
					end
				)::boolean,
				duration = (
					case
						when %(is_long_term)s is True then null
						else gm.nullify_empty_string(%(duration)s)
					end
				)::interval,

				fk_brand = %(pk_brand)s,
				fk_substance = %(pk_substance)s,
				fk_episode = %(pk_episode)s
			where
				pk = %(pk_substance_intake)s and
				xmin = %(xmin_substance_intake)s
			returning
				xmin as xmin_substance_intake
		"""
	]
	_updatable_fields = [
		u'started',
		u'preparation',
		u'strength',
		u'intake_is_approved_of',
		u'schedule',
		u'duration',
		u'aim',
		u'is_long_term',
		u'notes',
		u'pk_brand',
		u'pk_substance',
		u'pk_episode'
	]
	#--------------------------------------------------------
	def format(self, left_margin=0, date_format='%Y-%m-%d'):

		if self._payload[self._idx['duration']] is None:
			duration = gmTools.bool2subst (
				self._payload[self._idx['is_long_term']],
				_('long-term'),
				_('short-term'),
				_('?short-term')
			)
		else:
			duration = gmDateTime.format_interval (
				self._payload[self._idx['duration']],
				accuracy_wanted = gmDateTime.acc_days
			)

		line = u'%s%s (%s %s): %s %s %s (%s)' % (
			u' ' * left_margin,
			self._payload[self._idx['started']].strftime(date_format),
			gmTools.u_right_arrow,
			duration,
			self._payload[self._idx['substance']],
			self._payload[self._idx['strength']],
			self._payload[self._idx['preparation']],
			gmTools.bool2subst(self._payload[self._idx['is_currently_active']], _('ongoing'), _('inactive'), _('?ongoing'))
		)

		return line
	#--------------------------------------------------------
	def _get_external_code(self):
		drug = self.containing_drug

		if drug is None:
			return None

		return drug.external_code

	external_code = property(_get_external_code, lambda x:x)
	#--------------------------------------------------------
	def _get_containing_drug(self):
		if self._payload[self._idx['pk_brand']] is None:
			return None

		return cBrandedDrug(aPK_obj = self._payload[self._idx['pk_brand']])

	containing_drug = property(_get_containing_drug, lambda x:x)
	#--------------------------------------------------------
	def _get_parsed_schedule(self):
		tests = [
			# lead, trail
			'	1-1-1-1 ',
			# leading dose
			'1-1-1-1',
			'22-1-1-1',
			'1/3-1-1-1',
			'/4-1-1-1'
		]
		pattern = "^(\d\d|/\d|\d/\d|\d)[\s-]{1,5}\d{0,2}[\s-]{1,5}\d{0,2}[\s-]{1,5}\d{0,2}$"
		for test in tests:
			print test.strip(), ":", regex.match(pattern, test.strip())
#------------------------------------------------------------
def create_substance_intake(substance=None, atc=None, encounter=None, episode=None, preparation=None):

	args = {
		'desc': substance,
		'atc': atc,
		'enc': encounter,
		'epi': episode,
		'prep': preparation,
		'subst': create_used_substance(substance = substance, atc = atc)['pk']
	}

	cmd = u"""
insert into clin.substance_intake (
	fk_encounter,
	fk_episode,
	fk_substance,
	preparation,
	intake_is_approved_of
) values (
	%(enc)s,
	%(epi)s,
	%(subst)s,
	gm.nullify_empty_string(%(prep)s),
	False
)
returning pk
"""
	rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True)
	return cSubstanceIntakeEntry(aPK_obj = rows[0][0])
#------------------------------------------------------------
def delete_substance_intake(substance=None):
	cmd = u'delete from clin.substance_intake where pk = %(pk)s'
	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': {'pk': substance}}])
#============================================================
class cBrandedDrug(gmBusinessDBObject.cBusinessDBObject):
	"""Represents a drug as marketed by a manufacturer."""

	_cmd_fetch_payload = u"select *, xmin from ref.branded_drug where pk = %s"
	_cmds_store_payload = [
		u"""update ref.branded_drug set
				description = %(description)s,
				preparation = %(preparation)s,
				atc_code = %(atc_code)s,
				is_fake = %(is_fake)s,
				external_code = %(external_code)s,
				fk_data_source = %(fk_data_source)s
			where
				pk = %(pk)s and
				xmin = %(xmin)s
			returning
				xmin
		"""
	]
	_updatable_fields = [
		u'description',
		u'preparation',
		u'atc_code',
		u'is_fake',
		u'external_code',
		u'fk_data_source'
	]
	#--------------------------------------------------------
	def _get_external_code(self):
		if self._payload[self._idx['external_code']] is None:
			return None

		if regex.match(u'.+::.+', self._payload[self._idx['external_code']], regex.UNICODE) is None:
			# FIXME: maybe evaluate fk_data_source
			return None

		return regex.split(u'::', self._payload[self._idx['external_code']], 1)

	external_code = property(_get_external_code, lambda x:x)
	#--------------------------------------------------------
	def add_component(self, substance=None, atc=None):

		# normalize atc
		if atc is not None:
			if atc.strip() == u'':
				atc = None

		args = {
			'brand': self.pk_obj,
			'desc': substance,
			'atc': atc
		}

		# already exists ?
		cmd = u"SELECT pk FROM ref.substance_in_brand WHERE description = %(desc)s AND fk_brand = %(brand)s"
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		if len(rows) > 0:
			gmATC.propagate_atc(substance = substance, atc = atc)
			return

		# create it
		cmd = u"""
			INSERT INTO ref.substance_in_brand (fk_brand, description, atc_code)
			VALUES (%(brand)s, %(desc)s, %(atc)s)
		"""
		gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
		gmATC.propagate_atc(substance = substance, atc = atc)
#------------------------------------------------------------
def get_substances_in_brands():
	cmd = u'SELECT * FROM ref.v_substance_in_brand ORDER BY brand, substance'
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = False)
	return rows
#------------------------------------------------------------
def get_branded_drugs():

	cmd = u'SELECT pk FROM ref.branded_drug ORDER BY description'
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = False)

	return [ cBrandedDrug(aPK_obj = r['pk']) for r in rows ]
#------------------------------------------------------------
def get_drug_by_brand(brand_name=None, preparation=None):
	args = {'brand': brand_name, 'prep': preparation}

	cmd = u'SELECT pk FROM ref.branded_drug WHERE description = %(brand)s AND preparation = %(prep)s'
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)

	if len(rows) == 0:
		return None

	return cBrandedDrug(aPK_obj = rows[0]['pk'])
#------------------------------------------------------------
def create_branded_drug(brand_name=None, preparation=None):

	if get_drug_by_brand(brand_name = brand_name, preparation = preparation) is not None:
		return None

	cmd = u'insert into ref.branded_drug (description, preparation) values (%(brand)s, %(prep)s) returning pk'
	args = {'brand': brand_name, 'prep': preparation}
	rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True, get_col_idx = False)

	return cBrandedDrug(aPK_obj = rows[0]['pk'])
#------------------------------------------------------------
def delete_branded_drug(brand=None):
	cmd = u'delete from ref.branded_drug where pk = %(pk)s'
	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': {'pk': brand}}])
#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	from Gnumed.pycommon import gmLog2
	from Gnumed.pycommon import gmI18N

	gmI18N.activate_locale()
#	gmDateTime.init()
	#--------------------------------------------------------
	def test_MMI_interface():
		mmi = cGelbeListeWineInterface()
		print mmi
		print "interface definition:", mmi.version
		print "database versions:   ", mmi.get_data_source_version()
	#--------------------------------------------------------
	def test_MMI_file():
		mmi_file = cGelbeListeCSVFile(filename = sys.argv[2])
		for drug in mmi_file:
			print "-------------"
			print '"%s" (ATC: %s / PZN: %s)' % (drug['name'], drug['atc'], drug['pzn'])
			for stoff in drug['wirkstoffe']:
				print " Wirkstoff:", stoff
			print drug
		mmi_file.close()
	#--------------------------------------------------------
	def test_mmi_switch_to():
		mmi = cGelbeListeWineInterface()
		mmi.switch_to_frontend(blocking = False)
	#--------------------------------------------------------
	def test_mmi_select_drugs():
		mmi = cGelbeListeWineInterface()
		mmi_file = mmi.select_drugs()
		for drug in mmi_file:
			print "-------------"
			print '"%s" (ATC: %s / PZN: %s)' % (drug['name'], drug['atc'], drug['pzn'])
			for stoff in drug['wirkstoffe']:
				print " Wirkstoff:", stoff
			print drug
		mmi_file.close()
	#--------------------------------------------------------
	def test_mmi_import_drugs():
		mmi = cGelbeListeWineInterface()
		mmi.import_drugs()
	#--------------------------------------------------------
	def test_mmi_interaction_check():
		mmi = cGelbeListeInterface()
		print mmi
		print "interface definition:", mmi.version
		# Metoprolol + Hct vs Citalopram
		diclofenac = '7587712'
		phenprocoumon = '4421744'
		mmi.check_drug_interactions(pzn_list = [diclofenac, phenprocoumon])
	#--------------------------------------------------------
	#--------------------------------------------------------
	def test_create_substance_intake():
		drug = create_substance_intake (
			substance = u'Whiskey',
			atc = u'no ATC available',
			encounter = 1,
			episode = 1,
			preparation = 'a nice glass'
		)
		print drug
	#--------------------------------------------------------
	if (len(sys.argv)) > 1 and (sys.argv[1] == 'test'):
		test_MMI_interface()
		#test_MMI_file()
		#test_mmi_switch_to()
		#test_mmi_select_drugs()
		#test_mmi_import_substances()
		test_mmi_import_drugs()
		#test_interaction_check()
		#test_create_substance_intake()
#============================================================
# $Log: gmMedication.py,v $
# Revision 1.15  2009-11-29 19:59:31  ncq
# - improve substance/component creation with propagate-atc
#
# Revision 1.14  2009/11/29 15:57:27  ncq
# - while SQL results are dicts as far as *retrieval* is concerned,
#   they are NOT for inserting data into them, so use list access
#
# Revision 1.13  2009/11/28 18:27:30  ncq
# - much improved ATC detection on substance creation
# - create-patient-consumed-substance -> create-substance-intake
# - get-branded-drugs
# - get-substances-in-brands
# - delete-branded-drugs
#
# Revision 1.12  2009/11/24 19:57:22  ncq
# - implement getting/creating data souce entry for MMI
# - implement version retrieval for MMI
# - import-drugs()
# - check-drug-interactions()
# - cConsumedSubstance -> cSubstanceIntakeEntry + .external_code
# - cBrandedDrug
# - tests
#
# Revision 1.11  2009/11/06 15:05:07  ncq
# - get-substances-in-use
# - meds formatting
# - delete-patient-consumed-substance
#
# Revision 1.10  2009/10/29 17:16:59  ncq
# - return newly created substances from creator func and substance importer method
# - better naming
# - finish up cConsumedSubstance
#
# Revision 1.9  2009/10/28 16:40:12  ncq
# - add some docs about schedule parsing
#
# Revision 1.8  2009/10/26 22:29:05  ncq
# - better factorization of paths in MMI interface
# - update ATC on INN if now known
# - delete-consumed-substance
#
# Revision 1.7  2009/10/21 20:37:18  ncq
# - MMI uses cp1250, rather than cp1252, (at least under WINE) contrary to direct communication ...
# - use unicode csv reader
# - add a bunch of file cleanup
# - split MMI interface into WINE vs native Windows version
#
# Revision 1.6  2009/10/21 09:15:50  ncq
# - much improved MMI frontend
#
# Revision 1.5  2009/09/29 13:14:25  ncq
# - faulty ordering of definitions
#
# Revision 1.4  2009/09/01 22:16:35  ncq
# - improved interaction check test
#
# Revision 1.3  2009/08/24 18:36:20  ncq
# - add CSV file iterator
# - add BDT interaction check
#
# Revision 1.2  2009/08/21 09:56:37  ncq
# - start drug data source interfaces
# - add MMI/Gelbe Liste interface
#
# Revision 1.1  2009/05/12 12:02:01  ncq
# - start supporting current medications
#
#