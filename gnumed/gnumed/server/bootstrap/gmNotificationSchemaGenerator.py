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
__author__ = "Karsten.Hilbert@gmx.net"
__license__ = "GPL v2 or later (details at http://www.gnu.org)"

import sys, os.path, string, logging


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmPG2


_log = logging.getLogger('gm.bootstrapper')

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
drop trigger tr_%(sig)s_mod on %(schema)s.%(tbl)s cascade;
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
drop trigger tr_%(sig)s_mod on %(schema)s.%(tbl)s cascade;
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

-- ----------------------------------------------
-- sanity check trigger on
-- clin.clin_root_item child tables
-- ----------------------------------------------

\unset ON_ERROR_STOP
drop function clin.trf_sanity_check_enc_epi_insert() cascade;
\set ON_ERROR_STOP 1

create function clin.trf_sanity_check_enc_epi_insert()
	returns trigger
	 language 'plpgsql'
	as '
declare
	_identity_from_encounter integer;
	_identity_from_episode integer;
begin
	-- sometimes .fk_episode can actually be NULL (eg. clin.substance_intake)
	-- in which case we do not need to run the sanity check
	if NEW.fk_episode is NULL then
		return NEW;
	end if;

	select fk_patient into _identity_from_encounter from clin.encounter where pk = NEW.fk_encounter;

	select fk_patient into _identity_from_episode from clin.encounter where pk = (
		select fk_encounter from clin.episode where pk = NEW.fk_episode
	);

	if _identity_from_encounter <> _identity_from_episode then
		raise exception ''INSERT into %.%: Sanity check failed. Encounter % patient = %. Episode % patient = %.'',
			TG_TABLE_SCHEMA,
			TG_TABLE_NAME,
			NEW.fk_encounter,
			_identity_from_encounter,
			NEW.fk_episode,
			_identity_from_episode
		;
		return NULL;
	end if;

	return NEW;
end;
';
"""

trigger_narrative_mod_announce = """
\unset ON_ERROR_STOP
drop trigger tr_narrative_mod on %(schema)s.%(tbl)s cascade;
\set ON_ERROR_STOP 1

-- %(schema)s.%(tbl)s
create constraint trigger tr_narrative_mod
	after insert or delete or update
	on %(schema)s.%(tbl)s
	deferrable
	for each row
		execute procedure clin.trf_announce_narrative_mod();



\unset ON_ERROR_STOP
drop trigger tr_sanity_check_enc_epi_insert on %(schema)s.%(tbl)s cascade;
\set ON_ERROR_STOP 1

-- %(schema)s.%(tbl)s
create trigger tr_sanity_check_enc_epi_insert
	before insert
	on %(schema)s.%(tbl)s
	for each row
		execute procedure clin.trf_sanity_check_enc_epi_insert();
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

	# explicitly append dem.identity
	schema.append(trigger_identity_mod_announce)

	# explicitly append clin.waiting_list
	# it does have an identity accessor but we want a generic non-patient signal, too
	schema.append(trigger_ddl_without_pk % {
		'schema': 'clin',
		'tbl': 'waiting_list',
		'sig': 'waiting_list_generic'
	})

	# explicitly append dem.message_inbox with generic non-patient signal
	# it does have an identity accessor but we want a generic non-patient signal, too
	# this only works starting with v12
	schema.append(trigger_ddl_without_pk % {
		'schema': 'dem',
		'tbl': 'message_inbox',
		'sig': 'message_inbox_generic'
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
