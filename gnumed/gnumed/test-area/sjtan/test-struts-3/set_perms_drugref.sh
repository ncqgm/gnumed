#use this script to set the permissions for the users and the databases from the owner of the databases

read_users="_test-doc"
read_databases="drugref gnumed"

write_users="_test-doc"
write_databases="gnumed"


for db in $read_databases ; do

	tables=`psql -t -c "select tablename from pg_tables where not tablename like 'pg%';" $db`
	views=`psql -t -c "select viewname from pg_views where viewname not like 'pg%';" $db`


	for user in $read_users; do

		for x in $tables $views ; do 
			psql -c "grant select , references on $x to \"$user\"" $db;
		done;
		

	done;
done	



for db in $write_databases ; do

	tables=`psql -t -c "select tablename from pg_tables where not tablename like 'pg%';" $db`
	sequences=`psql -t -c "select relname from pg_statio_user_sequences;" $db`
	for user in $write_users; do


		for x in $tables $sequences ; do 
			psql -c "grant all on $x to \"$user\"" $db;
		done;
		

	done;
done	
