# -*- coding: utf8 -*-
"""Medication handling code.

license: GPL
"""
#============================================================
__version__ = "$Revision: 1.21 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

import sys, logging, csv, codecs, os, re as regex, subprocess, decimal
from xml.etree import ElementTree as etree


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
def drug2renal_insufficiency_url(search_term=None):

	if search_term is None:
		return u'http://www.dosing.de'

	terms = []
	names = []

	if isinstance(search_term, cBrandedDrug):
		if search_term['atc_code'] is not None:
			terms.append(search_term['atc_code'])

	elif isinstance(search_term, cSubstanceIntakeEntry):
		names.append(search_term['substance'])
		if search_term['atc_brand'] is not None:
			terms.append(search_term['atc_brand'])
		if search_term['atc_substance'] is not None:
			terms.append(search_term['atc_substance'])

	elif search_term is not None:
		names.append(u'%s' % search_term)
		terms.extend(gmATC.text2atc(text = u'%s' % search_term, fuzzy = True))

	for name in names:
		if name.endswith('e'):
			terms.append(name[:-1])
		else:
			terms.append(name)

	#url_template = u'http://www.google.de/#q=site%%3Adosing.de+%s'
	#url = url_template % u'+OR+'.join(terms)

	url_template = u'http://www.google.de/search?hl=de&source=hp&q=site%%3Adosing.de+%s&btnG=Google-Suche'
	url = url_template % u'+OR+'.join(terms)

	_log.debug(u'renal insufficiency URL: %s', url)

	return url
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
	#--------------------------------------------------------
	def _get_has_unknown_fields(self):
		return (gmTools.default_csv_reader_rest_key in self.csv_fieldnames)

	has_unknown_fields = property(_get_has_unknown_fields, lambda x:x)
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
	#--------------------------------------------------------
	def show_info_on_substance(self, substance=None):
		raise NotImplementedError
#============================================================
class cFreeDiamsInterface(cDrugDataSourceInterface):

	version = u'FreeDiams v0.5.0 interface'
	default_encoding = 'utf8'
	default_dob_format = '%Y/%m/%d'

	map_gender2mf = {
		'm': u'M',
		'f': u'F',
		'tf': u'H',
		'tm': u'H',
		'h': u'H'
	}
	#--------------------------------------------------------
	def __init__(self):
		cDrugDataSourceInterface.__init__(self)
		_log.info(cFreeDiamsInterface.version)

		paths = gmTools.gmPaths()
		self.__gm2fd_filename = os.path.join(paths.home_dir, '.gnumed', 'tmp', 'gm2freediams.xml')
		self.__fd2gm_filename = os.path.join(paths.home_dir, '.gnumed', 'tmp', 'freediams2gm.xml')
		self.__fd4gm_config_file = os.path.join(paths.home_dir, '.gnumed', 'freediams4gm.conf')

		self.path_to_binary = None
		self.__detect_binary()
	#--------------------------------------------------------
	def get_data_source_version(self):
		# ~/.freediams/config.ini: [License] -> AcceptedVersion=....

		if not self.__detect_binary():
			return False

		freediams = subprocess.Popen (
			args = u'--version',				# --version or -version or -v
			executable = self.path_to_binary,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
#			close_fds = True,					# Windows can't do that in conjunction with stdout/stderr = ... :-(
			universal_newlines = True
		)
		data, errors = freediams.communicate()
		version = regex.search('FreeDiams\s\d.\d.\d', data).group().split()[1]
		_log.debug('FreeDiams %s', version)

		return version
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
		"""http://ericmaeker.fr/FreeMedForms/di-manual/en/html/ligne_commandes.html"""

		if not self.__detect_binary():
			return False

		self.__create_gm2fd_file()
		open(self.__fd2gm_filename, 'wb').close()

		args = u'--exchange-in="%s"' % (self.__gm2fd_filename)
		cmd = r'%s %s' % (self.path_to_binary, args)
		if not gmShellAPI.run_command_in_shell(command = cmd, blocking = blocking):
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
			# .external_code_type: u'FR-CIS'
			# .external_cod: the CIS value
		"""
		self.switch_to_frontend(blocking = True)
		self.import_fd2gm_file()
	#--------------------------------------------------------
	def check_drug_interactions(self, drug_ids_list=None, substances=None):

		if substances is None:
			return
		if len(substances) < 2:
			return
		drug_ids_list = [ (s.external_code_type, s.external_code) for s in substances ]
		drug_ids_list = [ (code_value, code_type) for code_type, code_value in drug_ids_list if (code_value is not None)]

		if drug_ids_list < 2:
			return

		self.__create_prescription_file(drug_ids_list = drug_ids_list)
		self.switch_to_frontend(blocking = False)
	#--------------------------------------------------------
	def show_info_on_drug(self, drug=None):
		if drug is None:
			return
		self.switch_to_frontend()
	#--------------------------------------------------------
	def show_info_on_substance(self, substance=None):
		if substance is None:
			return
		self.__create_prescription_file (
			drug_ids_list = [(substance.external_code, substance.external_code_type)]
		)
		self.switch_to_frontend()
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __detect_binary(self):

		if self.path_to_binary is not None:
			return True

		found, cmd = gmShellAPI.find_first_binary(binaries = [
			r'/usr/bin/freediams',
			r'freediams',
			r'/Applications/FreeDiams.app/Contents/MacOs/FreeDiams',
			r'c:\programs\freediams\freediams.exe',
			r'freediams.exe'
		])

		if found:
			self.path_to_binary = cmd
			return True

		try:
			self.custom_path_to_binary
		except AttributeError:
			_log.error('cannot find FreeDiams binary, no custom path set')
			return False

		found, cmd = gmShellAPI.detect_external_binary(binary = self.custom_path_to_binary)
		if found:
			self.path_to_binary = cmd
			return True

		_log.error('cannot find FreeDiams binary')
		return False
	#--------------------------------------------------------
	def __create_prescription_file(self, drug_ids_list=None):

		xml = u"""<?xml version = "1.0" encoding = "UTF-8"?>

<FreeDiams>
	<DrugsDatabaseName>%s</DrugsDatabaseName>
	<FullPrescription version="0.4.0">

		%s

	</FullPrescription>
</FreeDiams>
"""
		drug_snippet = u"""<Prescription>
			<OnlyForTest>True</OnlyForTest>
			<Drug_UID>%s</Drug_UID>
			<!-- <Drug_UID_type>%s</Drug_UID_type> -->
		</Prescription>"""

		xml_file = codecs.open(self.__fd2gm_filename, 'wb', 'utf8')

		last_db_id = u'CA_HCDPD'
		drug_snippets = []
		for drug_id, db_id in drug_ids_list:
			last_db_id = db_id.replace(u'FreeDiams::', u'')
			drug_snippets.append(drug_snippet % (drug_id, last_db_id))

		xml_file.write(xml % (
			last_db_id,
			u'\n\t\t'.join(drug_snippets)
		))

		xml_file.close()
	#--------------------------------------------------------
	def __create_gm2fd_file(self):

		xml_file = codecs.open(self.__gm2fd_filename, 'wb', 'utf8')

		xml = u"""<?xml version="1.0" encoding="UTF-8"?>

<!-- Eric says the order of same-level nodes does not matter. -->

<FreeDiams_In version="0.5.0">
	<EMR name="GNUmed" uid="unused"/>
	<ConfigFile value="%s"/>
	<ExchangeOut value="%s" format="xml"/>				<!-- should perhaps better be html_xml ? -->
	<!-- <DrugsDatabase uid="can be set to a specific DB"/> -->
	<Ui editmode="select-only" blockPatientDatas="1"/>
	%%s
</FreeDiams_In>

<!--
		# FIXME: search by LOINC code and add (as soon as supported by FreeDiams ...)
		<Creatinine value="12" unit="mg/l or mmol/l"/>
		<Weight value="70" unit="kg or pd" />
		<Height value="170" unit="cm or "/>
		<ICD10 value="J11.0;A22;Z23"/>
-->
"""		% (
			self.__fd4gm_config_file,
			self.__fd2gm_filename
		)

		if self.patient is None:
			xml_file.write(xml % u'')
			xml_file.close()
			return

		name = self.patient.get_active_name()
		if self.patient['dob'] is None:
			dob = u''
		else:
			dob = self.patient['dob'].strftime(cFreeDiamsInterface.default_dob_format)

		emr = self.patient.get_emr()
		allgs = emr.get_allergies()
		atc_allgs = [
			a['atc_code'] for a in allgs if ((a['atc_code'] is not None) and (a['type'] == u'allergy'))
		]
		atc_sens = [
			a['atc_code'] for a in allgs if ((a['atc_code'] is not None) and (a['type'] == u'sensitivity'))
		]
		inn_allgs = [ a['allergene'] for a in allgs if a['type'] == u'allergy' ]
		inn_sens = [ a['allergene'] for a in allgs if a['type'] == u'sensitivity' ]
		# this is rather fragile: FreeDiams won't know what type of UID this is
		# (but it will assume it is of the type of the drug database in use)
		uid_allgs = [
			a['substance_code'] for a in allgs if ((a['substance_code'] is not None) and (a['type'] == u'allergy'))
		]
		uid_sens = [
			a['substance_code'] for a in allgs if ((a['substance_code'] is not None) and (a['type'] == u'sensitivity'))
		]

		patient_xml = u"""<Patient>
		<Identity
			  lastnames="%s"
			  firstnames="%s"
			  uid="%s"
			  dob="%s"
			  gender="%s"
		/>
		<ATCAllergies value="%s"/>
		<ATCIntolerances value="%s"/>

		<InnAllergies value="%s"/>
		<InnIntolerances value="%s"/>

		<DrugsUidAllergies value="%s"/>
		<DrugsUidIntolerances value="%s"/>
	</Patient>
"""		% (
			name['lastnames'],
			name['firstnames'],
			self.patient.ID,
			dob,
			cFreeDiamsInterface.map_gender2mf[self.patient['gender']],
			u';'.join(atc_allgs),
			u';'.join(atc_sens),
			u';'.join(inn_allgs),
			u';'.join(inn_sens),
			u';'.join(uid_allgs),
			u';'.join(uid_sens)
		)

		xml_file.write(xml % patient_xml)
		xml_file.close()
	#--------------------------------------------------------
	def import_fd2gm_file(self):
		"""
			If returning textual prescriptions (say, drugs which FreeDiams
			did not know) then "IsTextual" will be True and UID will be -1.
		"""
		fd2gm_xml = etree.ElementTree()
		fd2gm_xml.parse(self.__fd2gm_filename)

		data_src_pk = self.create_data_source_entry()

		db_id = fd2gm_xml.find('DrugsDatabaseName').text.strip()
		drugs = fd2gm_xml.findall('FullPrescription/Prescription')
		for drug in drugs:
			drug_name = drug.find('DrugName').text.replace(', )', ')').strip()
			drug_uid = drug.find('Drug_UID').text.strip()
			drug_form = drug.find('DrugForm').text.strip()
			#drug_atc = drug.find('DrugATC').text.strip()			# asked Eric to include

			new_drug = create_branded_drug(brand_name = drug_name, preparation = drug_form, return_existing = True)
			# update fields
			new_drug['is_fake_brand'] = False
			#new_drug['atc'] = drug_atc
			new_drug['external_code_type'] = u'FreeDiams::%s' % db_id
			new_drug['external_code'] = drug_uid
			new_drug['pk_data_source'] = data_src_pk
			new_drug.save()

			components = drug.getiterator('Composition')
			for comp in components:

				subst = comp.attrib['molecularName'].strip()

				amount = regex.match(r'\d+[.,]{0,1}\d*', comp.attrib['strenght'].strip())			# sic, typo
				if amount is None:
					amount = 99999
				else:
					amount = amount.group()

				unit = regex.sub(r'\d+[.,]{0,1}\d*', u'', comp.attrib['strenght'].strip()).strip()	# sic, typo
				if unit == u'':
					unit = u'*?*'

				inn = comp.attrib['inn'].strip()
				if inn != u'':
					create_consumable_substance(substance = inn, atc = None, amount = amount, unit = unit)
					if subst == u'':
						subst = inn

				new_drug.add_component(substance = subst, atc = None, amount = amount, unit = unit)
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
				new_substances.append(create_consumable_substance(substance = wirkstoff, atc = atc, amount = amount, unit = unit))

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
				new_substances.append(create_consumable_substance(substance = wirkstoff, atc = atc, amount = amount, unit = unit))

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
	def show_info_on_drug(self, drug=None):
		self.switch_to_frontend(blocking = True)
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
	'FreeDiams (France, US, Canada)': cFreeDiamsInterface
}
#============================================================
#============================================================
# substances in use across all patients
#------------------------------------------------------------
_SQL_get_consumable_substance = u"""
	SELECT *, xmin
	FROM ref.consumable_substance
	WHERE %s
"""

class cConsumableSubstance(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = _SQL_get_consumable_substance % u"pk = %s"
	_cmds_store_payload = [
		u"""UPDATE ref.consumable_substance SET
				description = %(description)s,
				atc_code = gm.nullify_empty_string(%(atc_code)s),
				amount = %(amount)s,
				unit = gm.nullify_empty_string(%(unit)s)
			WHERE
				pk = %(pk)s
					AND
				xmin = %(xmin)s
					AND
				-- must not currently be used with a patient directly
				NOT EXISTS (
					SELECT 1
					FROM clin.substance_intake
					WHERE
						fk_drug_component IS NULL
							AND
						fk_substance = %(pk)s
					LIMIT 1
				)
					AND
				-- must not currently be used with a patient indirectly, either
				NOT EXISTS (
					SELECT 1
					FROM clin.substance_intake
					WHERE
						fk_drug_component IS NOT NULL
							AND
						fk_drug_component = (
							SELECT r_ls2b.pk
							FROM ref.lnk_substance2brand r_ls2b
							WHERE fk_substance = %(pk)s
						)
					LIMIT 1
				)
--				-- must not currently be used with a branded drug
--				-- (but this would make it rather hard fixing branded drugs which contain only this substance)
--				NOT EXISTS (
--					SELECT 1
--					FROM ref.lnk_substance2brand
--					WHERE fk_substance = %(pk)s
--					LIMIT 1
--				)
			RETURNING
				xmin
		"""
	]
	_updatable_fields = [
		u'description',
		u'atc_code',
		u'amount',
		u'unit'
	]
	#--------------------------------------------------------
	def save_payload(self, conn=None):
		success, data = super(self.__class__, self).save_payload(conn = conn)

		if not success:
			return (success, data)

		if self._payload[self._idx['atc_code']] is not None:
			atc = self._payload[self._idx['atc_code']].strip()
			if atc != u'':
				gmATC.propagate_atc (
					substance = self._payload[self._idx['description']].strip(),
					atc = atc
				)

		return (success, data)
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_is_in_use_by_patients(self):
		cmd = u"""
			SELECT
				EXISTS (
					SELECT 1
					FROM clin.substance_intake
					WHERE
						fk_drug_component IS NULL
							AND
						fk_substance = %(pk)s
					LIMIT 1
				) OR EXISTS (
					SELECT 1
					FROM clin.substance_intake
					WHERE
						fk_drug_component IS NOT NULL
							AND
						fk_drug_component = (
							SELECT r_ls2b.pk
							FROM ref.lnk_substance2brand r_ls2b
							WHERE fk_substance = %(pk)s
						)
					LIMIT 1
				)"""
		args = {'pk': self.pk_obj}

		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		return rows[0][0]

	is_in_use_by_patients = property(_get_is_in_use_by_patients, lambda x:x)
	#--------------------------------------------------------
	def _get_is_drug_component(self):
		cmd = u"""
			SELECT EXISTS (
				SELECT 1
				FROM ref.lnk_substance2brand
				WHERE fk_substance = %(pk)s
				LIMIT 1
			)"""
		args = {'pk': self.pk_obj}

		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		return rows[0][0]

	is_drug_component = property(_get_is_drug_component, lambda x:x)
#------------------------------------------------------------
def get_consumable_substances(order_by=None):
	if order_by is None:
		order_by = u'true'
	else:
		order_by = u'true ORDER BY %s' % order_by
	cmd = _SQL_get_consumable_substance % order_by
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = True)
	return [ cConsumableSubstance(row = {'data': r, 'idx': idx, 'pk_field': 'pk'}) for r in rows ]
#------------------------------------------------------------
def create_consumable_substance(substance=None, atc=None, amount=None, unit=None):

	substance = substance
	if atc is not None:
		atc = atc.strip()

	args = {
		'desc': substance.strip(),
		'amount': decimal.Decimal(amount),
		'unit': unit.strip(),
		'atc': atc
	}
	cmd = u"""
		SELECT pk FROM ref.consumable_substance
		WHERE
			lower(description) = lower(%(desc)s)
				AND
			amount = %(amount)s
				AND
			unit = %(unit)s
		"""
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])

	if len(rows) == 0:
		cmd = u"""
			INSERT INTO ref.consumable_substance (description, atc_code, amount, unit) VALUES (
				%(desc)s,
				gm.nullify_empty_string(%(atc)s),
				%(amount)s,
				gm.nullify_empty_string(%(unit)s)
			) RETURNING pk"""
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True, get_col_idx = False)

	gmATC.propagate_atc(substance = substance, atc = atc)

	return cConsumableSubstance(aPK_obj = rows[0]['pk'])
#------------------------------------------------------------
def delete_consumable_substance(substance=None):
	args = {'pk': substance}
	cmd = u"""
DELETE FROM ref.consumable_substance
WHERE
	pk = %(pk)s
		AND

	-- must not currently be used with a patient
	NOT EXISTS (
		SELECT 1
		FROM clin.v_pat_substance_intake
		WHERE pk_substance = %(pk)s
		LIMIT 1
	)
		AND

	-- must not currently be used with a branded drug
	NOT EXISTS (
		SELECT 1
		FROM ref.lnk_substance2brand
		WHERE fk_substance = %(pk)s
		LIMIT 1
	)"""
	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
	return True
#============================================================
class cSubstanceIntakeEntry(gmBusinessDBObject.cBusinessDBObject):
	"""Represents a substance currently taken by a patient."""

	_cmd_fetch_payload = u"SELECT * FROM clin.v_pat_substance_intake WHERE pk_substance_intake = %s"
	_cmds_store_payload = [
		u"""UPDATE clin.substance_intake SET
				clin_when = %(started)s,
				discontinued = %(discontinued)s,
				discontinue_reason = gm.nullify_empty_string(%(discontinue_reason)s),
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
							(%(duration)s is NULL)
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

				fk_drug_component = %(pk_drug_component)s,
				fk_substance = %(pk_substance)s,
				fk_episode = %(pk_episode)s
			WHERE
				pk = %(pk_substance_intake)s
					AND
				xmin = %(xmin_substance_intake)s
			RETURNING
				xmin as xmin_substance_intake
		"""
	]
	_updatable_fields = [
		u'started',
		u'discontinued',
		u'discontinue_reason',
		u'preparation',
		u'intake_is_approved_of',
		u'schedule',
		u'duration',
		u'aim',
		u'is_long_term',
		u'notes',
		u'pk_drug_component',
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

		line = u'%s%s (%s %s): %s %s%s %s (%s)' % (
			u' ' * left_margin,
			self._payload[self._idx['started']].strftime(date_format),
			gmTools.u_right_arrow,
			duration,
			self._payload[self._idx['substance']],
			self._payload[self._idx['amount']],
			self._payload[self._idx['unit']],
			self._payload[self._idx['preparation']],
			gmTools.bool2subst(self._payload[self._idx['is_currently_active']], _('ongoing'), _('inactive'), _('?ongoing'))
		)

		return line
	#--------------------------------------------------------
	def turn_into_allergy(self, encounter_id=None, allergy_type='allergy'):
		allg = gmAllergy.create_allergy (
			allergene = self._payload[self._idx['substance']],
			allg_type = allergy_type,
			episode_id = self._payload[self._idx['pk_episode']],
			encounter_id = encounter_id
		)
		allg['substance'] = gmTools.coalesce (
			self._payload[self._idx['brand']],
			self._payload[self._idx['substance']]
		)
		allg['reaction'] = self._payload[self._idx['discontinue_reason']]
		allg['atc_code'] = gmTools.coalesce(self._payload[self._idx['atc_substance']], self._payload[self._idx['atc_brand']])
		if self._payload[self._idx['external_code_brand']] is not None:
			allg['substance_code'] = u'%s::::%s' % (self._payload[self._idx['external_code_type_brand']], self._payload[self._idx['external_code_brand']])
		allg['allergene'] = self._payload[self._idx['substance']]
		comps = [ c['substance'] for c in self.containing_drug.components ]
		if len(comps) == 0:
			allg['generics'] = self._payload[self._idx['substance']]
		else:
			allg['generics'] = u'; '.join(comps)

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
def create_substance_intake(substance=None, drug_component=None, atc=None, encounter=None, episode=None, preparation=None, amount=None, unit=None):

	args = {
		'enc': encounter,
		'epi': episode,
		'prep': preparation,
		'comp': drug_component,
		'subst': create_consumable_substance(substance = substance, atc = atc, amount = amount, unit = unit)['pk']
	}

	if drug_component is None:
		cmd = u"""
		INSERT INTO clin.substance_intake (
			fk_encounter,
			fk_episode,
			intake_is_approved_of,
			fk_substance,
			preparation
		) VALUES (
			%(enc)s,
			%(epi)s,
			False,
			%(subst)s,
			gm.nullify_empty_string(%(prep)s)
		)
		RETURNING pk"""
	else:
		cmd = u"""
		INSERT INTO clin.substance_intake (
			fk_encounter,
			fk_episode,
			intake_is_approved_of.
			fk_drug_component
		) VALUES (
			%(enc)s,
			%(epi)s,
			False,
			%(comp)s
		)
		RETURNING pk"""

	rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True)
	return cSubstanceIntakeEntry(aPK_obj = rows[0][0])
#------------------------------------------------------------
def delete_substance_intake(substance=None):
	cmd = u'delete from clin.substance_intake where pk = %(pk)s'
	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': {'pk': substance}}])
#------------------------------------------------------------
def format_substance_intake_notes(emr=None, output_format=u'latex', table_type=u'by-brand'):

	tex =  u'\n{\\small\n'
	tex += u'\\noindent %s\n' % _('Additional notes')
	tex += u'\n'
	tex += u'\\noindent \\begin{tabular}{|l|l|l|l|}\n'
	tex += u'\\hline\n'
	tex += u'%s & %s & %s & \\\\ \n' % (_('Substance'), _('Strength'), _('Brand'))
	tex += u'\\hline\n'
	tex += u'%s\n'
	tex += u'\n'
	tex += u'\\end{tabular}\n'
	tex += u'}\n'

	current_meds = emr.get_current_substance_intake (
		include_inactive = False,
		include_unapproved = False,
		order_by = u'brand, substance'
	)

	# create lines
	lines = []
	for med in current_meds:

		lines.append(u'%s & %s%s & %s %s & {\\scriptsize %s} \\\\ \n \\hline \n' % (
			med['substance'],
			med['amount'],
			med['unit'],
			gmTools.coalesce(med['brand'], u''),
			med['preparation'],
			gmTools.coalesce(med['notes'], u'')
		))

	return tex % u' \n'.join(lines)

#------------------------------------------------------------
def format_substance_intake(emr=None, output_format=u'latex', table_type=u'by-brand'):

	tex =  u'\\noindent %s {\\tiny (%s)\\par}\n' % (_('Medication list'), _('ordered by brand'))
	tex += u'\n'
	tex += u'\\noindent \\begin{tabular}{|l|l|}\n'
	tex += u'\\hline\n'
	tex += u'%s & %s \\\\ \n' % (_('Drug'), _('Regimen'))
	tex += u'\\hline\n'
	tex += u'\n'
	tex += u'\\hline\n'
	tex += u'%s\n'
	tex += u'\n'
	tex += u'\\end{tabular}\n'

	current_meds = emr.get_current_substance_intake (
		include_inactive = False,
		include_unapproved = False,
		order_by = u'brand, substance'
	)

	# aggregate data
	line_data = {}
	for med in current_meds:
		identifier = gmTools.coalesce(med['brand'], med['substance'])

		try:
			line_data[identifier]
		except KeyError:
			line_data[identifier] = {'brand': u'', 'preparation': u'', 'schedule': u'', 'aims': [], 'strengths': []}

		line_data[identifier]['brand'] = identifier
		line_data[identifier]['strengths'].append(u'%s%s' % (med['amount'].strip(), med['unit'].strip()))
		line_data[identifier]['preparation'] = med['preparation']
		line_data[identifier]['schedule'] = gmTools.coalesce(med['schedule'], u'')
		if med['aim'] not in line_data[identifier]['aims']:
			line_data[identifier]['aims'].append(med['aim'])

	# create lines
	already_seen = []
	lines = []
	line1_template = u'%s %s & %s \\\\'
	line2_template = u' & {\\scriptsize %s\\par} \\\\'

	for med in current_meds:
		identifier = gmTools.coalesce(med['brand'], med['substance'])

		if identifier in already_seen:
			continue

		already_seen.append(identifier)

		lines.append (line1_template % (
			line_data[identifier]['brand'],
			line_data[identifier]['preparation'],
			line_data[identifier]['schedule']
		))

		strengths = u'/'.join(line_data[identifier]['strengths'])
		if strengths == u'':
			template = u' & {\\scriptsize %s\\par} \\\\'
			for aim in line_data[identifier]['aims']:
				lines.append(template % aim)
		else:
			if len(line_data[identifier]['aims']) == 0:
				template = u'%s & \\\\'
				lines.append(template % strengths)
			else:
				template = u'%s & {\\scriptsize %s\\par} \\\\'
				lines.append(template % (strengths, line_data[identifier]['aims'][0]))
				template = u' & {\\scriptsize %s\\par} \\\\'
				for aim in line_data[identifier]['aims'][1:]:
					lines.append(template % aim)

		lines.append(u'\\hline')

	return tex % u' \n'.join(lines)
#============================================================
_SQL_get_drug_components = u'SELECT * FROM ref.v_drug_components WHERE %s'

class cDrugComponent(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = _SQL_get_drug_components % u'pk_component = %s'
	_cmds_store_payload = [
		u"""UPDATE ref.lnk_substance2brand SET
				fk_brand = %(pk_brand)s,
				fk_substance = %(pk_consumable_substance)s
			WHERE
				NOT EXISTS (
					SELECT 1
					FROM clin.substance_intake
					WHERE fk_drug_component = %(pk_component)s
					LIMIT 1
				)
					AND
				pk = %(pk_component)s
					AND
				xmin = %(xmin_lnk_substance2brand)s
			RETURNING
				xmin AS xmin_lnk_substance2brand
		"""
	]
	_updatable_fields = [
		u'pk_brand',
		u'pk_consumable_substance'
	]
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_containing_drug(self):
		return cBrandedDrug(aPK_obj = self._payload[self._idx['pk_brand']])

	containing_drug = property(_get_containing_drug, lambda x:x)
	#--------------------------------------------------------
	def _get_is_in_use_by_patients(self):
		return self._payload[self._idx['is_in_use']]

	is_in_use_by_patients = property(_get_is_in_use_by_patients, lambda x:x)
	#--------------------------------------------------------
	def _get_substance(self):
		return cConsumableSubstance(aPK_obj = self._payload[self._idx['pk_consumable_substance']])

	substance =  property(_get_substance, lambda x:x)
#------------------------------------------------------------
def get_drug_components():
	cmd = _SQL_get_drug_components % u'true ORDER BY brand, substance'
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = True)
	return [ cDrugComponent(row = {'data': r, 'idx': idx, 'pk_field': 'pk_component'}) for r in rows ]
#============================================================
class cBrandedDrug(gmBusinessDBObject.cBusinessDBObject):
	"""Represents a drug as marketed by a manufacturer."""

	_cmd_fetch_payload = u"SELECT * FROM ref.v_branded_drugs WHERE pk_brand = %s"
	_cmds_store_payload = [
		u"""UPDATE ref.branded_drug SET
				description = %(brand)s,
				preparation = %(preparation)s,
				atc_code = gm.nullify_empty_string(%(atc)s),
				external_code = gm.nullify_empty_string(%(external_code)s),
				external_code_type = gm.nullify_empty_string(%(external_code_type)s),
				is_fake = %(is_fake_brand)s,
				fk_data_source = %(pk_data_source)s
			WHERE
				pk = %(pk_brand)s
					AND
				xmin = %(xmin_branded_drug)s
			RETURNING
				xmin AS xmin_branded_drug
		"""
	]
	_updatable_fields = [
		u'brand',
		u'preparation',
		u'atc',
		u'is_fake_brand',
		u'external_code',
		u'external_code_type',
		u'pk_data_source'
	]
	#--------------------------------------------------------
	def save_payload(self, conn=None):
		success, data = super(self.__class__, self).save_payload(conn = conn)

		if not success:
			return (success, data)

		if self._payload[self._idx['atc']] is not None:
			atc = self._payload[self._idx['atc']].strip()
			if atc != u'':
				gmATC.propagate_atc (
					substance = self._payload[self._idx['brand']].strip(),
					atc = atc
				)

		return (success, data)
	#--------------------------------------------------------
	def set_substances_as_components(self, substances=None):

		if self._payload[self._idx['is_in_use']]:
			return False

		args = {'brand': self._payload[self._idx['pk_brand']]}

		queries = [{'cmd': u"DELETE FROM ref.lnk_substance2brand WHERE fk_brand = %(brand)s", 'args': args}]
		cmd = u'INSERT INTO ref.lnk_substance2brand (fk_brand, fk_substance) VALUES (%%(brand)s, %s)'
		for s in substances:
			queries.append({'cmd': cmd % s['pk'], 'args': args})

		gmPG2.run_rw_queries(queries = queries)
		self.refetch_payload()

		return True
	#--------------------------------------------------------
	def add_component(self, substance=None, atc=None, amount=None, unit=None, pk_substance=None):

		args = {
			'brand': self.pk_obj,
			'subst': consumable['description'],
			'atc': consumable['atc_code'],
			'pk_subst': pk_substance
		}

		if pk_substance is None:
			consumable = create_consumable_substance(substance = substance, atc = atc, amount = amount, unit = unit)
			args['pk_subst'] = consumable['pk']

		# already a component
		cmd = u"""
			SELECT pk_component
			FROM ref.v_drug_components
			WHERE
				pk_brand = %(brand)s
					AND
				((
					(lower(substance) = lower(%(subst)s))
						OR
					(lower(atc_substance) = lower(%(atc)s))
						OR
					(pk_consumable_substance = %(pk_subst)s)
				) IS TRUE)
		"""
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)

		if len(rows) > 0:
			return

		# create it
		cmd = u"""
			INSERT INTO ref.lnk_substance2brand (fk_brand, fk_substance)
			VALUES (%(brand)s, %(pk_subst)s)
		"""
		gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
	#------------------------------------------------------------
	def remove_component(self, substance=None):
		if len(self._payload[self._idx['components']]) == 1:
			_log.error('cannot remove the only component of a drug')
			return False

		args = {'brand': self.pk_obj, 'comp': substance}
		cmd = u"""
			DELETE FROM ref.lnk_substance2brand
			WHERE
				fk_brand = %(brand)s
					AND
				fk_substance = %(comp)s
					AND
				NOT EXISTS (
					SELECT 1
					FROM clin.substance_intake
					WHERE fk_drug_component = %(comp)s
					LIMIT 1
				)
		"""
		gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
		return True
	#--------------------------------------------------------
	# properties
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
		cmd = _SQL_get_drug_components % u'pk_brand = %(brand)s'
		args = {'brand': self._payload[self._idx['pk_brand']]}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		return [ cDrugComponent(row = {'data': r, 'idx': idx, 'pk_field': 'pk_component'}) for r in rows ]

	components = property(_get_components, lambda x:x)
	#--------------------------------------------------------
	def _get_components_as_substances(self):
		if self._payload[self._idx['pk_substances']] is None:
			return []
		cmd = _SQL_get_consumable_substance % u'pk IN %(pks)s'
		args = {'pks': tuple(self._payload[self._idx['pk_substances']])}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		return [ cConsumableSubstance(row = {'data': r, 'idx': idx, 'pk_field': 'pk'}) for r in rows ]

	components_as_substances = property(_get_components_as_substances, lambda x:x)
	#--------------------------------------------------------
	def _get_is_vaccine(self):
		cmd = u'SELECT EXISTS (SELECT 1 FROM clin.vaccine WHERE fk_brand = %(fk_brand)s)'
		args = {'fk_brand': self._payload[self._idx['pk_brand']]}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		return rows[0][0]

	is_vaccine = property(_get_is_vaccine, lambda x:x)
#------------------------------------------------------------
def get_branded_drugs():
	cmd = u'SELECT pk FROM ref.branded_drug ORDER BY description'
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = False)
	return [ cBrandedDrug(aPK_obj = r['pk']) for r in rows ]
#------------------------------------------------------------
def get_drug_by_brand(brand_name=None, preparation=None):
	args = {'brand': brand_name, 'prep': preparation}

	cmd = u'SELECT pk FROM ref.branded_drug WHERE lower(description) = lower(%(brand)s) AND lower(preparation) = lower(%(prep)s)'
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

	if return_existing:
		drug = get_drug_by_brand(brand_name = brand_name, preparation = preparation)
		if drug is not None:
			return drug

	cmd = u'INSERT INTO ref.branded_drug (description, preparation) VALUES (%(brand)s, %(prep)s) RETURNING pk'
	args = {'brand': brand_name, 'prep': preparation}
	rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True, get_col_idx = False)

	return cBrandedDrug(aPK_obj = rows[0]['pk'])
#------------------------------------------------------------
def delete_branded_drug(brand=None):
	queries = []
	args = {'pk': brand}

	# delete components
	cmd = u"""
		DELETE FROM ref.lnk_substance2brand
		WHERE
			fk_brand = %(pk)s
				AND
			NOT EXISTS (
				SELECT 1
				FROM clin.v_pat_substance_intake
				WHERE pk_brand = %(pk)s
				LIMIT 1
			)
	"""
	queries.append({'cmd': cmd, 'args': args})

	# delete drug
	cmd = u"""
		DELETE FROM ref.branded_drug
		WHERE
			pk = %(pk)s
				AND
			NOT EXISTS (
				SELECT 1
				FROM clin.v_pat_substance_intake
				WHERE pk_brand = %(pk)s
				LIMIT 1
			)
	"""
	queries.append({'cmd': cmd, 'args': args})

	gmPG2.run_rw_queries(queries = queries)
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
	from Gnumed.business import gmPerson

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
			raw_input()
			if mmi_file.has_unknown_fields is not None:
				print "has extra data under [%s]" % gmTools.default_csv_reader_rest_key
			for key in mmi_file.csv_fieldnames:
				print key, '->', drug[key]
			raw_input()
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
	# FreeDiams
	#--------------------------------------------------------
	def test_fd_switch_to():
		gmPerson.set_active_patient(patient = gmPerson.cIdentity(aPK_obj = 12))
		fd = cFreeDiamsInterface()
		fd.patient = gmPerson.gmCurrentPatient()
		fd.switch_to_frontend(blocking = True)
		fd.import_fd2gm_file()
	#--------------------------------------------------------
	def test_fd_show_interactions():
		gmPerson.set_active_patient(patient = gmPerson.cIdentity(aPK_obj = 12))
		fd = cFreeDiamsInterface()
		fd.patient = gmPerson.gmCurrentPatient()
		fd.check_drug_interactions(substances = fd.patient.get_emr().get_current_substance_intake(include_unapproved = True))
	#--------------------------------------------------------
	# generic
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
	def test_get_consumable_substances():
		for s in get_consumable_substances():
			print s
	#--------------------------------------------------------
	# MMI/Gelbe Liste
	#test_MMI_interface()
	#test_MMI_file()
	#test_mmi_switch_to()
	#test_mmi_select_drugs()
	#test_mmi_import_substances()
	#test_mmi_import_drugs()

	# FreeDiams
	#test_fd_switch_to()
	test_fd_show_interactions()

	# generic
	#test_interaction_check()
	#test_create_substance_intake()
	#test_show_components()
	#test_get_consumable_substances()
#============================================================
