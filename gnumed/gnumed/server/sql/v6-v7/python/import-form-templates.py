#==============================================================
# GNUmed database schema change script
#
# Source database version: v6
# Target database version: v7
#
# License: GPL
# Author: karsten.hilbert@gmx.net
# 
#==============================================================
# $Id: import-form-templates.py,v 1.1 2007-09-18 22:48:14 ncq Exp $
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
where name_long = 'Therapiebericht Physiotherapie (GNUmed-Standard)'
""",
		filename = os.path.join('..', 'sql', 'v6-v7', 'data', 'GNUmed-PT-Therapiebericht-Rezeptrueckseite.ott'),
		conn = conn
	)

#==============================================================
# $Log: import-form-templates.py,v $
# Revision 1.1  2007-09-18 22:48:14  ncq
# - added
#
#