#!/bin/sh

echo "getting a fresh gnumed cvs snapshot"
httrack -%i -w http://salaam.homeunix.com/~ncq/gnumed/snapshot/gnumed-latest-snapshot.tgz \
 -O "/home/basti/Firma/gnumed-devel-cd" -%P -N0 -s0 -p7 -S -a -K0 -%k -A25000 \
 -F "Mozilla/4.5 (compatible; HTTrack 3.0x; Windows 98)" -%F '' \
 -%s -P "proxy.uni-leipzig.de:3128" -x -%x -%u -%U www-data \

