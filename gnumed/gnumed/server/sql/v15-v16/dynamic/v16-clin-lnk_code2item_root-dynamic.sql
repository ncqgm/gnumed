-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

set check_function_bodies to on;

-- --------------------------------------------------------------
comment on table clin.lnk_code2item_root is
'The parent table of all tables linking codes to EMR structures.

Coding tables check this table for existence of their PK in
.fk_generic_code in order to prevent cascading DELETEs/UPDATEs
from breaking referential integrity.

EMR structure tables foreign key into children of this table in
order to link structures to codes.
';

GRANT select on clin.lnk_code2item_root to "gm-public";
GRANT usage on clin.lnk_code2item_root_pk_lnk_code2item_seq to "gm-public";

-- --------------------------------------------------------------
-- .code_modifier
comment on column clin.lnk_code2item_root.code_modifier is
'Usage specific modifier on the base code, say, certainty or laterality of ICD-10 codes.';

-- --------------------------------------------------------------
-- .fk_item
comment on column clin.lnk_code2item_root.fk_item is
'Foreign key to clin.* tables';

-- apply this to child tables:
--\unset ON_ERROR_STOP
--alter table clin.lnk_code2xxx drop constraint clin_lc2xxx_code_uniq_per_item cascade;
--\set ON_ERROR_STOP 1
--
--alter table clin.lnk_code2xxx
--	add constraint clin_lc2xxx_code_uniq_per_item
--		unique(fk_generic_code, fk_item);

-- --------------------------------------------------------------
-- .fk_generic_code
comment on column clin.lnk_code2item_root.fk_generic_code is
'Custom foreign key to ref.coding_system_root.pk_coding_system.';


-- apply this to child tables:
--alter table clin.lnk_code2xxx
--	alter column fk_generic_code
--		set not null;


-- INSERT
\unset ON_ERROR_STOP
drop function clin.trf_ins_lc2sth_fk_generic_code() cascade;
\set ON_ERROR_STOP 1

create or replace function clin.trf_ins_lc2sth_fk_generic_code()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_msg text;
BEGIN
	perform 1 from ref.coding_system_root where pk_coding_system = NEW.fk_generic_code;

	if FOUND then
		return NEW;
	end if;

	_msg := ''clin.trf_ins_lc2sth_fk_generic_code(): INSERT into ''
		|| TG_TABLE_SCHEMA || ''.'' || TG_TABLE_NAME || '': ''
		|| ''fk_generic_code=('' || NEW.fk_generic_code || '') ''
		|| ''does not exist in ref.coding_system_root.pk_coding_system'';
	raise foreign_key_violation using message = _msg;

	return NEW;
END;';

comment on function clin.trf_ins_lc2sth_fk_generic_code() is
	'Check foreign key integrity on insert to *.fk_generic_code -> ref.coding_system_root.pk_coding_system.';

-- apply this to child tables:
-- INSERT
--create trigger tr_ins_lc2sth_fk_generic_code
--	before insert on clin.lnk_code2xxx
--		for each row execute procedure clin.trf_ins_lc2sth_fk_generic_code();


-- UPDATE
\unset ON_ERROR_STOP
drop function clin.trf_upd_lc2sth_fk_generic_code() cascade;
\set ON_ERROR_STOP 1

create or replace function clin.trf_upd_lc2sth_fk_generic_code()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_msg text;
BEGIN
	perform 1 from ref.coding_system_root where pk_coding_system = NEW.fk_generic_code;

	if FOUND then
		return NEW;
	end if;

	_msg := ''clin.trf_upd_lc2sth_fk_generic_code(): UPDATE of ''
		|| TG_TABLE_SCHEMA || ''.'' || TG_TABLE_NAME || '': ''
		|| ''fk_generic_code=('' || NEW.fk_generic_code || '') ''
		|| ''does not exist in ref.coding_system_root.pk_coding_system, ''
		|| ''old fk_generic_code=('' || OLD.fk_generic_code || '')'';
	raise foreign_key_violation using message = _msg;

	return OLD;
END;';

comment on function clin.trf_upd_lc2sth_fk_generic_code() is
	'Check foreign key integrity on update of *.fk_generic_code -> ref.coding_system_root.pk_coding_system.';

-- apply this to child tables:
-- UPDATE
--create trigger tr_upd_lc2sth_fk_generic_code
--	before update on clin.lnk_code2xxx
--		for each row execute procedure clin.trf_upd_lc2sth_fk_generic_code();

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-clin-lnk_code2item_root-dynamic.sql', '1.0');
