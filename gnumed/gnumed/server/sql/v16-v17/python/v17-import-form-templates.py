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

	# medication list
	gmPG2.file2bytea (
		query = u"""
			UPDATE ref.paperwork_templates SET
				data = %(data)s::bytea,
				external_version = '17.0'
			WHERE
				name_long = 'Current medication list (GNUmed default)'
			""",
		filename = os.path.join('..', 'sql', 'v16-v17', 'data', 'v17-GNUmed-default_medication_list_template.tex'),
		conn = conn
	)

	# most recent vaccinations record
	gmPG2.file2bytea (
		query = u"""
			UPDATE ref.paperwork_templates SET
				data = %(data)s::bytea,
				external_version = '17.0'
			WHERE
				name_long = 'Most recent vaccinations (GNUmed default)'
			""",
		filename = os.path.join('..', 'sql', 'v16-v17', 'data', 'v17-GNUmed-default_latest_vaccinations_record_template.tex'),
		conn = conn
	)

	# vaccination history
	gmPG2.file2bytea (
		query = u"""
			update ref.paperwork_templates set
				data = %(data)s::bytea,
				external_version = '17.0'
			where
				name_long = 'Vaccination history (GNUmed default)'""",
		filename = os.path.join('..', 'sql', 'v16-v17', 'data', 'v17-GNUmed-default_vaccination_history_template.tex'),
		conn = conn
	)

	# Vorsorgevollmacht
	gmPG2.file2bytea (
		query = u"""
			UPDATE ref.paperwork_templates SET
				data = %(data)s::bytea
			WHERE
				name_long = 'Vorsorgevollmacht (Bundesministerium für Justiz, Deutschland)'""",
		filename = os.path.join('..', 'sql', 'v16-v17', 'data', 'DE_BMJ-Vorsorgevollmacht_Vorlage-11_2009.pdf'),
		conn = conn
	)

	# PKV-Rechnung mit USt.
	gmPG2.file2bytea (
		query = u"""
			UPDATE ref.paperwork_templates SET
				data = %(data)s::bytea
			WHERE
				name_long = 'Privatrechnung mit USt. (GNUmed-Vorgabe Deutschland)'""",
		filename = os.path.join('..', 'sql', 'v16-v17', 'data', 'v17-GNUmed-default_invoice_template-de.tex'),
		conn = conn
	)

	# PKV-Rechnung ohne USt.
	gmPG2.file2bytea (
		query = u"""
			UPDATE ref.paperwork_templates SET
				data = %(data)s::bytea
			WHERE
				name_long = 'Privatrechnung ohne USt. (GNUmed-Vorgabe Deutschland)'""",
		filename = os.path.join('..', 'sql', 'v16-v17', 'data', 'v17-GNUmed-default_invoice_template-de_no_vat.tex'),
		conn = conn
	)

	return True

#==============================================================
