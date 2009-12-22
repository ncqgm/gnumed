#==============================================================
# GNUmed database schema change script
#
# License: GPL
# Author: karsten.hilbert@gmx.net
# 
#==============================================================
# $Id: import-form-templates.py,v 1.1 2009-12-22 12:01:08 ncq Exp $
# $Revision: 1.1 $

#--------------------------------------------------------------
import os

from Gnumed.pycommon import gmPG2

#--------------------------------------------------------------
def run(conn=None):
	gmPG2.file2bytea (
		query = u"""
update ref.paperwork_templates
set data = %(data)s::bytea
where name_long = 'Current medication list (GNUmed default)'
""",
		filename = os.path.join('..', 'sql', 'v11-v12', 'data', 'GNUmed-default_medication_list_template.tex'),
		conn = conn
	)

#==============================================================
# $Log: import-form-templates.py,v $
# Revision 1.1  2009-12-22 12:01:08  ncq
# - import meds list template
#
#
#