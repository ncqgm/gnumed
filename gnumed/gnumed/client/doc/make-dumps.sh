#!/bin/bash

# license: GPL v2 or later
# author: Karsten.Hilbert@gmx.net

DB="gnumed_v22"

SCHEMADUMP=~/gm-schemadocs/gm-schema-dump.sql
DATADUMP=~/gm-schemadocs/gm-data-dump.sql
GMDUMP=~/gm-schemadocs/gm-db-dump.tgz

pg_dump -f $SCHEMADUMP --format=p --create --schema-only --username="gm-dbo" $DB
pg_dump -f $DATADUMP --format=p --data-only --column-inserts --username="gm-dbo" $DB

tar -cvzf $GMDUMP $SCHEMADUMP $DATADUMP
