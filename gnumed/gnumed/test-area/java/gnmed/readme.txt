
Dependencies.

Need to get :

1. hibernate2 libraries.
latest xdoclet build. Reason: no custom hbm tags so far. 

may need to modify net.sf.hibernate.cfg.PostgresqlDialect to return " cascade"
for correct dropping behaviour.

2. org.drugref.schema and data dumps to test the
clinical issues test case.


3. postcode.au.csv in the usual place 




Possible problems:

1. can't find postcodes.au.csv

re:import postcodes.au.csv

the gnumed-test.properties gives the relative path to this file.


2. can't import drugref.data.dump

postgres doesn't diagnose user authority problems.
-  Message looks like "\N" unexpected end of input.

re: importing drugref.data.dump
why important? past history and drugs don't work without this data.

THE MOST IMPORTANT THING IS THE USER CONNECTION IDENTITY IN 
THE START OF THE SCRIPT. EITHER CHANGE IHAYWOOD TO THE APPROPRIATE
USER WITH GRANTED PERMISSIONS, OR CREATE THE USER IHAYWOOD WITH 
GRANTED PERMISSIONS.


3. can't connect to database.

possible problems:

1. not running postgres
	- postgres not running
	- postgres not running as tcp service.

	
	- in cygwin run ipc-daemon, then pg_ctl start -D pgdata -o -i
	

2. postgres not allowing users connecting
	- checkout pgdata/pg_hba.conf

		
3. hibernate not looking for postgres
	- check hibernate properties , hibernate.dialect=

	- no jdbc driver for postgres in lib path

	- database, user name, or password not valid
		- hidden whitespace after username or password
		- wrong database name
		- wrong user name

4. Postgres not allowing sufficient access

	- create the relevant user. grant all for testing purposes
	to public schema.



