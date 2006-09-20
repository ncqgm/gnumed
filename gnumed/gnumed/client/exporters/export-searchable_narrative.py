# GNUmed vaccination metadata exporter
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/exporters/export-searchable_narrative.py,v $
# $Id: export-searchable_narrative.py,v 1.1 2006-09-20 12:31:08 ncq Exp $
__version__ = "$Revision: 1.1 $"
__author__ = "Karsten Hilbert"
__license__ = 'GPL'

import sys, codecs

import gmPG2
#============================================================

cmd = """
select
	soap_cat,
	narrative,
	src_table,
	(select rank from clin.soap_cat_ranks scr where scr.soap_cat=vn4s.soap_cat) as rank
from clin.v_narrative4search vn4s
where
	pk_patient=%(pat)s
order by
	pk_encounter			-- sort of chronologically
	, pk_health_issue
	, pk_episode
	, rank
	, src_table
"""

conn = gmPG2.get_connection(encoding='iso-8859-15')

rows, idx = gmPG2.run_ro_queries(link_obj=conn, queries=[{'cmd': cmd, 'args': {'pat': sys.argv[1]}}])

f = codecs.open('emr-%s-narrative-dump.txt' % sys.argv[1], 'wb', encoding='iso-8859-15', errors='strict')

for row in rows:
	f.write('%s: %s (%s)\n'.encode('iso-8859-15') % (row['soap_cat'], row['narrative'], row['src_table']))

f.close()

#============================================================
# $Log: export-searchable_narrative.py,v $
# Revision 1.1  2006-09-20 12:31:08  ncq
# - export search narrative into file
#
#