"""Automatic GNUmed notification trigger generation.

This module creates notification triggers on tables.

Theory of operation:

Any table that should send notifies must be recorded in
the table "notifying_tables".

FIXME: allow definition of how to retrieve the patient ID
"""
#==================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/bootstrap/gmNotificationSchemaGenerator.py,v $
__version__ = "$Revision: 1.16 $"
__author__ = "Karsten.Hilbert@gmx.net"
__license__ = "GPL (details at http://www.gnu.org)"

import sys, os.path, string

from Gnumed.pycommon import gmLog, gmPG2
_log = gmLog.gmDefLog
if __name__ == "__main__" :
	_log.SetAllLogLevels(gmLog.lData)

_log.Log(gmLog.lInfo, __version__)

#==================================================================
# SQL statements for notification triggers
#------------------------------------------------------------------
trigger_ddl = """
\unset ON_ERROR_STOP
drop function clin.trf_announce_%(sig)s_mod() cascade;
\set ON_ERROR_STOP 1

create function clin.trf_announce_%(sig)s_mod() returns trigger as '
declare
	episode_id integer;
	patient_id integer;
begin
	-- get episode ID
	if TG_OP = ''DELETE'' then
		episode_id := OLD.fk_episode;
	else
		episode_id := NEW.fk_episode;
	end if;
	-- backtrack to patient ID
	select into patient_id pk_patient
		from clin.v_pat_episodes vpep
		where vpep.pk_episode = episode_id
		limit 1;
	if not found then
		raise exception ''clin.trf_announce_%(sig)s_mod(): cannot find patient for episode [%%]'', episode_id;
	end if;
	-- now, execute() the NOTIFY
	execute ''notify "%(sig)s_mod_db:'' || patient_id || ''"'';
	return NULL;
end;
' language 'plpgsql';

create constraint trigger tr_%(sig)s_mod
	after insert or delete or update
	on clin.%(tbl)s
	deferrable
	for each row
		execute procedure clin.trf_announce_%(sig)s_mod()
;
"""
#------------------------------------------------------------------
def create_notification_schema(aCursor):
	cmd = "select table_name, notification_name from notifying_tables";
	rows, idx = gmPG2.run_ro_queries(link_obj = aCursor, queries = [{'cmd': cmd}])
	if len(rows) == 0:
		_log.Log(gmLog.lInfo, 'no notifying tables')
		return None
	_log.Log(gmLog.lData, rows)
	# for each notifying table
	schema = []
	for notifying_def in rows:
		tbl = notifying_def['table_name']
		sig = notifying_def['notification_name']
		schema.append(trigger_ddl % {'sig': sig, 'tbl': tbl})
		schema.append('-- ----------------------------------------------')
	return schema
#==================================================================
# main
#------------------------------------------------------------------
if __name__ == "__main__" :

	conn = gmGP2.get_connection(readonly=False, pooled=False)
	curs = conn.cursor()

	schema = create_notification_schema(curs)

	curs.close()
	conn.close()

	if schema is None:
		print "error creating schema"
		sys.exit(-1)

	file = open ('notification-schema.sql', 'wb')
	for line in schema:
		file.write("%s;\n" % line)
	file.close()

#==================================================================
# $Log: gmNotificationSchemaGenerator.py,v $
# Revision 1.16  2006-12-06 16:11:25  ncq
# - port to gmPG2
#
# Revision 1.15  2006/11/14 23:29:01  ncq
# - explicitely drop notifiation functions so we can change
#   return type from opaque to trigger
#
# Revision 1.14  2005/12/04 09:34:44  ncq
# - make fit for schema support
# - move some queries to gmPG
# - improve DDL templates (use or replace on functions)
#
# Revision 1.13  2005/09/13 11:51:42  ncq
# - properly drop trigger functions so update works
#
# Revision 1.12  2005/06/01 23:19:38  ncq
# - make notification triggers deferrable - useful for special
#   situations such as when loading a patient SQL dump
#
# Revision 1.11  2005/03/14 14:39:49  ncq
# - id_patient -> pk_patient
#
# Revision 1.10  2004/11/24 15:38:07  ncq
# - improve generated change triggers
#
# Revision 1.9  2004/09/17 20:57:12  ncq
# - use lowercase since things will be lowercase anyways
#
# Revision 1.8  2004/07/17 21:23:49  ncq
# - run_query now has verbosity argument, so use it
#
# Revision 1.7  2004/06/28 13:31:17  ncq
# - really fix imports, now works again
#
# Revision 1.6  2004/06/28 13:23:20  ncq
# - fix import statements
#
# Revision 1.5  2004/06/26 07:33:55  ncq
# - id_episode -> fk/pk_episode
#
# Revision 1.4  2004/04/17 11:54:16  ncq
# - v_patient_episodes -> v_pat_episodes
#
# Revision 1.3  2004/02/25 09:46:36  ncq
# - import from pycommon now, not python-common
#
# Revision 1.2  2003/12/01 22:10:55  ncq
# - typo
#
# Revision 1.1  2003/11/28 10:16:06  ncq
# - initial check-in
#
