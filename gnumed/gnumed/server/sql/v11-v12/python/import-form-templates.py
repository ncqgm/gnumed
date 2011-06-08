#==============================================================
# GNUmed database schema change script
#
# License: GPL v2 or later
# Author: karsten.hilbert@gmx.net
# 
#==============================================================
# $Id: import-form-templates.py,v 1.2 2010-01-21 08:49:31 ncq Exp $
# $Revision: 1.2 $

#--------------------------------------------------------------
import os

from Gnumed.pycommon import gmPG2

#--------------------------------------------------------------
def run(conn=None):

	# medication list
	gmPG2.file2bytea (
		query = u"""
update ref.paperwork_templates
set data = %(data)s::bytea
where name_long = 'Current medication list (GNUmed default)'
""",
		filename = os.path.join('..', 'sql', 'v11-v12', 'data', 'GNUmed-default_medication_list_template.tex'),
		conn = conn
	)

	# referral letter
	gmPG2.file2bytea (
		query = u"""
update ref.paperwork_templates
set data = %(data)s::bytea
where name_long = 'Referral letter (GNUmed default) [Dr.Rogerio Luz]'
""",
		filename = os.path.join('..', 'sql', 'v11-v12', 'data', 'GNUmed-default_referral_letter_template.tex'),
		conn = conn
	)

	return True

#==============================================================
# $Log: import-form-templates.py,v $
# Revision 1.2  2010-01-21 08:49:31  ncq
# - import referral letter template, too
#
# Revision 1.1  2009/12/22 12:01:08  ncq
# - import meds list template
#
#
#