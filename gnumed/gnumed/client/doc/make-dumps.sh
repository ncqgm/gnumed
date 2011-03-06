#!/bin/bash

# license: GPL
# author: Karsten.Hilbert@gmx.net

DB="gnumed_v15"

SCHEMADUMP=~/gm-schemadocs/gm-schema-dump.sql
DATADUMP=~/gm-schemadocs/gm-data-dump.sql
GMDUMP=~/gm-schemadocs/gm-db-dump.tgz

pg_dump -i -f $SCHEMADUMP -F p -C -s -U gm-dbo $DB
pg_dump -i -f $DATADUMP -F p -a -D -U gm-dbo $DB

tar -cvzf $GMDUMP $SCHEMADUMP $DATADUMP
