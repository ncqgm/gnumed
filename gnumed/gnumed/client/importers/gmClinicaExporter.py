#------------------------------------------------
# Clinica -> GNUmed-SQL exporter
#
# SQLite3 database
#
# http://pysqlite.googlecode.com/svn/doc/sqlite3.html
#
#------------------------------------------------

import sys
import os
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
Clinica_encounter_type = '[Clinica] encounter'
Clinica_episode = '[Clinica] episode'
#------------------------------------------------
def create_visit_sql(pk_patient, clinica_db):
	# CREATE TABLE visits (subsequent_checks TEXT, systemic_therapy TEXT, ID INTEGER PRIMARY KEY, laboratory_exam TEXT, diagnosis TEXT, histopathology TEXT, anamnesis TEXT, date TEXT, patient INTEGER, physical_examination TEXT, topical_therapy TEXT);

	curs = clinica_db.cursor()
	cmd = 'SELECT * FROM visits WHERE patient = %s' % pk_patient
	curs.execute(cmd)
	keys = [ r[0] for r in curs.description ]
	row = curs.fetchone()

	if row is None:
		print '-- no visits for patient'
		return

	row = dict(zip(keys, row))
	row['date'] = '%s-%s-%s:%s.%s' % (
		row['date'][:4],
		row['date'][5:7],
		row['date'][8:13],
		row['date'][14:16],
		row['date'][17:]
	)
	print '-- visit encounter'
	print "INSERT INTO clin.encounter (fk_patient, fk_type, started, last_affirmed) VALUES (currval('dem.identity_pk_seq'), (SELECT pk FROM clin.encounter_type WHERE description = '%s' LIMIT 1), '%s'::timestamp with time zone, '%s'::timestamp with time zone + '1m'::interval);" % (
		Clinica_encounter_type,
		row['date'],
		row['date']
	)
	print '-- import episode'
	print "INSERT INTO clin.episode (fk_health_issue, description, is_open, fk_encounter) VALUES (NULL, '%s', True, currval('clin.encounter_pk_seq'));" % Clinica_episode

	while row is not None:
		print '-- visit SOAP'
		print "INSERT INTO clin.clin_narrative (soap_cat, clin_when, narrative, fk_encounter, fk_episode) VALUES ('s', '%s'::timestamp with time zone, E'%s', currval('clin.encounter_pk_seq'), currval('clin.episode_pk_seq'));" % (
			row['date'],
			row['anamnesis']
		)
		sOap = _('%s\\n\\nLab work:\\n%s\\n\\nHistopathology:\\n%s') % (
			row['physical_examination'],
			row['laboratory_exam'],
			row['histopathology']
		)
		print "INSERT INTO clin.clin_narrative (soap_cat, clin_when, narrative, fk_encounter, fk_episode) VALUES ('o', '%s'::timestamp with time zone, E'%s', currval('clin.encounter_pk_seq'), currval('clin.episode_pk_seq'));" % (
			row['date'],
			sOap
		)
		print "INSERT INTO clin.clin_narrative (soap_cat, clin_when, narrative, fk_encounter, fk_episode) VALUES ('a', '%s'::timestamp with time zone, E'%s', currval('clin.encounter_pk_seq'), currval('clin.episode_pk_seq'));" % (
			row['date'],
			row['diagnosis']
		)
		soaP = _('Topical therapy:\\n%s\\n\\nSystemic therapy:\\n%s\\n\\nSubsequent checks:\\n%s') % (
			row['topical_therapy'],
			row['systemic_therapy'],
			row['subsequent_checks']
		)
		print "INSERT INTO clin.clin_narrative (soap_cat, clin_when, narrative, fk_encounter, fk_episode) VALUES ('p', '%s'::timestamp with time zone, E'%s', currval('clin.encounter_pk_seq'), currval('clin.episode_pk_seq'));" % (
			row['date'],
			soaP
		)

		row = curs.fetchone()
		if row is not None:
			row['date'] = '%s-%s-%s:%s.%s' % (
				row['date'][:4],
				row['date'][5:7],
				row['date'][8:13],
				row['date'][14:16],
				row['date'][17:]
			)
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
		'Clinica [#%s]' % row['ID'],
		none_equivalents = [None, ''],
		function4value = ('strip', None)
	)

	row['given_name'] = gmTools.coalesce (
		row['given_name'],
		'#%s' % row['ID'],
		none_equivalents = [None, ''],
		function4value = ('strip', None)
	)

	row['identification_code'] = gmTools.coalesce (
		row['identification_code'],
		None,
		none_equivalents = [None, ''],
		function4value = ('strip', None)
	)

	row['phone'] = gmTools.coalesce (
		row['phone'],
		None,
		none_equivalents = [None, ''],
		function4value = ('strip', None)
	)

	row['birth_date'] = gmTools.coalesce (
		row['birth_date'],
		None,
		none_equivalents = [None, ''],
		function4value = ('strip', None)
	)
	row['birth_date'] = '%s-%s-%s:%s.%s' % (
		row['birth_date'][:4],
		row['birth_date'][5:7],
		row['birth_date'][8:13],
		row['birth_date'][14:16],
		row['birth_date'][17:]
	)

	row['residence_address'] = gmTools.coalesce (
		row['residence_address'],
		None,
		none_equivalents = [None, ''],
		function4value = ('strip', None)
	)

	return row
#------------------------------------------------
def create_gnumed_import_sql(filename):
	# CREATE TABLE patients (gender TEXT, doctor INTEGER, surname TEXT, ID INTEGER PRIMARY KEY, identification_code TEXT, phone TEXT, given_name TEXT, birth_date TEXT, residence_address TEXT);

	print ''
	print 'set default_transaction_read_only to off;'
	print ''
	print "begin;"
	print ''

	now = gmDateTime.pydt_now_here().isoformat()

	clinica_db = sqlite.connect(database = filename)
	curs = clinica_db.cursor()
	cmd = 'select * from patients'
	curs.execute(cmd)
	keys = [ r[0] for r in curs.description ]
	row = curs.fetchone()

	if row is None:
		print "-- no patients in database"
		return

	row = sanitize_patient_row(dict(zip(keys, row)))
	print '-- import-related encounter type'
	print "INSERT INTO clin.encounter_type (description) SELECT '%s' WHERE NOT EXISTS (SELECT 1 FROM clin.encounter_type WHERE description = '%s' LIMIT 1);" % (
		Clinica_encounter_type,
		Clinica_encounter_type
	)

	while row is not None:
		print ''
		print '-- next patient'
		print "INSERT INTO dem.identity (gender, dob, comment) VALUES ('%s', NULL, 'Clinica import @ %s');" % (
			row['gender'],
			now
		)
		if row['birth_date'] is not None:
			if row['birth_date'].strip() != '':
				print """UPDATE dem.identity SET dob = '%s'::timestamp with time zone WHERE pk = currval('dem.identity_pk_seq');""" % row['birth_date']
		print """SELECT dem.add_name(currval('dem.identity_pk_seq')::integer, '%s'::text, '%s'::text, True);""" % (
			row['given_name'],
			row['surname']
		)
		print """INSERT INTO dem.lnk_identity2ext_id (id_identity, external_id, fk_origin) VALUES (currval('dem.identity_pk_seq'), '%s', dem.add_external_id_type('Clinica primary key', 'Clinica EMR'));""" % row['ID']
		if row['identification_code'] is not None:
			print """INSERT INTO dem.lnk_identity2ext_id (id_identity, external_id, fk_origin) VALUES (currval('dem.identity_pk_seq'), '%s', dem.add_external_id_type('Clinica-external ID', 'Clinica EMR'));""" % row['identification_code']
		if row['phone'] is not None:
			print """INSERT INTO dem.lnk_identity2comm (fk_identity, url, fk_type) VALUES (currval('dem.identity_pk_seq'), '%s', dem.create_comm_type('homephone'));""" % row['phone']
		if row['residence_address'] is not None:
			print """INSERT INTO dem.lnk_identity2comm (fk_identity, url, fk_type) VALUES (currval('dem.identity_pk_seq'), '%s', dem.create_comm_type('Clinica address'));""" % row['residence_address']

		create_visit_sql(row['ID'], clinica_db)

		row = curs.fetchone()
		if row is not None:
			row = sanitize_patient_row(dict(zip(keys, row)))

	print ''
	print '-- comment this out when you are ready to *really* run the data import:'
	print 'rollback;'
	print ''
	print 'commit;'
#------------------------------------------------
gmDateTime.init()
gmI18N.activate_locale()
gmI18N.install_domain(domain = 'gnumed')
try:
	filename = sys.argv[1]
	print '-- exporting from DB file:', sys.argv[1]
except IndexError:
	filename = os.path.expanduser('~/.config/clinica/clinica.db')
	print '-- exporting from Clinica default DB:', filename
create_gnumed_import_sql(filename)
