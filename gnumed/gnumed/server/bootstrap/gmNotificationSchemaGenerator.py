"""Automatic GnuMed notification trigger generation.

This module creates notification triggers on tables.

Theory of operation:

Any table that should send notifies must be recorded in
the table "notifying_tables".

FIXME: allow definition of how to retrieve the patient ID
"""
#==================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/bootstrap/gmNotificationSchemaGenerator.py,v $
__version__ = "$Revision: 1.3 $"
__author__ = "Karsten.Hilbert@gmx.net"
__license__ = "GPL"		# (details at http://www.gnu.org)

import sys, os.path, string

if __name__ == "__main__" :
	sys.path.append(os.path.join('..', '..', 'client', 'pycommon'))

import gmLog
_log = gmLog.gmDefLog
if __name__ == "__main__" :
	_log.SetAllLogLevels(gmLog.lData)

import gmPG

#==================================================================
# SQL statements for notification triggers
#------------------------------------------------------------------
trigger_schema = """
create function F_announce_%(sig)s_mod() returns opaque as '
declare
	episode_id integer;
	patient_id integer;
begin
	-- get episode ID
	if TG_OP = ''DELETE'' then
		episode_id := OLD.id_episode;
	else
		episode_id := NEW.id_episode;
	end if;
	-- backtrack to patient ID
	select into patient_id id_patient
		from v_patient_episodes vpep
		where vpep.id_episode = episode_id
		limit 1;
	-- now, execute() the NOTIFY
	execute ''notify "%(sig)s_mod_db:'' || patient_id || ''"'';
	return NULL;
end;
' language 'plpgsql';

create trigger TR_%(sig)s_mod
	after insert or delete or update
	on %(tbl)s
	for each row
		execute procedure F_announce_%(sig)s_mod()
;
"""
#------------------------------------------------------------------
def create_notification_schema(aCursor):
	cmd = "select table_name, notification_name from notifying_tables";
	if gmPG.run_query(aCursor, cmd) is None:
		return None
	rows = aCursor.fetchall()
	if len(rows) == 0:
		_log.Log(gmLog.lInfo, 'no notifying tables')
		return None
	_log.Log(gmLog.lData, rows)
	# for each notifying table
	schema = []
	for notifying_def in rows:
		tbl = notifying_def[0]
		sig = notifying_def[1]
		schema.append(trigger_schema % {'sig': sig, 'tbl': tbl})
		schema.append('-- ----------------------------------------------')
	return schema
#==================================================================
# main
#------------------------------------------------------------------
if __name__ == "__main__" :

	dbpool = gmPG.ConnectionPool()
	conn = dbpool.GetConnection('default')
	curs = conn.cursor()

	schema = create_notification_schema(curs)

	curs.close()
	conn.close()
	dbpool.ReleaseConnection('default')

	if schema is None:
		print "error creating schema"
		sys.exit(-1)

	file = open ('notification-schema.sql', 'wb')
	for line in schema:
		file.write("%s;\n" % line)
	file.close()

#==================================================================
# $Log: gmNotificationSchemaGenerator.py,v $
# Revision 1.3  2004-02-25 09:46:36  ncq
# - import from pycommon now, not python-common
#
# Revision 1.2  2003/12/01 22:10:55  ncq
# - typo
#
# Revision 1.1  2003/11/28 10:16:06  ncq
# - initial check-in
#
