#!/bin/sh

cd ../../
ln -vfsn client Gnumed
cd -
export PYTHONPATH="${PYTHONPATH}:../../"

echo "re-bootstrapping public database"
echo "dropping old database"
dropdb -U gm-dbowner -i gnumed
rm -rf *.log
echo "============================"
echo "bootstrappping core database"
./bootstrap_gm_db_system.py --log-file=redo-public-core.log --conf-file=bootstrap-monolithic_core.conf
echo "========================="
echo "adding data for locale DE"
./bootstrap_gm_db_system.py --log-file=redo-public-de.log --conf-file=bootstrap-de.conf
echo "========================="
echo "adding data for locale AU"
cd ../sql/country.specific/au/
make-postcode-sql.sh
cd -
./bootstrap_gm_db_system.py --log-file=redo-public-au.log --conf-file=bootstrap-au.conf
echo "================"
echo "adding test data"
./bootstrap_gm_db_system.py --log-file=redo-public-test_data.log --conf-file=bootstrap-test_data.conf
