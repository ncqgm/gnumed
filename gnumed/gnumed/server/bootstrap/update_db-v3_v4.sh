#!/bin/sh

cd ../../
ln -vfsn client Gnumed
cd -
export PYTHONPATH="${PYTHONPATH}:../../"

PREV_VER="3"
VER="4"
LOG="update_db-v3_v${VER}.log"
CONF="update_db-v3_v${VER}.conf"

#export GM_CORE_DB="gnumed_v${VER}_cp"
export GM_CORE_DB="gnumed_v${VER}"

echo "==========================================================="
echo "Bootstrapping GNUmed database."
echo ""
echo "This will non-destructively transform a GNUmed database"
echo "of version v${PREV_VER} into a version v${VER} database."
echo ""
echo "The name of the new database will be \"${GM_CORE_DB}\"."
echo "==========================================================="
echo "Dropping target database if there is any."
dropdb -U gm-dbo -i ${GM_CORE_DB}
rm -rf ${LOG}
echo "======================="
echo "bootstrapping database"
./bootstrap_gm_db_system.py --log-file=${LOG} --conf-file=${CONF}
