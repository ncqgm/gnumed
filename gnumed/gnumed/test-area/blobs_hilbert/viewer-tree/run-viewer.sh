#!/bin/sh

# this is a wrapper for the viewer
# set your command line arguments etc. here

# if you want another language than the standard system one
#LANG = "de_DE@euro"

# if you need to set a special base directory for some reason
#GMSHOWMEDDOCS_DIR = ""

python ./gmShowMedDocs.py \
	--conf-file=/home/ncq/.gnumed/gnumed-archive.conf \
	--text-domain=gnumed-archive \
	--log-file=/var/log/gnumed/archive-view.log
