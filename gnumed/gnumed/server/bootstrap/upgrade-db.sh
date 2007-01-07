#!/bin/sh

cd ../../
ln -vfsn client Gnumed
cd -
export PYTHONPATH="${PYTHONPATH}:../../"

PREV_VER="$1"
VER="$2"
LOG="update_db-v${PREV_VER}_v${VER}.log"
CONF="update_db-v${PREV_VER}_v${VER}.conf"
BAK_FILE="backup-upgrade-v${PREV_VER}-to-v${VER}-"`hostname`".sql.bz2"

export GM_CORE_DB="gnumed_v${VER}"

echo "==========================================================="
echo "Upgrading GNUmed database."
echo ""
echo "This will *non-destructively* create a new GNUmed database"
echo "of version v${VER} from an existing v${PREV_VER} database."
echo "Existing data is transferred and transformed as necessary."
echo ""
echo "The name of the new database will be \"${GM_CORE_DB}\"."
echo "==========================================================="
echo ""
echo "1) creating backup of existing database ..."
echo "   You may need to type in the password for gm-dbo."
pg_dump -d gnumed_v${PREV_VER} -U gm-dbo | bzip2 -z9 > ${BAK_FILE}
echo ""
echo "2) dropping target database if it exists ..."
dropdb -U gm-dbo -i ${GM_CORE_DB}
rm -rf ${LOG}
echo ""
echo "3) upgrading to new database ..."
./bootstrap_gm_db_system.py --log-file=${LOG} --conf-file=${CONF}
