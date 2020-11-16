-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
set default_transaction_read_only to off;

set check_function_bodies to on;

-- --------------------------------------------------------------
drop function if exists clin.get_next_export_item_list_position(IN _fk_identity integer) cascade;

create function clin.get_next_export_item_list_position(IN _fk_identity integer)
	returns integer
	language SQL
	as 'SELECT COALESCE(MAX(c_ei.list_position) + 1, 1) FROM clin.export_item c_ei WHERE c_ei.fk_identity = _fk_identity;'
;

comment on function clin.get_next_export_item_list_position(IN _fk_identity integer) is
	'Get the next list position for the given identity.';

-- --------------------------------------------------------------
-- add trigger as default
drop function if exists clin.trf_exp_item_set_list_pos_default() cascade;

create function clin.trf_exp_item_set_list_pos_default()
	returns trigger
	language plpgsql
	as '
BEGIN
	IF NEW.list_position IS NOT NULL THEN
		RETURN NEW;
	END IF;
	SELECT clin.get_next_export_item_list_position(NEW.fk_identity) INTO NEW.list_position;
	RETURN NEW;
END';

comment on function clin.trf_exp_item_set_list_pos_default() is
	'Set clin.export_item.list_postion to the "next" (max+1) value per-patient.';

create trigger tr_ins_upd_clin_exp_item_set_list_pos_default
	before insert or update on
		clin.export_item
	for
		each row
	execute procedure
		clin.trf_exp_item_set_list_pos_default();

-- --------------------------------------------------------------
-- update list_position to default (that is, populate it)
update clin.export_item c_ei set list_position = DEFAULT;

-- --------------------------------------------------------------
alter table clin.export_item
	alter column list_position set not null;

comment on column clin.export_item.list_position is
	'This is the per-identity list position for this export item.';

alter table clin.export_item
	add constraint uniq_list_pos_per_identity
		unique(fk_identity, list_position);

alter table clin.export_item
	add constraint assert_pos_list_pos
		check (list_position > 0);

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-export_item-dynamic.sql', '23.0');
