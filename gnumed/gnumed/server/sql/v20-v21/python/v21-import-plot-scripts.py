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
	external_version = 'v21.0'
where
	name_long = '1 test type plot script (GNUmed default)'
""",
		filename = os.path.join('..', 'sql', 'v20-v21', 'data', 'v21-gm2gpl-plot_one_test.gpl'),
		conn = conn
	)

	gmPG2.file2bytea (
		query = u"""
update ref.paperwork_templates
set
	data = %(data)s::bytea,
	external_version = 'v21.0'
where
	name_long = '2 test types plot script (GNUmed default)'
""",
		filename = os.path.join('..', 'sql', 'v20-v21', 'data', 'v21-gm2gpl-plot_two_tests.gpl'),
		conn = conn
	)

	return True
#==============================================================
