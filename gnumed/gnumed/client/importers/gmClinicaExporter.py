#------------------------------------------------
# Clinica -> GNUmed-SQL exporter
#
# SQLite3 database:
#
# CREATE TABLE config (id INTEGER PRIMARY KEY, key TEXT, value TEXT);
# CREATE TABLE doctors (surname TEXT, ID INTEGER PRIMARY KEY, phone TEXT, mobile TEXT, given_name TEXT);
#
# http://pysqlite.googlecode.com/svn/doc/sqlite3.html
#
#------------------------------------------------

import sys
import logging
import pysqlite2.dbapi2 as sqlite


# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')

from Gnumed.pycommon import gmLog2
from Gnumed.pycommon import gmI18N
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDateTime


_log = logging.getLogger('gm-clinica')


gender_map = {'MALE': 'm', 'FEMALE': 'f'}
#------------------------------------------------
def create_visit_sql(pk_patient, clinica_db):
	# CREATE TABLE visits (subsequent_checks TEXT, systemic_therapy TEXT, ID INTEGER PRIMARY KEY, laboratory_exam TEXT, diagnosis TEXT, histopathology TEXT, anamnesis TEXT, date TEXT, patient INTEGER, physical_examination TEXT, topical_therapy TEXT);

	curs = clinica_db.cursor()
	cmd = u'SELECT * FROM visits WHERE patient = %s' % pk_patient
	curs.execute(cmd)
	keys = [ r[0] for r in curs.description ]
	row = dict(zip(keys, curs.fetchone()))
	if row is not None:
		# create "import" encounter
		# create "import" episode
		#print "creating encounter"
		pass
	while row is not None:
		# create visit encounter

		# loop over SOAP:
		print u"""INSERT INTO clin.clin_narrative (soap_cat, clin_when, fk_encounter, fk_episode, narrative) VALUES ('s', '%s'::timestamp with time zone, E'%s', currval('clin.encounter_pk_seq'), currval('clin.episode_pk_seq'));""" % (
			row['date'],
			row['anamnesis']
		)
		sOap = _('%s\\n\\nLab work:\\n%s\\n\\nHistopathology:\\n%s') % (
			row['physical_examination'],
			row['laboratory_exam'],
			row['histopathology']
		)
		print u"""INSERT INTO clin.clin_narrative (soap_cat, clin_when, fk_encounter, fk_episode, narrative) VALUES ('o', '%s'::timestamp with time zone, E'%s', currval('clin.encounter_pk_seq'), currval('clin.episode_pk_seq'));""" % (
			row['date'],
			sOap
		)
		print u"""INSERT INTO clin.clin_narrative (soap_cat, clin_when, fk_encounter, fk_episode, narrative) VALUES ('a', '%s'::timestamp with time zone, E'%s', currval('clin.encounter_pk_seq'), currval('clin.episode_pk_seq'));""" % (
			row['date'],
			row['diagnosis']
		)
		soaP = _('Topical therapy:\\n%s\\n\\nSystemic therapy:\\n%s\\n\\nSubsequent checks:\\n%s') % (
			row['topical_therapy'],
			row['systemic_therapy'],
			row['subsequent_checks']
		)
		print u"""INSERT INTO clin.clin_narrative (soap_cat, clin_when, fk_encounter, fk_episode, narrative) VALUES ('p', '%s'::timestamp with time zone, E'%s', currval('clin.encounter_pk_seq'), currval('clin.episode_pk_seq'));""" % (
			row['date'],
			soaP
		)

		row = curs.fetchone()
#------------------------------------------------
def sanitize_patient_row(row):
	# CREATE TABLE patients (gender TEXT, doctor INTEGER, surname TEXT, ID INTEGER PRIMARY KEY, identification_code TEXT, phone TEXT, given_name TEXT, birth_date TEXT, residence_address TEXT);

	if row['gender'] is None:
		row['gender'] = 'h'
	elif row['gender'].upper() not in ['MALE', 'FEMALE']:
		row['gender'] = 'h'
	else:
		row['gender'] = gender_map[row['gender']]

	row['surname'] = gmTools.coalesce (
		row['surname'],
		u'Clinica [#%s]' % row['ID'],
		none_equivalents = [None, u''],
		function_initial = ('strip', None)
	)

	row['given_name'] = gmTools.coalesce (
		row['given_name'],
		u'#%s' % row['ID'],
		none_equivalents = [None, u''],
		function_initial = ('strip', None)
	)

	row['identification_code'] = gmTools.coalesce (
		row['identification_code'],
		None,
		none_equivalents = [None, u''],
		function_initial = ('strip', None)
	)

	row['phone'] = gmTools.coalesce (
		row['phone'],
		None,
		none_equivalents = [None, u''],
		function_initial = ('strip', None)
	)

	row['birth_date'] = gmTools.coalesce (
		row['birth_date'],
		None,
		none_equivalents = [None, u''],
		function_initial = ('strip', None)
	)

	row['residence_address'] = gmTools.coalesce (
		row['residence_address'],
		None,
		none_equivalents = [None, u''],
		function_initial = ('strip', None)
	)

	return row
#------------------------------------------------
def create_gnumed_import_sql():
	# CREATE TABLE patients (gender TEXT, doctor INTEGER, surname TEXT, ID INTEGER PRIMARY KEY, identification_code TEXT, phone TEXT, given_name TEXT, birth_date TEXT, residence_address TEXT);

	print "begin;"

	now = gmDateTime.pydt_now_here().isoformat()

	clinica_db = sqlite.connect(database = sys.argv[1])
	curs = clinica_db.cursor()
	cmd = u'select * from patients'
	curs.execute(cmd)
	keys = [ r[0] for r in curs.description ]
	row = dict(zip(keys, curs.fetchone()))
	if row is not None:
		row = sanitize_patient_row(row)
		u"""
		INSERT INTO clin.encounter_type (description) SELECT '' WHERE NOT EXISTS(SELECT xxxxxxxxxx)
		"""
		# ensure encounter type available

	while row is not None:
		print u''
		print u'-- next patient'
		print u"""INSERT INTO dem.identity (gender, dob, comment) VALUES ('%s', NULL, 'Clinica import @ %s');""" % (
			row['gender'],
			now
		)
		if row['birth_date'] is not None:
			if row['birth_date'].strip() != u'':
				print u"""UPDATE dem.identity SET dob = '%s'::timestamp with time zone WHERE pk = currval('dem.identity_pk_seq');""" % row['birth_date']
		print u"""SELECT dem.add_name(currval('dem.identity_pk_seq'), '%s', '%s', True);""" % (
			row['given_name'],
			row['surname']
		)
		print u"""INSERT INTO dem.lnk_identity2ext_id (id_identity, external_id, fk_origin) VALUES (currval('dem.identity_pk_seq'), '%s', dem.add_external_id_type('Clinica primary key', 'Clinica EMR'));""" % row['ID']
		if row['identification_code'] is not None:
			print u"""INSERT INTO dem.lnk_identity2ext_id (id_identity, external_id, fk_origin) VALUES (currval('dem.identity_pk_seq'), '%s', dem.add_external_id_type('Clinica-external ID', 'Clinica EMR'));""" % row['identification_code']
		if row['phone'] is not None:
			print u"""INSERT INTO dem.lnk_identity2phone (fk_identity, url, fk_type) VALUES (currval('dem.identity_pk_seq'), '%s', dem.create_comm_type('homephone'));""" % row['phone']
		if row['residence_address'] is not None:
			print u"""INSERT INTO dem.lnk_identity2phone (fk_identity, url, fk_type) VALUES (currval('dem.identity_pk_seq'), '%s', dem.create_comm_type('Clinica address'));""" % row['residence_address']

		create_visit_sql(row['ID'], clinica_db)

		row = sanitize_patient_row(dict(zip(keys, curs.fetchone())))

	print ''
	print 'commit;'
#------------------------------------------------
gmDateTime.init()
gmI18N.activate_locale()
gmI18N.install_domain(domain = 'gnumed')
create_gnumed_import_sql()
