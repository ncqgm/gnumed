# don't run this on your machine if you have a good setup

dropdb gnumed
createdb gnumed
createlang -d gnumed plpgsql
psql -f gmclinical_test_only.sql gnumed


