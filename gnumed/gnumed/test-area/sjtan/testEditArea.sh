createdb gnumed2

psql -c "drop schema public cascade" gnumed2
psql -c "create schema public" gnumed2

psql -f drugref.org.schema.dump gnumed2


psql -f drugref.org.data.dump gnumed2


