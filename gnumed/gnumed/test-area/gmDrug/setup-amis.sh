#!/bin/bash

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/gmDrug/setup-amis.sh,v $
# $Revision: 1.2 $

DB="amis"
host="localhost"
user="gm-dbowner"

dropdb $DB
createdb -e -h $host -U $user -E LATIN1 $DB "AMIS - German drug data" > setup-amis.log
psql -a -E -h $host -d $DB -U $user -f amis-create_tables.sql >> setup-amis.log
psql -a -E -h $host -d $DB -U $user -f amis-import_data.sql >> setup-amis.log

#--------------------------------------------
# $Log: setup-amis.sh,v $
# Revision 1.2  2002-11-10 13:54:14  ncq
# - log database creation
# - encoding set to LATIN1
#
# Revision 1.1  2002/11/10 13:46:37  ncq
# - first version
#
