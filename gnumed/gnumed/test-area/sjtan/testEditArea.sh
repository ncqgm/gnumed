# to dump the a test database


pg_dump -O -x gnumed > gnumed.dump # -O for no owner, and -x for no privileges


dropdb gnumed3
createdb gnumed3


psql -c "drop schema public cascade" gnumed3
psql -c "create schema public" gnumed3

#to get the test data from the dump from gnumed
psql -f gnumed.dump gnumed3


# to load the drug-ref stuff
psql -f drugref.org.schema.dump gnumed3


psql -f drugref.org.data.dump gnumed3


