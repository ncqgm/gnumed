-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten.Hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

--set default_transaction_read_only to off;
set check_function_bodies to on;

-- --------------------------------------------------------------
create or replace function gm.trf_announce_table_ins_upd()
	returns trigger
	language 'plpgsql'
	as '
declare
	_payload text;
	_pk_accessor_SQL text;
	_pk_col_val integer;
	_identity_accessor_SQL text;
	_pk_identity integer;
begin
	_pk_accessor_SQL := TG_ARGV[1];
	EXECUTE _pk_accessor_SQL INTO STRICT _pk_col_val USING NEW;
	_payload := ''operation='' || TG_OP || ''::'' || TG_ARGV[0] || ''::row PK='' || _pk_col_val;

	_identity_accessor_SQL := TG_ARGV[2];
	if _identity_accessor_SQL <> ''<NULL>'' then
		EXECUTE _identity_accessor_SQL INTO STRICT _pk_identity USING NEW;
		_payload := _payload || ''::person PK='' || _pk_identity;
	end if;

	perform pg_notify(''gm_table_mod'', _payload);
	return NULL;
end;
';


comment on function gm.trf_announce_table_ins_upd() is
'Trigger function announcing an INSERT or UPDATE to a table.

sends signal: gm_table_mod
payload:
	operation=INSERT/UPDATE,
	table=the table that is updated,
	PK name=the name of the PK column of the table (requires single column PKs),
	row PK=the PK of the affected row,
	person PK=the PK of the affected person,
';

-- --------------------------------------------------------------
create or replace function gm.trf_announce_table_del()
	returns trigger
	language 'plpgsql'
	as '
declare
	_payload text;
	_pk_accessor_SQL text;
	_pk_col_val integer;
	_identity_accessor_SQL text;
	_pk_identity integer;
begin
	_pk_accessor_SQL := TG_ARGV[1];
	EXECUTE _pk_accessor_SQL INTO STRICT _pk_col_val USING OLD;
	_payload := TG_ARGV[0] || ''::row PK='' || _pk_col_val;

	_identity_accessor_SQL := TG_ARGV[2];
	if _identity_accessor_SQL <> ''<NULL>'' then
		EXECUTE _identity_accessor_SQL INTO STRICT _pk_identity USING OLD;
		_payload := _payload || ''::person PK='' || _pk_identity;
	end if;

	perform pg_notify(''gm_table_mod'', _payload);
	return NULL;
end;
';


comment on function gm.trf_announce_table_del() is
'Trigger function announcing a DELETE on a table.

sends signal: gm_table_mod
payload:
	operation=DELETE,
	table=the table that is updated,
	PK name=the name of the PK column of the table (requires single column PKs),
	row PK=the PK of the affected row,
	person PK=the PK of the affected person,
';

-- --------------------------------------------------------------
-- the function
--		"clin.trf_sanity_check_enc_epi_insert()"
-- used to be hardcoded in gmNotificationSchema.py and was
-- re-created whenever that code was run
--
-- starting with gnumed_v20 we don't run (or even have)
-- "gmNotificationSchema.py" anymore
--
-- during bootstrapping we still run the v19 SQL scripts,
-- however (just like any other previous SQL)
--
-- the v19 notification SQL scripts includes a notification
-- trigger generation function
--		"gm.create_table_mod_triggers()"
-- which was previously used to piggy-back creating another
-- trigger to check encounter/episode consistency
--
-- *that* trigger, of course, still uses the old function
--		"clin.trf_sanity_check_enc_epi_insert()"
-- which is not created anymore because the script
-- "gmNotificationSchema.py" is no longer with us
--
-- hence we need to provide 
--		"clin.trf_sanity_check_enc_epi_insert()"
-- here in order to make it available for any v19 created
-- with the v20 bootstrapper (regardless of whether that v19
-- will be put to use with a 1.4 client or whether it will
-- only serve as the last stepping stone in bootstrapping v20
-- at which point the old function will be dropped again :-)
--
--
-- Do NOT backport this function to the 1.4/v19 branch !

drop function if exists clin.trf_sanity_check_enc_epi_insert() cascade;

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

-- --------------------------------------------------------------
create or replace function gm.create_table_mod_triggers(_schema_name name, _table_name name, _drop_old_triggers boolean)
	returns boolean
	language plpgsql
	as '
DECLARE
	_qualified_table text;
	_msg text;
	_payload text;
	_PK_col_name text;
	_pk_accessor_SQL text;
	_accessor_col text;
	_col_candidate text;
	_identity_accessor_SQL text;
	_cmd text;
	_old_signal text;
BEGIN
	_qualified_table := _schema_name || ''.'' || _table_name;
	raise notice ''gm.create_table_mod_triggers(): %'', _qualified_table;
	-- verify table exists
	if not exists(select 1 from information_schema.tables where table_schema = _schema_name and table_name = _table_name) then
		raise warning ''gm.create_table_mod_triggers(): table <%> does not exist'', _qualified_table;
		raise exception undefined_table;
		return false;
	end if;

	-- find PK column
	select
		pg_attribute.attname into _PK_col_name
	from
		pg_index, pg_class, pg_attribute
	where
		pg_class.oid = _qualified_table::regclass
			AND
		indrelid = pg_class.oid
			AND
		pg_attribute.attrelid = pg_class.oid
			AND
		pg_attribute.attnum = any(pg_index.indkey)
			AND
		indisprimary;
	if _PK_col_name is NULL then
		raise warning ''gm.create_table_mod_triggers(): table <%> lacks a primary key'', _qualified_table;
		raise exception undefined_column;
		return false;
	end if;

	_pk_accessor_SQL := ''select $1.'' || _PK_col_name;

	-- find identity accessor
	-- special case
	if _qualified_table = ''dem.identity'' then
		_identity_accessor_SQL := ''select $1.pk'';
	else
		-- look for columns by which to retrieve affected person
		_accessor_col := NULL;
		foreach _col_candidate in array array[''fk_identity'', ''fk_patient'', ''id_identity'', ''fk_encounter''] loop
			if exists (
				select 1 from pg_class, pg_attribute where
				pg_class.oid = _qualified_table::regclass
					AND
				pg_attribute.attname = _col_candidate
					AND
				pg_attribute.attrelid = pg_class.oid
			) then
				_accessor_col := _col_candidate;
				exit;
			end if;
		end loop;
		if _accessor_col is NULL then
			_identity_accessor_SQL := ''<NULL>'';
		elsif _accessor_col = ''fk_encounter'' then
			-- retrieve identity PK via fk_encounter
			_identity_accessor_SQL := ''select fk_patient from clin.encounter where pk = $1.fk_encounter limit 1'';
		elsif _accessor_col = ''fk_identity'' then
			-- retrieve identity PK via fk_identity
			_identity_accessor_SQL := ''select $1.fk_identity'';
		elsif _accessor_col = ''fk_patient'' then
			-- retrieve identity PK via fk_patient
			_identity_accessor_SQL := ''select $1.fk_patient'';
		elsif _accessor_col = ''id_identity'' then
			-- retrieve identity PK via id_identity
			_identity_accessor_SQL := ''select $1.id_identity'';
		end if;
	end if;

	-- drop triggers should they exist
	_cmd := ''drop trigger if exists tr_announce_'' || _schema_name || ''_'' || _table_name || ''_ins_upd on '' || _qualified_table || '' cascade;'';
	execute _cmd;
	_cmd := ''drop trigger if exists tr_announce_'' || _schema_name || ''_'' || _table_name || ''_del on '' || _qualified_table || '' cascade;'';
	execute _cmd;
	_cmd := ''drop trigger if exists tr_sanity_check_enc_epi_insert on '' || _qualified_table || '' cascade;'';
	execute _cmd;
	if _drop_old_triggers is true then
		select signal from gm.notifying_tables where schema_name = _schema_name and table_name = _table_name limit 1 into strict _old_signal;
		_cmd := ''drop function if exists '' || _schema_name || ''.trf_announce_'' || _table_name || ''_mod() cascade;'';
		execute _cmd;
		_cmd := ''drop function if exists '' || _schema_name || ''.trf_announce_'' || _old_signal || ''_mod() cascade;'';
		execute _cmd;
		_cmd := ''drop function if exists '' || _schema_name || ''.trf_announce_'' || _table_name || ''_mod_no_pk() cascade;'';
		execute _cmd;
		_cmd := ''drop function if exists '' || _schema_name || ''.trf_announce_'' || _old_signal || ''_mod_no_pk() cascade;'';
		execute _cmd;
		_cmd := ''drop function if exists '' || _schema_name || ''.trf_announce_'' || _table_name || ''_generic_mod_no_pk() cascade;'';
		execute _cmd;
		_cmd := ''drop function if exists '' || _schema_name || ''.trf_announce_'' || _old_signal || ''_generic_mod_no_pk() cascade;'';
		execute _cmd;
	end if;

	-- re-create triggers
	_payload := ''table='' || _qualified_table || ''::PK name='' || _PK_col_name;
	_cmd := ''create constraint trigger tr_announce_'' || _schema_name || ''_'' || _table_name || ''_ins_upd'';
	_cmd := _cmd || '' after insert or update'';
	_cmd := _cmd || '' on '' || _qualified_table;
	_cmd := _cmd || '' deferrable'';
	_cmd := _cmd || '' for each row'';
	if _identity_accessor_SQL is NULL then
		_cmd := _cmd || '' execute procedure gm.trf_announce_table_ins_upd('''''' || _payload || '''''', '''''' || _pk_accessor_SQL || '''''', NULL);'';
	else
		_cmd := _cmd || '' execute procedure gm.trf_announce_table_ins_upd('''''' || _payload || '''''', '''''' || _pk_accessor_SQL || '''''', '''''' || _identity_accessor_SQL || '''''');'';
	end if;
	execute _cmd;
	_payload := ''operation=DELETE::'' || _payload;
	_cmd := ''create constraint trigger tr_announce_'' || _schema_name || ''_'' || _table_name || ''_del'';
	_cmd := _cmd || '' after delete'';
	_cmd := _cmd || '' on '' || _qualified_table;
	_cmd := _cmd || '' deferrable'';
	_cmd := _cmd || '' for each row'';
	if _identity_accessor_SQL is NULL then
		_cmd := _cmd || '' execute procedure gm.trf_announce_table_del('''''' || _payload || '''''', '''''' || _pk_accessor_SQL || '''''', NULL);'';
	else
		_cmd := _cmd || '' execute procedure gm.trf_announce_table_del('''''' || _payload || '''''', '''''' || _pk_accessor_SQL || '''''', '''''' || _identity_accessor_SQL || '''''');'';
	end if;
	execute _cmd;
	-- encounter vs episode patient link sanity check trigger
	if exists (
		select 1 from information_schema.columns where
		table_schema = _schema_name and table_name = _table_name and column_name = ''fk_encounter''
	) then
		if exists (
			select 1 from information_schema.columns where
			table_schema = _schema_name and table_name = _table_name and column_name = ''fk_episode''
		) then
			_cmd := ''create trigger tr_sanity_check_enc_epi_insert before insert'';
			_cmd := _cmd || '' on '' || _qualified_table;
			_cmd := _cmd || '' for each row execute procedure clin.trf_sanity_check_enc_epi_insert();'';
			execute _cmd;
		end if;
	end if;

	return True;
END;
';


comment on function gm.create_table_mod_triggers(_schema_name name, _table_name name, _drop_old_triggers boolean) is
'This function can be run on any table in order to add notification triggers to that table.';

-- --------------------------------------------------------------
create or replace function gm.create_all_table_mod_triggers(_drop_old_triggers boolean)
	returns boolean
	language plpgsql
	as '
DECLARE
	_notify_table record;
	_cmd text;
	_total_success boolean;
BEGIN
	_total_success := True;
	-- loop over registered tables
	for _notify_table in select * from gm.notifying_tables loop
		BEGIN
			PERFORM gm.create_table_mod_triggers(_notify_table.schema_name, _notify_table.table_name, _drop_old_triggers);
		EXCEPTION
			WHEN undefined_table OR undefined_column THEN
				raise warning ''gm.create_all_table_mod_triggers(): error processing <%.%>, skipping'', _notify_table.schema_name, _notify_table.table_name;
				_total_success := False;
		END;
	end loop;
	return _total_success;
END;
';

comment on function gm.create_all_table_mod_triggers(_drop_old_triggers boolean) is
	'(Re)create all table mod triggers for all registered tables.';

-- --------------------------------------------------------------
-- cleanup old trigger leftovers

drop table if exists clin.active_substance cascade;
drop table if exists audit.log_active_substance cascade;
delete from gm.notifying_tables where schema_name = 'clin' and table_name = 'active_substance';
delete from gm.notifying_tables where schema_name = 'any schema' and table_name = 'clin.clin_root_item children';
delete from audit.audited_tables where "schema" = 'clin' and table_name = 'active_substance';

drop function if exists clin.trf_announce_narrative_mod() cascade;
drop function if exists clin.f_announce_clin_item_mod() cascade;

select gm.register_notifying_table('clin', 'clin_root_item');

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-notifications-dynamic.sql', '19.0');
