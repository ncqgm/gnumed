#!/bin/bash

#==============================================================
# author: Karsten Hilbert
# license: GPL v2
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
#  add the following line to a crontab file to run a
#  database backup at 12:47 and 19:47 every day
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
for BACKUP in ${BACKUP_BASENAME}-*.tar ; do

	# are the backup and ...
	TAR_OPEN=`lsof | grep ${BACKUP}`
	# ... the corresponding bz2 both open at the moment ?
	BZ2_OPEN=`lsof | grep ${BACKUP}.bz2`
	if test -z "${TAR_OPEN}" -a -z "${BZ2_OPEN}" ; then
		# no: remove the bz2 and start over compressing
		rm -f ${BACKUP}.bz2
	else
		# yes: skip to next backup
		continue
	fi

	bzip2 -zq -${COMPRESSION_LEVEL} ${BACKUP}
	bzip2 -tq ${BACKUP}.bz2
	# FIXME: add check for exit code

	chmod ${BACKUP_MASK} ${BACKUP}.bz2
	chown ${BACKUP_OWNER} ${BACKUP}.bz2

	# Reed-Solomon error protection support
#	if test -n ${ADD_ECC} ; then
#		rsbep
#	fi

	# GNotary support
	if test -n ${GNOTARY_TAN} ; then
		LOCAL_MAILER=`which mail`

		#SHA512="SHA 512:"`sha512sum -b ${BACKUP_FILENAME}.tar.bz2`
		SHA512=`openssl dgst -sha512 -hex ${BACKUP}.bz2`
		RMD160=`openssl dgst -ripemd160 -hex ${BACKUP}.bz2`

		export REPLYTO=${SIG_RECEIVER}

		# send mail
		(
			echo " "
			echo "<?xml version=\"1.0\" encoding=\"iso-8859-1\" ?>"
			echo "<message>"
			echo "	<tan>$GNOTARY_TAN</tan>"
			echo "	<action>notarize</action>"
			echo "	<hashes number=\"2\">"
			echo "		<hash file=\"${BACKUP}.bz2\" modified=\"${TS}\" algorithm=\"SHA-512\">${SHA512}</hash>"
			echo "		<hash file=\"${BACKUP}.bz2\" modified=\"${TS}\" algorithm=\"RIPE-MD-160\">${RMD160}</hash>"
			echo "	</hashes>"
			echo "</message>"
			echo " "
		) | $LOCAL_MAILER -s "gnotarize" $GNOTARY_SERVER
	fi

done

exit 0

#==============================================================
