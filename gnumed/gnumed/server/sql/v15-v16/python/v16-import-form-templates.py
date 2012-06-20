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

	# medication list
	gmPG2.file2bytea (
		query = u"""
update ref.paperwork_templates
set
	data = %(data)s::bytea,
	external_version = 'v16.0'
where
	name_long = 'Current medication list (GNUmed default)'
""",
		filename = os.path.join('..', 'sql', 'v15-v16', 'data', 'v16-GNUmed-default_medication_list_template.tex'),
		conn = conn
	)


	# Formularkopf
	gmPG2.file2bytea (
		query = u"""
update ref.paperwork_templates
set
	data = %(data)s::bytea,
	external_version = 'v16.0'
where
	name_long = 'Formularkopf (GNUmed-Vorgabe)'
""",
		filename = os.path.join('..', 'sql', 'v15-v16', 'data', 'v16-GNUmed-default_GKV_Formularkopf_template.tex'),
		conn = conn
	)


	return True

#==============================================================
