# -*- coding: utf8 -*-
"""Medication handling code.

license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmMedication.py,v $
# $Id: gmMedication.py,v 1.6 2009-10-21 09:15:50 ncq Exp $
__version__ = "$Revision: 1.6 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

import sys, logging, csv, codecs


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmBusinessDBObject, gmPG2, gmShellAPI
# gmTools


_log = logging.getLogger('gm.meds')
_log.info(__version__)

#============================================================
# wishlist:
# - --conf-file= for glwin.exe
# - wirkstoff: Konzentration auch in Multiprodukten

class cGelbeListeCSVFile(object):
	"""Iterator over a Gelbe Liste/MMI v8.2 CSV file."""

	version = u'Gelbe Liste/MMI v8.2 CSV file interface'
	default_transfer_file_windows = "c:\\rezept.txt"
	default_encoding = 'cp1252'
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

		self.csv_lines = csv.DictReader (
			self.csv_file,
			fieldnames = cGelbeListeCSVFile.csv_fieldnames,
			delimiter = ';',
			quotechar = '"'
		)
	#--------------------------------------------------------
	def __iter__(self):
		return self
	#--------------------------------------------------------
	def next(self):
		line = self.csv_lines.next()

		for field in cGelbeListeCSVFile.boolean_fields:
			line[field] = (line[field].strip() == 'T')

		# split field "Wirkstoff" by ";"
		line['wirkstoffe'] = [ wirkstoff.strip() for wirkstoff in line['wirkstoffe'].split(';') ]

		return line
	#--------------------------------------------------------
	def close(self):
		try: self.csv_file.close()
		except: pass
#============================================================
class cDrugDataSourceInterface(object):

	def switch_to_frontend(self):
		raise NotImplementedError
	#--------------------------------------------------------
	def select_drugs(self):
		raise NotImplementedError
	#--------------------------------------------------------
	def import_drugs_as_substances(self):
		raise NotImplementedError
	#--------------------------------------------------------
	def check_drug_interactions(self):
		raise NotImplementedError
#============================================================
class cGelbeListeInterface(cDrugDataSourceInterface):
	"""Support v8.2 CSV file interface only."""

	version = u'Gelbe Liste/MMI v8.2 interface'
	default_encoding = 'cp1252'
	bdt_line_template = u'%03d6210#%s\r\n'		# Medikament verordnet auf Kassenrezept
	bdt_line_base_length = 8
	startup_cmd = 'wine "C:\Programme\MMI PHARMINDEX\glwin.exe" "-KEEPBACKGROUND -CLOSETOTRAY -PRESCRIPTIONFILE %s"'
	default_csv_filename_wine = 'C:\\mmi2gm.csv'
	default_csv_filename_local = '~/.wine/drive_c/mmi2gm.csv'
	#--------------------------------------------------------
	def __init__(self):
		# use adjusted config.dat
		pass
	#--------------------------------------------------------
	def switch_to_frontend(self, csv_file=None, blocking=False):
		if csv_file is None:
			csv_file = cGelbeListeInterface.default_csv_filename_wine

		# must make sure csv file exists
		# also better to clean up interactions file
		#open(csv_file, 'wb').close()

		cmd = cGelbeListeInterface.startup_cmd % csv_file

		if not gmShellAPI.run_command_in_shell(command = cmd, blocking = blocking):
			_log.error('problem switching to the MMI drug database')
			return False

		return True
	#--------------------------------------------------------
	def select_drugs(self):
		if not self.switch_to_frontend(blocking = True):
			return None

		return cGelbeListeCSVFile(filename = cGelbeListeInterface.default_csv_filename_local)
	#--------------------------------------------------------
	def import_drugs_as_substances(self):
		selected_drugs = self.select_drugs()
		if selected_drugs is None:
			return False

		for drug in selected_drugs:
			for wirkstoff in drug['wirkstoffe']:
				# hopefully MMI eventually supports atc-per-substance in a drug :-(
				create_used_substance(substance = wirkstoff, atc = None)

		selected_drugs.close()
	#--------------------------------------------------------
	def check_drug_interactions(self, filename=None, pzn_list=None):
		"""For this to work the BDT interaction check must be configured in the MMI."""

		if len(pzn_list) < 2:
			return

		bdt_file = codecs.open(filename = filename, mode = 'wb', encoding = cGelbeListeInterface.default_encoding)

		for pzn in pzn_list:
			pzn = pzn.strip()
			lng = cGelbeListeInterface.bdt_line_base_length + len(pzn)
			bdt_file.write(cGelbeListeInterface.bdt_line_template % (lng, pzn))

		bdt_file.close()

		# FIXME: switch to IFAP
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
	'Gelbe Liste/MMI': cGelbeListeInterface
}
#============================================================
# substances in use across all patients
#------------------------------------------------------------
def create_used_substance(substance=None, atc=None):

	args = {'desc': substance, 'atc': atc}

	cmd = u'select pk from clin.consumed_substance where description = %(desc)s'
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])

	if len(rows) == 0:
		cmd = u'insert into clin.consumed_substance (description, atc_code) values (%(desc)s, gm.nullify_empty_string(%(atc)s)) returning pk'
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True)

	return rows[0][0]
#============================================================
class cConsumedSubstance(gmBusinessDBObject.cBusinessDBObject):
	"""Represents a substance currently taken by the patient."""

	_cmd_fetch_payload = u"select * from clin.v_pat_substance_intake where pk_substance_intake = %s"
	_cmds_store_payload = [
		# gm.nullify_empty_string()
#		u"""update clin.allergy_state set
#				last_confirmed = %(last_confirmed)s,
#				has_allergy = %(has_allergy)s,
#				comment = %(comment)s
#			where
#				pk = %(pk_allergy_state)s and
#				xmin = %(xmin_allergy_state)s""",
#		u"""select xmin_allergy_state from clin.v_pat_allergy_state where pk_allergy_state = %(pk_allergy_state)s"""
	]
	_updatable_fields = [
#		'last_confirmed',		# special value u'now' will set to datetime.datetime.now() in the local time zone
#		'has_allergy',			# verified against allergy_states (see above)
#		'comment'				# u'' maps to None / NULL
	]
#------------------------------------------------------------
def create_patient_consumed_substance(substance=None, atc=None, encounter=None, episode=None, preparation=None):

	args = {
		'desc': substance,
		'atc': atc,
		'enc': encounter,
		'epi': episode,
		'prep': preparation,
		'subst': create_used_substance(substance = substance, atc = atc)
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
	return cConsumedSubstance(aPK_obj = rows[0][0])
#============================================================
def get_substances_in_use():
	cmd = u'select * from clin.consumed_substance order by description'
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}])
	return rows
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
		mmi = cGelbeListeInterface()
		print mmi
		print "drug data source    :", sys.argv[2]
		print "interface definition:", mmi.version
		mmi.print_transfer_file(filename = sys.argv[2])
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
		mmi = cGelbeListeInterface()
		mmi.switch_to_frontend(blocking = False)
	#--------------------------------------------------------
	def test_mmi_select_drugs():
		mmi = cGelbeListeInterface()
		mmi_file = mmi.select_drugs()
		for drug in mmi_file:
			print "-------------"
			print '"%s" (ATC: %s / PZN: %s)' % (drug['name'], drug['atc'], drug['pzn'])
			for stoff in drug['wirkstoffe']:
				print " Wirkstoff:", stoff
			print drug
		mmi_file.close()
	#--------------------------------------------------------
	def test_mmi_import_substances():
		mmi = cGelbeListeInterface()
		mmi.import_drugs_as_substances()
	#--------------------------------------------------------
	def test_mmi_interaction_check():
		mmi = cGelbeListeInterface()
		print mmi
		print "interface definition:", mmi.version
		# Metoprolol + Hct vs Citalopram
		diclofenac = '7587712'
		phenprocoumon = '4421744'
		mmi.check_drug_interactions(filename = sys.argv[2], pzn_list = [diclofenac, phenprocoumon])
	#--------------------------------------------------------
	#--------------------------------------------------------
	def test_create_patient_consumed_substance():
		drug = create_patient_consumed_substance (
			substance = u'Whiskey',
			atc = u'no ATC available',
			encounter = 1,
			episode = 1,
			preparation = 'a nice glass'
		)
		print drug
	#--------------------------------------------------------
	if (len(sys.argv)) > 1 and (sys.argv[1] == 'test'):
		#test_MMI_interface()
		#test_MMI_file()
		#test_mmi_switch_to()
		test_mmi_select_drugs()
		#test_mmi_import_substances()
		#test_interaction_check()
		#test_create_patient_consumed_substance()
#============================================================
# $Log: gmMedication.py,v $
# Revision 1.6  2009-10-21 09:15:50  ncq
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