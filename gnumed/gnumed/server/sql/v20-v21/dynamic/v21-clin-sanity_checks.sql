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

	-- verify that it points to clin.encounter.pk
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
		raise exception
			''gm.create_enc_epi_sanity_check_trigger(): <%.%> does not point to clin.encounter.pk'', _qualified_table2check, _fk_encounter_col
			USING ERRCODE = ''invalid_foreign_key''
		;
		return false;
	end if;

	-- verify that it points to clin.episode.pk
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
		raise exception
			''gm.create_enc_epi_sanity_check_trigger(): <%.%> does not point to clin.episode.pk'', _qualified_table2check, _fk_episode_col
			USING ERRCODE = ''invalid_foreign_key''
		;
		return false;
	end if;

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
select gm.log_script_insertion('v21-clin-sanity_checks.sql', '21.0');
