#!/bin/bash

GITDIR="."
LOGDIR="."
BRANCH_ROOT="rel-1-8"
LATEST_BRANCH="rel-1-8-maint"

cd ${GITDIR}
git log ..${LATEST_BRANCH} > ${LOGDIR}/commits.log
echo "" >> ${LOGDIR}/commits.log
git log ${BRANCH_ROOT} >> ${LOGDIR}/commits.log
