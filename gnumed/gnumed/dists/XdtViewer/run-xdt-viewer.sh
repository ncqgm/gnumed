#!/bin/sh

# this is a wrapper for the XDT viewer
# set your command line arguments etc. here

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/dists/XdtViewer/Attic/run-xdt-viewer.sh,v $
# $Id: run-xdt-viewer.sh,v 1.1 2003-02-15 17:14:32 ncq Exp $

# if you want another language than the standard system one
#LANG = "de_DE@euro"

# if you need to set a special base directory for some reason
#GMXDTVIEWER_DIR = ""

python ./gmXdtViewer.py \
	--text-domain=gnumed \
	--log-file=/var/log/gnumed/xdt-viewer.log \
	--xdt-file=$1
