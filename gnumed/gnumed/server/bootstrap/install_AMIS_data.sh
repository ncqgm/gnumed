#! /bin/bash
# Author: Hilmar Berger
# License: GPL
# this script reads the name of a directory where AMIS data should be located
# and processes amis-import_data_template.sql so that the data can be copied to 
# the database. The result will be piped through psql. 

SQL_DIR=../sql
MODULES_DIR=../../client/pycommon/
GNUMED_DB=gnumed_v7

read -p "Please enter path to amis-data:" AMIS_DIR;
echo "You may have to type in the password for gm-dbo."
cat $SQL_DIR/country.specific/de/amis-import_data_template.sql | sed "s%AMIS_PATH%"$AMIS_DIR"%" |\
psql -d $GNUMED_DB -U gm-dbo

# eventually set config parameters for AMIS drug browser
echo "Now config parameters will be set in the GnuMed database so that GnuMed will"
echo "know which drug data should be accessed. These settings can be changed via"
echo "the Setup plugin in GnuMed. The corresponding parameters are"
echo "DrugReferenceBrowser.drugDBName and DrugReferenceBrowser.amis.configfile"
echo "stored under DEFAULT_USER_DEFAULT_WORKPLACE."
echo "You will have to login to the GnuMed database to write these data." 
env PYTHONPATH=$MODULES_DIR $MODULES_DIR/tools/transferDBset.py -i ./amis-config.set

# $Log: install_AMIS_data.sh,v $
# Revision 1.7  2007-09-24 18:39:06  ncq
# - work on v7
#
# Revision 1.6  2007/03/18 23:50:13  ncq
# - some fixes by Ruthard Baudach
#
# Revision 1.5  2005/01/12 14:47:49  ncq
# - in DB speak the database owner is customarily called dbo, hence use that
#
# Revision 1.4  2004/07/19 11:50:43  ncq
# - cfg: what used to be called "machine" really is "workplace", so fix
#
# Revision 1.3  2003/12/29 21:09:00  uid67323
# -added some informative messages
#
# Revision 1.2  2003/11/09 17:50:06  ncq
# - make sure data is imported as user gm-dbowner
#
# Revision 1.1  2003/11/09 14:53:40  hinnef
# moved files to bootstrap dir
#