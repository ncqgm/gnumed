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
	# Begleitbrief
	gmPG2.file2bytea (
		query = u"""
			UPDATE ref.paperwork_templates SET
				data = %(data)s::bytea,
				external_version = '22.9'
			WHERE
				name_long = 'Begleitbrief ohne medizinische Daten [K.Hilbert]'""",
		filename = os.path.join('..', 'sql', 'v21-v22', 'data', 'v22-Begleitbrief.tex'),
		conn = conn
	)

	# vaccination history
	gmPG2.file2bytea (
		query = u"""
			UPDATE ref.paperwork_templates SET
				data = %(data)s::bytea,
				external_version = '22.4'
			where
				name_long = 'Vaccination history (GNUmed default)'""",
		filename = os.path.join('..', 'sql', 'v21-v22', 'data', 'v22-GNUmed-default_vaccination_history_template.tex'),
		conn = conn
	)

	# most recent vaccinations record
	gmPG2.file2bytea (
		query = u"""
			UPDATE ref.paperwork_templates SET
				data = %(data)s::bytea,
				external_version = '22.4'
			WHERE
				name_long = 'Most recent vaccinations (GNUmed default)'
			""",
		filename = os.path.join('..', 'sql', 'v21-v22', 'data', 'v22-GNUmed-default_latest_vaccinations_record_template.tex'),
		conn = conn
	)

	# medication list
	gmPG2.file2bytea (
		query = u"""
			UPDATE ref.paperwork_templates SET
				data = %(data)s::bytea,
				external_version = '22.4'
			WHERE
				name_long = 'Current medication list (GNUmed default)'
			""",
		filename = os.path.join('..', 'sql', 'v21-v22', 'data', 'v22-GNUmed-default_medication_list_template.tex'),
		conn = conn
	)

	# most recent lab results
	gmPG2.file2bytea (
		query = u"""
			UPDATE ref.paperwork_templates SET
				data = %(data)s::bytea,
				external_version = '22.10'
			WHERE
				name_long = 'lab: most recent results (GNUmed default)'
			""",
		filename = os.path.join('..', 'sql', 'v21-v22', 'data', 'v22-GNUmed-default-latest_lab-template.tex'),
		conn = conn
	)

	#------------------------------------
	return True

#==============================================================
