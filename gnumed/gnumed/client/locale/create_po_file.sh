#!/bin/sh

# this tool can be used to generate a *.po file from all the gnumed client source

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/locale/Attic/create_po_file.sh,v $
# $Revision: 1.4 $

# where to look for files
BASE="$1"
# what to call the result
PONAME="$2"

echo "harvesting python source files in ${BASE} into the file ${2}.po"
find ${BASE} -follow -name '*.py' -print0 | xargs -0 pygettext.py -v -o ${2}.po "-"
