#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/Attic/gm-0_2-from-cvs.sh,v $
# $Revision: 1.2 $

# if there are unicode troubles you can force to ASCII with this:
#export LANG=en

cd ../
ln -vfsn client Gnumed
cd -
export PYTHONPATH="${PYTHONPATH}:../"
LOG="gm-0_2-from-cvs.log"
rm -vf $LOG

# prepare
cp -vf gm-0_2.conf tmp-gm-0_2.conf
python wxpython/gnumed.py --log-file=$LOG --conf-file=tmp-gm-0_2.conf --debug --override-schema-check
# --unicode-gettext=0
# clean up
rm -vf tmp-gm-0_2.conf
rm -vf tmp-gm-0_2.conf.gmCfg.bak
