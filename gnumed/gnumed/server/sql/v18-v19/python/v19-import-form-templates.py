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

	# invalid GKV-Rezept
	gmPG2.file2bytea (
		query = u"""
			update ref.paperwork_templates set
				data = %(data)s::bytea,
				external_version = '19.0'
			where
				name_long = 'ungültiges GKV-Rezept (GNUmed-Vorgabe)'""",
		filename = os.path.join('..', 'sql', 'v18-v19', 'data', 'v19-GNUmed-INVALID_default_GKV_Rezept_template.tex'),
		conn = conn
	)

	# Grünes Rezept
	gmPG2.file2bytea (
		query = u"""
			update ref.paperwork_templates set
				data = %(data)s::bytea,
				external_version = '19.0'
			where
				name_long = 'Grünes Rezept (DE, GNUmed-Vorgabe)'""",
		filename = os.path.join('..', 'sql', 'v18-v19', 'data', 'v19-GNUmed-Gruenes_Rezept_template.tex'),
		conn = conn
	)

	# medication list
	gmPG2.file2bytea (
		query = u"""
			UPDATE ref.paperwork_templates SET
				data = %(data)s::bytea,
				external_version = '19.0'
			WHERE
				name_long = 'Current medication list (GNUmed default)'
			""",
		filename = os.path.join('..', 'sql', 'v18-v19', 'data', 'v19-GNUmed-default_medication_list_template.tex'),
		conn = conn
	)

	return True

#==============================================================
