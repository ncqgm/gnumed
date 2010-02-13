#!/bin/bash

./remove_pyc.sh

echo "updating python client source from VCS"
git pull -v | tee git-pull.log

#export CVS_RSH="ssh"
#echo "diffing against CVS just to be sure"
#cvs -z9 diff | tee before-update.diff
#echo "updating python client source from VCS"
#cvs -z9 update -dP | tee update.log

