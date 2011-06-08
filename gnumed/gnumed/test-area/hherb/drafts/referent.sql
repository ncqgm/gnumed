-- project: GNUMed
-- database: (global)
-- purpose:  see comment below
-- author: hherb
-- copyright: Dr. Horst Herb, horst@hherb.com
-- license: GPL v2 or later (details at http://gnu.org)
-- version: 0.4
-- changelog:
-- 11.1.03:  first version

-- trigger function for checking remote referential integrity.

-- usage remote_ref (my_column, remote_service, remote_table, remote_column)
-- example: create trigger trig before insert or update for on mytable 
-- for each row execute procedure remote_ref ('patient_id', 'demographica', 'identity', 'id');
-- requires working PL/Python and dblink () installed

create function remote_ref (text, text, text, text) returns opaque as '
res = plpy.execute ("select conn from remote_dbs where service = ''%s''" % TD["args"][1])
if len (res) > 0:
 conn = res[0]
 query = lambda x: plpy.execute ("select dblink_tok (dblink (''%s'', ''%s''), 1)" % (conn, x))
else:
 query = lambda x: plpy.execute (x)

res = query ("select found (select from %s where %s = %s)" % (TD["args"][2], TD["args"][3], TD["new"][TD["args"][0]]))
if res[0][0] = "f":
 plpy.error ("Referential integrity violation on %s:%s (%s)" % (TD["args"][1], TD["args"]{2], TD["args"][2]))
else:
 return None
' language 'plpython';



