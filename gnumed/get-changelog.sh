#!/bin/sh

#=================================================
# $Id: get-changelog.sh,v 1.2 2008-04-14 16:59:46 ncq Exp $
# $Revision: 1.2 $
#-------------------------------------------------

REV1="rel-0-2-8-patches"
REV2="rel-0-2-8-patches"

# rev1 to rev2
#REVDEF="-r$REV1:$REV2"

# rev1 to rev2 without rev1
#REVDEF="-r$REV1::$REV2"

# start of branch until rev1
#REVDEF="-r:$REV1"

# start with rev1 until end of that branch
#REVDEF="-r$REV1:"

# start after rev1 until end of that branch
#REVDEF="-r$REV1::"

# all revisions on branch rev1
REVDEF="-r$REV1"

LOG=CHANGELOG$REVDEF.log

echo "Revision selection:" > $LOG
echo $REVDEF >> $LOG
echo "===================================================" >> $LOG
echo "" >> $LOG

# -S suppress non-matches
cvs log -S $REVDEF >> $LOG

#=================================================
# $Log: get-changelog.sh,v $
# Revision 1.2  2008-04-14 16:59:46  ncq
# - edit to actually produce something meaningful
#
# Revision 1.1  2006/11/07 15:21:01  ncq
# - extract changelog between revisions from CVS
#
#