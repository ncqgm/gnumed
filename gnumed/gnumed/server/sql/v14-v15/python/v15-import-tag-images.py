#==============================================================
# GNUmed database schema change script
#
# License: GPL
# Author: karsten.hilbert@gmx.net
# 
#==============================================================
import os

from Gnumed.pycommon import gmPG2

#--------------------------------------------------------------
def run(conn=None):

	# emr journal
	gmPG2.file2bytea (
		query = u"""
UPDATE ref.person_tag
SET image = %(data)s::bytea
WHERE description = 'Occupation: astronaut'
""",
		filename = os.path.join('..', 'sql', 'v14-v15', 'data', 'johnny_automatic_astronaut_s_helmet.png'),
		conn = conn
	)

	return True

#==============================================================
