
def help():
	print """
	client cmd line args.
	cmd line args:
		-gnumed try to call the identification component at 'gnumed' on localhost:5002/NameService	. If this is absent, will call the open-emeds id component at us/.../Pilot.
		
		-debug	debugging output
		-local  run a client using a local identification component( bypass orb)
		-level2 extra debugging
		-profile output a profile of test run.
		-profile2 output a profile file that can be inspected using the pstats package. See python docs


	server cmd line args:
		-sql	: print sql statements
		-debug	: print variable information
		-inspect : show execution frame upto sql call; show thread id
		-stats :show duration of sql calls, and cumulative time waiting for
			sql calls. show minimum and maximum sql timings. show
			start of sql statement with maximum timing.
		-pgdb : use pgdb in preference to pyPgSQL as dbapi.
		-fetch : show raw dbapi fetch results
	
	connection strings are :
		the dsn for the dbapi is in PlainConnectionProvider.py
		the corbaloc NameService url is in ResolveIdComponent.py
		the NameService directory paths for gnumed and openemed
		is also there.
		
		


	"""	

if __name__ == "__main__":
	help()
