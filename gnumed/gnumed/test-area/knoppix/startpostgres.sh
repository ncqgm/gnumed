#!/bin/sh
chmod 0700 /ramdisk/home/knoppix/postgres/data 
chown postgres.knoppix -R /ramdisk/home/knoppix/postgres/data 
/etc/init.d/postgresql start