# -*- coding: utf-8 -*-
"""Medication handling code.

license: GPL v2 or later
"""
#============================================================
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

import sys
import logging
import csv
import io
import os
import re as regex
import subprocess
import decimal
from xml.etree import ElementTree as etree
import datetime as pydt


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain('gnumed')
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
from Gnumed.business import gmCoding
from Gnumed.business import gmEMRStructItems


_log = logging.getLogger('gm.meds')

#_ = lambda x:x
DEFAULT_MEDICATION_HISTORY_EPISODE = _('Medication history')

#============================================================
def _on_substance_intake_modified():
	"""Always relates to the active patient."""
	gmHooks.run_hook_script(hook = u'after_substance_intake_modified')

gmDispatcher.connect(_on_substance_intake_modified, u'clin.substance_intake_mod_db')

#============================================================
def drug2renal_insufficiency_url(search_term=None):

	if search_term is None:
		return u'http://www.dosing.de'

	if isinstance(search_term, basestring):
		if search_term.strip() == u'':
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

	elif isinstance(search_term, cDrugComponent):
		names.append(search_term['substance'])
		if search_term['atc_brand'] is not None:
			terms.append(search_term['atc_brand'])
		if search_term['atc_substance'] is not None:
			terms.append(search_term['atc_substance'])

	elif isinstance(search_term, cConsumableSubstance):
		names.append(search_term['description'])
		if search_term['atc_code'] is not None:
			terms.append(search_term['atc_code'])

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

		self.csv_file = io.open(filename, mode = 'rt', encoding = cGelbeListeCSVFile.default_encoding)

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

	version = u'FreeDiams interface'
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
		# this file can be modified by the user as needed:
		self.__fd4gm_config_file = os.path.join(paths.home_dir, '.gnumed', 'freediams4gm.conf')
		_log.debug('FreeDiams config file for GNUmed use: %s', self.__fd4gm_config_file)

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
		return gmCoding.create_data_source (
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
		if os.name == 'nt':
			blocking = True
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
			r'C:\Program Files (x86)\FreeDiams\freediams.exe',
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
			substance_intakes = emr.get_current_medications (
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
			<Drug u1="%s" u2="" old="%s" u3="" db="%s">		<!-- "old" needs to be the same as "u1" if not known -->
				<DrugName>%s</DrugName>						<!-- just for identification when reading XML files -->
			</Drug>
		</Prescription>"""

		last_db_id = u'CA_HCDPD'
		for intake in intakes_pooled_by_brand.values():
			last_db_id = gmTools.xml_escape_string(text = intake['external_code_type_brand'].replace(u'FreeDiams::', u'').split(u'::')[0])
			drug_snippets.append(drug_snippet % (
				gmTools.xml_escape_string(text = intake['external_code_brand'].strip()),
				gmTools.xml_escape_string(text = intake['external_code_brand'].strip()),
				last_db_id,
				gmTools.xml_escape_string(text = intake['brand'].strip())
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
			<Drug u1="-1" u2="" old="" u3="" db="">
				<DrugName>%s</DrugName>
			</Drug>
			<Dose Note="%s" IsTextual="true" IsAld="false"/>
		</Prescription>"""
#				<DrugUidName></DrugUidName>
#				<DrugForm></DrugForm>
#				<DrugRoute></DrugRoute>
#				<DrugStrength/>

		for intake in non_fd_substance_intakes:
			drug_name = u'%s %s%s (%s)' % (
				intake['substance'],
				intake['amount'],
				intake['unit'],
				intake['preparation']
			)
			drug_snippets.append(drug_snippet % (
				gmTools.xml_escape_string(text = drug_name.strip()),
				gmTools.xml_escape_string(text = gmTools.coalesce(intake['schedule'], u''))
			))

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
			drug_snippets.append(drug_snippet % (
				gmTools.xml_escape_string(text = drug_name.strip()),
				gmTools.xml_escape_string(text = gmTools.coalesce(comps[0]['schedule'], u''))
			))

		# assemble XML file
		xml = u"""<?xml version = "1.0" encoding = "UTF-8"?>
<!DOCTYPE FreeMedForms>
<FreeDiams>
	<FullPrescription version="0.7.2">
		%s
	</FullPrescription>
</FreeDiams>
"""

		xml_file = io.open(self.__fd2gm_filename, mode = 'wt', encoding = 'utf8')
		xml_file.write(xml % u'\n\t\t'.join(drug_snippets))
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

		xml_file = io.open(self.__gm2fd_filename, mode = 'wt', encoding = 'utf8')

		xml = u"""<?xml version="1.0" encoding="UTF-8"?>

<FreeDiams_In version="0.5.0">
	<EMR name="GNUmed" uid="unused"/>
	<ConfigFile value="%s"/>
	<ExchangeOut value="%s" format="xml"/>
	<!-- <DrugsDatabase uid="can be set to a specific DB"/> -->
	<Ui editmode="%s" blockPatientDatas="1"/>
	%%s
</FreeDiams_In>
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
		inn_allgs = [
			a['allergene'] for a in allgs if ((a['allergene'] is not None) and (a['type'] == u'allergy'))
		]
		inn_sens = [
			a['allergene'] for a in allgs if ((a['allergene'] is not None) and (a['type'] == u'sensitivity'))
		]
		# this is rather fragile: FreeDiams won't know what type of UID this is
		# (but it will assume it is of the type of the drug database in use)
		# but eventually FreeDiams puts all drugs into one database :-)
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
		<!-- can be <7 characters class codes: -->
		<ATCAllergies value="%s"/>
		<ATCIntolerances value="%s"/>

		<InnAllergies value="%s"/>
		<InnIntolerances value="%s"/>

		<DrugsUidAllergies value="%s"/>
		<DrugsUidIntolerances value="%s"/>

		<!--
			# FIXME: search by LOINC code and add (as soon as supported by FreeDiams ...)
			<Creatinine value="12" unit="mg/l or mmol/l"/>
			<Weight value="70" unit="kg or pd" />
			<WeightInGrams value="70"/>
			<Height value="170" unit="cm or "/>
			<HeightInCentimeters value="170"/>
			<ICD10 value="J11.0;A22;Z23"/>
		-->

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

		_log.debug('importing FreeDiams prescription information from [%s]', filename)

		fd2gm_xml = etree.ElementTree()
		fd2gm_xml.parse(filename)

		pdfs = fd2gm_xml.findall('ExtraDatas/Printed')
		if len(pdfs) == 0:
			_log.debug('no PDF prescription files listed')
			return

		fd_filenames = []
		for pdf in pdfs:
			fd_filenames.append(pdf.attrib['file'])

		_log.debug('listed PDF prescription files: %s', fd_filenames)

		docs = self.patient.get_document_folder()
		emr = self.patient.get_emr()

		prescription = docs.add_prescription (
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
			part['obj_comment'] = _('copy of printed prescription')
			part.save()

		xml_part = parts[-1]
		xml_part['filename'] = u'freediams-prescription.xml'
		xml_part['obj_comment'] = _('prescription data')
		xml_part.save()

		# are we the intended reviewer ?
		from Gnumed.business.gmStaff import gmCurrentProvider
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

		xml_version = fd2gm_xml.find('FullPrescription').attrib['version']
		_log.debug('fd2gm file version: %s', xml_version)

		if xml_version in ['0.6.0', '0.7.2']:
			return self.__import_fd2gm_file_as_drugs_0_6_0(fd2gm_xml = fd2gm_xml, pk_data_source = data_src_pk)

		return self.__import_fd2gm_file_as_drugs_0_5(fd2gm_xml = fd2gm_xml, pk_data_source = data_src_pk)
	#--------------------------------------------------------
	def __import_fd2gm_file_as_drugs_0_6_0(self, fd2gm_xml=None, pk_data_source=None):

#		drug_id_name = db_def.attrib['drugUidName']
		fd_xml_prescriptions = fd2gm_xml.findall('FullPrescription/Prescription')

		self.__imported_drugs = []
		for fd_xml_prescription in fd_xml_prescriptions:
			drug_uid = fd_xml_prescription.find('Drug').attrib['u1'].strip()
			if drug_uid == u'-1':
				_log.debug('skipping textual drug')
				continue
			drug_db =  fd_xml_prescription.find('Drug').attrib['db'].strip()
			drug_uid_name = fd_xml_prescription.find('Drug/DrugUidName').text.strip()
			#drug_uid_name = u'<%s>' % drug_db
			drug_name = fd_xml_prescription.find('Drug/DrugName').text.replace(', )', ')').strip()
			drug_form = fd_xml_prescription.find('Drug/DrugForm').text.strip()
#			drug_atc = fd_xml_prescription.find('DrugATC')
#			if drug_atc is None:
#				drug_atc = u''
#			else:
#				if drug_atc.text is None:
#					drug_atc = u''
#				else:
#					drug_atc = drug_atc.text.strip()

			# create new branded drug
			new_drug = create_branded_drug(brand_name = drug_name, preparation = drug_form, return_existing = True)
			self.__imported_drugs.append(new_drug)
			new_drug['is_fake_brand'] = False
#			new_drug['atc'] = drug_atc
			new_drug['external_code_type'] = u'FreeDiams::%s::%s' % (drug_db, drug_uid_name)
			new_drug['external_code'] = drug_uid
			new_drug['pk_data_source'] = pk_data_source
			new_drug.save()

			# parse XML for composition records
			fd_xml_components = fd_xml_prescription.getiterator('Composition')
			comp_data = {}
			for fd_xml_comp in fd_xml_components:

				data = {}

				xml_strength = fd_xml_comp.attrib['strength'].strip()
				amount = regex.match(r'^\d+[.,]{0,1}\d*', xml_strength)
				if amount is None:
					amount = 99999
				else:
					amount = amount.group()
				data['amount'] = amount

				#unit = regex.sub(r'\d+[.,]{0,1}\d*', u'', xml_strength).strip()
				unit = (xml_strength[len(amount):]).strip()
				if unit == u'':
					unit = u'*?*'
				data['unit'] = unit

				# hopefully, FreeDiams gets their act together, eventually:
				atc = regex.match(r'[A-Za-z]\d\d[A-Za-z]{2}\d\d', fd_xml_comp.attrib['atc'].strip())
				if atc is None:
					data['atc'] = None
				else:
					atc = atc.group()
				data['atc'] = atc

				molecule_name = fd_xml_comp.attrib['molecularName'].strip()
				if molecule_name != u'':
					create_substance_dose(substance = molecule_name, atc = atc, amount = amount, unit = unit)
				data['molecule_name'] = molecule_name

				inn_name = fd_xml_comp.attrib['inn'].strip()
				if inn_name != u'':
					create_substance_dose(substance = inn_name, atc = atc, amount = amount, unit = unit)
				#data['inn_name'] = molecule_name
				data['inn_name'] = inn_name

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
					# normalize ATC
					if old_data['atc'] == u'':
						old_data['atc'] = data['atc']
					if data['atc'] == u'':
						data['atc'] = old_data['atc']
					# FT: transformed form
					# SA: active substance
					# it would be preferable to use the SA record because that's what's *actually*
					# contained in the drug, however FreeDiams does not list the amount thereof
					# (rather that of the INN)
					# FT and SA records of the same component carry the same nature_ID
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
					atc = data['atc'],
					amount = data['amount'],
					unit = data['unit']
				)
	#--------------------------------------------------------
	def __import_fd2gm_file_as_drugs_0_5(self, fd2gm_xml=None, pk_data_source=None):

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
			new_drug['pk_data_source'] = pk_data_source
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
					create_substance_dose(substance = molecule_name, atc = None, amount = amount, unit = unit)
				data['molecule_name'] = molecule_name

				inn_name = fd_xml_comp.attrib['inn'].strip()
				if inn_name != u'':
					create_substance_dose(substance = inn_name, atc = None, amount = amount, unit = unit)
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

		self.default_csv_filename = os.path.join(paths.tmp_dir, 'rezept.txt')
		self.default_csv_filename_arg = paths.tmp_dir
		self.interactions_filename = os.path.join(paths.tmp_dir, 'gm2mmi.bdt')
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
		except Exception:
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
			version_file = io.open(self.data_date_filename, mode = 'rt', encoding = 'utf8')
		except Exception:
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

		return gmCoding.create_data_source (
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

		if os.name == 'nt':
			blocking = True
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
				new_substances.append(create_substance_dose(substance = wirkstoff, atc = atc, amount = amount, unit = unit))

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
				new_substances.append(create_substance_dose(substance = wirkstoff, atc = atc, amount = amount, unit = unit))

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

		bdt_file = io.open(self.interactions_filename, mode = 'wt', encoding = cGelbeListeWindowsInterface.default_encoding)

		for pzn in drug_ids_list:
			pzn = pzn.strip()
			lng = cGelbeListeWindowsInterface.bdt_line_base_length + len(pzn)
			bdt_file.write(cGelbeListeWindowsInterface.bdt_line_template % (lng, pzn))

		bdt_file.close()

		self.switch_to_frontend(blocking = True)
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
			csv_file = io.open(filename, mode = 'rt', encoding = 'latin1')						# FIXME: encoding correct ?
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
_SQL_get_substance = u"SELECT *, xmin FROM ref.substance WHERE %s"

class cSubstance(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = _SQL_get_substance % u"pk = %s"
	_cmds_store_payload = [
		u"""UPDATE ref.substance SET
				description = %(description)s,
				atc = gm.nullify_empty_string(%(atc)s),
				intake_instructions = gm.nullify_empty_string(%(intake_instructions)s)
			WHERE
				pk = %(pk)s
					AND
				xmin = %(xmin)s
			RETURNING
				xmin
		"""
	]
	_updatable_fields = [
		u'description',
		u'atc',
		u'intake_instructions'
	]
	#--------------------------------------------------------
	def format(self, left_margin=0):
		return (u' ' * left_margin) + u'%s: %s%s%s' % (
			_('Substance'),
			self._payload[self._idx['description']],
			gmTools.coalesce(self._payload[self._idx['atc']], u'', u' [%s]'),
			gmTools.coalesce(self._payload[self._idx['intake_instructions']], u'', _(u'\n Instructions: %s'))
		)

	#--------------------------------------------------------
	def save_payload(self, conn=None):
		success, data = super(self.__class__, self).save_payload(conn = conn)

		if not success:
			return (success, data)

		if self._payload[self._idx['atc']] is not None:
			atc = self._payload[self._idx['atc']].strip()
			if atc != u'':
				gmATC.propagate_atc (
					substance = self._payload[self._idx['description']].strip(),
					atc = atc
				)

		return (success, data)
	#--------------------------------------------------------
	def exists_as_intake(self, pk_patient=None):
		return substance_intake_exists (
			pk_substance = self.pk_obj,
			pk_identity = pk_patient
		)

	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_is_in_use_by_patients(self):
		cmd = u"""
			SELECT EXISTS (
				SELECT 1
				FROM clin.v_substance_intakes
				WHERE pk_substance = %(pk)s
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
				FROM ref.v_drug_components
				WHERE pk_substance = %(pk)s
				LIMIT 1
			)"""
		args = {'pk': self.pk_obj}

		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		return rows[0][0]

	is_drug_component = property(_get_is_drug_component, lambda x:x)

#------------------------------------------------------------
def get_substances(order_by=None):
	if order_by is None:
		order_by = u'true'
	else:
		order_by = u'true ORDER BY %s' % order_by
	cmd = _SQL_get_substance % order_by
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = True)
	return [ cSubstance(row = {'data': r, 'idx': idx, 'pk_field': 'pk'}) for r in rows ]

#------------------------------------------------------------
def create_substance(substance=None, atc=None):
	if atc is not None:
		atc = atc.strip()

	args = {
		'desc': substance.strip(),
		'atc': atc
	}
	cmd = u"SELECT pk FROM ref.substance WHERE lower(description) = lower(%(desc)s)"
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])

	if len(rows) == 0:
		cmd = u"""
			INSERT INTO ref.substance (description, atc) VALUES (
				%(desc)s,
				gm.nullify_empty_string(%(atc)s)
			) RETURNING pk"""
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True, get_col_idx = False)

	gmATC.propagate_atc(substance = substance, atc = atc)

	return cSubstance(aPK_obj = rows[0]['pk'])

#------------------------------------------------------------
def create_substance_by_atc(substance=None, atc=None):

	if atc is None:
		raise ValueError('<atc> must be supplied')
	atc = atc.strip()
	if atc == u'':
		raise ValueError('<atc> cannot be empty: [%s]', atc)
	args = {
		'desc': substance.strip(),
		'atc': atc
	}
	cmd = u"""
		INSERT INTO ref.substance (description, atc)
			SELECT
				%(desc)s,
				%(atc)s
			WHERE NOT EXISTS (
				SELECT 1 FROM ref.substance WHERE atc = %(atc)s
			)
		RETURNING pk"""
	rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True, get_col_idx = False)
	if len(rows) == 0:
		cmd = u"SELECT pk FROM ref.substance WHERE atc = %(atc)s LIMIT 1"
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])

	return cSubstance(aPK_obj = rows[0]['pk'])

#------------------------------------------------------------
def delete_substance(pk_substance=None):
	args = {'pk': pk_substance}
	cmd = u"""
		DELETE FROM ref.substance WHERE
			pk = %(pk)s
				AND
			-- must not currently be used with a patient
			NOT EXISTS (
				SELECT 1 FROM clin.v_substance_intakes
				WHERE pk_substance = %(pk)s
				LIMIT 1
			)
				AND
			-- must not currently have doses defined for it
			NOT EXISTS (
				SELECT 1 FROM ref.dose
				WHERE fk_substance = %(pk)s
				LIMIT 1
			)
	"""
	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
	return True

#------------------------------------------------------------
class cSubstanceMatchProvider(gmMatchProvider.cMatchProvider_SQL2):

	_pattern = regex.compile(r'^\D+\s*\d+$', regex.UNICODE | regex.LOCALE)

	_normal_query = u"""
		SELECT
			data,
			field_label,
			list_label,
			rank
		FROM ((
			-- first: substance intakes which match
			SELECT
				pk_substance AS data,
				(description || ' ' || amount || ' ' || unit) AS field_label,
				(description || ' ' || amount || ' ' || unit || ' (%s)') AS list_label,
				1 AS rank
			FROM (
				SELECT DISTINCT ON (description, amount, unit)
					pk_substance,
					substance AS description,
					amount,
					unit
				FROM clin.v_nonbrand_intakes
			) AS normalized_intakes
			WHERE description %%(fragment_condition)s
		) UNION ALL (
			-- consumable substances which match - but are not intakes - are second
			SELECT
				pk AS data,
				(description || ' ' || amount || ' ' || unit) AS field_label,
				(description || ' ' || amount || ' ' || unit) AS list_label,
				2 AS rank
			FROM ref.consumable_substance
			WHERE
				description %%(fragment_condition)s
					AND
				pk NOT IN (
					SELECT fk_substance
					FROM clin.substance_intake
					WHERE fk_substance IS NOT NULL
				)
		)) AS candidates
		ORDER BY rank, list_label
		LIMIT 50""" % _('in use')

	_regex_query = 	u"""
		SELECT
			data,
			field_label,
			list_label,
			rank
		FROM ((
			SELECT
				pk_substance AS data,
				(description || ' ' || amount || ' ' || unit) AS field_label,
				(description || ' ' || amount || ' ' || unit || ' (%s)') AS list_label,
				1 AS rank
			FROM (
				SELECT DISTINCT ON (description, amount, unit)
					pk_substance,
					substance AS description,
					amount,
					unit
				FROM clin.v_nonbrand_intakes
			) AS normalized_intakes
			WHERE
				%%(fragment_condition)s
		) UNION ALL (
			-- matching substances which are not in intakes
			SELECT
				pk AS data,
				(description || ' ' || amount || ' ' || unit) AS field_label,
				(description || ' ' || amount || ' ' || unit) AS list_label,
				2 AS rank
			FROM ref.consumable_substance
			WHERE
				%%(fragment_condition)s
					AND
				pk NOT IN (
					SELECT fk_substance
					FROM clin.substance_intake
					WHERE fk_substance IS NOT NULL
				)
		)) AS candidates
		ORDER BY rank, list_label
		LIMIT 50""" % _('in use')

	#--------------------------------------------------------
	def getMatchesByPhrase(self, aFragment):
		"""Return matches for aFragment at start of phrases."""

		if cSubstanceMatchProvider._pattern.match(aFragment):
			self._queries = [cSubstanceMatchProvider._regex_query]
			fragment_condition = """description ILIKE %(desc)s
				AND
			amount::text ILIKE %(amount)s"""
			self._args['desc'] = u'%s%%' % regex.sub(r'\s*\d+$', u'', aFragment)
			self._args['amount'] = u'%s%%' % regex.sub(r'^\D+\s*', u'', aFragment)
		else:
			self._queries = [cSubstanceMatchProvider._normal_query]
			fragment_condition = u"ILIKE %(fragment)s"
			self._args['fragment'] = u"%s%%" % aFragment

		return self._find_matches(fragment_condition)
	#--------------------------------------------------------
	def getMatchesByWord(self, aFragment):
		"""Return matches for aFragment at start of words inside phrases."""

		if cSubstanceMatchProvider._pattern.match(aFragment):
			self._queries = [cSubstanceMatchProvider._regex_query]

			desc = regex.sub(r'\s*\d+$', u'', aFragment)
			desc = gmPG2.sanitize_pg_regex(expression = desc, escape_all = False)

			fragment_condition = """description ~* %(desc)s
				AND
			amount::text ILIKE %(amount)s"""

			self._args['desc'] = u"( %s)|(^%s)" % (desc, desc)
			self._args['amount'] = u'%s%%' % regex.sub(r'^\D+\s*', u'', aFragment)
		else:
			self._queries = [cSubstanceMatchProvider._normal_query]
			fragment_condition = u"~* %(fragment)s"
			aFragment = gmPG2.sanitize_pg_regex(expression = aFragment, escape_all = False)
			self._args['fragment'] = u"( %s)|(^%s)" % (aFragment, aFragment)

		return self._find_matches(fragment_condition)
	#--------------------------------------------------------
	def getMatchesBySubstr(self, aFragment):
		"""Return matches for aFragment as a true substring."""

		if cSubstanceMatchProvider._pattern.match(aFragment):
			self._queries = [cSubstanceMatchProvider._regex_query]
			fragment_condition = """description ILIKE %(desc)s
				AND
			amount::text ILIKE %(amount)s"""
			self._args['desc'] = u'%%%s%%' % regex.sub(r'\s*\d+$', u'', aFragment)
			self._args['amount'] = u'%s%%' % regex.sub(r'^\D+\s*', u'', aFragment)
		else:
			self._queries = [cSubstanceMatchProvider._normal_query]
			fragment_condition = u"ILIKE %(fragment)s"
			self._args['fragment'] = u"%%%s%%" % aFragment

		return self._find_matches(fragment_condition)

#------------------------------------------------------------
class cBrandOrSubstanceMatchProvider(gmMatchProvider.cMatchProvider_SQL2):

	# by brand name
	_query_brand_by_name = u"""
		SELECT
			ARRAY[1, pk]::INTEGER[]
				AS data,
			(description || ' (' || preparation || ')' || coalesce(' [' || atc_code || ']', ''))
				AS list_label,
			(description || ' (' || preparation || ')' || coalesce(' [' || atc_code || ']', ''))
				AS field_label,
			1 AS rank
		FROM ref.branded_drug
		WHERE description %(fragment_condition)s
		LIMIT 50
	"""
	_query_brand_by_name_and_strength = u"""
		SELECT
			ARRAY[1, pk_brand]::INTEGER[]
				AS data,
			(brand || ' (' || preparation || %s || amount || unit || ' ' || substance || ')' || coalesce(' [' || atc_brand || ']', ''))
				AS list_label,
			(brand || ' (' || preparation || %s || amount || unit || ' ' || substance || ')' || coalesce(' [' || atc_brand || ']', ''))
				AS field_label,
			1 AS rank
		FROM
			(SELECT *, brand AS description FROM ref.v_drug_components) AS _components
		WHERE %%(fragment_condition)s
		LIMIT 50
	""" % (
		_('w/'),
		_('w/')
	)

	# by component
	_query_component_by_name = u"""
		SELECT
			ARRAY[3, r_vdc1.pk_component]::INTEGER[]
				AS data,
			(r_vdc1.substance || ' ' || r_vdc1.amount || r_vdc1.unit || ' ' || r_vdc1.preparation || ' ('
				|| r_vdc1.brand || ' ['
					|| (
						SELECT array_to_string(array_agg(r_vdc2.amount), ' / ')
						FROM ref.v_drug_components r_vdc2
						WHERE r_vdc2.pk_brand = r_vdc1.pk_brand
					)
				|| ']'
			|| ')'
			)	AS field_label,
			(r_vdc1.substance || ' ' || r_vdc1.amount || r_vdc1.unit || ' ' || r_vdc1.preparation || ' ('
				|| r_vdc1.brand || ' ['
					|| (
						SELECT array_to_string(array_agg(r_vdc2.amount), ' / ')
						FROM ref.v_drug_components r_vdc2
						WHERE r_vdc2.pk_brand = r_vdc1.pk_brand
					)
				|| ']'
			|| ')'
			)	AS list_label,
			1 AS rank
		FROM
			(SELECT *, brand AS description FROM ref.v_drug_components) AS r_vdc1
		WHERE
			r_vdc1.substance %(fragment_condition)s
		LIMIT 50"""
	_query_component_by_name_and_strength = u"""
		SELECT
			ARRAY[3, r_vdc1.pk_component]::INTEGER[]
				AS data,
			(r_vdc1.substance || ' ' || r_vdc1.amount || r_vdc1.unit || ' ' || r_vdc1.preparation || ' ('
				|| r_vdc1.brand || ' ['
					|| (
						SELECT array_to_string(array_agg(r_vdc2.amount), ' / ')
						FROM ref.v_drug_components r_vdc2
						WHERE r_vdc2.pk_brand = r_vdc1.pk_brand
					)
				|| ']'
			|| ')'
			)	AS field_label,
			(r_vdc1.substance || ' ' || r_vdc1.amount || r_vdc1.unit || ' ' || r_vdc1.preparation || ' ('
				|| r_vdc1.brand || ' ['
					|| (
						SELECT array_to_string(array_agg(r_vdc2.amount), ' / ')
						FROM ref.v_drug_components r_vdc2
						WHERE r_vdc2.pk_brand = r_vdc1.pk_brand
					)
				|| ']'
			|| ')'
			)	AS list_label,
			1 AS rank
		FROM (SELECT *, substance AS description FROM ref.v_drug_components) AS r_vdc1
		WHERE
			%(fragment_condition)s
		ORDER BY list_label
		LIMIT 50"""

	# by substance name
	_query_substance_by_name = u"""
		SELECT
			data,
			field_label,
			list_label,
			rank
		FROM ((
			-- first: substance intakes which match, because we tend to reuse them often
			SELECT
				ARRAY[2, pk_substance]::INTEGER[] AS data,
				(description || ' ' || amount || ' ' || unit) AS field_label,
				(description || ' ' || amount || ' ' || unit || ' (%s)') AS list_label,
				1 AS rank
			FROM (
				SELECT DISTINCT ON (description, amount, unit)
					pk_substance,
					substance AS description,
					amount,
					unit
				FROM clin.v_nonbrand_intakes
			) AS normalized_intakes
			WHERE description %%(fragment_condition)s

		) UNION ALL (

			-- second: consumable substances which match but are not intakes
			SELECT
				ARRAY[2, pk]::INTEGER[] AS data,
				(description || ' ' || amount || ' ' || unit) AS field_label,
				(description || ' ' || amount || ' ' || unit) AS list_label,
				2 AS rank
			FROM ref.consumable_substance
			WHERE
				description %%(fragment_condition)s
					AND
				pk NOT IN (
					SELECT fk_substance
					FROM clin.substance_intake
					WHERE fk_substance IS NOT NULL
				)
		)) AS candidates
		--ORDER BY rank, list_label
		LIMIT 50""" % _('in use')
	_query_substance_by_name_and_strength = 	u"""
		SELECT
			data,
			field_label,
			list_label,
			rank
		FROM ((
			SELECT
				ARRAY[2, pk_substance]::INTEGER[] AS data,
				(description || ' ' || amount || ' ' || unit) AS field_label,
				(description || ' ' || amount || ' ' || unit || ' (%s)') AS list_label,
				1 AS rank
			FROM (
				SELECT DISTINCT ON (description, amount, unit)
					pk_substance,
					substance AS description,
					amount,
					unit
				FROM clin.v_nonbrand_intakes
			) AS normalized_intakes
			WHERE
				%%(fragment_condition)s

		) UNION ALL (

			-- matching substances which are not in intakes
			SELECT
				ARRAY[2, pk]::INTEGER[] AS data,
				(description || ' ' || amount || ' ' || unit) AS field_label,
				(description || ' ' || amount || ' ' || unit) AS list_label,
				2 AS rank
			FROM ref.consumable_substance
			WHERE
				%%(fragment_condition)s
					AND
				pk NOT IN (
					SELECT fk_substance
					FROM clin.substance_intake
					WHERE fk_substance IS NOT NULL
				)
		)) AS candidates
		--ORDER BY rank, list_label
		LIMIT 50""" % _('in use')

	_pattern = regex.compile(r'^\D+\s*\d+$', regex.UNICODE | regex.LOCALE)

	_master_query = u"""
		SELECT
			data, field_label, list_label, rank
		FROM ((%s) UNION (%s) UNION (%s))
			AS _union
		ORDER BY rank, list_label
		LIMIT 50
	"""
	#--------------------------------------------------------
	def getMatchesByPhrase(self, aFragment):
		"""Return matches for aFragment at start of phrases."""

		if cBrandOrSubstanceMatchProvider._pattern.match(aFragment):
			self._queries = [
				cBrandOrSubstanceMatchProvider._master_query % (
					cBrandOrSubstanceMatchProvider._query_brand_by_name_and_strength,
					cBrandOrSubstanceMatchProvider._query_substance_by_name_and_strength,
					cBrandOrSubstanceMatchProvider._query_component_by_name_and_strength
				)
			]
			#self._queries = [cBrandOrSubstanceMatchProvider._query_substance_by_name_and_strength]
			fragment_condition = """description ILIKE %(desc)s
				AND
			amount::text ILIKE %(amount)s"""
			self._args['desc'] = u'%s%%' % regex.sub(r'\s*\d+$', u'', aFragment)
			self._args['amount'] = u'%s%%' % regex.sub(r'^\D+\s*', u'', aFragment)
		else:
			self._queries = [
				cBrandOrSubstanceMatchProvider._master_query % (
					cBrandOrSubstanceMatchProvider._query_brand_by_name,
					cBrandOrSubstanceMatchProvider._query_substance_by_name,
					cBrandOrSubstanceMatchProvider._query_component_by_name
				)
			]
			#self._queries = [cBrandOrSubstanceMatchProvider._query_substance_by_name]
			fragment_condition = u"ILIKE %(fragment)s"
			self._args['fragment'] = u"%s%%" % aFragment

		return self._find_matches(fragment_condition)
	#--------------------------------------------------------
	def getMatchesByWord(self, aFragment):
		"""Return matches for aFragment at start of words inside phrases."""

		if cBrandOrSubstanceMatchProvider._pattern.match(aFragment):
			self._queries = [
				cBrandOrSubstanceMatchProvider._master_query % (
					cBrandOrSubstanceMatchProvider._query_brand_by_name_and_strength,
					cBrandOrSubstanceMatchProvider._query_substance_by_name_and_strength,
					cBrandOrSubstanceMatchProvider._query_component_by_name_and_strength
				)
			]
			#self._queries = [cBrandOrSubstanceMatchProvider._query_substance_by_name_and_strength]

			desc = regex.sub(r'\s*\d+$', u'', aFragment)
			desc = gmPG2.sanitize_pg_regex(expression = desc, escape_all = False)

			fragment_condition = """description ~* %(desc)s
				AND
			amount::text ILIKE %(amount)s"""

			self._args['desc'] = u"( %s)|(^%s)" % (desc, desc)
			self._args['amount'] = u'%s%%' % regex.sub(r'^\D+\s*', u'', aFragment)
		else:
			self._queries = [
				cBrandOrSubstanceMatchProvider._master_query % (
					cBrandOrSubstanceMatchProvider._query_brand_by_name,
					cBrandOrSubstanceMatchProvider._query_substance_by_name,
					cBrandOrSubstanceMatchProvider._query_component_by_name
				)
			]
			#self._queries = [cBrandOrSubstanceMatchProvider._query_substance_by_name]
			fragment_condition = u"~* %(fragment)s"
			aFragment = gmPG2.sanitize_pg_regex(expression = aFragment, escape_all = False)
			self._args['fragment'] = u"( %s)|(^%s)" % (aFragment, aFragment)

		return self._find_matches(fragment_condition)
	#--------------------------------------------------------
	def getMatchesBySubstr(self, aFragment):
		"""Return matches for aFragment as a true substring."""

		if cBrandOrSubstanceMatchProvider._pattern.match(aFragment):
			self._queries = [
				cBrandOrSubstanceMatchProvider._master_query % (
					cBrandOrSubstanceMatchProvider._query_brand_by_name_and_strength,
					cBrandOrSubstanceMatchProvider._query_substance_by_name_and_strength,
					cBrandOrSubstanceMatchProvider._query_component_by_name_and_strength
				)
			]
			#self._queries = [cBrandOrSubstanceMatchProvider._query_substance_by_name_and_strength]
			fragment_condition = """description ILIKE %(desc)s
				AND
			amount::text ILIKE %(amount)s"""
			self._args['desc'] = u'%%%s%%' % regex.sub(r'\s*\d+$', u'', aFragment)
			self._args['amount'] = u'%s%%' % regex.sub(r'^\D+\s*', u'', aFragment)
		else:
			self._queries = [
				cBrandOrSubstanceMatchProvider._master_query % (
					cBrandOrSubstanceMatchProvider._query_brand_by_name,
					cBrandOrSubstanceMatchProvider._query_substance_by_name,
					cBrandOrSubstanceMatchProvider._query_component_by_name
				)
			]
			#self._queries = [cBrandOrSubstanceMatchProvider._query_substance_by_name]
			fragment_condition = u"ILIKE %(fragment)s"
			self._args['fragment'] = u"%%%s%%" % aFragment

		return self._find_matches(fragment_condition)

#============================================================
# substance intakes
#------------------------------------------------------------
_SQL_get_substance_intake = u"SELECT * FROM clin.v_substance_intakes WHERE %s"

class cSubstanceIntakeEntry(gmBusinessDBObject.cBusinessDBObject):
	"""Represents a substance currently taken by a patient."""

	_cmd_fetch_payload = _SQL_get_substance_intake % 'pk_substance_intake = %s'
	_cmds_store_payload = [
		u"""UPDATE clin.substance_intake SET
				-- if .comment_on_start = '?' then .started will be mapped to NULL
				-- in the view, also, .started CANNOT be NULL any other way so far,
				-- so do not attempt to set .clin_when if .started is NULL
				clin_when = (
					CASE
						WHEN %(started)s IS NULL THEN clin_when
						ELSE %(started)s
					END
				)::timestamp with time zone,
				comment_on_start = gm.nullify_empty_string(%(comment_on_start)s),
				discontinued = %(discontinued)s,
				discontinue_reason = gm.nullify_empty_string(%(discontinue_reason)s),
				schedule = gm.nullify_empty_string(%(schedule)s),
				aim = gm.nullify_empty_string(%(aim)s),
				narrative = gm.nullify_empty_string(%(notes)s),
				intake_is_approved_of = %(intake_is_approved_of)s,
				harmful_use_type = %(harmful_use_type)s,
				fk_episode = %(pk_episode)s,
				-- only used to document "last checked" such that
				-- .clin_when -> .started does not have to change meaning
				fk_encounter = %(pk_encounter)s,

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
		u'comment_on_start',
		u'discontinued',
		u'discontinue_reason',
		u'intake_is_approved_of',
		u'schedule',
		u'duration',
		u'aim',
		u'is_long_term',
		u'notes',
		u'pk_episode',
		u'pk_encounter',
		u'harmful_use_type'
	]

	#--------------------------------------------------------
	def format_maximum_information(self, patient=None):
		return self.format (
			single_line = False,
			show_all_brand_components = True,
			include_metadata = True,
			date_format = '%Y %b %d',
			include_instructions = True
		).split(u'\n')

	#--------------------------------------------------------
	def format(self, left_margin=0, date_format='%Y %b %d', single_line=True, allergy=None, show_all_brand_components=False, include_metadata=True, include_instructions=False):

		# medication
		if self._payload[self._idx['harmful_use_type']] is None:
			if single_line:
				return self.format_as_single_line(left_margin = left_margin, date_format = date_format)
			return self.format_as_multiple_lines (
				left_margin = left_margin,
				date_format = date_format,
				allergy = allergy,
				show_all_brand_components = show_all_brand_components,
				include_instructions = include_instructions
			)

		# abuse
		if single_line:
			return self.format_as_single_line_abuse(left_margin = left_margin, date_format = date_format)

		return self.format_as_multiple_lines_abuse(left_margin = left_margin, date_format = date_format, include_metadata = include_metadata)

	#--------------------------------------------------------
	def format_as_single_line_abuse(self, left_margin=0, date_format='%Y %b %d'):
		return u'%s%s: %s (%s)' % (
			u' ' * left_margin,
			self._payload[self._idx['substance']],
			self.harmful_use_type_string,
			gmDateTime.pydt_strftime(self._payload[self._idx['last_checked_when']], '%b %Y')
		)

	#--------------------------------------------------------
	def format_as_single_line(self, left_margin=0, date_format='%Y %b %d'):

		if self._payload[self._idx['is_currently_active']]:
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
		else:
			duration = gmDateTime.pydt_strftime(self._payload[self._idx['discontinued']], date_format)

		line = u'%s%s (%s %s): %s %s%s %s (%s)' % (
			u' ' * left_margin,
			self.medically_formatted_start,
			gmTools.u_arrow2right,
			duration,
			self._payload[self._idx['substance']],
			self._payload[self._idx['amount']],
			self._payload[self._idx['unit']],
			self._payload[self._idx['preparation']],
			gmTools.bool2subst(self._payload[self._idx['is_currently_active']], _('ongoing'), _('inactive'), _('?ongoing'))
		)

		return line

	#--------------------------------------------------------
	def format_as_multiple_lines_abuse(self, left_margin=0, date_format='%Y %b %d', include_metadata=True):

		txt = u''
		if include_metadata:
			txt = _('Substance abuse entry                                              [#%s]\n') % self._payload[self._idx['pk_substance_intake']]
		txt += u' ' + _('Substance: %s [#%s]%s\n') % (
			self._payload[self._idx['substance']],
			self._payload[self._idx['pk_substance']],
			gmTools.coalesce(self._payload[self._idx['atc_substance']], u'', ' ATC %s')
		)
		txt += u' ' + _('Use type: %s\n') % self.harmful_use_type_string
		txt += u' ' + _('Last checked: %s\n') % gmDateTime.pydt_strftime(self._payload[self._idx['last_checked_when']], '%Y %b %d')
		if self._payload[self._idx['discontinued']] is not None:
			txt += _(' Discontinued %s\n') % (
				gmDateTime.pydt_strftime (
					self._payload[self._idx['discontinued']],
					format = date_format,
					accuracy = gmDateTime.acc_days
				)
			)
		txt += gmTools.coalesce(self._payload[self._idx['notes']], u'', _(' Notes: %s\n'))
		if include_metadata:
			txt += u'\n'
			txt += _(u'Revision: #%(row_ver)s, %(mod_when)s by %(mod_by)s.') % {
				'row_ver': self._payload[self._idx['row_version']],
				'mod_when': gmDateTime.pydt_strftime(self._payload[self._idx['modified_when']]),
				'mod_by': self._payload[self._idx['modified_by']]
			}

		return txt

	#--------------------------------------------------------
	def format_as_multiple_lines(self, left_margin=0, date_format='%Y %b %d', allergy=None, show_all_brand_components=False, include_instructions=False):

		txt = _('Substance intake entry (%s, %s)   [#%s]                     \n') % (
			gmTools.bool2subst (
				boolean = self._payload[self._idx['is_currently_active']],
				true_return = gmTools.bool2subst (
					boolean = self._payload[self._idx['seems_inactive']],
					true_return = _('active, needs check'),
					false_return = _('active'),
					none_return = _('assumed active')
				),
				false_return = _('inactive')
			),
			gmTools.bool2subst (
				boolean = self._payload[self._idx['intake_is_approved_of']],
				true_return = _('approved'),
				false_return = _('unapproved')
			),
			self._payload[self._idx['pk_substance_intake']]
		)

		if allergy is not None:
			certainty = gmTools.bool2subst(allergy['definite'], _('definite'), _('suspected'))
			txt += u'\n'
			txt += u' !! ---- Cave ---- !!\n'
			txt += u' %s (%s): %s (%s)\n' % (
				allergy['l10n_type'],
				certainty,
				allergy['descriptor'],
				gmTools.coalesce(allergy['reaction'], u'')[:40]
			)
			txt += u'\n'

		txt += u' ' + _('Substance: %s   [#%s]\n') % (self._payload[self._idx['substance']], self._payload[self._idx['pk_substance']])
		txt += u' ' + _('Preparation: %s\n') % self._payload[self._idx['preparation']]
		txt += u' ' + _('Amount per dose: %s %s') % (self._payload[self._idx['amount']], self._payload[self._idx['unit']])
		txt += u'\n'
		txt += gmTools.coalesce(self._payload[self._idx['atc_substance']], u'', _(' ATC (substance): %s\n'))

		txt += u'\n'

		txt += gmTools.coalesce (
			self._payload[self._idx['brand']],
			u'',
			_(' Brand name: %%s   [#%s]\n') % self._payload[self._idx['pk_brand']]
		)
		txt += gmTools.coalesce(self._payload[self._idx['atc_brand']], u'', _(' ATC (brand): %s\n'))
		if show_all_brand_components and (self._payload[self._idx['pk_brand']] is not None):
			brand = self.containing_drug
			if len(brand['pk_substances']) > 1:
				for comp in brand['components']:
					if comp.startswith(self._payload[self._idx['substance']] + u'::'):
						continue
					txt += _('  Other component: %s\n') % comp

		txt += u'\n'

		txt += gmTools.coalesce(self._payload[self._idx['schedule']], u'', _(' Regimen: %s\n'))

		if self._payload[self._idx['is_long_term']]:
			duration = u' %s %s' % (gmTools.u_arrow2right, gmTools.u_infinity)
		else:
			if self._payload[self._idx['duration']] is None:
				duration = u''
			else:
				duration = u' %s %s' % (gmTools.u_arrow2right, gmDateTime.format_interval(self._payload[self._idx['duration']], gmDateTime.acc_days))

		txt += _(' Started %s%s%s\n') % (
			self.medically_formatted_start,
			duration,
			gmTools.bool2subst(self._payload[self._idx['is_long_term']], _(' (long-term)'), _(' (short-term)'), u'')
		)

		if self._payload[self._idx['discontinued']] is not None:
			txt += _(' Discontinued %s\n') % (
				gmDateTime.pydt_strftime (
					self._payload[self._idx['discontinued']],
					format = date_format,
					accuracy = gmDateTime.acc_days
				)
			)
			txt += gmTools.coalesce(self._payload[self._idx['discontinue_reason']], u'', _(' Reason: %s\n'))

		txt += u'\n'

		txt += gmTools.coalesce(self._payload[self._idx['aim']], u'', _(' Aim: %s\n'))
		txt += gmTools.coalesce(self._payload[self._idx['episode']], u'', _(' Episode: %s\n'))
		txt += gmTools.coalesce(self._payload[self._idx['health_issue']], u'', _(' Health issue: %s\n'))
		txt += gmTools.coalesce(self._payload[self._idx['notes']], u'', _(' Advice: %s\n'))
		if self._payload[self._idx['intake_instructions']] is not None:
			txt = txt + u' '+ (_('Intake: %s') % self._payload[self._idx['intake_instructions']]) + u'\n'

		txt += u'\n'

		txt += _(u'Revision: #%(row_ver)s, %(mod_when)s by %(mod_by)s.') % {
			'row_ver': self._payload[self._idx['row_version']],
			'mod_when': gmDateTime.pydt_strftime(self._payload[self._idx['modified_when']]),
			'mod_by': self._payload[self._idx['modified_by']]
		}

		return txt

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
	def delete(self):
		return delete_substance_intake(substance = self._payload[self._idx['pk_substance_intake']])

	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_harmful_use_type_string(self):

		if self._payload[self._idx['harmful_use_type']] is None:
			return _('medication, not abuse')
		if self._payload[self._idx['harmful_use_type']] == 0:
			return _('no or non-harmful use')
		if self._payload[self._idx['harmful_use_type']] == 1:
			return _('presently harmful use')
		if self._payload[self._idx['harmful_use_type']] == 2:
			return _('presently addicted')
		if self._payload[self._idx['harmful_use_type']] == 3:
			return _('previously addicted')

	harmful_use_type_string = property(_get_harmful_use_type_string)

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
	def _get_medically_formatted_start(self):
		if self._payload[self._idx['comment_on_start']] == u'?':
			return u'?'

		start_prefix = u''
		if self._payload[self._idx['comment_on_start']] is not None:
			start_prefix = gmTools.u_almost_equal_to

		duration_taken = gmDateTime.pydt_now_here() - self._payload[self._idx['started']]

		three_months = pydt.timedelta(weeks = 13, days = 3)
		if duration_taken < three_months:
			return _('%s%s: %s ago%s') % (
				start_prefix,
				gmDateTime.pydt_strftime(self._payload[self._idx['started']], '%Y %b %d', u'utf8', gmDateTime.acc_days),
				gmDateTime.format_interval_medically(duration_taken),
				gmTools.coalesce(self._payload[self._idx['comment_on_start']], u'', u' (%s)')
			)

		five_years = pydt.timedelta(weeks = 265)
		if duration_taken < five_years:
			return _('%s%s: %s ago (%s)') % (
				start_prefix,
				gmDateTime.pydt_strftime(self._payload[self._idx['started']], '%Y %b', u'utf8', gmDateTime.acc_months),
				gmDateTime.format_interval_medically(duration_taken),
				gmTools.coalesce (
					self._payload[self._idx['comment_on_start']],
					gmDateTime.pydt_strftime(self._payload[self._idx['started']], '%b %d', u'utf8', gmDateTime.acc_days),
				)
			)

		return _('%s%s: %s ago (%s)') % (
			start_prefix,
			gmDateTime.pydt_strftime(self._payload[self._idx['started']], '%Y', u'utf8', gmDateTime.acc_years),
			gmDateTime.format_interval_medically(duration_taken),
			gmTools.coalesce (
				self._payload[self._idx['comment_on_start']],
				gmDateTime.pydt_strftime(self._payload[self._idx['started']], '%b %d', u'utf8', gmDateTime.acc_days),
			)
		)

	medically_formatted_start = property(_get_medically_formatted_start, lambda x:x)

	#--------------------------------------------------------
	def _get_medically_formatted_start_end(self):

		now = gmDateTime.pydt_now_here()

		if self._payload[self._idx['comment_on_start']] is None:
			start_prefix = u''
		else:
			start_prefix = gmTools.u_almost_equal_to

		# ongoing medication
		if self._payload[self._idx['discontinued']] is None:
			# calculate start string
			if self._payload[self._idx['started']] is None:
				start = gmTools.coalesce(self._payload[self._idx['comment_on_start']], u'?')
			else:
				started_ago = now - self._payload[self._idx['started']]
				three_months = pydt.timedelta(weeks = 13, days = 3)
				five_years = pydt.timedelta(weeks = 265)
				if started_ago < three_months:
					start = _('%s%s%s (%s ago)') % (
						start_prefix,
						gmDateTime.pydt_strftime(self._payload[self._idx['started']], format = '%Y %b %d', encoding = u'utf8', accuracy = gmDateTime.acc_days),
						gmTools.coalesce(self._payload[self._idx['comment_on_start']], u'', u' [%s]'),
						gmDateTime.format_interval_medically(started_ago)
					)
				elif started_ago < five_years:
					start = _('%s%s%s (%s ago, %s)') % (
						start_prefix,
						gmDateTime.pydt_strftime(self._payload[self._idx['started']], '%Y %b', u'utf8', gmDateTime.acc_months),
						gmTools.coalesce(self._payload[self._idx['comment_on_start']], u'', u' [%s]'),
						gmDateTime.format_interval_medically(started_ago),
						gmDateTime.pydt_strftime(self._payload[self._idx['started']], '%b %d', u'utf8', gmDateTime.acc_days)
					)
				else:
					start = _('%s%s%s (%s ago, %s)') % (
						start_prefix,
						gmDateTime.pydt_strftime(self._payload[self._idx['started']], '%Y', u'utf8', gmDateTime.acc_years),
						gmTools.coalesce(self._payload[self._idx['comment_on_start']], u'', u' [%s]'),
						gmDateTime.format_interval_medically(started_ago),
						gmDateTime.pydt_strftime(self._payload[self._idx['started']], '%b %d', u'utf8', gmDateTime.acc_days),
					)

			# calculate end string
			if self._payload[self._idx['is_long_term']]:
				end = u' %s %s' % (gmTools.u_arrow2right, gmTools.u_infinity)
				if self._payload[self._idx['duration']] is not None:
					duration = gmDateTime.format_interval(self._payload[self._idx['duration']], gmDateTime.acc_days)
					if self._payload[self._idx['started']] is None:
						planned_end_str = u''
					else:
						planned_end = self._payload[self._idx['started']] + self._payload[self._idx['duration']]
						if planned_end < now:
							planned_end_from_now_str = _(u'%s ago') % gmDateTime.format_interval(now - planned_end, gmDateTime.acc_days)
						else:
							planned_end_from_now_str = _(u'in %s') % gmDateTime.format_interval(planned_end - now, gmDateTime.acc_days)
						planned_end_str = _(u', until %s (%s)') % (
							gmDateTime.pydt_strftime(planned_end, '%Y %b %d', u'utf8', gmDateTime.acc_days),
							planned_end_from_now_str
						)
					end += _(u' (planned for %s%s)') % (duration, planned_end_str)
			else:
				if self._payload[self._idx['duration']] is None:
					end = u' %s ?' % gmTools.u_arrow2right
				else:
					duration = gmDateTime.format_interval(self._payload[self._idx['duration']], gmDateTime.acc_days)
					if self._payload[self._idx['started']] is None:
						planned_end_str = u''
					else:
						planned_end = self._payload[self._idx['started']] + self._payload[self._idx['duration']]
						if planned_end < now:
							planned_end_from_now_str = _(u'%s ago') % gmDateTime.format_interval(now - planned_end, gmDateTime.acc_days)
						else:
							planned_end_from_now_str = _(u'in %s') % gmDateTime.format_interval(planned_end - now, gmDateTime.acc_days)
						planned_end_str = _(u', until %s (%s)') % (
							gmDateTime.pydt_strftime(planned_end, '%Y %b %d', u'utf8', gmDateTime.acc_days),
							planned_end_from_now_str
						)
					end = _(u', planned for %s%s') % (duration, planned_end_str)

			txt = u'%s%s' % (start, end)

		# stopped medication
		else:
			duration_taken = self._payload[self._idx['discontinued']] - self._payload[self._idx['started']]
			if self._payload[self._idx['started']] is None:
				start = gmTools.coalesce(self._payload[self._idx['comment_on_start']], u'?')
			else:
				start = u'%s%s%s' % (
					start_prefix,
					gmDateTime.pydt_strftime(self._payload[self._idx['started']], format = '%Y %b %d', encoding = u'utf8', accuracy = gmDateTime.acc_days),
					gmTools.coalesce(self._payload[self._idx['comment_on_start']], u'', u' [%s]')
				)
			ended_ago = now - self._payload[self._idx['discontinued']]
			txt = _(u'%s ago (for %s: %s %s %s)') % (
				gmDateTime.format_interval_medically(ended_ago),
				gmDateTime.format_interval_medically(duration_taken),
				start,
				gmTools.u_arrow2right,
				gmDateTime.pydt_strftime(self._payload[self._idx['discontinued']], '%Y %b %d', u'utf8', gmDateTime.acc_days)
			)

		return txt

	medically_formatted_start_end = property(_get_medically_formatted_start_end, lambda x:x)

	#--------------------------------------------------------
	def _get_as_amts_latex(self, strict=True):
		return format_substance_intake_as_amts_latex(intake = self, strict=strict)

	as_amts_latex = property(_get_as_amts_latex, lambda x:x)

	#--------------------------------------------------------
	def _get_as_amts_data(self, strict=True):
		return format_substance_intake_as_amts_data(intake = self, strict = strict)

	as_amts_data = property(_get_as_amts_data, lambda x:x)

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
def get_substance_intakes(pk_patient=None):
	args = {'pat': pk_patient}
	if pk_patient is None:
		cmd = _SQL_get_substance_intake % u'true'
	else:
		cmd = _SQL_get_substance_intake % u'pk_patient = %(pat)s'
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = True)
	return [ cSubstanceIntakeEntry(row = {'data': r, 'idx': idx, 'pk_field': 'pk_substance_intake'}) for r in rows ]

#------------------------------------------------------------
def substance_intake_exists(pk_component=None, pk_substance=None, pk_identity=None, pk_brand=None, pk_dose=None):

	if [pk_substance, pk_component, pk_brand, pk_dose].count(None) != 3:
		raise ValueError('only one of pk_substance, pk_component, pk_dose, and pk_brand can be non-NULL')

	args = {
		'pk_comp': pk_component,
		'pk_subst': pk_substance,
		'pk_pat': pk_identity,
		'pk_brand': pk_brand,
		'pk_dose': pk_dose
	}
	where_parts = [u'fk_encounter IN (SELECT pk FROM clin.encounter WHERE fk_patient = %(pk_pat)s)']

	if pk_substance is not None:
		where_parts.append(u'fk_drug_component IN (SELECT pk FROM ref.lnk_dose2drug WHERE fk_dose IN (SELECT pk FROM ref.dose WHERE fk_substance = %(pk_subst)s))')
	if pk_dose is not None:
		where_parts.append(u'fk_drug_component IN (SELECT pk FROM ref.lnk_dose2drug WHERE fk_dose = %(pk_dose)s)')
	if pk_component is not None:
		where_parts.append(u'fk_drug_component = %(pk_comp)s')
	if pk_brand is not None:
		where_parts.append(u'fk_drug_component IN (SELECT pk FROM ref.lnk_dose2drug WHERE fk_brand = %(pk_brand)s)')

	cmd = u"""
		SELECT EXISTS (
			SELECT 1 FROM clin.substance_intake
			WHERE
				%s
			LIMIT 1
		)
	""" % u'\nAND\n'.join(where_parts)

	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])
	return rows[0][0]

#------------------------------------------------------------
def substance_intake_exists_by_atc(pk_identity=None, atc=None):

	if (atc is None) or (pk_identity is None):
		raise ValueError('atc and pk_identity cannot be None')

	args = {
		'pat': pk_identity,
		'atc': atc
	}
	where_parts = [
		u'pk_patient = %(pat)s',
		u'((atc_substance = %(atc)s) OR (atc_brand = %(atc)s))'
	]
	cmd = u"""
		SELECT EXISTS (
			SELECT 1 FROM clin.v_substance_intakes
			WHERE
				%s
			LIMIT 1
		)
	""" % u'\nAND\n'.join(where_parts)

	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])
	return rows[0][0]

#------------------------------------------------------------
def create_substance_intake(pk_component=None, pk_encounter=None, pk_episode=None, pk_brand=None):

	if [pk_component, pk_brand].count(None) != 1:
		raise ValueError('only one of pk_component and pk_brand can be non-NULL')

	args = {
		'pk_enc': pk_encounter,
		'pk_epi': pk_episode,
		'pk_comp': pk_component,
		'pk_brand': pk_brand
	}

	if pk_brand is not None:
		cmd = u"""
			INSERT INTO clin.substance_intake (
				fk_encounter,
				fk_episode,
				intake_is_approved_of,
				fk_drug_component
			) VALUES (
				%(pk_enc)s,
				%(pk_epi)s,
				False,
				-- select one of the components (the others will be added by a trigger)
				(SELECT pk FROM ref.lnk_dose2drug WHERE fk_brand = %(pk_brand)s LIMIT 1)
			)
			RETURNING pk"""

	if pk_component is not None:
		cmd = u"""
			INSERT INTO clin.substance_intake (
				fk_encounter,
				fk_episode,
				intake_is_approved_of,
				fk_drug_component
			) VALUES (
				%(pk_enc)s,
				%(pk_epi)s,
				False,
				%(pk_comp)s
			)
			RETURNING pk"""

	try:
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True)
	except gmPG2.dbapi.InternalError, exc:
		if exc.pgerror is None:
			raise
		exc = make_pg_exception_fields_unicode(exc)
		if 'prevent_duplicate_component' in exc.u_pgerror:
			_log.exception('will not create duplicate substance intake entry')
			_log.error(exc.u_pgerror)
			return None
		raise

	return cSubstanceIntakeEntry(aPK_obj = rows[0][0])

#------------------------------------------------------------
def delete_substance_intake(substance=None):
	cmd = u'DELETE FROM clin.substance_intake WHERE pk = %(pk)s'
	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': {'pk': substance}}])
	return True

#------------------------------------------------------------
# AMTS formatting
#------------------------------------------------------------
def format_substance_intake_as_amts_latex(intake=None, strict=True):

	_esc = gmTools.tex_escape_string

	# %(contains)s & %(brand)s & %(amount)s%(unit)s & %(preparation)s & \multicolumn{4}{l|}{%(schedule)s} & Einheit & %(notes)s & %(aim)s \tabularnewline \hline
	cells = []
	# components
	components = [ c.split('::') for c in intake.containing_drug['components'] ]
	if len(components) > 3:
		cells.append(_esc(u'WS-Kombi.'))
	elif len(components) == 1:
		c = components[0]
		if strict:
			cells.append(u'\\mbox{%s}' % _esc(c[0][:80]))
		else:
			cells.append(u'\\mbox{%s}' % _esc(c[0]))
	else:
		if strict:
			cells.append(u'\\fontsize{10pt}{12pt}\selectfont %s ' % u'\\newline '.join([u'\\mbox{%s}' % _esc(c[0][:80]) for c in components]))
		else:
			cells.append(u'\\fontsize{10pt}{12pt}\selectfont %s ' % u'\\newline '.join([u'\\mbox{%s}' % _esc(c[0]) for c in components]))
	# brand
	if strict:
		cells.append(_esc(intake['brand'][:50]))
	else:
		cells.append(_esc(intake['brand']))
	# Wirkstärken
	if len(components) > 3:
		cells.append(u'')
	elif len(components) == 1:
		c = components[0]
		if strict:
			cells.append(_esc((u'%s%s' % ((u'%s' % c[1]).replace(u'.', u','), c[2]))[:11]))
		else:
			cells.append(_esc(u'%s%s' % ((u'%s' % c[1]).replace(u'.', u','), c[2])))
	else:
		if strict:
			cells.append(u'\\fontsize{10pt}{12pt}\selectfont %s ' % u'\\newline\\ '.join([_esc((u'%s%s' % ((u'%s' % c[1]).replace(u'.', u','), c[2]))[:11]) for c in components]))
		else:
			cells.append(u'\\fontsize{10pt}{12pt}\selectfont %s ' % u'\\newline\\ '.join([_esc(u'%s%s' % ((u'%s' % c[1]).replace(u'.', u','), c[2])) for c in components]))
	# preparation
	if strict:
		cells.append(_esc(intake['preparation'][:7]))
	else:
		cells.append(_esc(intake['preparation']))
	# schedule - for now be simple - maybe later parse 1-1-1-1 etc
	if intake['schedule'] is None:
		cells.append(u'\\multicolumn{4}{p{3.2cm}|}{\\ }')
	else:
		# spec says [:20] but implementation guide says: never trim
		if len(intake['schedule']) > 20:
			cells.append(u'\\multicolumn{4}{>{\\RaggedRight}p{3.2cm}|}{\\fontsize{10pt}{12pt}\selectfont %s}' % _esc(intake['schedule']))
		else:
			cells.append(u'\\multicolumn{4}{>{\\RaggedRight}p{3.2cm}|}{%s}' % _esc(intake['schedule']))
	# Einheit to take
	cells.append(u'')#[:20]
	# notes
	if intake['notes'] is None:
		cells.append(u' ')
	else:
		if strict:
			cells.append(_esc(intake['notes'][:80]))
		else:
			cells.append(u'\\fontsize{10pt}{12pt}\selectfont %s ' % _esc(intake['notes']))
	# aim
	if intake['aim'] is None:
		cells.append(u' ')
	else:
		if strict:
			cells.append(_esc(intake['aim'][:50]))
		else:
			cells.append(u'\\fontsize{10pt}{12pt}\selectfont %s ' % _esc(intake['aim']))

	table_row = u' & '.join(cells)
	table_row += u'\\tabularnewline\n\\hline'

	return table_row

#------------------------------------------------------------
def format_substance_intake_as_amts_data(intake=None, strict=True):

	if not strict:
		pass
		# relax length checks

	fields = []

	# components
	components = [ c.split('::') for c in intake.containing_drug['components'] ]
	if len(components) > 3:
		fields.append(u'WS-Kombi.')
	elif len(components) == 1:
		c = components[0]
		fields.append(c[0][:80])
	else:
		fields.append(u'~'.join([c[0][:80] for c in components]))
	# brand
	fields.append(intake['brand'][:50])
	# Wirkstärken
	if len(components) > 3:
		fields.append(u'')
	elif len(components) == 1:
		c = components[0]
		fields.append((u'%s%s' % (c[1], c[2]))[:11])
	else:
		fields.append(u'~'.join([(u'%s%s' % (c[1], c[2]))[:11] for c in components]))
	# preparation
	fields.append(intake['preparation'][:7])
	# schedule - for now be simple - maybe later parse 1-1-1-1 etc
	fields.append(gmTools.coalesce(intake['schedule'], u'')[:20])
	# Einheit to take
	fields.append(u'')#[:20]
	# notes
	fields.append(gmTools.coalesce(intake['notes'], u'')[:80])
	# aim
	fields.append(gmTools.coalesce(intake['aim'], u'')[:50])

	return u'|'.join(fields)

#------------------------------------------------------------
def calculate_amts_data_check_symbol(intakes=None):

	# first char of generic substance or brand name
	first_chars = []
	for intake in intakes:
		first_chars.append(intake['brand'][0])

	# add up_per page
	val_sum = 0
	for first_char in first_chars:
		# ziffer: ascii+7
		if first_char.isdigit():
			val_sum += (ord(first_char) + 7)
		# großbuchstabe: ascii
		# kleinbuchstabe ascii(großbuchstabe)
		if first_char.isalpha():
			val_sum += ord(first_char.upper())
		# other: 0

	# get remainder of sum mod 36
	tmp, remainder = divmod(val_sum, 36)
	# 0-9 -> '0' - '9'
	if remainder < 10:
		return u'%s' % remainder
	# 10-35 -> 'A' - 'Z'
	return chr(remainder + 55)

#------------------------------------------------------------
def generate_amts_data_template_definition_file(work_dir=None, strict=True):

	if not strict:
		return __generate_enhanced_amts_data_template_definition_file(work_dir = work_dir)

	amts_fields = [
		u'MP',
		u'020',	# Version
		u'DE',	# Land
		u'DE',	# Sprache
		u'1',	# Zeichensatz 1 = Ext ASCII (fest) = ISO8859-1 = Latin1
		u'$<today::%Y%m%d::8>$',
		u'$<amts_page_idx::::1>$',				# to be set by code using the template
		u'$<amts_total_pages::::1>$',			# to be set by code using the template
		u'0',	# Zertifizierungsstatus

		u'$<name::%(firstnames)s::45>$',
		u'$<name::%(lastnames)s::45>$',
		u'',	# Patienten-ID
		u'$<date_of_birth::%Y%m%d::8>$',

		u'$<<range_of::$<praxis::%(praxis)s,%(branch)s::>$,$<current_provider::::>$::30>>$',
		u'$<praxis_address::%(street)s %(number)s %(subunit)s|%(postcode)s|%(urb)s::57>$',		# 55+2 because of 2 embedded "|"s
		u'$<praxis_comm::workphone::20>$',
		u'$<praxis_comm::email::80>$',

		#u'264 $<allergy_state::::21>$',				# param 1, Allergien 25-4 (4 for "264 ", spec says max of 25)
		u'264 Seite $<amts_total_pages::::1>$ unten',	# param 1, Allergien 25-4 (4 for "264 ", spec says max of 25)
		u'', # param 2, not used currently
		u'', # param 3, not used currently

		# Medikationseinträge
		u'$<amts_intakes_as_data::::9999999>$',

		u'$<amts_check_symbol::::1>$',	# Prüfzeichen, value to be set by code using the template, *per page* !
		u'#@',							# Endesymbol
	]

	amts_fname = gmTools.get_unique_filename (
		prefix = 'gm2amts_data-',
		suffix = '.txt',
		tmp_dir = work_dir
	)
	amts_template = io.open(amts_fname, mode = 'wt', encoding = 'utf8')
	amts_template.write(u'[form]\n')
	amts_template.write(u'template = $template$\n')
	amts_template.write(u'|'.join(amts_fields))
	amts_template.write(u'\n')
	amts_template.write(u'$template$\n')
	amts_template.close()

	return amts_fname

#------------------------------------------------------------
def __generate_enhanced_amts_data_template_definition_file(work_dir=None):

	amts_fields = [
		u'MP',
		u'020',	# Version
		u'DE',	# Land
		u'DE',	# Sprache
		u'1',	# Zeichensatz 1 = Ext ASCII (fest) = ISO8859-1 = Latin1
		u'$<today::%Y%m%d::8>$',
		u'1',	# idx of this page
		u'1',	# total pages
		u'0',	# Zertifizierungsstatus

		u'$<name::%(firstnames)s::>$',
		u'$<name::%(lastnames)s::>$',
		u'',	# Patienten-ID
		u'$<date_of_birth::%Y%m%d::8>$',

		u'$<praxis::%(praxis)s,%(branch)s::>$,$<current_provider::::>$',
		u'$<praxis_address::%(street)s %(number)s %(subunit)s::>$',
		u'$<praxis_address::%(postcode)s::>$',
		u'$<praxis_address::%(urb)s::>$',
		u'$<praxis_comm::workphone::>$',
		u'$<praxis_comm::email::>$',

		#u'264 $<allergy_state::::>$', 					# param 1, Allergien
		u'264 Seite 1 unten',							# param 1, Allergien
		u'', # param 2, not used currently
		u'', # param 3, not used currently

		# Medikationseinträge
		u'$<amts_intakes_as_data_enhanced::::>$',

		u'$<amts_check_symbol::::1>$',	# Prüfzeichen, value to be set by code using the template, *per page* !
		u'#@',							# Endesymbol
	]

	amts_fname = gmTools.get_unique_filename (
		prefix = 'gm2amts_data-utf8-unabridged-',
		suffix = '.txt',
		tmp_dir = work_dir
	)
	amts_template = io.open(amts_fname, mode = 'wt', encoding = 'utf8')
	amts_template.write(u'[form]\n')
	amts_template.write(u'template = $template$\n')
	amts_template.write(u'|'.join(amts_fields))
	amts_template.write(u'\n')
	amts_template.write(u'$template$\n')
	amts_template.close()

	return amts_fname

#------------------------------------------------------------
# other formatting
#------------------------------------------------------------
def format_substance_intake_notes(emr=None, output_format=u'latex', table_type=u'by-brand'):

	tex = u'\\noindent %s\n' % _('Additional notes')
	tex += u'%%%% requires "\\usepackage{longtable}"\n'
	tex += u'%%%% requires "\\usepackage{tabu}"\n'
	tex += u'\\noindent \\begin{longtabu} to \\textwidth {|X[,L]|r|X[,L]|}\n'
	tex += u'\\hline\n'
	tex += u'%s {\\scriptsize (%s)} & %s & %s \\tabularnewline \n' % (_('Substance'), _('Brand'), _('Strength'), _('Aim'))
	tex += u'\\hline\n'
	tex += u'\\hline\n'
	tex += u'%s\n'
	tex += u'\\end{longtabu}\n'

	current_meds = emr.get_current_medications (
		include_inactive = False,
		include_unapproved = False,
		order_by = u'brand, substance'
	)

	# create lines
	lines = []
	for med in current_meds:
		brand = u'{\\small :} {\\tiny %s}' % gmTools.tex_escape_string(med['brand'])
		if med['aim'] is None:
			aim = u''
		else:
			aim = u'{\\scriptsize %s}' % gmTools.tex_escape_string(med['aim'])
		lines.append(u'%s ({\\small %s}%s) & %s%s & %s \\tabularnewline\n \\hline' % (
			gmTools.tex_escape_string(med['substance']),
			gmTools.tex_escape_string(med['preparation']),
			brand,
			med['amount'],
			gmTools.tex_escape_string(med['unit']),
			aim
		))

	return tex % u'\n'.join(lines)

#------------------------------------------------------------
def format_substance_intake(emr=None, output_format=u'latex', table_type=u'by-brand'):

	# FIXME: add intake_instructions

	tex = u'\\noindent %s {\\tiny (%s)}\n' % (
		gmTools.tex_escape_string(_('Medication list')),
		gmTools.tex_escape_string(_('ordered by brand'))
	)
	tex += u'%% requires "\\usepackage{longtable}"\n'
	tex += u'%% requires "\\usepackage{tabu}"\n'
	tex += u'\\begin{longtabu} to \\textwidth {|X[-1,L]|X[2.5,L]|}\n'
	tex += u'\\hline\n'
	tex += u'%s & %s \\tabularnewline \n' % (
		gmTools.tex_escape_string(_('Drug')),
		gmTools.tex_escape_string(_('Regimen / Advice'))
	)
	tex += u'\\hline\n'
	tex += u'%s\n'
	tex += u'\\end{longtabu}\n'

	current_meds = emr.get_current_medications (
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
			line_data[identifier] = {'brand': u'', 'preparation': u'', 'schedule': u'', 'notes': [], 'strengths': []}

		line_data[identifier]['brand'] = identifier
		line_data[identifier]['strengths'].append(u'%s %s%s' % (med['substance'][:20], med['amount'], med['unit'].strip()))
		line_data[identifier]['preparation'] = med['preparation']
		if med['duration'] is not None:
			line_data[identifier]['schedule'] = u'%s: ' % gmDateTime.format_interval(med['duration'], gmDateTime.acc_days, verbose = True)
		line_data[identifier]['schedule'] += gmTools.coalesce(med['schedule'], u'')
		if med['notes'] is not None:
			if med['notes'] not in line_data[identifier]['notes']:
				line_data[identifier]['notes'].append(med['notes'])

	# create lines
	already_seen = []
	lines = []
	line1_template = u'\\rule{0pt}{3ex}{\\Large %s} %s & %s \\tabularnewline'
	line2_template = u'{\\tiny %s}                     & {\\scriptsize %s} \\tabularnewline'
	line3_template = u'                                & {\\scriptsize %s} \\tabularnewline'

	for med in current_meds:
		identifier = gmTools.coalesce(med['brand'], med['substance'])

		if identifier in already_seen:
			continue

		already_seen.append(identifier)

		lines.append (line1_template % (
			gmTools.tex_escape_string(line_data[identifier]['brand']),
			gmTools.tex_escape_string(line_data[identifier]['preparation']),
			gmTools.tex_escape_string(line_data[identifier]['schedule'])
		))

		strengths = gmTools.tex_escape_string(u' / '.join(line_data[identifier]['strengths']))
		if len(line_data[identifier]['notes']) == 0:
			first_note = u''
		else:
			first_note = gmTools.tex_escape_string(line_data[identifier]['notes'][0])
		lines.append(line2_template % (strengths, first_note))
		if len(line_data[identifier]['notes']) > 1:
			for note in line_data[identifier]['notes'][1:]:
				lines.append(line3_template % gmTools.tex_escape_string(note))

		lines.append(u'\\hline')

	return tex % u'\n'.join(lines)

#============================================================
# drug components
#------------------------------------------------------------
_SQL_get_drug_components = u'SELECT * FROM ref.v_drug_components WHERE %s'

class cDrugComponent(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = _SQL_get_drug_components % u'pk_component = %s'
	_cmds_store_payload = [
		u"""UPDATE ref.lnk_dose2drug SET
				fk_brand = %(pk_brand)s,
				fk_dose = %(pk_dose)s
			WHERE
				pk = %(pk_component)s
					AND
				NOT EXISTS (
					SELECT 1
					FROM clin.substance_intake
					WHERE fk_drug_component = %(pk_component)s
					LIMIT 1
				)
					AND
				xmin = %(xmin_lnk_dose2drug)s
			RETURNING
				xmin AS xmin_lnk_dose2drug
		"""
	]
	_updatable_fields = [
		u'pk_brand',
		u'pk_dose'
	]
	#--------------------------------------------------------
	def format(self, left_margin=0):
		lines = []
		lines.append(u'%s %s%s/%s' % (
			self._payload[self._idx['substance']],
			self._payload[self._idx['amount']],
			self._payload[self._idx['unit']],
			gmTools.coalesce(gmTools.coalesce(self._payload[self._idx['dose_unit']], _('delivery unit of %s') % self._payload[self._idx['preparation']]))
		))
		lines.append(_('Component of %s (%s)') % (
			self._payload[self._idx['brand']],
			self._payload[self._idx['preparation']]
		))
		if self._payload[self._idx['intake_instructions']] is not None:
			lines.append(_(u'Instructions: %s') % self._payload[self._idx['intake_instructions']])
		if self._payload[self._idx['atc_substance']] is not None:
			lines.append(_('ATC (substance): %s') % self._payload[self._idx['atc_substance']])
		if self._payload[self._idx['atc_brand']] is not None:
			lines.append(_('ATC (brand): %s') % self._payload[self._idx['atc_brand']])
		if self._payload[self._idx['external_code']] is not None:
			lines.append(u'%s: %s' % (
				self._payload[self._idx['external_code_type']],
				self._payload[self._idx['external_code']]
			))
		if self._payload[self._idx['is_fake_brand']]:
			lines.append(_('this is a component of a fake brand'))

		return (u' ' * left_margin) + (u'\n' + (u' ' * left_margin)).join(lines)
	#--------------------------------------------------------
	def exists_as_intake(self, pk_patient=None):
		return substance_intake_exists (
			pk_component = self._payload[self._idx['pk_component']],
			pk_identity = pk_patient
		)

	#--------------------------------------------------------
	def turn_into_intake(self, emr=None, encounter=None, episode=None):
		return create_substance_intake (
			pk_component = self._payload[self._idx['pk_component']],
			pk_encounter = encounter,
			pk_episode = episode
		)

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
	def _get_substance_dose(self):
		return cSubstanceDose(aPK_obj = self._payload[self._idx['pk_dose']])

	substance_dose =  property(_get_substance_dose, lambda x:x)

	#--------------------------------------------------------
	def _get_substance(self):
		return cSubstance(aPK_obj = self._payload[self._idx['pk_substance']])

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
		SELECT DISTINCT ON (list_label)
			r_vdc1.pk_component
				AS data,
			(r_vdc1.substance || ' '
				|| r_vdc1.amount || r_vdc1.unit || ' '
				|| r_vdc1.preparation || ' ('
				|| r_vdc1.brand || ' ['
					|| (
						SELECT array_to_string(array_agg(r_vdc2.amount), ' / ')
						FROM ref.v_drug_components r_vdc2
						WHERE r_vdc2.pk_brand = r_vdc1.pk_brand
					)
				|| ']'
			 || ')'
			)	AS field_label,
			(r_vdc1.substance || ' '
				|| r_vdc1.amount || r_vdc1.unit || ' '
				|| r_vdc1.preparation || ' ('
				|| r_vdc1.brand || ' ['
					|| (
						SELECT array_to_string(array_agg(r_vdc2.amount), ' / ')
						FROM ref.v_drug_components r_vdc2
						WHERE r_vdc2.pk_brand = r_vdc1.pk_brand
					)
				|| ']'
			 || ')'
			)	AS list_label
		FROM ref.v_drug_components r_vdc1
		WHERE
			r_vdc1.substance %(fragment_condition)s
				OR
			r_vdc1.brand %(fragment_condition)s
		ORDER BY list_label
		LIMIT 50"""

	_query_desc_and_amount = u"""
		SELECT DISTINCT ON (list_label)
			pk_component AS data,
			(r_vdc1.substance || ' '
				|| r_vdc1.amount || r_vdc1.unit || ' '
				|| r_vdc1.preparation || ' ('
				|| r_vdc1.brand || ' ['
					|| (
						SELECT array_to_string(array_agg(r_vdc2.amount), ' / ')
						FROM ref.v_drug_components r_vdc2
						WHERE r_vdc2.pk_brand = r_vdc1.pk_brand
					)
				|| ']'
			 || ')'
			)	AS field_label,
			(r_vdc1.substance || ' '
				|| r_vdc1.amount || r_vdc1.unit || ' '
				|| r_vdc1.preparation || ' ('
				|| r_vdc1.brand || ' ['
					|| (
						SELECT array_to_string(array_agg(r_vdc2.amount), ' / ')
						FROM ref.v_drug_components r_vdc2
						WHERE r_vdc2.pk_brand = r_vdc1.pk_brand
					)
				|| ']'
			 || ')'
			)	AS list_label
		FROM ref.v_drug_components
		WHERE
			%(fragment_condition)s
		ORDER BY list_label
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
# branded drugs
#------------------------------------------------------------
_SQL_get_branded_drug = u"SELECT * FROM ref.v_branded_drugs WHERE %s"

class cBrandedDrug(gmBusinessDBObject.cBusinessDBObject):
	"""Represents a drug as marketed by a manufacturer."""

	_cmd_fetch_payload = _SQL_get_branded_drug % u'pk_brand = %s'
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
	def format(self, left_margin=0):
		lines = []
		lines.append(u'%s (%s)' % (
			self._payload[self._idx['brand']],
			self._payload[self._idx['preparation']]
			)
		)
		if self._payload[self._idx['atc']] is not None:
			lines.append(u'ATC: %s' % self._payload[self._idx['atc']])
		if self._payload[self._idx['external_code']] is not None:
			lines.append(u'%s: %s' % (self._payload[self._idx['external_code_type']], self._payload[self._idx['external_code']]))
		if self._payload[self._idx['components']] is not None:
			lines.append(_('Components:'))
			for comp in self._payload[self._idx['components']]:
				lines.append(u' ' + comp)
		if self._payload[self._idx['is_fake_brand']]:
			lines.append(u'')
			lines.append(_('this is a fake brand'))
		if self.is_vaccine:
			lines.append(_('this is a vaccine'))

		return (u' ' * left_margin) + (u'\n' + (u' ' * left_margin)).join(lines)

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
	def set_substance_doses_as_components(self, substance_doses=None):
		if self.is_in_use_by_patients:
			return False

		pk_doses2keep = [ s['pk_dose'] for s in substance_doses ]
		args = {'pk_brand': self._payload[self._idx['pk_brand']]}
		queries = []

		# INSERT those which are not there yet
		cmd = u"""
			INSERT INTO ref.lnk_dose2drug (
				fk_brand,
				fk_dose
			)
			SELECT
				%(pk_brand)s,
				%(pk_dose)s
			WHERE NOT EXISTS (
				SELECT 1 FROM ref.lnk_dose2drug
				WHERE
					fk_brand = %(pk_brand)s
						AND
					fk_dose = %(pk_dose)s
			)"""
		for pk in pk_doses2keep:
			args['pk_dose'] = pk
			queries.append({'cmd': cmd, 'args': args})

		# DELETE those that don't belong anymore
		args['doses2keep'] = tuple(pk_doses2keep)
		cmd = u"""
			DELETE FROM ref.lnk_dose2drug
			WHERE
				fk_brand = %(pk_brand)s
					AND
				fk_dose NOT IN %(doses2keep)s"""
		queries.append({'cmd': cmd, 'args': args})

		gmPG2.run_rw_queries(queries = queries)
		self.refetch_payload()

		return True

	#--------------------------------------------------------
	def add_component(self, substance=None, atc=None, amount=None, unit=None, dose_unit=None, pk_dose=None, pk_substance=None):

		if pk_dose is None:
			if pk_substance is None:
				pk_dose = create_substance_dose(substance = substance, atc = atc, amount = amount, unit = unit, dose_unit = dose_unit)['pk_dose']
			else:
				pk_dose = create_substance_dose(pk_substance = pk_substance, atc = atc, amount = amount, unit = unit, dose_unit = dose_unit)['pk_dose']

		args = {
			'pk_dose': pk_dose,
			'pk_brand': self.pk_obj
		}

		cmd = u"""
			INSERT INTO ref.lnk_dose2drug (fk_brand, fk_dose)
			SELECT
				%(pk_brand)s,
				%(pk_dose)s
			WHERE NOT EXISTS (
				SELECT 1 FROM ref.lnk_dose2drug
				WHERE
					fk_brand = %(pk_brand)s
						AND
					fk_dose = %(pk_dose)s
			)"""
		gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
		self.refetch_payload()

	#------------------------------------------------------------
	def remove_component(self, pk_dose=None, pk_substance=None, pk_component=None):
		if len(self._payload[self._idx['components']]) == 1:
			_log.error('will not remove the only component of a drug')
			return False

		args = {'pk_brand': self.pk_obj, 'pk_substance': pk_substance, 'pk_dose': pk_dose, 'pk_component': pk_component}

		if pk_component is None:
			if pk_dose is None:
				cmd = u"SELECT pk FROM ref.dose WHERE fk_substance = %(pk_substance)s"
				rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])
				pk_dose = rows[0][0]
			cmd = u"""
				DELETE FROM ref.lnk_dose2drug
				WHERE
					fk_brand = %(pk_brand)s
						AND
					fk_dose = %(pk_dose)s
						AND
					NOT EXISTS (
						SELECT 1 FROM clin.v_substance_intakes
						WHERE pk_dose = %(pk_dose)s
						LIMIT 1
					)"""
		else:
			cmd = u"""
				DELETE FROM ref.lnk_dose2drug
				WHERE
					pk = %(pk_component)s
						AND
					NOT EXISTS (
						SELECT 1 FROM clin.substance_intake
						WHERE fk_drug_component = %(pk_component)s
						LIMIT 1
					)"""

		gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
		self.refetch_payload()
		return True

	#--------------------------------------------------------
	def exists_as_intake(self, pk_patient=None):
		return substance_intake_exists (
			pk_brand = self._payload[self._idx['pk_brand']],
			pk_identity = pk_patient
		)

	#--------------------------------------------------------
	def turn_into_intake(self, emr=None, encounter=None, episode=None):
		return create_substance_intake (
			pk_brand = self._payload[self._idx['pk_brand']],
			pk_encounter = encounter,
			pk_episode = episode
		)

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
	def _get_components_as_doses(self):
		if self._payload[self._idx['pk_doses']] is None:
			return []
		cmd = _SQL_get_substance_dose % u'pk_dose IN %(pks)s'
		args = {'pks': tuple(self._payload[self._idx['pk_doses']])}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		return [ cSubstanceDose(row = {'data': r, 'idx': idx, 'pk_field': 'pk_dose'}) for r in rows ]

	components_as_doses = property(_get_components_as_doses, lambda x:x)

	#--------------------------------------------------------
	def _get_components_as_substances(self):
		if self._payload[self._idx['pk_substances']] is None:
			return []
		cmd = _SQL_get_substance % u'pk IN %(pks)s'
		args = {'pks': tuple(self._payload[self._idx['pk_substances']])}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		return [ cConsumableSubstance(row = {'data': r, 'idx': idx, 'pk_field': 'pk'}) for r in rows ]

	components_as_substances = property(_get_components_as_substances, lambda x:x)

	#--------------------------------------------------------
	def _get_is_fake_brand(self):
		return self._payload[self._idx['is_fake_brand']]

	is_fake_brand = property(_get_is_fake_brand, lambda x:x)

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
				SELECT 1 FROM clin.substance_intake WHERE
					fk_drug_component IN (
						SELECT pk FROM ref.lnk_dose2drug WHERE fk_brand = %(pk)s
					)
				LIMIT 1
			)"""
		args = {'pk': self.pk_obj}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		return rows[0][0]

	is_in_use_by_patients = property(_get_is_in_use_by_patients, lambda x:x)

#------------------------------------------------------------
def get_branded_drugs():
	cmd = _SQL_get_branded_drug % u'TRUE ORDER BY brand'
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = True)
	return [ cBrandedDrug(row = {'data': r, 'idx': idx, 'pk_field': 'pk_brand'}) for r in rows ]

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
def delete_branded_drug(pk_brand=None):
	queries = []
	# delete components
	cmd = u"""
		DELETE FROM ref.lnk_dose2drug
		WHERE
			fk_brand = %(pk)s
				AND
			NOT EXISTS (
				SELECT 1
				FROM clin.v_substance_intakes
				WHERE pk_brand = %(pk)s
				LIMIT 1
			)"""
	queries.append({'cmd': cmd, 'args': args})
	# delete drug
	cmd = u"""
		DELETE FROM ref.branded_drug
		WHERE
			pk = %(pk)s
				AND
			NOT EXISTS (
				SELECT 1 FROM clin.v_substance_intakes
				WHERE pk_brand = %(pk)s
				LIMIT 1
			)"""
	args = {'pk': pk_brand}
	queries.append({'cmd': cmd, 'args': args})
	gmPG2.run_rw_queries(queries = queries)

#============================================================
# convenience functions
#------------------------------------------------------------
def create_default_medication_history_episode(pk_health_issue=None, encounter=None, link_obj=None):
	return gmEMRStructItems.create_episode (
		pk_health_issue = pk_health_issue,
		episode_name = DEFAULT_MEDICATION_HISTORY_EPISODE,
		is_open = False,
		allow_dupes = False,
		encounter = encounter,
		link_obj = link_obj
	)

#------------------------------------------------------------
def get_tobacco():
	tobacco = create_branded_drug (
		brand_name = _(u'nicotine'),
		preparation = _(u'tobacco'),
		return_existing = True
	)
	tobacco['is_fake_brand'] = True
	tobacco.save()
	nicotine = create_substance_dose_by_atc (
		substance = _('nicotine'),
		atc = gmATC.ATC_NICOTINE,
		amount = 1,
		unit = u'pack',
		dose_unit = u'year'
	)
	tobacco.set_substance_doses_as_components(substance_doses = [nicotine])
	return tobacco

#------------------------------------------------------------
def get_alcohol():
	drink = create_branded_drug (
		brand_name = _(u'alcohol'),
		preparation = _(u'liquid'),
		return_existing = True
	)
	drink['is_fake_brand'] = True
	drink.save()
	ethanol = create_substance_dose_by_atc (
		substance = _(u'ethanol'),
		atc = gmATC.ATC_ETHANOL,
		amount = 1,
		unit = u'g',
		dose_unit = u'ml'
	)
	drink.set_substance_doses_as_components(substance_doses = [ethanol])
	return drink

#------------------------------------------------------------
def get_other_drug(name=None, pk_dose=None):
	drug = create_branded_drug (
		brand_name = name,
		preparation = _(u'unit'),
		return_existing = True
	)
	drug['is_fake_brand'] = True
	drug.save()
	if pk_dose is None:
		content = create_substance_dose (
			substance = name,
			amount = 1,
			unit = _(u'unit'),
			dose_unit = _(u'unit')
		)
	else:
		content = {'pk_dose': pk_dose}		#cSubstanceDose(aPK_obj = pk_dose)
	drug.set_substance_doses_as_components(substance_doses = [content])
	return drug

#============================================================
# substance doses
#------------------------------------------------------------
_SQL_get_substance_dose = u"SELECT * FROM ref.v_substance_doses WHERE %s"

class cSubstanceDose(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = _SQL_get_substance_dose % u"pk_dose = %s"
	_cmds_store_payload = [
		u"""UPDATE ref.dose SET
				amount = %(amount)s,
				unit = %(unit)s,
				dose_unit = gm.nullify_empty_string(%(dose_unit)s)
			WHERE
				pk = %(pk_dose)s
					AND
				xmin = %(xmin_dose)s
			RETURNING
				xmin as xmin_dose,
				pk as pk_dose
		"""
	]
	_updatable_fields = [
		u'amount',
		u'unit',
		u'dose_unit'
	]
	#--------------------------------------------------------
	def format(self, left_margin=0):
		return (u' ' * left_margin) + u'%s: %s %s%s/%s%s%s' % (
			_('Substance dose'),
			self._payload[self._idx['substance']],
			self._payload[self._idx['amount']],
			self._payload[self._idx['unit']],
			gmTools.coalesce(gmTools.coalesce(self._payload[self._idx['dose_unit']], _('delivery unit'))),
			gmTools.coalesce(self._payload[self._idx['atc_substance']], u'', u' [%s]'),
			gmTools.coalesce(self._payload[self._idx['intake_instructions']], u'', u'\n' + (u' ' * left_margin) + u' ' + _(u'Instructions: %s'))
		)

	#--------------------------------------------------------
	def exists_as_intake(self, pk_patient=None):
		return substance_intake_exists (
			pk_dose = self.pk_obj,
			pk_identity = pk_patient
		)

	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_is_in_use_by_patients(self):
		cmd = u"""
			SELECT EXISTS (
				SELECT 1
				FROM clin.v_substance_intakes
				WHERE pk_substance = %(pk)s
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
				FROM ref.v_drug_components
				WHERE pk_substance = %(pk)s
				LIMIT 1
			)"""
		args = {'pk': self.pk_obj}

		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		return rows[0][0]

	is_drug_component = property(_get_is_drug_component, lambda x:x)

#------------------------------------------------------------
def get_substance_doses(order_by=None):
	if order_by is None:
		order_by = u'true'
	else:
		order_by = u'true ORDER BY %s' % order_by
	cmd = _SQL_get_substance_dose % order_by
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = True)
	return [ cSubstanceDose(row = {'data': r, 'idx': idx, 'pk_field': 'pk_dose'}) for r in rows ]

#------------------------------------------------------------
def create_substance_dose(pk_substance=None, substance=None, atc=None, amount=None, unit=None, dose_unit=None):

	if [pk_substance, substance].count(None) != 1:
		raise ValueError('exctly one of <pk_substance> and <substance> must be None')

	converted, amount = gmTools.input2decimal(amount)
	if not converted:
		raise ValueError('<amount> must be a number: %s (%s)', amount, type(amount))

	if pk_substance is None:
		pk_substance = create_substance(substance = substance, atc = atc)['pk']

	args = {
		'pk_subst': pk_substance,
		'amount': amount,
		'unit': unit.strip(),
		'dose_unit': dose_unit.strip()
	}
	cmd = u"""
		SELECT pk FROM ref.dose
		WHERE
			fk_substance = %(pk_subst)s
				AND
			amount = %(amount)s
				AND
			unit = %(unit)s
				AND
			dose_unit IS NOT DISTINCT FROM gm.nullify_empty_string(%(dose_unit)s)
		"""
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])

	if len(rows) == 0:
		cmd = u"""
			INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit) VALUES (
				%(pk_subst)s,
				%(amount)s,
				gm.nullify_empty_string(%(unit)s),
				gm.nullify_empty_string(%(dose_unit)s)
			) RETURNING pk"""
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True, get_col_idx = False)

	return cSubstanceDose(aPK_obj = rows[0]['pk'])

#------------------------------------------------------------
def create_substance_dose_by_atc(substance=None, atc=None, amount=None, unit=None, dose_unit=None):
	return create_substance_dose (
		pk_substance = create_substance_by_atc(substance = substance, atc = atc)['pk'],
		amount = amount,
		unit = unit,
		dose_unit = dose_unit
	)

#------------------------------------------------------------
def delete_substance_dose(pk_dose=None):
	args = {'pk': pk_dose}
	cmd = u"""
		DELETE FROM ref.dose WHERE
			pk = %(pk_dose)s
				AND
			-- must not currently be used with a patient
			NOT EXISTS (
				SELECT 1 FROM clin.v_substance_intakes
				WHERE pk_dose = %(pk_dose)s
				LIMIT 1
			)
				AND
			-- must not currently be linked to a drug
			NOT EXISTS (
				SELECT 1 FROM ref.lnk_dose2drug
				WHERE fk_dose = %(pk_dose)s
				LIMIT 1
			)
	"""
	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
	return True

#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.pycommon import gmLog2
	#from Gnumed.pycommon import gmI18N
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
		mmi.switch_to_frontend(blocking = True)
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
		gmPerson.set_active_patient(patient = gmPerson.cPerson(aPK_obj = 12))
		fd = cFreeDiamsInterface()
		fd.patient = gmPerson.gmCurrentPatient()
#		fd.switch_to_frontend(blocking = True)
		fd.import_fd2gm_file_as_drugs(filename = sys.argv[2])
	#--------------------------------------------------------
	def test_fd_show_interactions():
		gmPerson.set_active_patient(patient = gmPerson.cPerson(aPK_obj = 12))
		fd = cFreeDiamsInterface()
		fd.patient = gmPerson.gmCurrentPatient()
		fd.check_interactions(substances = fd.patient.get_emr().get_current_medications(include_unapproved = True))
	#--------------------------------------------------------
	# generic
	#--------------------------------------------------------
	def test_create_substance_intake():
		drug = create_substance_intake (
			pk_component = 2,
			pk_encounter = 1,
			pk_episode = 1
		)
		print drug

	#--------------------------------------------------------
	def test_get_substances():
		for s in get_substances():
			#print s
			print s.format()

	#--------------------------------------------------------
	def test_get_doses():
		for d in get_substance_doses():
			#print d
			print d.format()

	#--------------------------------------------------------
	def test_get_components():
		for c in get_drug_components():
			#print c
			print '--------------------------------------'
			print c.format()
			print c.substance_dose.format()
			print c.substance.format()

	#--------------------------------------------------------
	def test_get_drugs():
		for d in get_branded_drugs():
			if d['is_fake_brand'] or d.is_vaccine:
				continue
			print '--------------------------------------'
			print d.format()
			for c in d.components:
				print '-------'
				print c.format()
				print c.substance_dose.format()
				print c.substance.format()

	#--------------------------------------------------------
	def test_get_intakes():
		for i in get_substance_intakes():
			#print i
			print u'\n'.join(i.format_maximum_information())

	#--------------------------------------------------------
	def test_get_habit_drugs():
		print get_tobacco().format()
		print get_alcohol().format()
		print get_other_drug(name = u'LSD').format()

	#--------------------------------------------------------
	def test_drug2renal_insufficiency_url():
		drug2renal_insufficiency_url(search_term = 'Metoprolol')
	#--------------------------------------------------------
	def test_medically_formatted_start_end():
		cmd = u"SELECT pk_substance_intake FROM clin.v_substance_intakes"
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}])
		for row in rows:
			entry = cSubstanceIntakeEntry(row['pk_substance_intake'])
			print u'==============================================================='
			print entry.format(left_margin = 1, single_line = False, show_all_brand_components = True)
			print u'--------------------------------'
			print entry.medically_formatted_start_end
			gmTools.prompted_input()

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
	#test_drug2renal_insufficiency_url()
	#test_interaction_check()
	#test_medically_formatted_start_end()

	#test_get_substances()
	#test_get_doses()
	#test_get_components()
	#test_get_drugs()
	#test_create_substance_intake()
	#test_get_intakes()
	test_get_habit_drugs()
