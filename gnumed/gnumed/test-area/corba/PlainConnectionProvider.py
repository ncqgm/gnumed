import sys, traceback, inspect, time

try:
	import pgdb
except:
	print sys.exc_info()[0]

try:
	from pyPgSQL import PgSQL
except:
	print sys.exc_info()[0]

class PlainConnectionProvider:

	def __init__(self, dsn = None, dbapi = None):

		if dsn == None:
			dsn ="localhost:gnumed:gm-dbowner:pg"

		if dbapi == None:
			use_pgdb = '-pgdb' in sys.argv

			try:
				from pyPgSQL import PgSQL
				dbapi = PgSQL
				l = dsn.split(':')
				if len(l) == 4:
					l = [l[0]] + [''] + l[1:]
					dsn = ':'.join(l)

			except:
				print sys.exc_info()[0], sys.exc_info()[1]
				use_pgdb = 1

			if use_pgdb:

				import pgdb
				dbapi = pgdb


		self.dsn = dsn
		try:
			self.conn = dbapi.connect(dsn)
			return
		except:
			print sys.exc_info()[0], sys.exc_info()[1]

		self.conn = PgSQL.connect(dsn)

	def getConnection(self):

		if self.conn.__class__ <> ConnectionWrapper:
			self.conn = ConnectionWrapper(self.conn)
		return self.conn

class ConnectionWrapper :
	def __init__(self, real_conn):
		self.debug =  '-debug' in sys.argv
		self.conn = real_conn
		self.acursor = self.conn.cursor()
		self.statements = {}
		self.total_time = 0.0
		self.min_time = 1000.
		self.max_time = 0.0
		self.calls = 0

	def cursor(self):
		if self.acursor == None:
			self.acursor = self.conn.cursor()
		return self

	def execute(self, stmt, args = None):

		if '-sql' in sys.argv:
			print "execute: ", stmt, " ; args = ", args
			print

		if '-inspect' in sys.argv:
			print "current thread", thread.get_ident()
			frame = inspect.currentframe()
			l = inspect.getouterframes(frame)
			for x in l:
				print
				print x

			#for x in l[0:-1]:
			#	print inspect.getframeinfo(x)
		if self.statements.has_key(stmt) and self.statements[stmt] == args:
			print "WARNING attempted  duplicate statement execute in same commit context."



		self.statements[stmt] = args
		t = time.time()
		if args == None:
			self.acursor.execute(stmt)
		else:
			self.acursor.execute(stmt, args)
		t1 = time.time()
		diff = t1 - t
		if diff > self.max_time:
			self.max_time = diff
			self.max_statement = stmt
			print "**** THIS STATEMENT HAS TAKEN THE MAX_TIME OF", diff
			print "**** STATEMENT"
			print stmt
			print "**** END STATEMENT"

		if diff < self.min_time:
			self.min_time = diff
			self.min_statement = stmt
		self.calls += 1
		self.total_time += diff

		if '-stats' in sys.argv:
			print "current sql time=",diff , "stmt begins=",stmt[0:80],  ": total calls = ", self.calls, ",TOTAL sql time using ", self.conn, " = ", self.total_time, " , min_time =", self.min_time, " max_time", self.max_time
			print
		self._update_properties()

	def executemany(self, stmt, params= []):
		if '-sql' in sys.argv:
			print "execute: ", stmt, '; params = ',params
			print

		self.acursor.executemany(stmt, params)
		self._update_properties()

	def _update_properties(self):
		self.description = self.acursor.description
		self.rowcount = self.acursor.rowcount

	def fetchone(self):
		if self.debug and '-fetch' in sys.argv:
			result = self.acursor.fetchone()
			print result
			return result
		return self.acursor.fetchone()

	def fetchmany(self, n):
		if self.debug and '-fetch' in sys.argv:
			result = self.acursor.fetchmany(n)
			print "Rows fetched = ", len(result)
			print result
			return result

		return self.acursor.fetchmany(n)

	def fetchall(self):
		if self.debug and '-fetch' in sys.argv:
			result = self.acursor.fetchall()
			print "Rows fetched = ", len(result)
			print result
			return result

		return self.acursor.fetchall()

	def commit(self):
		if self.debug:
			print "committing"
		self.conn.commit()
		self.statements = {}

	def rollback(self):
		if self.debug:
			print "rollback"
		self.conn.rollback()
		self.statements = {}

