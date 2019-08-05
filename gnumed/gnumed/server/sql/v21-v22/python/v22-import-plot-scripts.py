#==============================================================
# GNUmed database schema change script
#
# License: GPL v2 or later
# Author: karsten.hilbert@gmx.net
# 
#==============================================================
import os

from Gnumed.pycommon import gmPG2

#--------------------------------------------------------------
def run(conn=None):

	# update
	gmPG2.file2bytea (
		query = u"""
			UPDATE ref.paperwork_templates
			SET
				data = %(data)s::bytea,
				external_version = 'v22.7'
			WHERE
				name_long = '1 test type plot script (GNUmed default)'
			""",
		filename = os.path.join('..', 'sql', 'v21-v22', 'data', 'v22-gm2gpl-plot_one_test.gpl'),
		conn = conn
	)

	# update
	gmPG2.file2bytea (
		query = u"""
			UPDATE ref.paperwork_templates
			SET
				data = %(data)s::bytea,
				external_version = 'v22.7'
			WHERE
				name_long = '2 test types plot script (GNUmed default)'
			""",
		filename = os.path.join('..', 'sql', 'v21-v22', 'data', 'v22-gm2gpl-plot_two_tests.gpl'),
		conn = conn
	)

	# new
	gmPG2.file2bytea (
		query = u"""
			UPDATE ref.paperwork_templates
			SET
				data = %(data)s::bytea,
				external_version = 'v22.7'
			WHERE
				name_long = 'lab results plot: many test types (GNUmed default)'
			""",
		filename = os.path.join('..', 'sql', 'v21-v22', 'data', 'v22-gm2gpl-plot_many_tests.gpl'),
		conn = conn
	)

	return True
#==============================================================
