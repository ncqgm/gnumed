#!/bin/sh

echo "re-bootstrapping maximum database"
echo "dropping old database"
dropdb -U postgres gnumed
echo "---------------------------"
echo "bootstrappping new database"
rm -rf redo-max-core.log
./bootstrap-gm_db_system.py --log-file=redo-max-core.log --conf-file=bootstrap-monolithic_core.conf
echo "-------------------------"
echo "adding data for locale DE"
rm -rf redo-max-de.log
./bootstrap-gm_db_system.py --log-file=redo-max-de.log --conf-file=bootstrap-de.conf
echo "-------------------------"
echo "adding data for locale AU"
echo "generating AU post code SQL script"
cd ../sql/country.specific/au/
python postcode_import.py postcodes.au.csv | uniq > postcodes.au.sql 2> postcodes.au.log
cd -
rm -rf redo-max-au.log
./bootstrap-gm_db_system.py --log-file=redo-max-au.log --conf-file=bootstrap-au.conf
echo "----------------"
echo "adding test data"
rm -rf redo-max-test_data.log
./bootstrap-gm_db_system.py --log-file=redo-max-test_data.log --conf-file=bootstrap-test_data.conf
echo "-------------------"
echo "importing AMIS data"
./install_AMIS_data.sh
echo "--------------------"
echo "importing some blobs"
cd ~/Bilder/Vietnam/archive
python import-test-blobs.py
cd -
