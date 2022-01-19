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

	#------------------------------------
	# recalls
	gmPG2.file2bytea (
		query = u"""
			UPDATE ref.paperwork_templates SET
				data = %(data)s::bytea,
				external_version = '22.17'
			WHERE
				name_long = 'Upcoming Recalls (GNUmed default)'""",
		filename = os.path.join('..', 'sql', 'v21-v22', 'data', 'v22-GNUmed-default_recalls_template.tex'),
		conn = conn
	)
	#------------------------------------
	return True

#==============================================================
