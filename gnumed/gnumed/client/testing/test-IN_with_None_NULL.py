import psycopg2
print "psycopg2:", psycopg2.__version__

dsn = 'dbname=gnumed_v21 port=5432 user=any-doc password=any-doc sslmode=prefer'

conn = psycopg2.connect(dsn=dsn)
curs = conn.cursor()

cmd = "SELECT 1 IN %(SET)s"
args = {'SET': tuple((1,2,3,None))}
curs.execute(cmd, args)
print curs.fetchall()

curs.close()
conn.close()
