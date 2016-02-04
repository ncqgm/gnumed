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

	# AMTS Medikationsplan
	gmPG2.file2bytea (
		query = u"""
			UPDATE ref.paperwork_templates SET
				data = %(data)s::bytea
			WHERE
				name_long = 'Medikationsplan (Deutschland, AMTS)'""",
		filename = os.path.join('..', 'sql', 'v20-v21', 'data', 'v21-Medikationsplan_AMTS-2.0.tex'),
		conn = conn
	)

	# AMTS Medikationsplan (nicht konform)
	gmPG2.file2bytea (
		query = u"""
			UPDATE ref.paperwork_templates SET
				data = %(data)s::bytea
			WHERE
				name_long = 'Medikationsplan (Deutschland, NICHT konform zu AMTS)'""",
		filename = os.path.join('..', 'sql', 'v20-v21', 'data', 'v21-Medikationsplan_AMTS-2.0-nicht_konform.tex'),
		conn = conn
	)

	# German current meds list
	gmPG2.file2bytea (
		query = u"""
			UPDATE ref.paperwork_templates SET
				data = %(data)s::bytea
			WHERE
				name_long = 'Liste aktueller Medikamente (GNUmed)'""",
		filename = os.path.join('..', 'sql', 'v20-v21', 'data', 'v21-aktuelle-Medikationsliste.tex'),
		conn = conn
	)

	# Begleitbrief
	gmPG2.file2bytea (
		query = u"""
			UPDATE ref.paperwork_templates SET
				data = %(data)s::bytea,
				external_version = '21.0'
			WHERE
				name_long = 'Begleitbrief ohne medizinische Daten [K.Hilbert]'""",
		filename = os.path.join('..', 'sql', 'v20-v21', 'data', 'v21-Begleitbrief.tex'),
		conn = conn
	)

	return True

#==============================================================
