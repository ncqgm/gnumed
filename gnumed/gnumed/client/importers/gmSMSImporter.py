
import sys, datetime as dt


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmI18N, gmDateTime
from Gnumed.business import gmPerson


# define some defaults
external_id_type = 'SMS-Waage'
idx_date = 1
idx_gsm = 2
idx_sms = 3
soap_cat = 'o'
weight_template = 'aktuelles Gewicht (%s)::%s'
#==============================================
class cLogin:
	pass

def usage():
	print("use like this:")
	print("")
	print(" gmSMSImporter.py <date> <gsm> <weight>")
	print(" <weight> must be: <patient id>:::<weight value>")
	print("")
	print(" current command line:", sys.argv)

def run_importer():

	# map data from commandline
	try:
		date = sys.argv[idx_date]
		gsm = sys.argv[idx_gsm]
		sms = sys.argv[idx_sms]
		pk_patient, weight = sms.split(':::')
	except Exception:
		return False

	print(date, gsm)

	# find patient by gsm
#	cmd1 = u"select dem.add_external_id_type(%(desc)s, %(org)s)"
#	args1 = {'desc': external_id_type, 'org': u'gmSMSImporter.py'}
#	cmd2 = u'select pk from dem.enum_ext_id_types where name = %(desc)s'
#	rows = gmPG2.run_rw_queries (
#		queries = [
#			{'sql': cmd1, 'args': args1},
#			{'sql': cmd2, 'args': args1}
#		],
#		return_data = True
#	)
#	ext_id_pk = rows[0][0]

#	cmd = u"""
#select li2id.id_identity
#from dem.lnk_identity2ext_id li2id
#where
#	li2id.external_id = %(id)s and
#	fk_origin = %(src)s"""
#	args = {'id': gsm, 'src': ext_id_pk}

#	rows = gmPG2.run_ro_queries (
#		queries = [{'sql': cmd, 'args': args}],
#		return_data = True
#	)
#	if len(rows) == 0:
#		print "patient with GSM [%s] not found" % gsm
#		return False
#	pk_patient = rows[0][0]

	gmPerson.set_active_patient(patient = gmPerson.cPerson(aPK_obj = pk_patient))

	# ensure structure of EMR
	curr_pat = gmPerson.gmCurrentPatient()
	emr = curr_pat.emr
	epi = emr.add_episode(episode_name = 'Gewichtsmonitoring', is_open = False)

	# and import our stuff
	emr.add_clin_narrative (
		note = weight_template % (dt.datetime.now().strftime('%X'), weight),
		soap_cat = soap_cat,
		episode = epi
	)

	return True
#==============================================
if __name__ == '__main__':

	gmI18N.activate_locale()
	gmI18N.install_domain(domain = 'gnumed')
	gmDateTime.init()

	login = cLogin()
	login.database = 'gnumed_v9'
	login.host = 'publicdb.gnumed.de'
	login.port = 5432
	login.user = 'any-doc'
	login.password = 'any-doc'

	if not run_importer():
		usage()
		sys.exit()
