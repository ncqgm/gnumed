#!/bin/sh

echo "re-bootstrapping public database"
echo "dropping old database"
dropdb -U gm-dbowner gnumed-public
echo "bootstrappping new database"
rm -rf redo-public.log
bootstrap-gm_db_system.py --log-file=redo-public.log --conf-file=bootstrap-public_db.conf
