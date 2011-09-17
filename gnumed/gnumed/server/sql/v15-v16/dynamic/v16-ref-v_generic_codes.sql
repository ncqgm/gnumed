-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
-- triggers ensuring backwards referential integrity from coding tables

-- UPDATE
\unset ON_ERROR_STOP
drop function ref.trf_upd_ref_code_tbl_check_backlink() cascade;
\set ON_ERROR_STOP 1

create or replace function ref.trf_upd_ref_code_tbl_check_backlink()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_msg text;
BEGIN
	if NEW.pk_coding_system = OLD.pk_coding_system then
		return NEW;
	end if;

	perform 1 from clin.lnk_code2item_root where fk_generic_code = NEW.pk_coding_system;

	if not FOUND then
		return NEW;
	end if;

	_msg := ''ref.trf_upd_ref_code_tbl_check_backlink(): UPDATE of ''
		|| TG_TABLE_SCHEMA || ''.'' || TG_TABLE_NAME || '': ''
		|| ''pk_coding_system=('' || NEW.pk_coding_system || '') ''
		|| ''in use in clin.lnk_code2item_root.fk_generic_code, ''
		|| ''old pk_coding_system=('' || OLD.pk_coding_system || '')'';
	raise foreign_key_violation using message = _msg;

	return OLD;
END;';

comment on function ref.trf_upd_ref_code_tbl_check_backlink() is
	'When updating any child of ref.coding_system_root check whether its row is being used in any clin.lnk_code2item_root child.';


-- DELETE
\unset ON_ERROR_STOP
drop function ref.trf_del_ref_code_tbl_check_backlink() cascade;
\set ON_ERROR_STOP 1

create or replace function ref.trf_del_ref_code_tbl_check_backlink()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_msg text;
BEGIN
	perform 1 from clin.lnk_code2item_root where fk_generic_code = NEW.pk_coding_system;

	if not FOUND then
		return OLD;
	end if;

	_msg := ''ref.trf_del_ref_code_tbl_check_backlink(): DELETE from ''
		|| TG_TABLE_SCHEMA || ''.'' || TG_TABLE_NAME || '': ''
		|| ''pk_coding_system=('' || NEW.pk_coding_system || '') ''
		|| ''in use in clin.lnk_code2item_root.fk_generic_code, ''
		|| ''old pk_coding_system=('' || OLD.pk_coding_system || '')'';
	raise foreign_key_violation using message = _msg;

	return OLD;
END;';

comment on function ref.trf_del_ref_code_tbl_check_backlink() is
	'When deleting from any child of ref.coding_system_root check whether its row is being used in any clin.lnk_code2item_root child.';

-- apply this to child tables:
--
--\unset ON_ERROR_STOP
--drop trigger tr_upd_ref_code_tbl_check_backlink on ref.xxxxx;
--drop trigger tr_del_ref_code_tbl_check_backlink on ref.xxxxx;
--\set ON_ERROR_STOP 1
--
-- UPDATE
--create trigger tr_upd_ref_code_tbl_check_backlink
--	before update on ref.xxxxx
--		for each row execute procedure ref.trf_upd_ref_code_tbl_check_backlink();

-- DELETE
--create trigger tr_del_ref_code_tbl_check_backlink
--	before update on ref.xxxxx
--		for each row execute procedure ref.trf_del_ref_code_tbl_check_backlink();

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view ref.v_generic_codes cascade;
\set ON_ERROR_STOP 1


create view ref.v_generic_codes as
select
	r_csr.pk_coding_system
		as pk_generic_code,

	r_csr.code,
	r_csr.term,
	r_ds.name_long,
	r_ds.name_short,
	r_ds.version,
	r_ds.lang,

	r_csr.tableoid::regclass
		as code_table,
	r_csr.fk_data_source
		as pk_data_source
from
	ref.coding_system_root r_csr
		join ref.data_source r_ds on r_ds.pk = r_csr.fk_data_source
;


comment on view ref.v_generic_codes is 'Denormalized generic codes.';


grant select on ref.v_generic_codes to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-ref-v_generic_codes.sql', 'Revision 1');

-- ==============================================================
