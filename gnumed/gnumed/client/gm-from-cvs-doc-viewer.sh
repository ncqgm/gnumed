#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/Attic/gm-from-cvs-doc-viewer.sh,v $
# $Revision: 1.1 $

# maybe force some locale setting here
#export LANG=fr

# start GnuMed
cd ../
ln -vfsn client Gnumed
cd -
export PYTHONPATH="${PYTHONPATH}:../"
python wxpython/gnumed.py --log-file=./gm-slave-doc-viewer.log --conf-file=/home/ncq/.gnumed/gm-doc-viewer.conf --debug
