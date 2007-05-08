#!/bin/bash

#==============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/gm-backup_database.sh,v $
# $Id: gm-backup_database.sh,v 1.6 2007-05-08 11:18:20 ncq Exp $
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
#  1       15      backup-gnumed-<your-company>    /usr/bin/gm-backup_database.sh
#
#
# cron
# ----
#  add the following line to a crontab file to run a
#  database backup at 12:47 and 19:47 every day
#
#  47 12,19 * * * * /usr/bin/gm-backup_database.sh
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
HOST=`hostname`
BACKUP_BASENAME="backup-${GM_DATABASE}-${INSTANCE_OWNER}-${HOST}"
BACKUP_FILENAME="${BACKUP_BASENAME}-${TS}"

# create dumps
cd ${BACKUP_DIR}
pg_dump -C -U ${GM_DBO} -d ${GM_DATABASE} -p ${GM_PORT} -f ${BACKUP_FILENAME}-database.sql
sudo -u postgres pg_dumpall -g -p ${GM_PORT} > ${BACKUP_FILENAME}-roles.sql

# compress and test it
tar -cWf ${BACKUP_FILENAME}.tar ${BACKUP_FILENAME}-database.sql ${BACKUP_FILENAME}-roles.sql
bzip2 -zq9 ${BACKUP_FILENAME}.tar
bzip2 -tq ${BACKUP_FILENAME}.tar.bz2
# clean up
rm -f ${BACKUP_FILENAME}-database.sql
rm -f ${BACKUP_FILENAME}-roles.sql

# give to admin owner
chmod ${BACKUP_MASK} ${BACKUP_FILENAME}.tar.bz2
chown ${BACKUP_OWNER} ${BACKUP_FILENAME}.tar.bz2

if test ! -z ${GNOTARY_TAN} ; then

	# GNotary support
	LOCAL_MAILER=`which mail`

	#SHA512="SHA 512:"`sha512sum -b ${BACKUP_FILENAME}.tar.bz2`
	SHA512=`openssl dgst -sha512 -hex ${BACKUP_FILENAME}.tar.bz2`
	RMD160=`openssl dgst -ripemd160 -hex ${BACKUP_FILENAME}.tar.bz2`

	export REPLYTO=$SIG_RECEIVER

	# send mail
	(
		echo "Subject: gnotarize"
		echo " "
		echo "<?xml version=\"1.0\" encoding=\"iso-8859-1\" ?>"
		echo "<message>"
		echo "	<tan>$GNOTARY_TAN</tan>"
		echo "	<action>notarize</action>"
		echo "	<hashes number=\"2\">"
		echo "		<hash file=\"${BACKUP_FILENAME}.tar.bz2\" modified=\"${TS}\" algorithm=\"SHA-512\">$SHA512</hash>"
		echo "		<hash file=\"${BACKUP_FILENAME}.tar.bz2\" modified=\"${TS}\" algorithm=\"RIPE-MD-160\">$RMD160</hash>"
		echo "	</hashes>"
		echo "</message>"
		echo " "
	) | $LOCAL_MAILER -s "gnotarize" $GNOTARY_SERVER

fi

# zip up any leftover backups
shopt -s -q nullglob
for OLD_BACKUP in ${BACKUP_DIR}/${BACKUP_BASENAME}-*.tar ; do
	# but only if there isn't already a corresponding *.bz2
	if test ! -f ${OLD_BACKUP}.bz2 ; then
		bzip2 -zq9 ${OLD_BACKUP}
		bzip2 -tq ${OLD_BACKUP}
	fi
done

exit 0

#==============================================================
# $Log: gm-backup_database.sh,v $
# Revision 1.6  2007-05-08 11:18:20  ncq
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