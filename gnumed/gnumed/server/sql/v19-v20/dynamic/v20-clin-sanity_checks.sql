-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
\set ON_ERROR_STOP 1

--set default_transaction_read_only to off;

set check_function_bodies to on;

-- --------------------------------------------------------------
-- drop old function (and triggers)
drop function if exists clin.trf_sanity_check_enc_epi_insert() cascade;

create or replace function clin.trf_sanity_check_enc_epi_ins_upd()
	returns trigger
	 language 'plpgsql'
	as '
declare
	_fk_encounter_col text;
	_enc_pk integer;
	_fk_episode_col text;
	_epi_pk integer;
	_identity_from_encounter integer;
	_identity_from_episode integer;
	_cmd text;
begin
	_fk_encounter_col := TG_ARGV[0];
	_fk_episode_col := TG_ARGV[1];

	_cmd := ''select $1.'' || _fk_encounter_col;
	EXECUTE _cmd INTO STRICT _enc_pk USING NEW;
	select fk_patient into _identity_from_encounter from clin.encounter where pk = _enc_pk;
--	raise notice ''%: % -> %'', _cmd, _enc_pk, _identity_from_encounter;

	_cmd := ''select $1.'' || _fk_episode_col;
	EXECUTE _cmd INTO STRICT _epi_pk USING NEW;
	select fk_patient into _identity_from_episode from clin.encounter where pk = (select fk_encounter from clin.episode where pk = _epi_pk);
--	raise notice ''%: % -> %'', _cmd, _epi_pk, _identity_from_episode;

	if _identity_from_encounter <> _identity_from_episode then
		raise exception ''% into %.%: Sanity check failed. %=% -> patient=%. %=% -> patient=%.'',
			TG_OP,
			TG_TABLE_SCHEMA,
			TG_TABLE_NAME,
			_fk_encounter_col,
			_enc_pk,
			_identity_from_encounter,
			_fk_episode_col,
			_epi_pk,
			_identity_from_episode
		;
		return NULL;
	end if;

	return NEW;
end;
';


comment on function clin.trf_sanity_check_enc_epi_ins_upd() is
	'this function is used in triggers and checks whether foreign keys to clin.episode.pk and clin.encounter.pk on a single table ultimately point to the same patient';

-- --------------------------------------------------------------
create or replace function gm.create_enc_epi_sanity_check_trigger(_schema_name name, _table_name name, _fk_encounter_col name, _fk_episode_col name)
	returns boolean
	language plpgsql
	as '
DECLARE
	_qualified_table2check text;
	_msg text;
	_cmd text;
BEGIN
	_qualified_table2check := _schema_name || ''.'' || _table_name;
	raise notice ''gm.create_enc_epi_sanity_check_trigger(): % (.% vs .%)'', _qualified_table2check, _fk_encounter_col, _fk_episode_col;

	-- verify table exists
	if not exists(select 1 from information_schema.tables where table_schema = _schema_name and table_name = _table_name) then
		raise warning ''gm.create_enc_epi_sanity_check_trigger(): table <%> does not exist'', _qualified_table2check;
		raise exception undefined_table;
		return false;
	end if;

	-- verify points to clin.encounter.pk
	if not exists (
		select 1
		from
			pg_catalog.pg_constraint fk_tbl
		where
			fk_tbl.contype = ''f''
				AND
			fk_tbl.confrelid = ''clin.encounter''::regclass
				AND
			fk_tbl.conrelid = _qualified_table2check::regclass
				AND
			fk_tbl.confkey[1] = (
				select attnum from pg_catalog.pg_attribute col_tbl
				where
					col_tbl.attname = ''pk''
						AND
					col_tbl.attrelid = ''clin.encounter''::regclass
			)
				AND
			fk_tbl.conkey[1] = (
				select attnum from pg_catalog.pg_attribute col_tbl
				where
					col_tbl.attname = _fk_encounter_col
						AND
					col_tbl.attrelid = _qualified_table2check::regclass
			)
	) then
		raise warning ''gm.create_enc_epi_sanity_check_trigger(): <%.%> does not point to clin.encounter.pk'', _qualified_table2check, _fk_encounter_col;
		raise exception invalid_foreign_key;
		return false;
	end if;

	-- verify points to clin.episode.pk
	if not exists (
		select 1
		from
			pg_catalog.pg_constraint fk_tbl
		where
			fk_tbl.contype = ''f''
				AND
			fk_tbl.confrelid = ''clin.episode''::regclass
				AND
			fk_tbl.conrelid = _qualified_table2check::regclass
				AND
			fk_tbl.confkey[1] = (
				select attnum from pg_catalog.pg_attribute col_tbl
				where
					col_tbl.attname = ''pk''
						AND
					col_tbl.attrelid = ''clin.episode''::regclass
			)
				AND
			fk_tbl.conkey[1] = (
				select attnum from pg_catalog.pg_attribute col_tbl
				where
					col_tbl.attname = _fk_episode_col
						AND
					col_tbl.attrelid = _qualified_table2check::regclass
			)
	) then
		raise warning ''gm.create_enc_epi_sanity_check_trigger(): <%.%> does not point to clin.episode.pk'', _qualified_table2check, _fk_episode_col;
		raise exception invalid_foreign_key;
		return false;
	end if;

	-- drop old trigger (remove in v21)
	_cmd := ''drop trigger if exists tr_sanity_check_enc_epi_insert on '' || _qualified_table2check || '' cascade'';
	execute _cmd;

	-- re-create trigger
	_cmd := ''drop trigger if exists tr_sanity_check_enc_epi_ins_upd on '' || _qualified_table2check || '' cascade'';
	execute _cmd;
	_cmd := ''create trigger tr_sanity_check_enc_epi_ins_upd '';
	_cmd := _cmd || ''before insert or update '';
	_cmd := _cmd || ''on '' || _qualified_table2check || '' '';
	_cmd := _cmd || ''for each row when (NEW.fk_episode is not null) '';
	_cmd := _cmd || ''execute procedure clin.trf_sanity_check_enc_epi_ins_upd('''''' || _fk_encounter_col || '''''', '''''' || _fk_episode_col || '''''')'';
	execute _cmd;

	return True;
END;
';


comment on function gm.create_enc_epi_sanity_check_trigger(_schema_name name, _table_name name, _fk_encounter_col name, _fk_episode_col name) is
	'This function can be run on any table in order to add enccounter <-> episode sanity check triggers to that table.';

-- --------------------------------------------------------------
create or replace function gm.create_all_enc_epi_sanity_check_triggers()
	returns boolean
	language plpgsql
	as '
DECLARE
	_schema name;
	_table name;
	_qualified_table2check name;
	_fk_encounter_col name;
	_fk_episode_col name;
	_total_success boolean;
BEGIN
	raise notice ''gm.create_all_enc_epi_sanity_check_triggers()'';

	_total_success := True;
	-- loop over tables with encounter AND episode FKs
	-- (assumes there is only one of each)
	for _schema, _table in
		select
			(select pg_n.nspname from pg_catalog.pg_namespace pg_n where pg_n.oid = pg_c.relnamespace),
			pg_c.relname
		from pg_class pg_c
		where pg_c.oid in (
			select distinct fk_tbl.conrelid
			from pg_catalog.pg_constraint fk_tbl
			where
				exists (
					select 1 from pg_catalog.pg_constraint fk_tbl1
					where
						fk_tbl1.contype = ''f''
							and
						fk_tbl1.conrelid = fk_tbl.conrelid
							and
						fk_tbl1.confrelid = ''clin.encounter''::regclass
							and
						fk_tbl1.confkey[1] = (
							select attnum from pg_catalog.pg_attribute col_tbl
							where
								col_tbl.attname = ''pk''
									AND
								col_tbl.attrelid = ''clin.encounter''::regclass
						)
				)
					and
				exists (
					select 1 from pg_catalog.pg_constraint fk_tbl2
					where
						fk_tbl2.contype = ''f''
							and
						fk_tbl2.conrelid = fk_tbl.conrelid
							and
						fk_tbl2.confrelid = ''clin.episode''::regclass
							and
						fk_tbl2.confkey[1] = (
							select attnum from pg_catalog.pg_attribute col_tbl
							where
								col_tbl.attname = ''pk''
									AND
								col_tbl.attrelid = ''clin.episode''::regclass
						)
				)
		)
	loop
		_qualified_table2check := _schema || ''.'' || _table;
		raise notice ''gm.create_all_enc_epi_sanity_check_triggers(): processing %'', _qualified_table2check;

		-- find encounter FK column name
		select col_tbl.attname into _fk_encounter_col
		from pg_catalog.pg_attribute col_tbl
		where
			col_tbl.attrelid = _qualified_table2check::regclass
				and
			col_tbl.attnum = (
				select fk_tbl.conkey[1]
				from pg_catalog.pg_constraint fk_tbl
				where
					fk_tbl.contype = ''f''
						and
					fk_tbl.conrelid = _qualified_table2check::regclass
						and
					fk_tbl.confrelid = ''clin.encounter''::regclass
						and
					fk_tbl.confkey[1] = (
						select col_tbl1.attnum
						from pg_catalog.pg_attribute col_tbl1
						where
							col_tbl1.attname = ''pk''
								AND
							col_tbl1.attrelid = ''clin.encounter''::regclass
					)
				)
			;

		-- find episode FK column name
		select col_tbl.attname into _fk_episode_col
		from pg_catalog.pg_attribute col_tbl
		where
			col_tbl.attrelid = _qualified_table2check::regclass
				and
			col_tbl.attnum = (
				select fk_tbl.conkey[1]
				from pg_catalog.pg_constraint fk_tbl
				where
					fk_tbl.contype = ''f''
						and
					fk_tbl.conrelid = _qualified_table2check::regclass
						and
					fk_tbl.confrelid = ''clin.episode''::regclass
						and
					fk_tbl.confkey[1] = (
						select col_tbl1.attnum
						from pg_catalog.pg_attribute col_tbl1
						where
							col_tbl1.attname = ''pk''
								AND
							col_tbl1.attrelid = ''clin.episode''::regclass
					)
				)
			;

		-- now create the trigger
		BEGIN
			PERFORM gm.create_enc_epi_sanity_check_trigger(_schema, _table, _fk_encounter_col, _fk_episode_col);
		EXCEPTION
			WHEN undefined_table OR invalid_foreign_key THEN
				raise warning ''gm.create_all_enc_epi_sanity_check_triggers(): error processing <%.%>, skipping'', _schema, _table;
				_total_success := False;
		END;

	end loop;
	return _total_success;
END;
';

comment on function gm.create_all_enc_epi_sanity_check_triggers() is
	'(Re)create sanity check triggers for all tables which have both fk_encounter and fk_episode.';

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-clin-sanity_checks.sql', '20.0');
