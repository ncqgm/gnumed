#!/bin/sh

cd ../../
ln -vfsn client Gnumed
cd -
export PYTHONPATH="${PYTHONPATH}:../"

echo "re-bootstrapping public database"
echo "dropping old database"
dropdb -U postgres gnumed
echo "*******************************"
echo "bootstrapping new core database"
rm -f redo-de-core.log
./bootstrap-gm_db_system.py --log-file=redo-de-core.log --conf-file=bootstrap-monolithic_core.conf
echo "****************************************"
echo "now adding database features for Germany"
rm -f redo-de-specific.log
./bootstrap-gm_db_system.py --log-file=redo-de-specific.log --conf-file=bootstrap-de.conf
