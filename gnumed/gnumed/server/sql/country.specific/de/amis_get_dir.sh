#! /bin/bash
# Author: Hilmar Berger
# License: GPL
# this script reads the name of a directory where AMIS data should be located
# and processes amis-import_data_template.sql so that the data can be copied to 
# the database. The result will be stored in amis-import_data.sql. This file
# will then be run.

read -p "Please enter path to amis-data:" AMIS_DIR;
cat amis-import_data_template.sql | sed "s%AMIS_PATH%"$AMIS_DIR"%" > amis-import_data.sql
