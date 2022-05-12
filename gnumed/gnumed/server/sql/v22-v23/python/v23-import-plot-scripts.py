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
				external_version = 'v23.0'
			WHERE
				name_long = 'lab results plot: many test types (GNUmed default)'
			""",
		filename = os.path.join('..', 'sql', 'v22-v23', 'data', 'v23-gm2gpl-plot_many_tests.gpl'),
		conn = conn
	)

	return True
#==============================================================
