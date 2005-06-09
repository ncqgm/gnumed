"""Test for concurrency detection to work.

Run this script in many parallel instances against one
GNUmed database in order to torture test the business
object concurrency conflict detection.
"""
#============================================================
# $Id: concurrency-torture-test.py,v 1.1 2005-06-09 21:16:50 ncq Exp $
__version__ = "$Revision: 1.1 $"
__author__ = "Karsten Hilbert"
__license__ = "GPL"

import time, sys, random

from Gnumed.pycommon import gmPG
from Gnumed.business import gmClinNarrative

magic_string = 'xxxxx_detection_torture_test_magic_cookie_xxxxx'
#============================================================
def wait_random(max_time=1000):
	val = random.randrange(0, max_time, 1)
	time.sleep(float(val) / 1000)
#------------------------------------------------------------
def create_narr():
	# don't worry about which patient we chose, just be consistent
	cmd = "select pk_episode, pk_encounter from v_pat_narrative limit 1"
	data = gmPG.run_ro_query('historica', cmd)
	narr = gmClinNarrative.create_clin_narrative (
		narrative = magic_string,
		soap_cat = 's',
		episode_id = data[0][0],
		encounter_id = data[0][1]
	)
	return narr
#------------------------------------------------------------
def find_narr():
	cmd = "select pk from clin_narrative where narrative = %s limit 1"
	data = gmPG.run_ro_query (
		'clinical',
		cmd,
		None,
		magic_string
	)
	if len(data) == 0:
		return create_narr()
	return gmClinNarrative.cNarrative(aPK_obj=data[0][0])
#------------------------------------------------------------
def mutate_narr(narr=None):
	if narr is None:
		return
	wait_random(1000)
	if narr['is_rfe']:
		narr['is_rfe'] = False
	else:
		narr['soap_cat'] = 's'
		narr['is_rfe'] = True
	wait_random(125)
	successful, data = narr.save_payload()
	if successful:
		return
	err, msg = data
	if err == 2:
		print "==> concurrency triggered integrity violation detected"
		if msg == 'c':
			print " => someone CHANGED our row ..."
		elif msg == 'd':
			print " => someone DELETED our row ..."
		elif msg == 'l':
			print " => someone LOCKED our row for update ..."
		else:
			print " => unknown cause: ", msg
		for key in narr.get_updatable_fields():
			if (narr[key] != narr.original_payload[key]) or (narr[key] != narr.modified_payload[key]):
				print 'conflict in: [%s]' % key
				print 'originally : "%s"' % narr.original_payload[key]
				print 'currently  : "%s"' % narr[key]
				print 'we wanted  : "%s"' % narr.modified_payload[key]
	else:
		print "=> another error"
		print "error", err
		print "message", msg
	return

#============================================================
# main
#------------------------------------------------------------
if __name__ == '__main__':
	print "========================================="
	print "GNUmed concurrency detection torture test"
	print "========================================="
	loops = int(sys.argv[1])
	conn_pool = gmPG.ConnectionPool()
	print "Seeding pseudo-random number generator ..."
	random.seed()
	print "Initial random delay ..."
	wait_random(2000)

	print "Running torture loop %s times ..." % loops
	for loop in range(loops):
		print '.'
		narr = find_narr()
		mutate_narr(narr)

	print "Cleaning up ..."
	conn_pool.StopListeners()
	print "Done."

#============================================================
# $Log: concurrency-torture-test.py,v $
# Revision 1.1  2005-06-09 21:16:50  ncq
# - torture-test our concurrency conflict detection
#
