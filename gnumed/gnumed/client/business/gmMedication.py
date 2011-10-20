# -*- coding: utf8 -*-
"""Medication handling code.

license: GPL v2 or later
"""
#============================================================
__version__ = "$Revision: 1.21 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

import sys
import logging
import csv
import codecs
import os
import re as regex
import subprocess
import decimal
from xml.etree import ElementTree as etree


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.pycommon import gmBusinessDBObject
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmShellAPI
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmMatchProvider
from Gnumed.pycommon import gmHooks
from Gnumed.pycommon import gmDateTime

from Gnumed.business import gmATC
from Gnumed.business import gmAllergy
from Gnumed.business.gmDocuments import DOCUMENT_TYPE_PRESCRIPTION
from Gnumed.business.gmDocuments import create_document_type


_log = logging.getLogger('gm.meds')
_log.info(__version__)


DEFAULT_MEDICATION_HISTORY_EPISODE = _('Medication history')
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
		if search_term['atc'] is not None:
			terms.append(search_term['atc'])

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

	url_template = u'http://www.google.com/search?hl=de&source=hp&q=site%%3Adosing.de+%s&btnG=Google-Suche'
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
		self.reviewer = None
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
	def import_drugs(self):
		self.switch_to_frontend()
	#--------------------------------------------------------
	def check_interactions(self, substance_intakes=None):
		self.switch_to_frontend()
	#--------------------------------------------------------
	def show_info_on_drug(self, substance_intake=None):
		self.switch_to_frontend()
	#--------------------------------------------------------
	def show_info_on_substance(self, substance_intake=None):
		self.switch_to_frontend()
	#--------------------------------------------------------
	def prescribe(self, substance_intakes=None):
		self.switch_to_frontend()
		return []
#============================================================
class cFreeDiamsInterface(cDrugDataSourceInterface):

	version = u'FreeDiams v0.5.4 interface'
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

		self.__imported_drugs = []

		self.__gm2fd_filename = gmTools.get_unique_filename(prefix = r'gm2freediams-', suffix = r'.xml')
		_log.debug('GNUmed -> FreeDiams "exchange-in" file: %s', self.__gm2fd_filename)
		self.__fd2gm_filename = gmTools.get_unique_filename(prefix = r'freediams2gm-', suffix = r'.xml')
		_log.debug('GNUmed <-> FreeDiams "exchange-out"/"prescription" file: %s', self.__fd2gm_filename)
		paths = gmTools.gmPaths()
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
	def switch_to_frontend(self, blocking=False, mode='interactions'):
		"""http://ericmaeker.fr/FreeMedForms/di-manual/en/html/ligne_commandes.html"""

		_log.debug('calling FreeDiams in [%s] mode', mode)

		self.__imported_drugs = []

		if not self.__detect_binary():
			return False

		self.__create_gm2fd_file(mode = mode)

		args = u'--exchange-in="%s"' % (self.__gm2fd_filename)
		cmd = r'%s %s' % (self.path_to_binary, args)
		if not gmShellAPI.run_command_in_shell(command = cmd, blocking = blocking):
			_log.error('problem switching to the FreeDiams drug database')
			return False

		if blocking == True:
			self.import_fd2gm_file_as_drugs()

		return True
	#--------------------------------------------------------
	def import_drugs(self):
		self.switch_to_frontend(blocking = True)
	#--------------------------------------------------------
	def check_interactions(self, substance_intakes=None):
		if substance_intakes is None:
			return
		if len(substance_intakes) < 2:
			return

		self.__create_prescription_file(substance_intakes = substance_intakes)
		self.switch_to_frontend(mode = 'interactions', blocking = False)
	#--------------------------------------------------------
	def show_info_on_drug(self, substance_intake=None):
		if substance_intake is None:
			return

		self.__create_prescription_file(substance_intakes = [substance_intake])
		self.switch_to_frontend(mode = 'interactions', blocking = False)
	#--------------------------------------------------------
	def show_info_on_substance(self, substance_intake=None):
		self.show_info_on_drug(substance_intake = substance_intake)
	#--------------------------------------------------------
	def prescribe(self, substance_intakes=None):
		if substance_intakes is None:
			if not self.__export_latest_prescription():
				self.__create_prescription_file()
		else:
			self.__create_prescription_file(substance_intakes = substance_intakes)

		self.switch_to_frontend(mode = 'prescription', blocking = True)
		self.import_fd2gm_file_as_prescription()

		return self.__imported_drugs
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
			r'C:\Program Files\FreeDiams\freediams.exe',
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

		if self.custom_path_to_binary is None:
			_log.error('cannot find FreeDiams binary')
			return False

		found, cmd = gmShellAPI.detect_external_binary(binary = self.custom_path_to_binary)
		if found:
			self.path_to_binary = cmd
			return True

		_log.error('cannot find FreeDiams binary')
		return False
	#--------------------------------------------------------
	def __export_latest_prescription(self):

		if self.patient is None:
			_log.debug('cannot export latest FreeDiams prescriptions w/o patient')
			return False

		docs = self.patient.get_document_folder()
		prescription = docs.get_latest_freediams_prescription()
		if prescription is None:
			_log.debug('no FreeDiams prescription available')
			return False

		for part in prescription.parts:
			if part['filename'] == u'freediams-prescription.xml':
				if part.export_to_file(filename = self.__fd2gm_filename) is not None:
					return True

		_log.error('cannot export latest FreeDiams prescription to XML file')

		return False
	#--------------------------------------------------------
	def __create_prescription_file(self, substance_intakes=None):
		"""FreeDiams calls this exchange-out or prescription file.

			CIS stands for Unique Speciality Identifier (eg bisoprolol 5 mg, gel).
			CIS is AFSSAPS specific, but pharmacist can retreive drug name with the CIS.
			AFSSAPS is the French FDA.

			CIP stands for Unique Presentation Identifier (eg 30 pills plaq)
			CIP if you want to specify the packaging of the drug (30 pills
			thermoformed tablet...) -- actually not really usefull for french
			doctors.
			# .external_code_type: u'FR-CIS'
			# .external_cod: the CIS value

		OnlyForTest:
			OnlyForTest drugs will be processed by the IA Engine but
			not printed (regardless of FreeDiams mode). They are shown
			in gray in the prescription view.

			Select-only is a mode where FreeDiams creates a list of drugs
			not a full prescription. In this list, users can add ForTestOnly
			drug if they want to
				1. print the list without some drugs
				2. but including these drugs in the IA engine calculation

			Select-Only mode does not have any relation with the ForTestOnly drugs.

		IsTextual:
			What is the use and significance of the
				<IsTextual>true/false</IsTextual>
			flag when both <DrugName> and <TextualDrugName> exist ?

			This tag must be setted even if it sounds like a duplicated
			data. This tag is needed inside FreeDiams code.

		INN:
			GNUmed will pass the substance in <TextualDrugName
			and will also pass <INN>True</INN>.

			Eric:	Nop, this is not usefull because pure textual drugs
					are not processed but just shown.
		"""
		# virginize file
		open(self.__fd2gm_filename, 'wb').close()

		# make sure we've got something to do
		if substance_intakes is None:
			if self.patient is None:
				_log.warning('cannot create prescription file because there is neither a patient nor a substance intake list')
				# do fail because __export_latest_prescription() should not have been called without patient
				return False
			emr = self.patient.get_emr()
			substance_intakes = emr.get_current_substance_intake (
				include_inactive = False,
				include_unapproved = True
			)

		drug_snippets = []

		# process FD drugs
		fd_intakes = [ i for i in substance_intakes if (
			(i['intake_is_approved_of'] is True)
				and
			(i['external_code_type_brand'] is not None)
				and
			(i['external_code_type_brand'].startswith(u'FreeDiams::'))
		)]

		intakes_pooled_by_brand = {}
		for intake in fd_intakes:
			# this will leave only one entry per brand
			# but FreeDiams knows the components ...
			intakes_pooled_by_brand[intake['brand']] = intake
		del fd_intakes

		drug_snippet = u"""<Prescription>
			<IsTextual>False</IsTextual>
			<DrugName>%s</DrugName>
			<Drug_UID>%s</Drug_UID>
			<Drug_UID_type>%s</Drug_UID_type>		<!-- not yet supported by FreeDiams -->
		</Prescription>"""

		last_db_id = u'CA_HCDPD'
		for intake in intakes_pooled_by_brand.values():
			last_db_id = gmTools.xml_escape_string(text = intake['external_code_type_brand'].replace(u'FreeDiams::', u'').split(u'::')[0])
			drug_snippets.append(drug_snippet % (
				gmTools.xml_escape_string(text = intake['brand'].strip()),
				gmTools.xml_escape_string(text = intake['external_code_brand'].strip()),
				last_db_id
			))

		# process non-FD drugs
		non_fd_intakes = [ i for i in substance_intakes if (
			(i['intake_is_approved_of'] is True)
			and (
				(i['external_code_type_brand'] is None)
					or
				(not i['external_code_type_brand'].startswith(u'FreeDiams::'))
			)
		)]

		non_fd_brand_intakes = [ i for i in non_fd_intakes if i['brand'] is not None ]
		non_fd_substance_intakes = [ i for i in non_fd_intakes if i['brand'] is None ]
		del non_fd_intakes

		drug_snippet = u"""<Prescription>
			<IsTextual>True</IsTextual>
			<TextualDrugName>%s</TextualDrugName>
		</Prescription>"""

		for intake in non_fd_substance_intakes:
			drug_name = u'%s %s%s (%s)%s' % (
				intake['substance'],
				intake['amount'],
				intake['unit'],
				intake['preparation'],
				gmTools.coalesce(intake['schedule'], u'', _('\n Take: %s'))
			)
			drug_snippets.append(drug_snippet % gmTools.xml_escape_string(text = drug_name.strip()))

		intakes_pooled_by_brand = {}
		for intake in non_fd_brand_intakes:
			brand = u'%s %s' % (intake['brand'], intake['preparation'])
			try:
				intakes_pooled_by_brand[brand].append(intake)
			except KeyError:
				intakes_pooled_by_brand[brand] = [intake]

		for brand, comps in intakes_pooled_by_brand.iteritems():
			drug_name = u'%s\n' % brand
			for comp in comps:
				drug_name += u'  %s %s%s\n' % (
					comp['substance'],
					comp['amount'],
					comp['unit']
			)
			if comps[0]['schedule'] is not None:
				drug_name += gmTools.coalesce(comps[0]['schedule'], u'', _('Take: %s'))
			drug_snippets.append(drug_snippet % gmTools.xml_escape_string(text = drug_name.strip()))

		# assemble XML file
		xml = u"""<?xml version = "1.0" encoding = "UTF-8"?>

<FreeDiams>
	<DrugsDatabaseName>%s</DrugsDatabaseName>
	<FullPrescription version="0.5.0">

		%s

	</FullPrescription>
</FreeDiams>
"""

		xml_file = codecs.open(self.__fd2gm_filename, 'wb', 'utf8')
		xml_file.write(xml % (
			last_db_id,
			u'\n\t\t'.join(drug_snippets)
		))
		xml_file.close()

		return True
	#--------------------------------------------------------
	def __create_gm2fd_file(self, mode='interactions'):

		if mode == 'interactions':
			mode = u'select-only'
		elif mode == 'prescription':
			mode = u'prescriber'
		else:
			mode = u'select-only'

		xml_file = codecs.open(self.__gm2fd_filename, 'wb', 'utf8')

		xml = u"""<?xml version="1.0" encoding="UTF-8"?>

<FreeDiams_In version="0.5.0">
	<EMR name="GNUmed" uid="unused"/>
	<ConfigFile value="%s"/>
	<ExchangeOut value="%s" format="xml"/>
	<!-- <DrugsDatabase uid="can be set to a specific DB"/> -->
	<Ui editmode="%s" blockPatientDatas="1"/>
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
			self.__fd2gm_filename,
			mode
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
			gmTools.xml_escape_string(text = name['lastnames']),
			gmTools.xml_escape_string(text = name['firstnames']),
			self.patient.ID,
			dob,
			cFreeDiamsInterface.map_gender2mf[self.patient['gender']],
			gmTools.xml_escape_string(text = u';'.join(atc_allgs)),
			gmTools.xml_escape_string(text = u';'.join(atc_sens)),
			gmTools.xml_escape_string(text = u';'.join(inn_allgs)),
			gmTools.xml_escape_string(text = u';'.join(inn_sens)),
			gmTools.xml_escape_string(text = u';'.join(uid_allgs)),
			gmTools.xml_escape_string(text = u';'.join(uid_sens))
		)

		xml_file.write(xml % patient_xml)
		xml_file.close()
	#--------------------------------------------------------
	def import_fd2gm_file_as_prescription(self, filename=None):

		if filename is None:
			filename = self.__fd2gm_filename

		fd2gm_xml = etree.ElementTree()
		fd2gm_xml.parse(filename)

		pdfs = fd2gm_xml.findall('ExtraDatas/Printed')
		if len(pdfs) == 0:
			return

		fd_filenames = []
		for pdf in pdfs:
			fd_filenames.append(pdf.attrib['file'])

		docs = self.patient.get_document_folder()
		emr = self.patient.get_emr()

		prescription = docs.add_document (
			document_type = create_document_type (
				document_type = DOCUMENT_TYPE_PRESCRIPTION
			)['pk_doc_type'],
			encounter = emr.active_encounter['pk_encounter'],
			episode = emr.add_episode (
				episode_name = DEFAULT_MEDICATION_HISTORY_EPISODE,
				is_open = False
			)['pk_episode']
		)
		prescription['ext_ref'] = u'FreeDiams'
		prescription.save()
		fd_filenames.append(filename)
		success, msg, parts = prescription.add_parts_from_files(files = fd_filenames)
		if not success:
			_log.error(msg)
			return

		for part in parts:
			part['obj_comment'] = _('copy')
			part.save()

		xml_part = parts[-1]
		xml_part['filename'] = u'freediams-prescription.xml'
		xml_part['obj_comment'] = _('data')
		xml_part.save()

		# are we the intended reviewer ?
		from Gnumed.business.gmPerson import gmCurrentProvider
		me = gmCurrentProvider()
		# if so: auto-sign the prescription
		if xml_part['pk_intended_reviewer'] == me['pk_staff']:
			prescription.set_reviewed(technically_abnormal = False, clinically_relevant = False)
	#--------------------------------------------------------
	def import_fd2gm_file_as_drugs(self, filename=None):
		"""
			If returning textual prescriptions (say, drugs which FreeDiams
			did not know) then "IsTextual" will be True and UID will be -1.
		"""
		if filename is None:
			filename = self.__fd2gm_filename

		# FIXME: do not import IsTextual drugs, or rather, make that configurable

		fd2gm_xml = etree.ElementTree()
		fd2gm_xml.parse(filename)

		data_src_pk = self.create_data_source_entry()

		db_def = fd2gm_xml.find('DrugsDatabaseName')
		db_id = db_def.text.strip()
		drug_id_name = db_def.attrib['drugUidName']
		fd_xml_drug_entries = fd2gm_xml.findall('FullPrescription/Prescription')

		self.__imported_drugs = []
		for fd_xml_drug in fd_xml_drug_entries:
			drug_uid = fd_xml_drug.find('Drug_UID').text.strip()
			if drug_uid == u'-1':
				_log.debug('skipping textual drug')
				continue		# it's a TextualDrug, skip it
			drug_name = fd_xml_drug.find('DrugName').text.replace(', )', ')').strip()
			drug_form = fd_xml_drug.find('DrugForm').text.strip()
			drug_atc = fd_xml_drug.find('DrugATC')
			if drug_atc is None:
				drug_atc = u''
			else:
				if drug_atc.text is None:
					drug_atc = u''
				else:
					drug_atc = drug_atc.text.strip()

			# create new branded drug
			new_drug = create_branded_drug(brand_name = drug_name, preparation = drug_form, return_existing = True)
			self.__imported_drugs.append(new_drug)
			new_drug['is_fake_brand'] = False
			new_drug['atc'] = drug_atc
			new_drug['external_code_type'] = u'FreeDiams::%s::%s' % (db_id, drug_id_name)
			new_drug['external_code'] = drug_uid
			new_drug['pk_data_source'] = data_src_pk
			new_drug.save()

			# parse XML for composition records
			fd_xml_components = fd_xml_drug.getiterator('Composition')
			comp_data = {}
			for fd_xml_comp in fd_xml_components:

				data = {}

				amount = regex.match(r'\d+[.,]{0,1}\d*', fd_xml_comp.attrib['strenght'].strip())			# sic, typo
				if amount is None:
					amount = 99999
				else:
					amount = amount.group()
				data['amount'] = amount

				unit = regex.sub(r'\d+[.,]{0,1}\d*', u'', fd_xml_comp.attrib['strenght'].strip()).strip()	# sic, typo
				if unit == u'':
					unit = u'*?*'
				data['unit'] = unit

				molecule_name = fd_xml_comp.attrib['molecularName'].strip()
				if molecule_name != u'':
					create_consumable_substance(substance = molecule_name, atc = None, amount = amount, unit = unit)
				data['molecule_name'] = molecule_name

				inn_name = fd_xml_comp.attrib['inn'].strip()
				if inn_name != u'':
					create_consumable_substance(substance = inn_name, atc = None, amount = amount, unit = unit)
				data['inn_name'] = molecule_name

				if molecule_name == u'':
					data['substance'] = inn_name
					_log.info('linking INN [%s] rather than molecularName as component', inn_name)
				else:
					data['substance'] = molecule_name

				data['nature'] = fd_xml_comp.attrib['nature'].strip()
				data['nature_ID'] = fd_xml_comp.attrib['natureLink'].strip()

				# merge composition records of SA/FT nature
				try:
					old_data = comp_data[data['nature_ID']]
					# normalize INN
					if old_data['inn_name'] == u'':
						old_data['inn_name'] = data['inn_name']
					if data['inn_name'] == u'':
						data['inn_name'] = old_data['inn_name']
					# normalize molecule
					if old_data['molecule_name'] == u'':
						old_data['molecule_name'] = data['molecule_name']
					if data['molecule_name'] == u'':
						data['molecule_name'] = old_data['molecule_name']
					# FT: transformed form
					# SA: active substance
					# it would be preferable to use the SA record because that's what's *actually*
					# contained in the drug, however FreeDiams does not list the amount thereof
					# (rather that of the INN)
					if data['nature'] == u'FT':
						comp_data[data['nature_ID']] = data
					else:
						comp_data[data['nature_ID']] = old_data

				# or create new record
				except KeyError:
					comp_data[data['nature_ID']] = data

			# actually create components from (possibly merged) composition records
			for key, data in comp_data.items():
				new_drug.add_component (
					substance = data['substance'],
					atc = None,
					amount = data['amount'],
					unit = data['unit']
				)
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
		try:
			open(self.data_date_filename, 'wb').close()
		except StandardError:
			_log.error('problem querying the MMI drug database for version information')
			_log.exception('cannot create MMI drug database version file [%s]', self.data_date_filename)
			self.__data_date = None
			self.__online_update_date = None
			return {
				'data': u'?',
				'online_update': u'?'
			}

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

		try:
			# must make sure csv file exists
			open(self.default_csv_filename, 'wb').close()
		except IOError:
			_log.exception('problem creating GL/MMI <-> GNUmed exchange file')
			return False

		if cmd is None:
			cmd = (u'%s %s' % (self.path_to_binary, self.args)) % self.default_csv_filename_arg

		if not gmShellAPI.run_command_in_shell(command = cmd, blocking = blocking):
			_log.error('problem switching to the MMI drug database')
			# apparently on the first call MMI does not
			# consistently return 0 on success
#			return False

		return True
	#--------------------------------------------------------
	def __let_user_select_drugs(self):

		# better to clean up interactions file
		open(self.interactions_filename, 'wb').close()

		if not self.switch_to_frontend(blocking = True):
			return None

		return cGelbeListeCSVFile(filename = self.default_csv_filename)
	#--------------------------------------------------------
	def import_drugs_as_substances(self):

		selected_drugs = self.__let_user_select_drugs()
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

		selected_drugs = self.__let_user_select_drugs()
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
			drug['is_fake_brand'] = False
			drug['atc'] = entry['atc']
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
	def check_interactions(self, drug_ids_list=None, substances=None):
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
	'FreeDiams (FR, US, CA, ZA)': cFreeDiamsInterface
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
						fk_drug_component IN (
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

	converted, amount = gmTools.input2decimal(amount)
	if not converted:
		raise ValueError('<amount> must be a number: %s (%s)', amount, type(amount))

	args = {
		'desc': substance.strip(),
		'amount': amount,
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
#------------------------------------------------------------
class cSubstanceMatchProvider(gmMatchProvider.cMatchProvider_SQL2):

	_pattern = regex.compile(r'^\D+\s*\d+$', regex.UNICODE | regex.LOCALE)
	_query1 = u"""
		SELECT
			pk::text,
			(description || ' ' || amount || ' ' || unit) as subst
		FROM ref.consumable_substance
		WHERE description %(fragment_condition)s
		ORDER BY subst
		LIMIT 50"""
	_query2 = u"""
		SELECT
			pk::text,
			(description || ' ' || amount || ' ' || unit) as subst
		FROM ref.consumable_substance
		WHERE
			%(fragment_condition)s
		ORDER BY subst
		LIMIT 50"""

	#--------------------------------------------------------
	def getMatchesByPhrase(self, aFragment):
		"""Return matches for aFragment at start of phrases."""

		if cSubstanceMatchProvider._pattern.match(aFragment):
			self._queries = [cSubstanceMatchProvider._query2]
			fragment_condition = """description ILIKE %(desc)s
				AND
			amount::text ILIKE %(amount)s"""
			self._args['desc'] = u'%s%%' % regex.sub(r'\s*\d+$', u'', aFragment)
			self._args['amount'] = u'%s%%' % regex.sub(r'^\D+\s*', u'', aFragment)
		else:
			self._queries = [cSubstanceMatchProvider._query1]
			fragment_condition = u"ILIKE %(fragment)s"
			self._args['fragment'] = u"%s%%" % aFragment

		return self._find_matches(fragment_condition)
	#--------------------------------------------------------
	def getMatchesByWord(self, aFragment):
		"""Return matches for aFragment at start of words inside phrases."""

		if cSubstanceMatchProvider._pattern.match(aFragment):
			self._queries = [cSubstanceMatchProvider._query2]

			desc = regex.sub(r'\s*\d+$', u'', aFragment)
			desc = gmPG2.sanitize_pg_regex(expression = desc, escape_all = False)

			fragment_condition = """description ~* %(desc)s
				AND
			amount::text ILIKE %(amount)s"""

			self._args['desc'] = u"( %s)|(^%s)" % (desc, desc)
			self._args['amount'] = u'%s%%' % regex.sub(r'^\D+\s*', u'', aFragment)
		else:
			self._queries = [cSubstanceMatchProvider._query1]
			fragment_condition = u"~* %(fragment)s"
			aFragment = gmPG2.sanitize_pg_regex(expression = aFragment, escape_all = False)
			self._args['fragment'] = u"( %s)|(^%s)" % (aFragment, aFragment)

		return self._find_matches(fragment_condition)
	#--------------------------------------------------------
	def getMatchesBySubstr(self, aFragment):
		"""Return matches for aFragment as a true substring."""

		if cSubstanceMatchProvider._pattern.match(aFragment):
			self._queries = [cSubstanceMatchProvider._query2]
			fragment_condition = """description ILIKE %(desc)s
				AND
			amount::text ILIKE %(amount)s"""
			self._args['desc'] = u'%%%s%%' % regex.sub(r'\s*\d+$', u'', aFragment)
			self._args['amount'] = u'%s%%' % regex.sub(r'^\D+\s*', u'', aFragment)
		else:
			self._queries = [cSubstanceMatchProvider._query1]
			fragment_condition = u"ILIKE %(fragment)s"
			self._args['fragment'] = u"%%%s%%" % aFragment

		return self._find_matches(fragment_condition)
#============================================================
class cSubstanceIntakeEntry(gmBusinessDBObject.cBusinessDBObject):
	"""Represents a substance currently taken by a patient."""

	_cmd_fetch_payload = u"SELECT * FROM clin.v_pat_substance_intake WHERE pk_substance_intake = %s"
	_cmds_store_payload = [
		u"""UPDATE clin.substance_intake SET
				clin_when = %(started)s,
				discontinued = %(discontinued)s,
				discontinue_reason = gm.nullify_empty_string(%(discontinue_reason)s),
				schedule = gm.nullify_empty_string(%(schedule)s),
				aim = gm.nullify_empty_string(%(aim)s),
				narrative = gm.nullify_empty_string(%(notes)s),
				intake_is_approved_of = %(intake_is_approved_of)s,
				fk_episode = %(pk_episode)s,

				preparation = (
					case
						when %(pk_brand)s is NULL then %(preparation)s
						else NULL
					end
				)::text,

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
				)::interval
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

		if self._payload[self._idx['pk_brand']] is None:
			allg['generics'] = self._payload[self._idx['substance']]
		else:
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
def create_substance_intake(pk_substance=None, pk_component=None, preparation=None, encounter=None, episode=None):

	args = {
		'enc': encounter,
		'epi': episode,
		'comp': pk_component,
		'subst': pk_substance,
		'prep': preparation
	}

	if pk_component is None:
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
				%(prep)s
			)
			RETURNING pk"""
	else:
		cmd = u"""
			INSERT INTO clin.substance_intake (
				fk_encounter,
				fk_episode,
				intake_is_approved_of,
				fk_drug_component
			) VALUES (
				%(enc)s,
				%(epi)s,
				False,
				%(comp)s
			)
			RETURNING pk"""

	try:
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True)
	except gmPG2.dbapi.InternalError, e:
		if e.pgerror is None:
			raise
		if 'prevent_duplicate_component' in e.pgerror:
			_log.exception('will not create duplicate substance intake entry')
			_log.error(e.pgerror)
			return None
		raise

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
	tex += u'\\noindent \\begin{tabularx}{\\textwidth}{|X|l|X|p{7.5cm}|}\n'
	tex += u'\\hline\n'
	tex += u'%s {\\scriptsize (%s)} & %s & %s \\\\ \n' % (_('Substance'), _('Brand'), _('Strength'), _('Advice'))
	tex += u'\\hline\n'
	tex += u'%s\n'
	tex += u'\n'
	tex += u'\\end{tabularx}\n'
	tex += u'}\n'

	current_meds = emr.get_current_substance_intake (
		include_inactive = False,
		include_unapproved = False,
		order_by = u'brand, substance'
	)

	# create lines
	lines = []
	for med in current_meds:
		lines.append(u'%s%s %s & %s%s & %s \\\\ \n \\hline \n' % (
			med['substance'],
			gmTools.coalesce(med['brand'], u'', u' {\\scriptsize (%s)}'),
			med['preparation'],
			med['amount'],
			med['unit'],
			gmTools.coalesce(med['notes'], u'', u'{\\scriptsize %s}')
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
		line_data[identifier]['strengths'].append(u'%s%s' % (med['amount'], med['unit'].strip()))
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
#------------------------------------------------------------
class cDrugComponentMatchProvider(gmMatchProvider.cMatchProvider_SQL2):

	_pattern = regex.compile(r'^\D+\s*\d+$', regex.UNICODE | regex.LOCALE)
	_query_desc_only = u"""
		SELECT DISTINCT ON (component)
			pk_component,
			(substance || ' ' || amount || unit || ' ' || preparation || ' (' || brand ||  ')')
				AS component
		FROM ref.v_drug_components
		WHERE
			substance %(fragment_condition)s
				OR
			brand %(fragment_condition)s
		ORDER BY component
		LIMIT 50"""
	_query_desc_and_amount = u"""

		SELECT DISTINCT ON (component)
			pk_component,
			(substance || ' ' || amount || unit || ' ' || preparation || ' (' || brand ||  ')')
				AS component
		FROM ref.v_drug_components
		WHERE
			%(fragment_condition)s
		ORDER BY component
		LIMIT 50"""
	#--------------------------------------------------------
	def getMatchesByPhrase(self, aFragment):
		"""Return matches for aFragment at start of phrases."""

		if cDrugComponentMatchProvider._pattern.match(aFragment):
			self._queries = [cDrugComponentMatchProvider._query_desc_and_amount]
			fragment_condition = """(substance ILIKE %(desc)s OR brand ILIKE %(desc)s)
				AND
			amount::text ILIKE %(amount)s"""
			self._args['desc'] = u'%s%%' % regex.sub(r'\s*\d+$', u'', aFragment)
			self._args['amount'] = u'%s%%' % regex.sub(r'^\D+\s*', u'', aFragment)
		else:
			self._queries = [cDrugComponentMatchProvider._query_desc_only]
			fragment_condition = u"ILIKE %(fragment)s"
			self._args['fragment'] = u"%s%%" % aFragment

		return self._find_matches(fragment_condition)
	#--------------------------------------------------------
	def getMatchesByWord(self, aFragment):
		"""Return matches for aFragment at start of words inside phrases."""

		if cDrugComponentMatchProvider._pattern.match(aFragment):
			self._queries = [cDrugComponentMatchProvider._query_desc_and_amount]

			desc = regex.sub(r'\s*\d+$', u'', aFragment)
			desc = gmPG2.sanitize_pg_regex(expression = desc, escape_all = False)

			fragment_condition = """(substance ~* %(desc)s OR brand ~* %(desc)s)
				AND
			amount::text ILIKE %(amount)s"""

			self._args['desc'] = u"( %s)|(^%s)" % (desc, desc)
			self._args['amount'] = u'%s%%' % regex.sub(r'^\D+\s*', u'', aFragment)
		else:
			self._queries = [cDrugComponentMatchProvider._query_desc_only]
			fragment_condition = u"~* %(fragment)s"
			aFragment = gmPG2.sanitize_pg_regex(expression = aFragment, escape_all = False)
			self._args['fragment'] = u"( %s)|(^%s)" % (aFragment, aFragment)

		return self._find_matches(fragment_condition)
	#--------------------------------------------------------
	def getMatchesBySubstr(self, aFragment):
		"""Return matches for aFragment as a true substring."""

		if cDrugComponentMatchProvider._pattern.match(aFragment):
			self._queries = [cDrugComponentMatchProvider._query_desc_and_amount]
			fragment_condition = """(substance ILIKE %(desc)s OR brand ILIKE %(desc)s)
				AND
			amount::text ILIKE %(amount)s"""
			self._args['desc'] = u'%%%s%%' % regex.sub(r'\s*\d+$', u'', aFragment)
			self._args['amount'] = u'%s%%' % regex.sub(r'^\D+\s*', u'', aFragment)
		else:
			self._queries = [cDrugComponentMatchProvider._query_desc_only]
			fragment_condition = u"ILIKE %(fragment)s"
			self._args['fragment'] = u"%%%s%%" % aFragment

		return self._find_matches(fragment_condition)

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

		if self.is_in_use_by_patients:
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
			'subst': substance,
			'atc': atc,
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
		self.refetch_payload()
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
		self.refetch_payload()

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
	#--------------------------------------------------------
	def _get_is_in_use_by_patients(self):
		cmd = u"""
			SELECT EXISTS (
				SELECT 1
				FROM clin.substance_intake
				WHERE
					fk_drug_component IS NOT NULL
						AND
					fk_drug_component IN (
						SELECT r_ls2b.pk
						FROM ref.lnk_substance2brand r_ls2b
						WHERE fk_brand = %(pk)s
					)
				LIMIT 1
			)"""
		args = {'pk': self.pk_obj}

		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		return rows[0][0]

	is_in_use_by_patients = property(_get_is_in_use_by_patients, lambda x:x)
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
	def test_mmi_let_user_select_drugs():
		mmi = cGelbeListeWineInterface()
		mmi_file = mmi.__let_user_select_drugs()
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
		mmi.check_interactions(drug_ids_list = [diclofenac, phenprocoumon])
	#--------------------------------------------------------
	# FreeDiams
	#--------------------------------------------------------
	def test_fd_switch_to():
		gmPerson.set_active_patient(patient = gmPerson.cIdentity(aPK_obj = 12))
		fd = cFreeDiamsInterface()
		fd.patient = gmPerson.gmCurrentPatient()
#		fd.switch_to_frontend(blocking = True)
		fd.import_fd2gm_file_as_drugs(filename = sys.argv[2])
	#--------------------------------------------------------
	def test_fd_show_interactions():
		gmPerson.set_active_patient(patient = gmPerson.cIdentity(aPK_obj = 12))
		fd = cFreeDiamsInterface()
		fd.patient = gmPerson.gmCurrentPatient()
		fd.check_interactions(substances = fd.patient.get_emr().get_current_substance_intake(include_unapproved = True))
	#--------------------------------------------------------
	# generic
	#--------------------------------------------------------
	def test_create_substance_intake():
		drug = create_substance_intake (
			pk_component = 2,
			encounter = 1,
			episode = 1
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
	def test_drug2renal_insufficiency_url():
		drug2renal_insufficiency_url(search_term = 'Metoprolol')
	#--------------------------------------------------------
	# MMI/Gelbe Liste
	#test_MMI_interface()
	#test_MMI_file()
	#test_mmi_switch_to()
	#test_mmi_let_user_select_drugs()
	#test_mmi_import_substances()
	#test_mmi_import_drugs()

	# FreeDiams
	#test_fd_switch_to()
	#test_fd_show_interactions()

	# generic
	#test_interaction_check()
	#test_create_substance_intake()
	#test_show_components()
	#test_get_consumable_substances()

	test_drug2renal_insufficiency_url()
#============================================================
