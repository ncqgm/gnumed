#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/Attic/setup-for-de.sh,v $
# $Revision: 1.1 $

DB=gnumed

psql -f gmconfiguration.sql $DB 
psql -f gmidentity.sql $DB 
#gmgis MUST follow gmidentity now because of id_type in identities_addresses
psql -f gmgis.sql $DB 

#psql -f country.specific/au/postcodes.au.sql $DB 
