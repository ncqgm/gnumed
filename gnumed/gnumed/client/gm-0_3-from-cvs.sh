#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/Attic/gm-0_3-from-cvs.sh,v $
# $Revision: 1.1 $

cd ../
ln -vfsn client Gnumed
cd -
export PYTHONPATH="${PYTHONPATH}:../"
LOG="gm-0_3-from-cvs.log"
rm -vf $LOG

# prepare
cp -vf gm-0_3.conf tmp-gm-0_3.conf
python wxpython/gnumed.py --log-file=$LOG --conf-file=tmp-gm-0_3.conf --debug --override-schema-check
# --unicode-gettext=0
# clean up
rm -vf tmp-gm-0_3.conf
rm -vf tmp-gm-0_3.conf.gmCfg.bak
