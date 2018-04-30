#!/bin/bash

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
