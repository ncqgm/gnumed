# -*- coding: utf8 -*-
"""Medication handling code.

license: GPL
"""
#============================================================
__version__ = "$Revision: 1.21 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

import sys, logging, csv, codecs, os, re as regex


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmBusinessDBObject, gmPG2, gmShellAPI, gmTools
from Gnumed.pycommon import gmDispatcher, gmDateTime, gmHooks
from Gnumed.business import gmATC, gmAllergy


_log = logging.getLogger('gm.meds')
_log.info(__version__)

#============================================================
def _on_substance_intake_modified():
	"""Always relates to the active patient."""
	gmHooks.run_hook_script(hook = u'after_substance_intake_modified')

gmDispatcher.connect(_on_substance_intake_modified, u'substance_intake_mod_db')

#============================================================
# this should be in gmCoding.py
def create_data_source(long_name=None, short_name=None, version=None, source=None, language=None):

		args = {
			'lname': long_name,
			'sname': short_name,
			'ver': version,
			'src': source,
			'lang': language
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
		u't_rezept_pflicht',				# Thalidomid-Rezept
		u'erstattbares_medizinprodukt',
		u'hilfsmittel',
		u'hzv_rabattkennung',
		u'hzv_preis'
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
		u't_rezept_pflicht',
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
		if line['wirkstoffe'].strip() == u'':
			line['wirkstoffe'] = []
		else:
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
	def __init__(self):
		self.patient = None
		self.custom_path_to_binary = None
	#--------------------------------------------------------
	def get_data_source_version(self):
		raise NotImplementedError
	#--------------------------------------------------------
	def create_data_source_entry(self):
		raise NotImplementedError
	#--------------------------------------------------------
	def switch_to_frontend(self, blocking=False):
		raise NotImplementedError
	#--------------------------------------------------------
	def select_drugs(self):
		raise NotImplementedError
	#--------------------------------------------------------
	def import_drugs(self):
		raise NotImplementedError
	#--------------------------------------------------------
	def check_drug_interactions(self, drug_ids_list=None, substances=None):
		raise NotImplementedError
	#--------------------------------------------------------
	def show_info_on_drug(self, drug=None):
		raise NotImplementedError
#============================================================
class cFreeDiamsInterface(cDrugDataSourceInterface):

	"""http://ericmaeker.fr/FreeMedForms/di-manual/ligne_commandes.html"""

	version = u'FreeDiams v0.3.0 interface'
	default_encoding = 'utf8'
	default_dob_format = '%d/%m/%Y'

	map_gender2mf = {
		'm': u'M',
		'f': u'F',
		'tf': u'F',
		'tm': u'M',
		'h': u'H'
	}
	#--------------------------------------------------------
	def __init__(self):
		cDrugDataSourceInterface.__init__(self)
		_log.info(cFreeDiamsInterface.version)

		paths = gmTools.gmPaths()
		self.__exchange_filename = os.path.join(paths.home_dir, '.gnumed', 'tmp', 'gm2freediams.xml')
	#--------------------------------------------------------
	def get_data_source_version(self):
		#> Coded. Available next release
		#> Use --version or -version or -v
		return u'0.3.0'
		# ~/.freediams/config.ini: [License] -> AcceptedVersion=....
	#--------------------------------------------------------
	def create_data_source_entry(self):
		return create_data_source (
			long_name = u'"FreeDiams" Drug Database Frontend',
			short_name = u'FreeDiams',
			version = self.get_data_source_version(),
			source = u'http://ericmaeker.fr/FreeMedForms/di-manual/index.html',
			language = u'fr'			# actually to be multi-locale
		)
	#--------------------------------------------------------
	def switch_to_frontend(self, blocking=False):
		"""	--medintux : définit une utilisation spécifique à MedinTux.
			--exchange="xxx" : définit le fichier d'échange entre les deux applications.
			--chrono : Chronomètres diverses fonctions du testeur d'interactions (proposé à des fins de déboggage)
			--transmit-dosage = non documenté.
		"""
		found, cmd = gmShellAPI.find_first_binary(binaries = [
			self.custom_path_to_binary,
			r'/usr/bin/freediams',
			r'freediams',
			r'/Applications/FreeDiams.app/Contents/MacOs/FreeDiams',
			r'c:\programs\freediams\freediams.exe',
			r'freediams.exe'
		])

		if not found:
			_log.error('cannot find FreeDiams binary')
			return False

		# make sure csv file exists
		open(self.__exchange_filename, 'wb').close()
		args = u'--exchange="%s"' % self.__exchange_filename

		if self.patient is not None:

			args += u' --patientname="%(firstnames)s %(lastnames)s"' % self.patient.get_active_name()

			args += u' --gender=%s' % cFreeDiamsInterface.map_gender2mf[self.patient['gender']]

			if self.patient['dob'] is not None:
				args += u' --dateofbirth="%s"' % self.patient['dob'].strftime(cFreeDiamsInterface.default_dob_format)

			# FIXME: search by LOINC code and add
			# --weight="dd" : définit le poids du patient (en kg)
			# --size="ddd" : définit la taille du patient (en cm)
			# --clcr="dd.d" : définit la clairance de la créatinine du patient (en ml/min)
			# --creatinin="dd" : définit la créatininémie du patient (en mg/l)

		cmd = r'%s %s' % (cmd, args)

		if not gmShellAPI.run_command_in_shell(command = cmd):
			_log.error('problem switching to the FreeDiams drug database')
			return False

		return True
	#--------------------------------------------------------
	def select_drugs(self):
		self.switch_to_frontend()
	#--------------------------------------------------------
	def import_drugs(self):
		"""FreeDiams ONLY use CIS.

			CIS stands for Unique Speciality Identifier (eg bisoprolol 5 mg, gel).
			CIS is AFSSAPS specific, but pharmacist can retreive drug name with the CIS.
			AFSSAPS is the French FDA.

			CIP stands for Unique Presentation Identifier (eg 30 pills plaq)
			CIP if you want to specify the packaging of the drug (30 pills
			thermoformed tablet...) -- actually not really usefull for french
			doctors.
		"""
		self.switch_to_frontend()
		# .external_code_type: u'FR-CIS'
		# .external_cod: the CIS value
	#--------------------------------------------------------
	def check_drug_interactions(self, drug_ids_list=None, substances=None):
		self.switch_to_frontend()
	#--------------------------------------------------------
	def show_info_on_drug(self, drug=None):
		# pass in CIS
		self.switch_to_frontend()
#============================================================
class cGelbeListeWindowsInterface(cDrugDataSourceInterface):
	"""Support v8.2 CSV file interface only."""

	version = u'Gelbe Liste/MMI v8.2 interface'
	default_encoding = 'cp1250'
	bdt_line_template = u'%03d6210#%s\r\n'		# Medikament verordnet auf Kassenrezept
	bdt_line_base_length = 8
	#--------------------------------------------------------
	def __init__(self):

		cDrugDataSourceInterface.__init__(self)

		_log.info(u'%s (native Windows)', cGelbeListeWindowsInterface.version)

		self.path_to_binary = r'C:\Programme\MMI PHARMINDEX\glwin.exe'
		self.args = r'-KEEPBACKGROUND -PRESCRIPTIONFILE %s -CLOSETOTRAY'

		paths = gmTools.gmPaths()

		self.default_csv_filename = os.path.join(paths.home_dir, '.gnumed', 'tmp', 'rezept.txt')
		self.default_csv_filename_arg = os.path.join(paths.home_dir, '.gnumed', 'tmp')
		self.interactions_filename = os.path.join(paths.home_dir, '.gnumed', 'tmp', 'gm2mmi.bdt')
		self.data_date_filename = r'C:\Programme\MMI PHARMINDEX\datadate.txt'

		self.__data_date = None
		self.__online_update_date = None

		# use adjusted config.dat
	#--------------------------------------------------------
	def get_data_source_version(self, force_reload=False):

		if self.__data_date is not None:
			if not force_reload:
				return {
					'data': self.__data_date,
					'online_update': self.__online_update_date
				}

		open(self.data_date_filename, 'wb').close()

		cmd = u'%s -DATADATE' % self.path_to_binary
		if not gmShellAPI.run_command_in_shell(command = cmd, blocking = True):
			_log.error('problem querying the MMI drug database for version information')
			self.__data_date = None
			self.__online_update_date = None
			return {
				'data': u'?',
				'online_update': u'?'
			}

		try:
			version_file = open(self.data_date_filename, 'rU')
		except StandardError:
			_log.error('problem querying the MMI drug database for version information')
			_log.exception('cannot open MMI drug database version file [%s]', self.data_date_filename)
			self.__data_date = None
			self.__online_update_date = None
			return {
				'data': u'?',
				'online_update': u'?'
			}

		self.__data_date = version_file.readline()[:10]
		self.__online_update_date = version_file.readline()[:10]
		version_file.close()

		return {
			'data': self.__data_date,
			'online_update': self.__online_update_date
		}
	#--------------------------------------------------------
	def create_data_source_entry(self):
		versions = self.get_data_source_version()

		return create_data_source (
			long_name = u'Medikamentendatenbank "mmi PHARMINDEX" (Gelbe Liste)',
			short_name = u'GL/MMI',
			version = u'Daten: %s, Preise (Onlineupdate): %s' % (versions['data'], versions['online_update']),
			source = u'Medizinische Medien Informations GmbH, Am Forsthaus Gravenbruch 7, 63263 Neu-Isenburg',
			language = u'de'
		)
	#--------------------------------------------------------
	def switch_to_frontend(self, blocking=False, cmd=None):

		# must make sure csv file exists
		open(self.default_csv_filename, 'wb').close()

		if cmd is None:
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

			_log.debug('importing drug: %s %s', entry['name'], entry['darreichungsform'])

			if entry[u'hilfsmittel']:
				_log.debug('skipping Hilfsmittel')
				continue

			if entry[u'erstattbares_medizinprodukt']:
				_log.debug('skipping sonstiges Medizinprodukt')
				continue

			# create branded drug (or get it if it already exists)
			drug = create_branded_drug(brand_name = entry['name'], preparation = entry['darreichungsform'])
			if drug is None:
				drug = get_drug_by_brand(brand_name = entry['name'], preparation = entry['darreichungsform'])
			new_drugs.append(drug)

			# update fields
			drug['is_fake'] = False
			drug['atc_code'] = entry['atc']
			drug['external_code_type'] = u'DE-PZN'
			drug['external_code'] = entry['pzn']
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
	def check_drug_interactions(self, drug_ids_list=None, substances=None):
		"""For this to work the BDT interaction check must be configured in the MMI."""

		if drug_ids_list is None:
			if substances is None:
				return
			if len(substances) < 2:
				return
			drug_ids_list = [ (s.external_code_type, s.external_code) for s in substances ]
			drug_ids_list = [ code_value for code_type, code_value in drug_ids_list if (code_value is not None) and (code_type == u'DE-PZN')]

		else:
			if len(drug_ids_list) < 2:
				return

		if drug_ids_list < 2:
			return

		bdt_file = codecs.open(filename = self.interactions_filename, mode = 'wb', encoding = cGelbeListeWindowsInterface.default_encoding)

		for pzn in drug_ids_list:
			pzn = pzn.strip()
			lng = cGelbeListeWindowsInterface.bdt_line_base_length + len(pzn)
			bdt_file.write(cGelbeListeWindowsInterface.bdt_line_template % (lng, pzn))

		bdt_file.close()

		self.switch_to_frontend(blocking = False)
	#--------------------------------------------------------
	def show_info_on_substance(self, substance=None):

		cmd = None

		if substance.external_code_type == u'DE-PZN':
			cmd = u'%s -PZN %s' % (self.path_to_binary, substance.external_code)

		if cmd is None:
			name = gmTools.coalesce (
				substance['brand'],
				substance['substance']
			)
			cmd = u'%s -NAME %s' % (self.path_to_binary, name)

		# better to clean up interactions file
		open(self.interactions_filename, 'wb').close()

		self.switch_to_frontend(cmd = cmd)
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
	'Deutschland: Gelbe Liste/MMI (Windows)': cGelbeListeWindowsInterface,
	'Deutschland: Gelbe Liste/MMI (WINE)': cGelbeListeWineInterface,
	'France: FreeDiams': cFreeDiamsInterface
}
#============================================================
# substances in use across all patients
#------------------------------------------------------------
def get_substances_in_use():
	cmd = u'select * from clin.consumed_substance order by description'
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}])
	return rows
#------------------------------------------------------------
def get_substance_by_pk(pk=None):
	cmd = u'select * from clin.consumed_substance WHERE pk = %(pk)s'
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': {'pk': pk}}])
	if len(rows) == 0:
		return None
	return rows[0]
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
				discontinued = %(discontinued)s,
				discontinue_reason = gm.nullify_empty_string(%(discontinue_reason)s),
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
							(%(duration)s IS NULL)
						) is True then null
						else %(is_long_term)s
					end
				)::boolean,
				duration = (
					case
						when %(is_long_term)s is True then null
						else %(duration)s
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
		u'discontinued',
		u'discontinue_reason',
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
	def turn_into_allergy(self, encounter_id=None, allergy_type='allergy'):
		allg = gmAllergy.create_allergy (
			substance = gmTools.coalesce (
				self._payload[self._idx['brand']],
				self._payload[self._idx['substance']]
			),
			allg_type = allergy_type,
			episode_id = self._payload[self._idx['pk_episode']],
			encounter_id = encounter_id
		)
		allg['reaction'] = self._payload[self._idx['discontinue_reason']]
		allg['atc_code'] = gmTools.coalesce(self._payload[self._idx['atc_substance']], self._payload[self._idx['atc_brand']])
		if self._payload[self._idx['external_code_brand']] is not None:
			allg['substance_code'] = u'%s::::%s' % (self._payload[self._idx['external_code_type_brand']], self._payload[self._idx['external_code_brand']])
		allg['generics'] = self._payload[self._idx['substance']]

		allg.save()
		return allg
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_ddd(self):

		try: self.__ddd
		except AttributeError: self.__ddd = None

		if self.__ddd is not None:
			return self.__ddd

		if self._payload[self._idx['atc_substance']] is not None:
			ddd = gmATC.atc2ddd(atc = self._payload[self._idx['atc_substance']])
			if len(ddd) != 0:
				self.__ddd = ddd[0]
		else:
			if self._payload[self._idx['atc_brand']] is not None:
				ddd = gmATC.atc2ddd(atc = self._payload[self._idx['atc_brand']])
				if len(ddd) != 0:
					self.__ddd = ddd[0]

		return self.__ddd

	ddd = property(_get_ddd, lambda x:x)
	#--------------------------------------------------------
	def _get_external_code(self):
		drug = self.containing_drug

		if drug is None:
			return None

		return drug.external_code

	external_code = property(_get_external_code, lambda x:x)
	#--------------------------------------------------------
	def _get_external_code_type(self):
		drug = self.containing_drug

		if drug is None:
			return None

		return drug.external_code_type

	external_code_type = property(_get_external_code_type, lambda x:x)
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
				atc_code = gm.nullify_empty_string(%(atc_code)s),
				external_code = gm.nullify_empty_string(%(external_code)s),
				external_code_type = gm.nullify_empty_string(%(external_code_type)s),
				is_fake = %(is_fake)s,
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
		u'external_code_type',
		u'fk_data_source'
	]
	#--------------------------------------------------------
	def _get_external_code(self):
		if self._payload[self._idx['external_code']] is None:
			return None

		return self._payload[self._idx['external_code']]

	external_code = property(_get_external_code, lambda x:x)
	#--------------------------------------------------------
	def _get_external_code_type(self):

		# FIXME: maybe evaluate fk_data_source ?
		if self._payload[self._idx['external_code_type']] is None:
			return None

		return self._payload[self._idx['external_code_type']]

	external_code_type = property(_get_external_code_type, lambda x:x)
	#--------------------------------------------------------
	def _get_components(self):
		cmd = u'select * from ref.substance_in_brand where fk_brand = %(brand)s'
		args = {'brand': self._payload[self._idx['pk']]}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		return rows

	components = property(_get_components, lambda x:x)
	#--------------------------------------------------------
	def add_component(self, substance=None, atc=None):

		# normalize atc
		atc = gmATC.propagate_atc(substance = substance, atc = atc)

		args = {
			'brand': self.pk_obj,
			'desc': substance,
			'atc': atc
		}

		# already exists ?
		cmd = u"""
			SELECT pk
			FROM ref.substance_in_brand
			WHERE
				fk_brand = %(brand)s
					AND
				((description = %(desc)s) OR ((atc_code = %(atc)s) IS TRUE))
			"""
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		if len(rows) > 0:
			return

		# create it
		cmd = u"""
			INSERT INTO ref.substance_in_brand (fk_brand, description, atc_code)
			VALUES (%(brand)s, %(desc)s, %(atc)s)
		"""
		gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
	#------------------------------------------------------------
	def remove_component(substance=None):
		delete_component_from_branded_drug(brand = self.pk_obj, component = substance)
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
def create_branded_drug(brand_name=None, preparation=None, return_existing=False):

	if preparation is None:
		preparation = _('units')

	if preparation.strip() == u'':
		preparation = _('units')

	drug = get_drug_by_brand(brand_name = brand_name, preparation = preparation)

	if drug is not None:
		if return_existing:
			return drug
		return None

	cmd = u'insert into ref.branded_drug (description, preparation) values (%(brand)s, %(prep)s) returning pk'
	args = {'brand': brand_name, 'prep': preparation}
	rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True, get_col_idx = False)

	return cBrandedDrug(aPK_obj = rows[0]['pk'])
#------------------------------------------------------------
def delete_branded_drug(brand=None):
	cmd = u'delete from ref.branded_drug where pk = %(pk)s'
	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': {'pk': brand}}])
#------------------------------------------------------------
def delete_component_from_branded_drug(brand=None, component=None):
	cmd = u'delete from ref.substance_in_brand where fk_brand = %(brand)s and pk = %(comp)s'
	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': {'brand': brand, 'comp': component}}])
#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

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
		mmi.check_drug_interactions(drug_ids_list = [diclofenac, phenprocoumon])
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
	def test_show_components():
		drug = cBrandedDrug(aPK_obj = sys.argv[2])
		print drug
		print drug.components
	#--------------------------------------------------------
	#test_MMI_interface()
	#test_MMI_file()
	#test_mmi_switch_to()
	#test_mmi_select_drugs()
	#test_mmi_import_substances()
	#test_mmi_import_drugs()
	#test_interaction_check()
	#test_create_substance_intake()
	test_show_components()
#============================================================
