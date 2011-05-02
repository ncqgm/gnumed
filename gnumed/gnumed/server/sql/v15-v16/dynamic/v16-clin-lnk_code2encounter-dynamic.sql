-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
comment on table clin.lnk_code2encounter is
'Links codes to encounters.';


grant select on clin.lnk_code2encounter to group "gm-public";
grant insert, update, delete on clin.lnk_code2encounter to group "gm-doctors";
grant usage on clin.lnk_code2encounter_pk_seq to group "gm-doctors";

-- --------------------------------------------------------------
-- .fk_item
comment on column clin.lnk_code2encounter.fk_item is
'Foreign key to clin.encounter';


\unset ON_ERROR_STOP
alter table clin.lnk_code2encounter drop foreign key lnk_code2encounter_fk_item_fkey cascade;
\set ON_ERROR_STOP 1


alter table clin.lnk_code2encounter
	add foreign key (fk_item)
		references clin.encounter(pk)
		on update cascade				-- update if encounter is updated
		on delete cascade;				-- delete if encounter is deleted


\unset ON_ERROR_STOP
drop index idx_c_lc2enc_fk_item cascade;
\set ON_ERROR_STOP 1

create index idx_c_lc2enc_fk_item on clin.lnk_code2encounter(fk_item);

-- --------------------------------------------------------------
-- .fk_generic_code
comment on column clin.lnk_code2encounter.fk_generic_code is
'Custom foreign key to ref.coding_system_root.';


alter table clin.lnk_code2encounter
	alter column fk_generic_code
		set not null;


-- INSERT
create trigger tr_ins_lc2sth_fk_generic_code
	before insert on clin.lnk_code2encounter
		for each row execute procedure clin.trf_ins_lc2sth_fk_generic_code();


-- UPDATE
create trigger tr_upd_lc2sth_fk_generic_code
	before update on clin.lnk_code2encounter
		for each row execute procedure clin.trf_upd_lc2sth_fk_generic_code();

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-clin-lnk_code2encounter-dynamic.sql', '1.0');
