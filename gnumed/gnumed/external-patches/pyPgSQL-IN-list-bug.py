"""pyPgSQL single-element-list bug with IN queries

You can work around this problem by testing whether the
argument to the IN condition is a single-element list and
duplicating that single element if it is one.
"""

def test(a, b, *args):
	print "a:   ", a
	print "b:   ", b
	print "args:", args, type(args)

#test(1, 2, 3)
#test(1, 2, 3, 4)

#tmp = tuple([3])

#test(1,2,tmp)


import gmPG

def run_query(cur, cmd, *args):
	print "args:", args, type(args)
	cur.execute(cmd, *args)

pool = gmPG.ConnectionPool()
conn = pool.GetConnection('historica', extra_verbose=1)
curs = conn.cursor()

print "this will succeed:"
list = [1,2]
print "list:", list, type(list)
cmd = "select * from pg_class where relowner in %s"
run_query(curs, cmd, (tuple(list),))

print "---------------"
print "this will fail:"
IN_list = (1,)
print "list:", IN_list, type(IN_list)
cmd = "select * from pg_class where relowner in %s"
#run_query(curs, cmd, (IN_list,))

curs.execute(cmd, IN_list)

curs.close()
