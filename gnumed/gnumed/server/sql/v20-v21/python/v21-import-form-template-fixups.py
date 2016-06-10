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

	# CD/DVD sleeve
	gmPG2.file2bytea (
		query = u"""
			UPDATE ref.paperwork_templates SET
				data = %(data)s::bytea,
				external_version = '21.0'
			WHERE
				name_long = 'CD/DVD sleeve [K.Hilbert]'""",
		filename = os.path.join('..', 'sql', 'v20-v21', 'data', 'v21-CD_DVD-sleeve.tex'),
		conn = conn
	)

	return True

#==============================================================
