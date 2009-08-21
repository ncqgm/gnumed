# -*- coding: utf8 -*-
"""Medication handling code.

license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmMedication.py,v $
# $Id: gmMedication.py,v 1.2 2009-08-21 09:56:37 ncq Exp $
__version__ = "$Revision: 1.2 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

import sys, logging, csv, codecs


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmBusinessDBObject
# gmPG2, gmTools


_log = logging.getLogger('gm.meds')
_log.info(__version__)
#============================================================
class cDrugDataSourceInterface(object):
	pass
#============================================================
class cGelbeListeInterface(cDrugDataSourceInterface):
	"""Support v8.2 CSV file interface only."""

	version = u'v8.2 CSV file interface'
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
		u't-rezept-pflicht',
		u'erstattbares_medizinprodukt',
		u'hilfsmittel'
	]

	def __init__(self):
		# use adjusted config.txt
		pass
	#--------------------------------------------------------
	def print_transfer_file(self, filename=None):

		csv_file = codecs.open(filename = filename, mode = 'rUb', encoding = cGelbeListeInterface.default_encoding)

		csv_lines = csv.DictReader (
			csv_file,
			fieldnames = cGelbeListeInterface.csv_fieldnames,
			delimiter = ';',
			quotechar = '"'
		)

		for line in csv_lines:
			print "--------------------------------------------------------------------"[:31]
			for key in cGelbeListeInterface.csv_fieldnames:
				tmp = ('%s                                                ' % key)[:30]
				print '%s: %s' % (tmp, line[key])

		csv_file.close()
#============================================================
class cConsumedSubstance(gmBusinessDBObject.cBusinessDBObject):
	"""Represents a substance currently taken by the patient."""

	_cmd_fetch_payload = u"select * from clin.v_pat_substance_intake where pk_substance_intake = %s"
	_cmds_store_payload = [
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
	#--------------------------------------------------------
	if (len(sys.argv)) > 1 and (sys.argv[1] == 'test'):
		test_MMI_interface()

#============================================================
# $Log: gmMedication.py,v $
# Revision 1.2  2009-08-21 09:56:37  ncq
# - start drug data source interfaces
# - add MMI/Gelbe Liste interface
#
# Revision 1.1  2009/05/12 12:02:01  ncq
# - start supporting current medications
#
#