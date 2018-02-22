#!/bin/bash

# license: GPL v2 or later
# author: Karsten.Hilbert@gmx.net

DB_LIST="gnumed_v21 gnumed_v22"
#DB_LIST="$1"
SCHEMA_LIST="public gm clin dem blobs ref bill i18n"

export PGUSER="gm-dbo"

for DB in ${DB_LIST} ; do

	mkdir -p ~/gm-schemadocs/${DB}

	postgresql_autodoc -d ${DB} -f ~/gm-schemadocs/${DB}/gnumed-entire_schema -t html
	postgresql_autodoc -d ${DB} -f ~/gm-schemadocs/${DB}/gnumed-entire_schema -t dot
	grep -v log_ ~/gm-schemadocs/${DB}/gnumed-entire_schema.dot > ~/gm-schemadocs/${DB}/gnumed-entire_schema-no_audit.dot
	dot -Tsvg -o ~/gm-schemadocs/${DB}/gnumed-entire_schema.svg ~/gm-schemadocs/${DB}/gnumed-entire_schema-no_audit.dot

	for SCHEMA in ${SCHEMA_LIST} ; do

		postgresql_autodoc -d ${DB} -s ${SCHEMA} -f ~/gm-schemadocs/${DB}/gnumed-schema_${SCHEMA} -t html
		postgresql_autodoc -d ${DB} -s ${SCHEMA} -f ~/gm-schemadocs/${DB}/gnumed-schema_${SCHEMA} -t dot
		postgresql_autodoc -d ${DB} -s ${SCHEMA} -f ~/gm-schemadocs/${DB}/gnumed-schema_${SCHEMA} -t dia
		postgresql_autodoc -d ${DB} -s ${SCHEMA} -f ~/gm-schemadocs/${DB}/gnumed-schema_${SCHEMA} -t zigzag.dia

		grep -v log_ ~/gm-schemadocs/${DB}/gnumed-schema_${SCHEMA}.dot > ~/gm-schemadocs/${DB}/gnumed-schema_${SCHEMA}-no_audit.dot

		dot -Tpng -o ~/gm-schemadocs/${DB}/gnumed-schema_${SCHEMA}.png ~/gm-schemadocs/${DB}/gnumed-schema_${SCHEMA}-no_audit.dot
		dot -Tpdf -o ~/gm-schemadocs/${DB}/gnumed-schema_${SCHEMA}.pdf ~/gm-schemadocs/${DB}/gnumed-schema_${SCHEMA}-no_audit.dot
		dot -Tsvg -o ~/gm-schemadocs/${DB}/gnumed-schema_${SCHEMA}.svg ~/gm-schemadocs/${DB}/gnumed-schema_${SCHEMA}-no_audit.dot

	done

done

ln -s -T ~/gm-schemadocs/gnumed_v21 ~/gm-schemadocs/release
ln -s -T ~/gm-schemadocs/gnumed_v22 ~/gm-schemadocs/devel
