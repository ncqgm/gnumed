# coding: utf8
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

	# vaccination history
	gmPG2.file2bytea (
		query = u"""
			update ref.paperwork_templates set
				data = %(data)s::bytea,
				external_version = '18.0'
			where
				name_long = 'Upcoming Recalls (GNUmed default)'""",
		filename = os.path.join('..', 'sql', 'v17-v18', 'data', 'v18-GNUmed-default_recalls_template.tex'),
		conn = conn
	)

	return True

#==============================================================
