# GNUmed searchable text exporter
#============================================================
__author__ = "Karsten Hilbert"
__license__ = 'GPL v2 or later'

import sys

sys.path.insert(0, '../../')

from Gnumed.pycommon import gmPG2
#============================================================

cmd = """
SELECT
	soap_cat,
	narrative,
	src_table,
	(SELECT rank FROM clin.soap_cat_ranks scr WHERE scr.soap_cat = vn4s.soap_cat) AS rank
FROM
	clin.v_narrative4search vn4s
WHERE
	pk_patient = %(pat)s
ORDER BY
	pk_encounter			-- sort of chronologically sorted
	, pk_health_issue
	, pk_episode
	, rank
	, src_table
"""

conn = gmPG2.get_connection()

rows = gmPG2.run_ro_queries(link_obj=conn, queries=[{'sql': cmd, 'args': {'pat': sys.argv[1]}}])

f = open('emr-%s-narrative-dump.txt' % sys.argv[1], mode = 'wt', encoding = 'utf8', errors = 'strict')

for row in rows:
	f.write('%s: %s (%s)\n'.encode('utf8') % (row['soap_cat'], row['narrative'], row['src_table']))

f.close()

#============================================================
