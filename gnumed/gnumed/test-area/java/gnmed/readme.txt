
Dependencies.

a) java sdk1.4

b) postgresql with a java driver.

c) cygwin if running on windows. Will need ipc commands (ipc_daemon).




d) a working ant build tool.


e) hibernate2 libraries. including junit. 


f) xdoclet:
use latest xdoclet build. Reason: don't need to merge custom hbm tags. 
Put the xdoclet library files in the same lib directory as the hibernate
files ; the ant build.xml script should be configured to run from
that library directory, if it is  in the base directory.






g) org.drugref.schema and data dumps to test the
clinical issues test case. The schema is to validate the data
loading does work on postgres with a matching schema, but don't need the schema
when initializing this test application, in fact the  drugref schema will
prevent this app initialization working so need to drop it ( e.g. drop schema public cascade).
and then recreate schema public and grant the user access.




* re hibernate2: tables don't drop without cascades,  may need to modify the PostgresqlDialect java class in the hibernate2; alternatively just drop the
schema public and recreate it, adding the allowed users with granted permissions.
(at the moment, security is secondary to debugging and function implementation).




2. General Targets to get it working:

the right tools all work. maybe run the tests in ant , hibernate, and xdoclet.
Sometimes the version is wrong ( hibernate1 instead of hibernate2, the
old xdoclet etc...)


a working postgres listening on tcp with permitted users configured in
the data directory being served from (check  pg_hba.conf file).


check permissions are all right in the files and directory in unix.


run the tests incrementally : e.g.

make sure gnmed_test.properties has schema.has.been.exported = false 
and probably better if logging = off , then, 
testPostcodeCSV to generate the addresses tables.



then psql -f org.drugref.data.dump your_database  (template1)

import drugref.org.data  ( not schema at the moment).
this should ensure that testPostcodeCSV is generating the right
schema, which is tagged in hibernate inside the java data files to fit
 the drugreg.org data tables.


sh list.sh to list the ant targets, try running ant test.

If no test runs, check permissions are correct, make sure the 
Hibernate distribution example is working, and compare the hibernate.properties
files. ( Don't forget the dreaded invisible space after the name or password
for the connection).


3.things that make it easier to develop:

UML tool for grunt work code generation and also for overview when
navigating data classes.


IDE for code completion so that RSI doesn't develop.




common configuration problems:
-	drugref schema still in database: drop the schema.
-	not having pg_hba.conf permissions
-	not adding the user with the password in postgres for
	the database.

-	not having right user name or password in hibernate.properties,
	or	maybe having a space after password or username.
-	possibly wrong library jar files , or missing jar files 
	(e.g. the postgres.jar file), or jar files not in lib.
-	






