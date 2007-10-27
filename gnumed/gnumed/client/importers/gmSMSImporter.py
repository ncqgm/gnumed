
import sys


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmPG2, gmI18N, gmDateTime
from Gnumed.business import gmPerson


# define some defaults
external_id_type = u'SMS-Waage'
idx_date = 1
idx_gsm = 2
idx_sms = 3
soap_cat = u'o'
weight_template = u'aktuelles Gewicht::%s'
#==============================================
class cLogin:
	pass

def usage():
	print "use like this:"
	print ""
	print " gmSMSImporter.py <date> <gsm> <weight>"
	print " <weight> must be: <patient id>:::<weight value>"
	print ""
	print " current command line:", sys.argv

def run_importer():

	# map data from commandline
	try:
		date = sys.argv[idx_date]
		gsm = sys.argv[idx_gsm]
		sms = sys.argv[idx_sms]
		pk_patient, weight = sms.split(':::')
	except:
		return False

	# find patient by gsm
#	cmd1 = u"select dem.add_external_id_type(%(desc)s, %(org)s, %(ctxt)s)"
#	args1 = {'desc': external_id_type, 'org': u'gmSMSImporter.py', 'ctxt': u'p'}
#	cmd2 = u'select pk from dem.enum_ext_id_types where name = %(desc)s'
#	rows, idx = gmPG2.run_rw_queries (
#		queries = [
#			{'cmd': cmd1, 'args': args1},
#			{'cmd': cmd2, 'args': args1}
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

#	rows, idx = gmPG2.run_ro_queries (
#		queries = [{'cmd': cmd, 'args': args}],
#		return_data = True
#	)
#	if len(rows) == 0:
#		print "patient with GSM [%s] not found" % gsm
#		return False
#	pk_patient = rows[0][0]

	gmPerson.set_active_patient(patient = gmPerson.cIdentity(aPK_obj = pk_patient))

	# ensure structure of EMR
	curr_pat = gmPerson.gmCurrentPatient()
	emr = curr_pat.get_emr()
	epi = emr.add_episode(episode_name = u'Gewichtsmonitoring', is_open = False)

	# and import our stuff
	narr = emr.add_clin_narrative (
		note = weight_template % weight,
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
	login.database = u'gnumed_v8'
	login.host = u'salaam.homeunix.com'
	login.port = 5432
	login.user = u'any-doc'
	login.password = u'any-doc'
	gmPG2.set_default_login(login = login)

	if not run_importer():
		usage()
		sys.exit()
