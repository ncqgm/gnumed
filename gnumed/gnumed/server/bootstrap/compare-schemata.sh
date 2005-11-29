#!/bin/sh

# ============================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/bootstrap/compare-schemata.sh,v $
# $Id: compare-schemata.sh,v 1.1 2005-11-29 22:09:18 ncq Exp $
# ============================================

DB1="gnumed_v2_new"
DB2="gnumed_v2_cp"
LOG="schema-diff.txt"

touch $LOG

echo $DB1 >> $LOG
echo "-----------------------------" >> $LOG
psql -d $DB1 -U gm-dbo -c "select md5(gm_concat_table_structure());" >> $LOG
echo "-----------------------------" >> $LOG
echo $DB2 >> $LOG
echo "-----------------------------" >> $LOG
psql -d $DB2 -U gm-dbo -c "select md5(gm_concat_table_structure());" >> $LOG
echo "-----------------------------" >> $LOG
echo "diff -Bub $DB1 $DB2"
echo "-----------------------------" >> $LOG
psql -d $DB1 -U gm-dbo -c "select gm_concat_table_structure();" > new.txt
psql -d $DB2 -U gm-dbo -c "select gm_concat_table_structure();" > cp.txt
diff -Bub new.txt cp.txt >> $LOG
rm -vf new.txt
rm -vf cp.txt
echo "-----------------------------" >> $LOG
less $LOG

# ============================================
# $Log: compare-schemata.sh,v $
# Revision 1.1  2005-11-29 22:09:18  ncq
# - convenience script for comparing two database schemata
#
#
