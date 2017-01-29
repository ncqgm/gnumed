#!/bin/bash

#==============================================================
# author: Karsten Hilbert
# license: GPL v2 or later
#
# anacron
# -------
#  The following line could be added to a system's
#  /etc/anacrontab to make sure it creates daily
#  database backups for GNUmed:
#
#  1       15      gnumed-<your-company>-sign-backups    /usr/bin/gm-zip+sign_backups.sh
#
#
# cron
# ----
#  Add the following line to a crontab file to sign
#  database backups at 12:47 and 19:47 every day:
#
#  47 12,19 * * * * /usr/bin/gm-zip+sign_backups.sh
#
#
# It is useful to have a PROCMAIL rule for the GNotary server replies
# piping them into the stoarage area where the backups are kept.
#==============================================================

CONF="/etc/gnumed/gnumed-backup.conf"

#==============================================================
# There really should not be any need to
# change anything below this line.
#==============================================================

# load config file
if [ -r ${CONF} ] ; then
	. ${CONF}
else
	echo "Cannot read configuration file ${CONF}. Aborting."
	exit 1
fi

TS=`date +%Y-%m-%d-%H-%M-%S`
BACKUP_BASENAME="backup-${GM_DATABASE}-${INSTANCE_OWNER}"

cd ${BACKUP_DIR}
if test "$?" != "0" ; then
	echo "Cannot change into backup directory [${BACKUP_DIR}]. Aborting."
	exit 1
fi

shopt -s -q nullglob

# zip up any backups
AGGREGATE_EXIT_CODE=0
for TAR_FILE in ${BACKUP_BASENAME}-*.tar ; do

	BZ2_FILE="${TAR_FILE}.bz2"

	# are the backup and ...
	TAR_OPEN=`lsof | grep ${TAR_FILE}`
	# ... the corresponding bz2 both open at the moment ?
	BZ2_OPEN=`lsof | grep ${BZ2_FILE}`
	if test -z "${TAR_OPEN}" -a -z "${BZ2_OPEN}" ; then
		# no: remove the bz2 and start over compressing
		rm -f ${BZ2_FILE}
	else
		# yes: skip to next backup
		continue
	fi

	# verify tar archive
	# already done by backup script:
	# if verification fails, *.tar.untested
	# will not have been renamed to *.tar

	# compress tar archive
	# I have tried "xz -9 -e" and it did not make much of
	# a difference (48 MB in a 1.2 GB backup)
	#xz --quiet --extreme --check sha256 --no-warn -${COMPRESSION_LEVEL} ${BACKUP}
	#xz --quiet --test ${BACKUP}.xz
	bzip2 --quiet --keep --compress -${COMPRESSION_LEVEL} ${TAR_FILE}
	RESULT="$?"
	if test "${RESULT}" != "0" ; then
		echo "Compressing tar archive [${TAR_FILE}] as bz2 failed (${RESULT}). Skipping."
		AGGREGATE_EXIT_CODE=${RESULT}
		continue
	fi
	# verify compressed archive
	bzip2 --quiet --test ${BZ2_FILE}
	RESULT="$?"
	if test "${RESULT}" != "0" ; then
		echo "Verifying compressed archive [${BZ2_FILE}] failed (${RESULT}). Removing."
		AGGREGATE_EXIT_CODE=${RESULT}
		rm -f ${BZ2_FILE}
		continue
	fi
	rm -f ${TAR_FILE}
	chmod ${BACKUP_MASK} ${BZ2_FILE}
	chown ${BACKUP_OWNER} ${BZ2_FILE}

	# GNotary support
	if test -n ${GNOTARY_TAN} ; then
		LOCAL_MAILER=`which mail`

		#SHA512="SHA 512:"`sha512sum -b ${BACKUP_FILENAME}.tar.bz2`
		SHA512=`openssl dgst -sha512 -hex ${BZ2_FILE}`
		RMD160=`openssl dgst -ripemd160 -hex ${BZ2_FILE}`

		export REPLYTO=${SIG_RECEIVER}

		# send mail
		(
			echo " "
			echo "<?xml version=\"1.0\" encoding=\"iso-8859-1\" ?>"
			echo "<message>"
			echo "	<tan>$GNOTARY_TAN</tan>"
			echo "	<action>notarize</action>"
			echo "	<hashes number=\"2\">"
			echo "		<hash file=\"${BZ2_FILE}\" modified=\"${TS}\" algorithm=\"SHA-512\">${SHA512}</hash>"
			echo "		<hash file=\"${BZ2_FILE}\" modified=\"${TS}\" algorithm=\"RIPE-MD-160\">${RMD160}</hash>"
			echo "	</hashes>"
			echo "</message>"
			echo " "
		) | $LOCAL_MAILER -s "gnotarize" $GNOTARY_SERVER
	fi

done


exit ${AGGREGATE_EXIT_CODE}
