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
				external_version = '22.9'
			WHERE
				name_long = 'Begleitbrief ohne medizinische Daten [K.Hilbert]'""",
		filename = os.path.join('..', 'sql', 'v21-v22', 'data', 'v22-Begleitbrief.tex'),
		conn = conn
	)

	# German current meds list
	gmPG2.file2bytea (
		query = u"""
			UPDATE ref.paperwork_templates SET
				data = %(data)s::bytea,
				external_version = '22.4'
			WHERE
				name_long = 'Liste aktueller Medikamente (GNUmed)'""",
		filename = os.path.join('..', 'sql', 'v21-v22', 'data', 'v22-aktuelle-Medikationsliste.tex'),
		conn = conn
	)

	# GNUmed icons
	gmPG2.file2bytea (
		query = u"""
			update ref.keyword_expansion set
				textual_data = NULL,
				binary_data = %(data)s::bytea
			where
				keyword = '$$gnumed_patient_media_export_icon'""",
		filename = os.path.join('..', 'sql', 'v21-v22', 'data', 'GNUmed_Data_2.ico'),
		conn = conn
	)

	gmPG2.file2bytea (
		query = u"""
			update ref.keyword_expansion set
				textual_data = NULL,
				binary_data = %(data)s::bytea
			where
				keyword = '$$gnumed_patient_media_export_icon_2'""",
		filename = os.path.join('..', 'sql', 'v21-v22', 'data', 'GNUmed_Data.ico'),
		conn = conn
	)

	# Begleitbrief mit Diagnosen
	gmPG2.file2bytea (
		query = u"""
			UPDATE ref.paperwork_templates SET
				data = %(data)s::bytea,
				external_version = '22.9'
			WHERE
				name_long = 'Begleitbrief mit Diagnosen [K.Hilbert]'""",
		filename = os.path.join('..', 'sql', 'v21-v22', 'data', 'v22-Begleitbrief_mit_Diagnosen.tex'),
		conn = conn
	)

	return True

#---------------------------

	# AMTS Medikationsplan
	gmPG2.file2bytea (
		query = u"""
			UPDATE ref.paperwork_templates SET
				data = %(data)s::bytea
			WHERE
				name_long = 'Medikationsplan (Deutschland, AMTS)'""",
		filename = os.path.join('..', 'sql', 'v21-v22', 'data', 'v22-Medikationsplan_AMTS-2.0.tex'),
		conn = conn
	)

	# AMTS Medikationsplan (nicht konform)
	gmPG2.file2bytea (
		query = u"""
			UPDATE ref.paperwork_templates SET
				data = %(data)s::bytea
			WHERE
				name_long = 'Medikationsplan (Deutschland, NICHT konform zu AMTS)'""",
		filename = os.path.join('..', 'sql', 'v21-v22', 'data', 'v22-Medikationsplan_AMTS-2.0-nicht_konform.tex'),
		conn = conn
	)

#==============================================================
