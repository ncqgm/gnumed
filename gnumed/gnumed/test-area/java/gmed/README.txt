further docs in ./docs

1.setup postgres
    - in windows, cygwin with cygipc library , and postgres is needed.
            - the cygipc daemon must run before the postmaster.
	- make sure postgres as a template1 database , 
	with the user and password granted access ( all is simplest)
	for the chosen user.
	- make sure the pg_hba.conf file in the pgdata directory which
	serves the postgres database as an entry for localhost accesss
	(127.0.0.1 )  and the user and access type ( password or md5)
	-make sure the pg_ctl start -D pgdata -o -i  is used to start
	the database. -o -i option allows tcp access which jdbc needs.
	-test the access using psql -h 127.0.0.1 template1 -U or something
	and see the user name and password works.

2.Setup the jdbc access.
	edit the hibernate.properties
	change the user to the user name
	and password to the correct password
	make sure there is no trailing invisible whitespace after either.
	


	

to build  you need jdk1.4 and ant , and the libraries of used in hibernate 1.2,
and the correct postgres jdbc jar file from the postgresql distribution.

ant ddl

ant 

to run

ant test_observations
ant test_multi_persons
ant test_measurement

to run the current tests.

PS* change the jvmarg schema-export=on in the build.xml file  if schema export needs to be run to setup a database for any of the tests ( only the first run is needed).


You hopefully will be rewarded with lots of text , and a filled up
database.

