
import sys

if __name__ == '__main__':
	sys.path.insert(0, '../../')

from Gnumed.pycommon import gmPG2

print "Please log in as GNUmed database owner:"
gmPG2.get_connection()

print ""
print ""
print "Looking for dangling clin.clin_root_item rows ..."

print ""
print "1) rows with dangling .fk_episode:"
cmd = """
	SELECT *, tableoid::regclass AS src_table FROM clin.clin_root_item
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.episode WHERE pk = clin.clin_root_item.fk_episode
	)"""
rows = gmPG2.run_ro_queries(queries = [{'sql': cmd}])
for row in rows:
	print "=> dangling row:", row
	print "   verifying corresponding child table row in [%s] ..." % row['src_table']
	cmd = "SELECT * from %s WHERE pk_audit = %%(pk_audit)s" % row['src_table']
	args = {'pk_audit': row['pk_audit']}
	child_rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	if len(child_rows) == 0:
		print "NO CHILD TABLE ROW, SOMETHING IS BROKEN"
	for child_row in child_rows:
		print '=> [%s] row:' % row['src_table'], child_row
	print "   looking for most recent row about episode %s in audit table ..." % row['fk_episode']
	cmd = """
		SELECT * FROM audit.log_episode WHERE
			pk = %(pk_epi)s
		ORDER BY row_version DESC
		LIMIT 1
	"""
	args = {'pk_epi': row['fk_episode']}
	audit_rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	for audit_row in audit_rows:
		print '=> audited row:', audit_row

print ""
print "2) rows with dangling .fk_encounter:"
cmd = """
	SELECT *, tableoid::regclass AS src_table FROM clin.clin_root_item
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.encounter WHERE pk = clin.clin_root_item.fk_encounter
	)"""
rows = gmPG2.run_ro_queries(queries = [{'sql': cmd}])
for row in rows:
	print "=> dangling row:", row
	print "   verifying corresponding child table row in [%s] ..." % row['src_table']
	cmd = "SELECT * from %s WHERE pk_audit = %%(pk_audit)s" % row['src_table']
	args = {'pk_audit': row['pk_audit']}
	child_rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	if len(child_rows) == 0:
		print "NO CHILD TABLE ROW, SOMETHING IS BROKEN"
	for child_row in child_rows:
		print '=> [%s] row:' % row['src_table'], child_row
	print "   looking for most recent row about encounter %s in audit table ..." % row['fk_encounter']
	cmd = """
		SELECT * FROM audit.log_encounter WHERE
			pk = %(pk_enc)s
		ORDER BY row_version DESC
		LIMIT 1
	"""
	args = {'pk_enc': row['fk_encounter']}
	audit_rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	for audit_row in audit_rows:
		print '=> audited row:', audit_row
