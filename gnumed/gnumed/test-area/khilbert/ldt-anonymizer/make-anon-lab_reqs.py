# -*- coding: latin-1 -*-
"""GnuMed LDT anonymizer.

This script anonymizes German pathology result
files in LDT format.

copyright: authors
"""
#===============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/khilbert/ldt-anonymizer/make-anon-lab_reqs.py,v $
# $Id: make-anon-lab_reqs.py,v 1.3 2004-06-26 07:33:55 ncq Exp $
__version__ = "$Revision: 1.3 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL, details at http://www.gnu.org"

import fileinput, sys, random, time

from Gnumed.pycommon import gmPG, gmLoginInfo, gmLog
from Gnumed.business import gmPathLab, gmPatient

from Gnumed.pycommon.gmPyCompat import *

_log = gmLog.gmDefLog
_log.SetAllLogLevels(gmLog.lData)

def usage():
	print """use like this:"
$> python make-anon-lab_reqs <ldt-datei>"

This will generate lab requests for all sample IDs found
in <ldt-datei>. All requests will belong to Laborata
Testwoman.
"""
	sys.exit()	

print "accessing patient Laborata Testwoman"
# set encoding
gmPG.set_default_client_encoding('latin1')
# setup login defs
auth_data = gmLoginInfo.LoginInfo(
	user = 'any-doc',
	passwd = 'any-doc',
	host = 'hherb.com',
	port = 5432,
	database = 'gnumed'
)
backend = gmPG.ConnectionPool(login = auth_data)

pat_data = {
	'lastnames': 'Testwoman',
	'firstnames': 'Laborata',
	'gender': 'f'
}
searcher = gmPatient.cPatientSearcher_SQL()
pat_ids = searcher.get_patient_ids(search_dict = pat_data)

if len(pat_ids) == 0:
	print "cannot find Laborata Testwoman"
	sys.exit()
if len(pat_ids) > 1:
	print "more than one patient for Laborata Testwoman"
	sys.exit()

patid = pat_ids[0]
print "Laborata Testwoman has ID [%s]" % patid
pat = gmPatient.gmCurrentPatient(aPKey=patid)
emr = pat.get_clinical_record()
enc_id = emr.get_active_encounter()['pk_encounter']
print "encounter", enc_id
epi_id = emr.get_active_episode()['pk_episode']
print "episode", epi_id

infilename = sys.argv[1]
print "generating request IDs from LDT file [%s]" % infilename

for line in fileinput.input(infilename):
	tmp = line.replace('\r','')
	tmp = tmp.replace('\n','')
	line_type = tmp[3:7]
	line_data = tmp[7:]
	if line_type == '8310':
		_log.Log(gmLog.lInfo, "creating lab request for ID [%s]" % line_data)
		print "creating lab request for ID [%s]" % line_data
		status = emr.add_lab_request(
			lab = 'your own practice',
			req_id = line_data
		)
		if status is None:
			print "ERROR: failed"
		else:
			print "INFO: success"

pat.cleanup()
del pat
del emr
backend.StopListeners()
print "done"

#===============================================================
# $Log: make-anon-lab_reqs.py,v $
# Revision 1.3  2004-06-26 07:33:55  ncq
# - id_episode -> fk/pk_episode
#
# Revision 1.2  2004/06/23 21:12:43  ncq
# - cleanup
# - use emr.add_lab_request()
# - properly use emr.cleanup()/patient.cleanup()
#
# Revision 1.1  2004/06/02 00:08:16  ncq
# - tailor to Laborata Testwoman
#
