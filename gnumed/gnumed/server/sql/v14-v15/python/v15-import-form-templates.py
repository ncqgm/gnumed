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

	# medical statement (certificate)
	gmPG2.file2bytea (
		query = u"""
update ref.paperwork_templates
set data = %(data)s::bytea
where name_long = 'Medical statement (GNUmed default)'
""",
		filename = os.path.join('..', 'sql', 'v14-v15', 'data', 'GNUmed-default_medical_statement_template.tex'),
		conn = conn
	)

	# Bescheinigung
	gmPG2.file2bytea (
		query = u"""
update ref.paperwork_templates
set data = %(data)s::bytea
where name_long = 'Bescheinigung (GNUmed-Vorgabe)'
""",
		filename = os.path.join('..', 'sql', 'v14-v15', 'data', 'GNUmed-default_bescheinigung_template.tex'),
		conn = conn
	)

	# referral letter
	gmPG2.file2bytea (
		query = u"""
update ref.paperwork_templates
set
	data = %(data)s::bytea,
	external_version = 'v15'
where name_long = 'Referral letter (GNUmed default) [Dr.Rogerio Luz]'
""",
		filename = os.path.join('..', 'sql', 'v14-v15', 'data', 'GNUmed-default_referral_letter_template.tex'),
		conn = conn
	)

	# consultation report
	gmPG2.file2bytea (
		query = u"""
update ref.paperwork_templates
set
	data = %(data)s::bytea,
	external_version = 'v15'
where name_long = 'Consultation report (GNUmed default)'
""",
		filename = os.path.join('..', 'sql', 'v14-v15', 'data', 'GNUmed-default_consultation_report_template.tex'),
		conn = conn
	)

	return True
#==============================================================
