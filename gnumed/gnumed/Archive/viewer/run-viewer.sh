#!/bin/sh

# this is a wrapper for the viewer
# set your command line arguments etc. here

# if you want another language than the standard system one
#LANG = "de_DE@euro"

# if you need to set a special base directory for some reason
#GMSHOWMEDDOCS_DIR = ""

CONF=~/.gnumed/gnumed-archive.conf

python ./gmShowMedDocs.py \
	--conf-file=$CONF \
	--text-domain=gnumed \
	--log-file=/var/log/gnumed/archive-view.log
