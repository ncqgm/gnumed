import string



query = """SELECT pg_trigger.*, pg_proc.proname, pg_class.relname, pg_type.typname
        FROM pg_proc INNER JOIN pg_trigger ON pg_proc.oid = pg_trigger.tgfoid 
		INNER JOIN pg_class ON pg_trigger.tgrelid = pg_class.oid 
		INNER JOIN pg_type ON pg_trigger.tgtype = pg_type.oid 
		WHERE pg_class.relname = '%s'"""



def listForeignKeys(con, table):
	global query
	references = {}
	cur = con.cursor()
	cur.execute(query % table)
	fkresult = cur.fetchall()
	for fk in fkresult:
		fkarray = repr(fk['tgargs'])
		fkname, referencing_table, referenced_table, dummy, referencing_column, referenced_column, dummy2  = string.split(fkarray, '\\x00')
		references[referencing_column] = (referenced_table, referenced_column)
	return references

	
if __name__ == "__main__":
	from pyPgSQL import PgSQL as DB
	db = DB.connect(database='gnumed')
	fk = listForeignKeys(db, 'urb')
	for key in fk.keys():
		print key, ' -> ', fk[key]
