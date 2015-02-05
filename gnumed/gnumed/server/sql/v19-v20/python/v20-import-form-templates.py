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

	# PKV-Rechnung mit USt.
	gmPG2.file2bytea (
		query = u"""
			UPDATE ref.paperwork_templates SET
				data = %(data)s::bytea,
				external_version = '20.0'
			WHERE
				name_long = 'Privatrechnung mit USt. (GNUmed-Vorgabe Deutschland)'""",
		filename = os.path.join('..', 'sql', 'v19-v20', 'data', 'v20-GNUmed-default_invoice_template-de.tex'),
		conn = conn
	)

	# PKV-Rechnung ohne USt.
	gmPG2.file2bytea (
		query = u"""
			UPDATE ref.paperwork_templates SET
				data = %(data)s::bytea,
				external_version = '20.0'
			WHERE
				name_long = 'Privatrechnung ohne USt. (GNUmed-Vorgabe Deutschland)'""",
		filename = os.path.join('..', 'sql', 'v19-v20', 'data', 'v20-GNUmed-default_invoice_template-de_no_vat.tex'),
		conn = conn
	)

	# referral letter
	gmPG2.file2bytea (
		query = u"""
			UPDATE ref.paperwork_templates SET
				data = %(data)s::bytea,
				external_version = '20.0'
			WHERE
				name_long = 'Referral letter (GNUmed default) [Dr.Rogerio Luz]'""",
		filename = os.path.join('..', 'sql', 'v19-v20', 'data', 'v20-GNUmed-default_referral_letter_template.tex'),
		conn = conn
	)

	# Begleitbrief
	gmPG2.file2bytea (
		query = u"""
			UPDATE ref.paperwork_templates SET
				data = %(data)s::bytea,
				external_version = '20.0'
			WHERE
				name_long = 'Begleitbrief ohne medizinische Daten [K.Hilbert]'""",
		filename = os.path.join('..', 'sql', 'v19-v20', 'data', 'v20-Begleitbrief.tex'),
		conn = conn
	)

	# consultation report
	gmPG2.file2bytea (
		query = u"""
			UPDATE ref.paperwork_templates SET
				data = %(data)s::bytea,
				external_version = '20.4'
			WHERE
				name_long = 'Consultation report (GNUmed default)'""",
		filename = os.path.join('..', 'sql', 'v19-v20', 'data', 'v20-GNUmed-default_consultation_report_template.tex'),
		conn = conn
	)

	return True

#==============================================================
