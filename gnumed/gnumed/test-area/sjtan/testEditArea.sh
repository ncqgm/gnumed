createdb gnumed2

psql -e "drop schema public cascade" gnumed2
psql -e "create schema public" gnumed2

psql -f drugref.org.schema.dump gnumed2


psql -f drugref.org.data.dump gnumed2


