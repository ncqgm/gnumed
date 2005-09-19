#!/bin/sh

cd ../../
ln -vfsn client Gnumed
cd -
export PYTHONPATH="${PYTHONPATH}:../../"

VER="2"
export GM_CORE_DB="gnumed_v${VER}"

echo "==========================================================="
echo "Bootstrapping GNUmed database."
echo ""
echo "This will set up a GNUmed database of version v${VER}"
echo "with the name \"${GM_CORE_DB}\"."
echo "It contains all the currently working parts including"
echo "localizations for countries you don't live in. This does"
echo "not disturb the operation of the GNUmed client in your"
echo "country in any way."
echo "==========================================================="
echo "Dropping old database if there is any."
dropdb -U gm-dbo -i $GM_CORE_DB
rm -rf redo-v${VER}.log
echo "======================="
echo "bootstrappping database"
./bootstrap_gm_db_system.py --log-file=redo-v${VER}.log --conf-file=redo-v${VER}.conf
