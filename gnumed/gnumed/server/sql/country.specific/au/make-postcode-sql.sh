#!/bin/sh

#-------------------------------------------------------
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/au/make-postcode-sql.sh,v $
# $Revision: 1.2 $
# license: GPL
# author: Karsten Hilbert
#-------------------------------------------------------

echo "re-generating postcodes.au.sql"
python postcode_import.py postcodes.au.csv | uniq > postcodes.au.sql 2> postcodes.au.log

#-------------------------------------------------------
# $Log: make-postcode-sql.sh,v $
# Revision 1.2  2004-07-18 11:57:42  ncq
# - generate AU postcodes SQL from source CSV
#
