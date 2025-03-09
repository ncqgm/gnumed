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

	# Begleitbrief
	gmPG2.file2bytea (
		query = u"""
			UPDATE ref.paperwork_templates SET
				data = %(data)s::bytea,
				external_version = '23.0'
			WHERE
				name_long = 'Begleitbrief [K.Hilbert]'""",
		filename = os.path.join('..', 'sql', 'v22-v23', 'data', 'v23-Begleitbrief.tex'),
		conn = conn
	)
	return True

#==============================================================
