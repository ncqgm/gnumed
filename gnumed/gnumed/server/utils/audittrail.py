#!/usr/bin/python
#!/usr/bin/python
#############################################################################
#
# auditrail.py - automatic generation of audit trail triggers for
#                any gnumed database.
# Principle: any table that needs to be audited (all modifications
#            logged) must inherit a given parent table
#            This script finds all descendant of that parent table and
#            creates all neccessary tables and trigger functions
#            neccessary to establish the audit trail
# ---------------------------------------------------------------------------
#
# @author: Dr. Horst Herb
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: nil
# @change log:
#	12.07.2001 hherb first draft, untested
#
# @TODO: Almost everything
############################################################################
"""Module that allows to create "audit trail" tables, triggers and functions
"""

import pg

#this query returns all tables inherited from a specified table in a tuple list
query_table_descendants = """select relname, oid from pg_class where \
                              pg_class.oid in (select inhrelid from pg_inherits where inhparent = \
                              (select oid from pg_class where relname = '%s'));"""

#this query returns all attributes AND their data types in a tuple list
query_table_attributes = """SELECT a.attname, format_type(a.atttypid, a.atttypmod) \
                             FROM pg_class c, pg_attribute a
                             WHERE c.relname = '%s'
                             AND a.attnum > 0 AND a.attrelid = c.oid
                             ORDER BY a.attnum;"""

trigger_statement = """CREATE TRIGGER %s BEFORE UPDATE OR DELETE ON %s \n \
FOR EACH ROW EXECUTE PROCEDURE %s;"""



def o(s):
    print s

#=================================================================

def get_children(db, parent_table):
    """Returns all descendants of "parent_table" in a tuple list
    Iterate through the list and access individual table names by index 0"""

    return db.query(query_table_descendants % parent_table).getresult()

#=================================================================

def get_attributes(db, child_table):
    return db.query(query_table_attributes % child_table).getresult()

#=================================================================

def create_audit_table(tablename):
    o("DROP TABLE %s;\n" % tablename)
    o("CREATE TABLE %s () INHERITS(audit_object);" % tablename)

#=================================================================

def create_trigfunc(db, child_table, audit_prefix="audit_"):
    tablename = child_table[0]
    funcname = audit_prefix + tablename
    trigname = 'tr_' + funcname
    auditname = tablename + '_hx'

    #check first whether the audit table exists, and create it if not
    if db.query("SELECT oid FROM pg_class where relname = '%s'" % auditname).ntuples() == 0:
        create_audit_table(auditname)

    o("DROP FUNCTION %s();\n" % funcname)

    o("CREATE FUNCTION %s() RETURNS OPAQUE AS '" % funcname)
    o("BEGIN")
    o("NEW.updated := OLD.updated+1;")
    o("INSERT INTO %s VALUES (" % auditname)
    attributes = get_attributes(db, tablename)
    for attr in attributes:
        o("OLD." + attr[0])
    o(");")
    o("return NEW;")
    o("END' LANGUAGE 'plpgsql';\n")

    o("DROP TRIGGER %s ON %s:\n" % (trigname, funcname))
    o(trigger_statement % (trigname, tablename, funcname)+'\n')


#=================================================================


if __name__ == "__main__" :

    dbname = raw_input("name of database:")
    parenttable = raw_input("name of parent table:")

    #connect to the database backend
    db = pg.connect(dbname)

    #get a list of all tables derived from gnumed_object
    children = get_children(db, parenttable)

    #for each derived table
    for child in children:
        create_trigfunc(db, child)
