
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

I don't know which will work best: 
using a sql dump is too slow.

usually if the user is authorized, loading the complete dump including
schema AFTER loading the gnmed hibernate schema mapping,  works.
(drugref org table and column names are mapped the same names).

It seems to be either a authorized user problem : 
try creating user xxxxx and grant all on public schema to xxxx
where xxxx is the user which connects near the top of the dump file.
e.g. pgsql, hherb , ihaywood.

in cygwin  psql interactive, and \i drugref.org.dump seems to work.




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
            - the error message when trying to create tables will be 
                no namespace for table xxxxx.
            - this means the connecting user specified in the hibernate.properties file
            has not been granted table creating permission in the database being used.
            psql into the database , and grant access.


        
        
