#!/bin/bash

#==============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/gm-zip+sign_backups.sh,v $
# $Id: gm-zip+sign_backups.sh,v 1.2 2007-06-12 13:21:53 ncq Exp $
#
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

# load config file
CONF="/etc/gnumed/gnumed-backup.conf"
if [ -r ${CONF} ] ; then
	. ${CONF}
else
	echo "Cannot read configuration file ${CONF}. Aborting."
	exit 1
fi

#==============================================================
# There really should not be any need to
# change anything below this line.
#==============================================================

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
	# but only if there isn't already a corresponding *.bz2
	if test ! -f ${BACKUP}.bz2 ; then

		bzip2 -zq -${COMPRESSION_LEVEL} ${BACKUP}
		bzip2 -tq ${BACKUP}.bz2
		# FIXME: add check for exit code

		chmod ${BACKUP_MASK} ${BACKUP}.bz2
		chown ${BACKUP_OWNER} ${BACKUP}.bz2

		# GNotary support
		if test ! -z ${GNOTARY_TAN} ; then

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
	fi
done

exit 0

#==============================================================
# $Log: gm-zip+sign_backups.sh,v $
# Revision 1.2  2007-06-12 13:21:53  ncq
# - remove redundant lines from mail body
#
# Revision 1.1  2007/06/05 14:53:44  ncq
# - factored out from the actual backup script
#
# Revision 1.10  2007/05/17 15:17:24  ncq
# - abort on ping error
#
# Revision 1.9  2007/05/17 15:16:23  ncq
# - set backup base name based on GM_HOST, not localhost
# - ping remote GM_HOST before trying to dump
#
# Revision 1.8  2007/05/14 21:29:24  ncq
# - start supporting dumps from remote hosts
#
# Revision 1.7  2007/05/14 16:46:33  ncq
# - be a bit more resource friendly
#
# Revision 1.6  2007/05/08 11:18:20  ncq
# - robustify
# - include database creation commands, dump roles only
#
# Revision 1.5  2007/05/07 08:06:16  ncq
# - include roles in dump
# - make zipping up old backups safer
#
# Revision 1.4  2007/05/01 19:41:38  ncq
# - better docs
# - factor out config
#
# Revision 1.3  2007/04/27 13:30:49  ncq
# - add FIXME
#
# Revision 1.2  2007/02/19 10:35:14  ncq
# - add some (ana)crontab lines and a few lines of documentation
#
# Revision 1.1  2007/02/16 15:33:37  ncq
# - renamed for smoother compliance into target systems
#
# Revision 1.6  2007/02/13 17:10:03  ncq
# - better docs
# - bzip up leftover dumps from when bzipping got interrupted by, say, shutdown
#
# Revision 1.5  2007/01/24 22:56:05  ncq
# - support gnotarization
#
# Revision 1.4  2007/01/07 23:10:24  ncq
# - more documentation
# - add backup file permission mask
#
# Revision 1.3  2006/12/25 22:55:10  ncq
# - comment on gnotary support
#
# Revision 1.2  2006/12/21 19:01:21  ncq
# - add target owner chown
#
# Revision 1.1  2006/12/05 14:48:08  ncq
# - first release of a backup script
#
#