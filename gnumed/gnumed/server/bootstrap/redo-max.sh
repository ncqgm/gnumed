#!/bin/sh

echo "re-bootstrapping maximum database"
echo "dropping old database"
dropdb -U gm-dbowner gnumed
echo "---------------------------"
echo "bootstrappping new database"
rm -rf redo-max-core.log
bootstrap-gm_db_system.py --log-file=redo-max-core.log --conf-file=bootstrap-monolithic_core.conf
echo "-------------------------"
echo "adding data for locale DE"
bootstrap-gm_db_system.py --log-file=redo-max-de.log --conf-file=bootstrap-de.conf
echo "-------------------------"
echo "adding data for locale AU"
bootstrap-gm_db_system.py --log-file=redo-max-au.log --conf-file=bootstrap-au.conf
echo "----------------"
echo "adding test data"
bootstrap-gm_db_system.py --log-file=redo-max-test_data.log --conf-file=bootstrap-test_data.conf
echo "--------------------"
echo "importing some blobs"
cd ~/Bilder/Vietnam/archive
python import-test-blobs.py
echo "-------------------"
echo "importing AMIS data"
cd -
install_AMIS_data.sh
