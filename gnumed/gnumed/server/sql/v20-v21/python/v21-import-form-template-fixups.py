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

	# Begleitbrief
	gmPG2.file2bytea (
		query = u"""
			UPDATE ref.paperwork_templates SET
				data = %(data)s::bytea,
				external_version = '21.8'
			WHERE
				name_long = 'Begleitbrief ohne medizinische Daten [K.Hilbert]'""",
		filename = os.path.join('..', 'sql', 'v20-v21', 'data', 'v21-Begleitbrief.tex'),
		conn = conn
	)

	# AMTS Medikationsplan v2.3, nicht konform
	gmPG2.file2bytea (
		query = u"""
			UPDATE ref.paperwork_templates SET
				data = %(data)s::bytea
			WHERE
				name_long = 'Medikationsplan 2.3 (AMTS, Deutschland)'""",
		filename = os.path.join('..', 'sql', 'v20-v21', 'data', 'v21-Medikationsplan_AMTS-2.3.tex'),
		conn = conn
	)

	# AMTS Medikationsplan v2.3, nicht konform
	gmPG2.file2bytea (
		query = u"""
			UPDATE ref.paperwork_templates SET
				data = %(data)s::bytea
			WHERE
				name_long = 'Medikationsplan AMTS (~2.3, NICHT konform, Deutschland)'""",
		filename = os.path.join('..', 'sql', 'v20-v21', 'data', 'v21-Medikationsplan_AMTS-2.3-nicht_konform.tex'),
		conn = conn
	)

	# AMTS Medikationsplan v2.3, nicht konform, blanko
	gmPG2.file2bytea (
		query = u"""
			UPDATE ref.paperwork_templates SET
				data = %(data)s::bytea
			WHERE
				name_long = 'Medikationsplan AMTS (blanko, ~2.3, NICHT konform, Deutschland)'""",
		filename = os.path.join('..', 'sql', 'v20-v21', 'data', 'v21-Medikationsplan_AMTS-2.3-nicht_konform-blanko.tex'),
		conn = conn
	)

	return True

#==============================================================
