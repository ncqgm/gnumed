#use this script to set the permissions for the users and the databases from the owner of the databases

read_users="_test-doc"
#read_databases="drugref gnumed"
read_databases="drugref"

#write_users="_test-doc"
#write_databases="gnumed"


for db in $read_databases ; do
	echo "get tables"
	tables=`psql -t -c "select tablename from pg_tables where not tablename like 'pg%';" $db`
	echo "get views"
	views=`psql -t -c "select viewname from pg_views where viewname not like 'pg%';" $db`


	for user in $read_users; do
		lines=`
		for x in $tables $views ; do 
			echo "grant select , references on $x to \"$user\";"
		done;`
	done;
	echo "granting read rights"
	echo $lines | psql  $db 
done	



#for db in $write_databases ; do
#	echo "getting tables for write access"
#	tables=`psql -t -c "select tablename from pg_tables where not tablename like 'pg%' and not tablename like 'log$';" $db`
#	echo "getting sequences for write access"
#	sequences=`psql -t -c "select relname from pg_statio_user_sequences;" $db`
#	for user in $write_users; do


#		for x in $tables $sequences ; do 
#			psql -e -c "grant all on $x to \"$user\"" $db;
#		done;
		

#	done;
#done	
