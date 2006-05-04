"""Test for concurrency detection to work.
"""
#============================================================
# $Id: detect-concurrency.py,v 1.2 2006-05-04 09:49:20 ncq Exp $
__version__ = "$Revision: 1.2 $"
__author__ = "Karsten Hilbert"
__license__ = "GPL"

import time, sys

from Gnumed.pycommon import gmPG
from Gnumed.business import gmClinNarrative, gmPerson
#============================================================

db = gmPG.ConnectionPool()
pat = gmPerson.ask_for_patient()
#gmPerson.set_active_patient(patient=pat)
emr = pat.get_emr()
epi = emr.get_episodes()[0]

print "creating new narrative row"
note = emr.add_clin_narrative (
	note = 'testing concurrency detection: %s' % time.time(),
	episode = epi
)
print "primary key:", note['pk_narrative']
print "xmin before change:", note['xmin_clin_narrative']

print "waiting for narrative row (xmin) to change"
print "manually update the clin_narrative row with pk=<%s> in the database now" % note['pk_narrative']
cmd = "select xmin from clin_narrative where pk=%s"
while 1:
	data = gmPG.run_ro_query('historica', cmd, None, note['pk_narrative'])
	if data[0][0] != note['xmin_clin_narrative']:
		break

print "narrative row (xmin) changed"
print "xmin after change:", data[0][0]

print "provoking concurrency triggered integrity violation"

note['narrative'] = 'cannot change note to this line'
successful, data = note.save_payload()

if successful:
	sys.exit()
err, msg = data
if err == 2:
	print "concurrency triggered integrity violation detected"
	print "=================================================="
	if msg == 'c':
		print "someone *changed* our row"
	elif msg == 'd':
		print "someone *deleted* our row"
	for key in note.get_updatable_fields():
		if (note[key] != note.original_payload[key]) or (note[key] != note.modified_payload[key]):
			print 'originally: "%s"' % note.original_payload[key]
			print 'currently : "%s"' % note[key]
			print 'we wanted : "%s"' % note.modified_payload[key]
else:
	print "other error"

db.StopListeners()

#============================================================
# $Log: detect-concurrency.py,v $
# Revision 1.2  2006-05-04 09:49:20  ncq
# - get_clinical_record() -> get_emr()
# - adjust to changes in set_active_patient()
# - need explicit set_active_patient() after ask_for_patient() if wanted
#
# Revision 1.1  2005/04/11 17:59:41  ncq
# - write a test which proves our concurrency detection works
#
