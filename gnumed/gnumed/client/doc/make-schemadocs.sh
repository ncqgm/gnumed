#!/bin/bash

# license: GPL v2 or later
# author: Karsten.Hilbert@gmx.net

DB_LIST="gnumed_v16 gnumed_v17"
#DB_LIST="$1"

export PGUSER="gm-dbo"

for DB in ${DB_LIST} ; do

	mkdir -p ~/gm-schemadocs/${DB}/

	postgresql_autodoc -d ${DB} -f ~/gm-schemadocs/${DB}/gnumed-schema -t html
	postgresql_autodoc -d ${DB} -f ~/gm-schemadocs/${DB}/gnumed-schema -t dot
	postgresql_autodoc -d ${DB} -f ~/gm-schemadocs/${DB}/gnumed-schema -t dia
	postgresql_autodoc -d ${DB} -f ~/gm-schemadocs/${DB}/gnumed-schema -t zigzag.dia

	grep -v log_ ~/gm-schemadocs/${DB}/gnumed-schema.dot > ~/gm-schemadocs/${DB}/gnumed-schema-no_audit.dot

	dot -Tpng -o ~/gm-schemadocs/${DB}/gnumed-schema.png ~/gm-schemadocs/${DB}/gnumed-schema-no_audit.dot

done

ln -s ~/gm-schemadocs/gnumed_v16 ~/gm-schemadocs/release
ln -s ~/gm-schemadocs/gnumed_v17 ~/gm-schemadocs/devel
