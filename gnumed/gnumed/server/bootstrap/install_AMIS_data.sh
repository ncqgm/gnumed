#! /bin/bash
# Author: Hilmar Berger
# License: GPL
# this script reads the name of a directory where AMIS data should be located
# and processes amis-import_data_template.sql so that the data can be copied to 
# the database. The result will be piped through psql. 

SQL_DIR=../sql
MODULES_DIR=../../client/python-common/
GNUMED_DB=gnumed

read -p "Please enter path to amis-data:" AMIS_DIR;
echo "You may have to type in the password for gm-dbowner."
cat $SQL_DIR/country.specific/de/amis-import_data_template.sql | sed "s%AMIS_PATH%"$AMIS_DIR"%" |\
psql -d $GNUMED_DB -U gm-dbowner

# eventually set config parameters for AMIS drug browser
env PYTHONPATH=$MODULES_DIR $MODULES_DIR/tools/transferDBset.py -i ./amis-config.set

# $Log: install_AMIS_data.sh,v $
# Revision 1.2  2003-11-09 17:50:06  ncq
# - make sure data is imported as user gm-dbowner
#
# Revision 1.1  2003/11/09 14:53:40  hinnef
# moved files to bootstrap dir
#