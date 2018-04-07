import psycopg2
print "psycopg2:", psycopg2.__version__

dsn = 'dbname=gnumed_v21 port=5432 user=any-doc password=any-doc sslmode=prefer'

conn = psycopg2.connect(dsn=dsn)
curs = conn.cursor()

cmd = "set timezone to 'Asia/Colombo'"
curs.execute(cmd)
cmd = "select '1901-01-01 11:11:11.111+01'::timestamp with time zone"
curs.execute(cmd)

print curs.fetchall()

curs.close()
conn.close()
