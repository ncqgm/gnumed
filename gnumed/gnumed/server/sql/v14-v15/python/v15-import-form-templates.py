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
update ref.paperwork_templates
set data = %(data)s::bytea
where name_long = 'EMR Journal (GNUmed default)'
""",
		filename = os.path.join('..', 'sql', 'v14-v15', 'data', 'GNUmed-default_emr_journal_template.tex'),
		conn = conn
	)

	return True

#==============================================================
