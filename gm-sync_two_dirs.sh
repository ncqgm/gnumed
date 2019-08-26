#!/bin/bash

# can be used to import external dev trees like DWV or Timeline

set -o pipefail


SOURCEDIR="$1"
TARGETDIR="$2"

if test "${SOURCEDIR}" = "" ; then
	echo "$0: <SOURCEDIR> must not be empty"
	exit 1
fi
cd ${SOURCEDIR}
RESULT="$?"
if test "${RESULT}" != "0" ; then
	echo "$0: cannot cd into ${SOURCEDIR} (${RESULT})"
	exit ${RESULT}
fi
cd -


if test "${TARGETDIR}" = "" ; then
	echo "$0: <TARGETDIR> must not be empty"
	exit 1
fi
cd ${TARGETDIR}
RESULT="$?"
if test "${RESULT}" != "0" ; then
	echo "$0: cannot cd into ${TARGETDIR} (${RESULT})"
	exit ${RESULT}
fi
cd -


RSYNC_OPTS="--verbose --human-readable --itemize-changes --checksum --recursive --one-file-system --links --munge-links --perms --times --hard-links --xattrs --acls --delete-delay"
rsync --dry-run ${RSYNC_OPTS} ${SOURCEDIR}/ ${TARGETDIR} | less
RESULT="$?"
if test "${RESULT}" != "0" ; then
	echo "$0: rsync failed (${RESULT})"
	exit ${RESULT}
fi


read -p "Really update (type yes or no) ? "
if test "${REPLY}" != "yes" ; then
	echo "Aborted."
	exit 0
fi


#rsync --dry-run ${RSYNC_OPTS} ${SOURCEDIR}/ ${TARGETDIR} | tee $0.log
rsync ${RSYNC_OPTS} ${SOURCEDIR}/ ${TARGETDIR} | tee $0.log
RESULT="$?"
echo "result: ${RESULT}"
exit ${RESULT}
