#!/bin/sh

echo "re-bootstrapping public database"
echo "dropping old database"
dropdb -U gm-dbowner gnumed
echo "============================"
echo "bootstrappping core database"
rm -rf redo-public.log
bootstrap-gm_db_system.py --log-file=redo-public-core.log --conf-file=bootstrap-monolithic_core.conf
echo "========================="
echo "adding data for locale DE"
rm -rf redo-public-de.log
bootstrap-gm_db_system.py --log-file=redo-public-de.log --conf-file=bootstrap-de.conf
echo "========================="
echo "adding data for locale AU"
rm -rf redo-public-au.log
bootstrap-gm_db_system.py --log-file=redo-public-au.log --conf-file=bootstrap-au.conf
echo "================"
echo "adding test data"
rm -rf redo-public-test_data.log
bootstrap-gm_db_system.py --log-file=redo-public-test_data.log --conf-file=bootstrap-test_data.conf
