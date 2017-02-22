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
	_payload := ''operation='' || TG_OP || ''::'' || TG_ARGV[0] || ''::row PK='' || coalesce(_pk_col_val::text, ''NULL'');

	_identity_accessor_SQL := TG_ARGV[2];
	if _identity_accessor_SQL <> ''<NULL>'' then
		EXECUTE _identity_accessor_SQL INTO STRICT _pk_identity USING NEW;
		_payload := _payload || ''::person PK='' || coalesce(_pk_identity::text, ''NULL'');
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
	_payload := TG_ARGV[0] || ''::row PK='' || coalesce(_pk_col_val::text, ''NULL'');

	_identity_accessor_SQL := TG_ARGV[2];
	if _identity_accessor_SQL <> ''<NULL>'' then
		--raise notice ''%.%: %'', TG_TABLE_SCHEMA, TG_TABLE_NAME, _identity_accessor_SQL;
		EXECUTE _identity_accessor_SQL INTO STRICT _pk_identity USING OLD;
		_payload := _payload || ''::person PK='' || coalesce(_pk_identity::text, ''NULL'');
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
drop function if exists gm.create_table_mod_triggers(_schema_name name, _table_name name, _drop_old_triggers boolean);

create or replace function gm.create_table_mod_triggers(_schema_name name, _table_name name)
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
		if _accessor_col = ''fk_encounter'' then					-- retrieve identity PK via fk_encounter
			_identity_accessor_SQL := ''select fk_patient from clin.encounter where pk = $1.fk_encounter limit 1'';
		elsif _accessor_col = ''fk_identity'' then					-- retrieve identity PK via fk_identity
			_identity_accessor_SQL := ''select $1.fk_identity'';
		elsif _accessor_col = ''fk_patient'' then					-- retrieve identity PK via fk_patient
			_identity_accessor_SQL := ''select $1.fk_patient'';
		elsif _accessor_col = ''id_identity'' then					-- retrieve identity PK via id_identity
			_identity_accessor_SQL := ''select $1.id_identity'';
		else
			_identity_accessor_SQL := ''<NULL>'';
		end if;
	end if;

	-- drop triggers should they exist
	-- new-name announcement triggers
	_cmd := ''drop trigger if exists zzz_tr_announce_'' || _schema_name || ''_'' || _table_name || ''_ins_upd on '' || _qualified_table || '' cascade;'';
	execute _cmd;
	_cmd := ''drop trigger if exists zzz_tr_announce_'' || _schema_name || ''_'' || _table_name || ''_del on '' || _qualified_table || '' cascade;'';
	execute _cmd;

	-- re-create triggers
	-- 1) INSERT/UPDATE
	_payload := ''table='' || _qualified_table || ''::PK name='' || _PK_col_name;
	_cmd := ''create constraint trigger zzz_tr_announce_'' || _schema_name || ''_'' || _table_name || ''_ins_upd'';
	_cmd := _cmd || '' after insert or update'';
	_cmd := _cmd || '' on '' || _qualified_table;
	-- needed so a SELECT inside, say, _identity_accessor_SQL running
	-- concurrently to a "lengthy" TX does not create a serialization
	-- failure by being a rw-dependancy pivot
	_cmd := _cmd || '' deferrable initially deferred'';
	_cmd := _cmd || '' for each row'';
	_cmd := _cmd || '' execute procedure gm.trf_announce_table_ins_upd('''''' || _payload || '''''', '''''' || _pk_accessor_SQL || '''''', '''''' || _identity_accessor_SQL || '''''');'';
	execute _cmd;
	-- 2) DELETE
	_payload := ''operation=DELETE::'' || _payload;
	_cmd := ''create constraint trigger zzz_tr_announce_'' || _schema_name || ''_'' || _table_name || ''_del'';
	_cmd := _cmd || '' after delete'';
	_cmd := _cmd || '' on '' || _qualified_table;
	-- needed so a SELECT inside, say, _identity_accessor_SQL running
	-- concurrently to a "lengthy" TX does not create a serialization
	-- failure by being a rw-dependancy pivot
	_cmd := _cmd || '' deferrable initially deferred'';
	_cmd := _cmd || '' for each row'';
	_cmd := _cmd || '' execute procedure gm.trf_announce_table_del('''''' || _payload || '''''', '''''' || _pk_accessor_SQL || '''''', '''''' || _identity_accessor_SQL || '''''');'';
	execute _cmd;

	return True;
END;
';


comment on function gm.create_table_mod_triggers(_schema_name name, _table_name name) is
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
			PERFORM gm.create_table_mod_triggers(_notify_table.schema_name, _notify_table.table_name);
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
select gm.log_script_insertion('v22-notifications-dynamic.sql', '22.0');
