#!/bin/sh
httrack -%i -w http://[WikiName]:[password]@salaam.homeunix.com/twiki/bin/viewauth/Gnumed/WebHome \
 -O "/home/basti/Firma/gnumed-devel-cd" -%P -N0 -s0 -p7 -S -a -K0 -%k -A25000 \
 -F "Mozilla/4.5 (compatible; HTTrack 3.0x; Windows 98)" -%F '' \
 -%s -P "proxy.uni-leipzig.de:3128" -x -%x -%u -%U www-data \
 '+*.png' '+*.gif' '+*.jpg' '+*.css' '+*.js' '+salaam.homeunix.com/*.pdf' \
 '+salaam.homeunix.com/twiki/bin/view*/Gnumed/*' \
 '-salaam.homeunix.com/bin/twiki/view*/Gnumed/*?raw=*' \
 '+salaam.homeunix.com/bin/twiki/view*/Gnumed/*?raw=on' \
 '-salaam.homeunix.com/bin/twiki/view*/Gnumed/*?skin=*' \
 '+salaam.homeunix.com/bin/twiki/view*/Gnumed/*?skin=pattern' \
 '+salaam.homeunix.com/pub/Gnumed/*'