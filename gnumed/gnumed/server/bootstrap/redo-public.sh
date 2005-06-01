#!/bin/sh

cd ../../
ln -vfsn client Gnumed
cd -
export PYTHONPATH="${PYTHONPATH}:../../"

# standard database name
DB_NAME="gnumed"
# or else override it
#export GM_CORE_DB="gm-test"
#DB_NAME="gm-test"

echo "==========================================================="
echo "Bootstrapping public database."
echo ""
echo "This will set up a GNUmed database intended for public use."
echo "It contains all the currently working parts including"
echo "localizations for countries you don't live in. This does"
echo "not disturb the operation of the GNUmed client in your"
echo "country in any way."
echo "==========================================================="
echo "Dropping old database if there is any."
dropdb -U gm-dbo -i $DB_NAME
rm -rf *.log
#echo "========================="
#echo "making data for locale AU"
#cd ../sql/country.specific/au/
#make-postcode-sql.sh
#cd -
echo "======================="
echo "bootstrappping database"
./bootstrap_gm_db_system.py --log-file=redo-public.log --conf-file=redo-public.conf
