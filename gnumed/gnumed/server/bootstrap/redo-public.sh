#!/bin/sh

cd ../../
ln -vfsn client Gnumed
cd -
export PYTHONPATH="${PYTHONPATH}:../../"

echo "================================"
echo "re-bootstrapping public database"
echo "dropping old database"
dropdb -U gm-dbo -i gnumed
rm -rf *.log

echo "========================="
echo "making data for locale AU"
cd ../sql/country.specific/au/
make-postcode-sql.sh
cd -
echo "======================="
echo "bootstrappping database"
./bootstrap_gm_db_system.py --log-file=redo-public.log --conf-file=redo-public.conf
