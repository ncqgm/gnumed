#!/bin/bash

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/gmDrug/setup-amis.sh,v $
# $Revision: 1.1 $

DB="amis"
host="localhost"
user="gm-dbowner"

dropdb $DB
createdb $DB
psql -a -E -h $host -d $DB -U $user -f amis-create_tables.sql > create-amis.log
psql -a -E -h $host -d $DB -U $user -f amis-import_data.sql >> create-amis.log

#--------------------------------------------
# $Log: setup-amis.sh,v $
# Revision 1.1  2002-11-10 13:46:37  ncq
# - first version
#
