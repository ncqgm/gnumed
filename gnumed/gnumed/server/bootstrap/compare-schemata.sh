#!/bin/bash

# ============================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/bootstrap/compare-schemata.sh,v $
# $Id: compare-schemata.sh,v 1.6 2008-08-01 10:38:25 ncq Exp $
# ============================================

DB1="gnumed_v7"
DB2="gnumed_v7"
LOG="schema-diff.txt"

rm -vf $LOG
touch $LOG

echo "Comparing database schemata" >> $LOG
echo "---------------------------" >> $LOG
echo $DB1 >> $LOG
psql -d $DB1 -U gm-dbo -A -c "select md5(gm.concat_table_structure());" >> $LOG
echo $DB2 >> $LOG
psql -d $DB2 -U gm-dbo -A -c "select md5(gm.concat_table_structure());" >> $LOG
echo "-----------------------------" >> $LOG
echo "diff -Bub $DB1 $DB2" >> $LOG
echo "-----------------------------" >> $LOG
psql -d $DB1 -U gm-dbo -c "select gm.concat_table_structure();" > new.txt
psql -d $DB2 -U gm-dbo -c "select gm.concat_table_structure();" > cp.txt
diff -Bub new.txt cp.txt >> $LOG
rm -vf new.txt
rm -vf cp.txt
echo "-----------------------------" >> $LOG
less $LOG

# ============================================
# $Log: compare-schemata.sh,v $
# Revision 1.6  2008-08-01 10:38:25  ncq
# - /bin/sh -> /bin/bash
#
# Revision 1.5  2007/06/11 19:48:14  ncq
# - bump database version
#
# Revision 1.4  2007/05/07 16:31:09  ncq
# - use new database maint functions in gm.
#
# Revision 1.3  2007/04/27 13:31:11  ncq
# - bump version
#
# Revision 1.2  2005/11/29 22:40:25  ncq
# - improved layout
#
# Revision 1.1  2005/11/29 22:09:18  ncq
# - convenience script for comparing two database schemata
#
#
