#!/bin/bash

# license: GPL v2 or later
# author: Karsten.Hilbert@gmx.net

DB="gnumed_v17"

SCHEMADUMP=~/gm-schemadocs/gm-schema-dump.sql
DATADUMP=~/gm-schemadocs/gm-data-dump.sql
GMDUMP=~/gm-schemadocs/gm-db-dump.tgz

pg_dump -i -f $SCHEMADUMP -F p -C -s -U gm-dbo $DB
pg_dump -i -f $DATADUMP -F p -a -D -U gm-dbo $DB

tar -cvzf $GMDUMP $SCHEMADUMP $DATADUMP
