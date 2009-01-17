"""Automatic GNUmed notification trigger generation.

This module creates notification triggers on tables.

Theory of operation:

Any table that should send notifies must be recorded in
the table "gm.notifying_tables".

Any table inheriting from clin.clin_root_item is added
automatically and the signal narrative_mod_db is sent
from it.
"""
#==================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/bootstrap/gmNotificationSchemaGenerator.py,v $
__version__ = "$Revision: 1.32 $"
__author__ = "Karsten.Hilbert@gmx.net"
__license__ = "GPL (details at http://www.gnu.org)"

import sys, os.path, string, logging


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmPG2


_log = logging.getLogger('gm.bootstrapper')
_log.info(__version__)

#==================================================================
# SQL statements for notification triggers
#------------------------------------------------------------------

# this map defines how table columns can be used in SQL to
# access the identity PK related to a row in that table
col2identity_accessor = {
	'fk_encounter': u"""-- retrieve identity PK via fk_encounter
	if TG_OP = ''DELETE'' then
		select into _pk_identity fk_patient from clin.encounter where pk = OLD.fk_encounter limit 1;
	else
		select into _pk_identity fk_patient from clin.encounter where pk = NEW.fk_encounter limit 1;
	end if;""",

	'fk_identity': u"""-- retrieve identity PK via fk_identity
	if TG_OP = ''DELETE'' then
		_pk_identity := OLD.fk_identity;
	else
		_pk_identity := NEW.fk_identity;
	end if;""",

	'fk_patient': u"""-- retrieve identity PK via fk_patient
	if TG_OP = ''DELETE'' then
		_pk_identity := OLD.fk_patient;
	else
		_pk_identity := NEW.fk_patient;
	end if;""",

	'id_identity': u"""-- retrieve identity PK via id_identity
	if TG_OP = ''DELETE'' then
		_pk_identity := OLD.id_identity;
	else
		_pk_identity := NEW.id_identity;
	end if;"""
}

trigger_ddl_without_pk = """
-- ----------------------------------------------
\unset ON_ERROR_STOP
drop function %(schema)s.trf_announce_%(sig)s_mod() cascade;
drop function %(schema)s.trf_announce_%(sig)s_mod_no_pk() cascade;
\set ON_ERROR_STOP 1

create function %(schema)s.trf_announce_%(sig)s_mod_no_pk() returns trigger as '
begin
	execute ''notify "%(sig)s_mod_db:"'';
	return NULL;
end;
' language 'plpgsql';

create constraint trigger tr_%(sig)s_mod
	after insert or delete or update
	on %(schema)s.%(tbl)s
	deferrable
	for each row
		execute procedure %(schema)s.trf_announce_%(sig)s_mod_no_pk();

-- tell backend listener to NOT listen for patient-specific signals on this table
update
	gm.notifying_tables
set
	carries_identity_pk = False
where
	schema_name = '%(schema)s'
	and table_name = '%(tbl)s'
	and signal = '%(sig)s';
"""

trigger_ddl_with_pk = """
-- ----------------------------------------------
\unset ON_ERROR_STOP
drop function %(schema)s.trf_announce_%(sig)s_mod() cascade;
\set ON_ERROR_STOP 1

create function %(schema)s.trf_announce_%(sig)s_mod() returns trigger as '
declare
	_pk_identity integer;
begin
	_pk_identity := NULL;

	%(identity_accessor)s

	-- soft error out if not found
	if _pk_identity is NULL then
		raise notice ''%(schema)s.trf_announce_%(sig)s_mod(): cannot determine identity PK on table <%(schema)s.%(tbl)s>'';
		return NULL;
	end if;

	-- now, execute() the NOTIFY
	execute ''notify "%(sig)s_mod_db:'' || _pk_identity || ''"'';
	return NULL;
end;
' language 'plpgsql';

create constraint trigger tr_%(sig)s_mod
	after insert or delete or update
	on %(schema)s.%(tbl)s
	deferrable
	for each row
		execute procedure %(schema)s.trf_announce_%(sig)s_mod();

-- tell backend listener to listen for patient-specific signals on this table
update
	gm.notifying_tables
set
	carries_identity_pk = True
where
	schema_name = '%(schema)s'
	and table_name = '%(tbl)s'
	and signal = '%(sig)s';
"""

func_narrative_mod_announce = """
-- ----------------------------------------------
-- narrative modfication announcement triggers
-- on clin.clin_root_item child tables
-- ----------------------------------------------

\unset ON_ERROR_STOP
drop function clin.trf_announce_narrative_mod() cascade;
\set ON_ERROR_STOP 1

create function clin.trf_announce_narrative_mod()
	returns trigger
	 language 'plpgsql'
	as '
declare
	_pk_identity integer;
begin
	_pk_identity := NULL;

	-- retrieve identity PK via fk_encounter
	if TG_OP = ''DELETE'' then
		select into _pk_identity fk_patient from clin.encounter where pk = OLD.fk_encounter limit 1;
	else
		select into _pk_identity fk_patient from clin.encounter where pk = NEW.fk_encounter limit 1;
	end if;

	-- soft error out if not found
	if _pk_identity is NULL then
		raise notice ''clin.trf_announce_narrative_mod(): cannot determine identity PK on clin.clin_root_item child table'';
		return NULL;
	end if;

	-- now, execute() the NOTIFY
	execute ''notify "narrative_mod_db:'' || _pk_identity || ''"'';
	return NULL;
end;
';

-- tell backend listener to listen for patient-specific signals on this table
-- it does in fact not matter which table this is about,
-- it suffices to record the signal at all

delete from gm.notifying_tables where
	schema_name = 'any schema'
	and signal = 'narrative';

insert into gm.notifying_tables (
	schema_name, table_name, signal, carries_identity_pk
) values (
	'any schema',
	'clin.clin_root_item children',
	'narrative',
	True
);
"""

trigger_narrative_mod_announce = """
-- %(schema)s.%(tbl)s
create constraint trigger tr_narrative_mod
	after insert or delete or update
	on %(schema)s.%(tbl)s
	deferrable
	for each row
		execute procedure clin.trf_announce_narrative_mod();
"""



dem_identity_accessor = u"""-- retrieve identity PK via pk
	if TG_OP = ''DELETE'' then
		_pk_identity := OLD.pk;
	else
		_pk_identity := NEW.pk;
	end if;"""

trigger_identity_mod_announce = """
\unset ON_ERROR_STOP
drop function dem.trf_identity_mod() cascade;
drop function dem.trf_identity_mod_no_pk() cascade;
\set ON_ERROR_STOP 1

%s
""" % (trigger_ddl_with_pk % {
		'schema': 'dem',
		'tbl': 'identity',
		'sig': 'identity',
		'identity_accessor': dem_identity_accessor
	}
)

#------------------------------------------------------------------
def create_narrative_notification_schema(cursor):

	rows = gmPG2.get_child_tables (
		schema = u'clin',
		table = u'clin_root_item',
		link_obj = cursor
	)

	_log.info('child tables of clin.clin_root_item:')
	_log.info(', '.join([ u'%s.%s' % (r[0], r[1]) for r in rows ]))

	ddl = [func_narrative_mod_announce]

	for row in rows:
		ddl.append(trigger_narrative_mod_announce % {'schema': row[0], 'tbl': row[1]})

	ddl.append('-- ----------------------------------------------')

	return ddl
#------------------------------------------------------------------
def create_notification_schema(cursor):
	cmd = u"""
select
	schema_name, table_name, signal
from
	gm.notifying_tables
where
	schema_name != 'any schema'
		and
	schema_name != 'any'
"""
	rows, idx = gmPG2.run_ro_queries(link_obj = cursor, queries = [{'cmd': cmd}])

	if len(rows) == 0:
		_log.info('no notifying tables')
		return None

	_log.info('known identity accessor columns: %s' % col2identity_accessor.keys())

	# for each notifying table
	schema = []
	for notifying_def in rows:
		_log.info('creating notification DDL for: %s' % notifying_def)

		# does table have a known patient-related column ?
		identity_access_col = None
		for key in col2identity_accessor.keys():
			cmd = u"""select exists (
				select 1 from information_schema.columns where
					table_schema = %(schema)s and
					table_name = %(tbl)s and
					column_name = %(col)s
				)"""
			args = {
				'schema': notifying_def['schema_name'],
				'tbl': notifying_def['table_name'],
				'col': key
			}
			rows, idx = gmPG2.run_ro_queries(link_obj = cursor, queries = [{'cmd': cmd, 'args': args}])
			if rows[0][0] is True:
				identity_access_col = key
				break

		if identity_access_col is not None:
			_log.info('identity accessor on table [%s.%s] is column [%s]' % (
				notifying_def['schema_name'],
				notifying_def['table_name'],
				identity_access_col
			))
			schema.append(trigger_ddl_with_pk % {
				'schema': notifying_def['schema_name'],
				'tbl': notifying_def['table_name'],
				'sig': notifying_def['signal'],
				'identity_accessor': col2identity_accessor[identity_access_col]
			})
		else:
			_log.info('no known identity accessor found on table [%s.%s]' % (
				notifying_def['schema_name'],
				notifying_def['table_name']
			))
			if '%s.%s' % (notifying_def['schema_name'], notifying_def['table_name']) == 'dem.identity':
				_log.info('skipping dem.identity')
				continue
			schema.append(trigger_ddl_without_pk % {
				'schema': notifying_def['schema_name'],
				'tbl': notifying_def['table_name'],
				'sig': notifying_def['signal']
			})

	# explicitely append dem.identity
	schema.append(trigger_identity_mod_announce)

	# explicitely append clin.waiting_list with generic non-patient signal
	schema.append(trigger_ddl_without_pk % {
		'schema': 'clin',
		'tbl': 'waiting_list',
		'sig': 'waiting_list_generic'
	})

	schema.append('-- ----------------------------------------------')

	return schema
#==================================================================
# main
#------------------------------------------------------------------
if __name__ == "__main__" :

	logging.getLogger().setLevel(logging.DEBUG)

	conn = gmPG2.get_connection(readonly=True, pooled=False)
	curs = conn.cursor()

	schema = create_notification_schema(curs)
	schema.extend(create_narrative_notification_schema(curs))

	curs.close()
	conn.close()

	if schema is None:
		print "error creating schema"
		sys.exit(-1)

	file = open('notification-schema.sql', 'wb')
	for line in schema:
		file.write("%s\n" % line)
	file.close()

#==================================================================
# $Log: gmNotificationSchemaGenerator.py,v $
# Revision 1.32  2009-01-17 23:13:18  ncq
# - better name for non-identity announcers
# - explicitely disable identity listening for non-identity tables
# - improve dem.identity support
# - add explicit generic waiting list support
#
# Revision 1.31  2009/01/08 16:43:58  ncq
# - no more fk_identity in blobs.doc_med so remove identity accessor mapping
#
# Revision 1.30  2008/07/10 08:36:27  ncq
# - protect against old mischief, too
#
# Revision 1.29  2008/07/10 08:19:30  ncq
# - protect standard notification generation against existence of
#   dummy entry for narrative notification used for telling client
#   backend listener what to listen for (that is, don't fail notification
#   generation on "any schema"."clin.clin_root_item children")
#
# Revision 1.28  2008/04/11 12:30:22  ncq
# - create notification schema for clin.clin_root_item children
#
# Revision 1.27  2008/01/07 14:15:43  ncq
# - port to gmCfg2/gmLog2
# - create database with default transaction mode set to readonly
#
# Revision 1.26  2007/11/28 22:38:10  ncq
# - make it know about dem.identity
#
# Revision 1.25  2007/11/28 14:01:07  ncq
# - fix ,
#
# Revision 1.24  2007/11/28 11:57:01  ncq
# - support id_identity as person pk accessor
#
# Revision 1.23  2007/11/05 12:11:16  ncq
# - do not FAIL on not being able to find the pk_identity for
#   notification, it's likely due to a framing transaction
#   deleting our parent record
#
# Revision 1.22  2007/11/04 22:59:17  ncq
# - remove completed TODO item
#
# Revision 1.21  2007/10/30 12:53:07  ncq
# - if a table attaches the patient pk document that fact for the backend listener
#
# Revision 1.20  2007/10/30 08:30:17  ncq
# - greatly smarten up notification trigger generation
#   - now determine identity column at bootstrap time
#     rather than trigger runtime
#   - autodetect patient related tables
#
# Revision 1.19  2007/10/25 12:28:30  ncq
# - need to PERFORM, not SELECT when throwing away results
# - proper quoting
#
# Revision 1.18  2007/10/23 21:32:54  ncq
# - fix test suite
# - improve generated triggers
#
# Revision 1.17  2006/12/18 17:38:19  ncq
# - u''ify 2 queries
#
# Revision 1.16  2006/12/06 16:11:25  ncq
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
