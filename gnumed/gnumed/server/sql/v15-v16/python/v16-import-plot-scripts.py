#==============================================================
# GNUmed database schema change script
#
# License: GPL v2 or later
# Author: karsten.hilbert@gmx.net
# 
#==============================================================

#--------------------------------------------------------------
import os

from Gnumed.pycommon import gmPG2

#--------------------------------------------------------------
def run(conn=None):

	gmPG2.file2bytea (
		query = u"""
update ref.paperwork_templates
set
	data = %(data)s::bytea,
	external_version = 'v16.0'
where
	name_long = '1 test type plot script (GNUmed default)'
""",
		filename = os.path.join('..', 'sql', 'v15-v16', 'data', 'v16-gm2gpl-plot_1_test.scr'),
		conn = conn
	)

	gmPG2.file2bytea (
		query = u"""
update ref.paperwork_templates
set
	data = %(data)s::bytea,
	external_version = 'v16.0'
where
	name_long = '2 test types plot script (GNUmed default)'
""",
		filename = os.path.join('..', 'sql', 'v15-v16', 'data', 'v16-gm2gpl-plot_2_tests.scr'),
		conn = conn
	)

	return True
#==============================================================
