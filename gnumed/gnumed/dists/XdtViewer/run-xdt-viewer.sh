#!/bin/sh

# this is a wrapper for the XDT viewer
# set your command line arguments etc. here

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/dists/XdtViewer/Attic/run-xdt-viewer.sh,v $
# $Id: run-xdt-viewer.sh,v 1.2 2005-12-06 22:45:39 shilbert Exp $

# if you want another language than the standard system one
#LANG = "de_DE@euro"

# if you need to set a special base directory for some reason
#GMXDTVIEWER_DIR = ""

python ./gmXdtViewer.py --text-domain=gnumed --xdt-file=$1
