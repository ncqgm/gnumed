#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/Attic/gm-0_1-from-cvs.sh,v $
# $Revision: 1.1 $

# if there are unicode troubles you can force to ASCII with this:
#export LANG=en

cd ../
ln -vfsn client Gnumed
cd -
export PYTHONPATH="${PYTHONPATH}:../"
rm -vf gm-0_1-from-cvs.log
python wxpython/gnumed.py --log-file=gm-0_1-from-cvs.log --conf-file=gm-0_1.conf --debug
# --unicode-gettext=0
