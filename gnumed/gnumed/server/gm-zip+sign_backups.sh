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
set -o pipefail


# do not run twice
[ "${FLOCKER}" != "$0" ] && exec env FLOCKER="$0" flock --exclusive --nonblock "$0" "$0" "$@" || :


# load config file
if [ -r ${CONF} ] ; then
	. ${CONF}
else
	echo "Cannot read configuration file ${CONF}. Aborting."
	exit 1
fi

TS=$(date +%Y-%m-%d-%H-%M-%S)
BACKUP_BASENAME="backup-${GM_DATABASE}-${INSTANCE_OWNER}"

cd "${BACKUP_DIR}"
if test "$?" != "0" ; then
	echo "Cannot change into backup directory [${BACKUP_DIR}]. Aborting."
	exit 1
fi


shopt -s -q nullglob				# no glob matches -> ""
AGGREGATE_EXIT_CODE=0


# find any leftover, untested tar files
# and test them so they can be compressed
for TAR_UNTESTED in ${BACKUP_BASENAME}-*.tar.untested ; do

	# test
	tar --extract --to-stdout --file="${TAR_UNTESTED}" > /dev/null
	RESULT="$?"
	if test "${RESULT}" != "0" ; then
		echo "Verifying backup tar archive [${TAR_UNTESTED}] failed (${RESULT}). Skipping."
		AGGREGATE_EXIT_CODE=${RESULT}
		continue
	fi

	# rename to final archive name
	TAR_FINAL=$(basename "${TAR_UNTESTED}" .untested)
	mv --force "${TAR_UNTESTED}" "${TAR_FINAL}"
	RESULT="$?"
	if test "${RESULT}" != "0" ; then
		echo "Cannot rename tar archive (${RESULT}). Skipping."
		echo "FILES: ${TAR_UNTESTED} => ${TAR_FINAL}"
		AGGREGATE_EXIT_CODE=${RESULT}
		continue
	fi
	chown "${BACKUP_OWNER}" "${TAR_FINAL}"

done


# zip up any backups
for TAR_FINAL in ${BACKUP_BASENAME}-*.tar ; do

	BZ2_FINAL="${TAR_FINAL}.bz2"
	BZ2_SCRATCH="${BZ2_FINAL}.partial"
	BZ2_UNTESTED="${BZ2_FINAL}.untested"

	# compress tar archive
	# I have tried "xz -9 -e" and it did not make much of
	# a difference (48 MB in a 1.2 GB backup)
	#xz --quiet --extreme --check sha256 --no-warn -${COMPRESSION_LEVEL} ${BACKUP}
	#xz --quiet --test ${BACKUP}.xz
	bzip2 --quiet --stdout --keep --compress -"${COMPRESSION_LEVEL}" "${TAR_FINAL}" > "${BZ2_SCRATCH}"
	RESULT="$?"
	if test "${RESULT}" != "0" ; then
		echo "Compressing tar archive [${TAR_FINAL}] into [${BZ2_SCRATCH}] failed (${RESULT}). Skipping."
		AGGREGATE_EXIT_CODE=${RESULT}
		rm --force "${BZ2_SCRATCH}"
		continue
	fi
	# rename to "untested" archive name
	mv --force "${BZ2_SCRATCH}" "${BZ2_UNTESTED}"
	RESULT="$?"
	if test "${RESULT}" != "0" ; then
		echo "Renaming compressed archive [${BZ2_SCRATCH}] to [${BZ2_UNTESTED}] failed (${RESULT}). Skipping."
		AGGREGATE_EXIT_CODE=${RESULT}
		continue
	fi
	# verify compressed archive
	bzip2 --quiet --test "${BZ2_UNTESTED}"
	RESULT="$?"
	if test "${RESULT}" != "0" ; then
		echo "Verifying compressed archive [${BZ2_UNTESTED}] failed (${RESULT}). Removing."
		AGGREGATE_EXIT_CODE=${RESULT}
		rm --force "${BZ2_UNTESTED}"
		continue
	fi
	# rename to final archive name
	mv --force "${BZ2_UNTESTED}" "${BZ2_FINAL}"
	RESULT="$?"
	if test "${RESULT}" != "0" ; then
		echo "Renaming tested compressed archive [${BZ2_UNTESTED}] to [${BZ2_FINAL}] failed (${RESULT}). Skipping."
		AGGREGATE_EXIT_CODE=${RESULT}
		continue
	fi

	rm --force "${TAR_FINAL}"
	chmod "${BACKUP_MASK}" "${BZ2_FINAL}"
	chown "${BACKUP_OWNER}" "${BZ2_FINAL}"

	# GNotary support
	if test -n "${GNOTARY_TAN}" ; then
		LOCAL_MAILER=$(which mail)

		#SHA512="SHA 512:"`sha512sum -b ${BACKUP_FILENAME}.tar.bz2`
		SHA512=$(openssl dgst -sha512 -hex "${BZ2_FINAL}")
		RMD160=$(openssl dgst -ripemd160 -hex "${BZ2_FINAL}")

		export REPLYTO=${SIG_RECEIVER}

		# send mail
		(
			echo " "
			echo "<?xml version=\"1.0\" encoding=\"iso-8859-1\" ?>"
			echo "<message>"
			echo "	<tan>$GNOTARY_TAN</tan>"
			echo "	<action>notarize</action>"
			echo "	<hashes number=\"2\">"
			echo "		<hash file=\"${BZ2_FINAL}\" modified=\"${TS}\" algorithm=\"SHA-512\">${SHA512}</hash>"
			echo "		<hash file=\"${BZ2_FINAL}\" modified=\"${TS}\" algorithm=\"RIPE-MD-160\">${RMD160}</hash>"
			echo "	</hashes>"
			echo "</message>"
			echo " "
		) | $LOCAL_MAILER -s "gnotarize" "$GNOTARY_SERVER"
	fi

done


exit ${AGGREGATE_EXIT_CODE}
