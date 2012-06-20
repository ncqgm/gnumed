-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
comment on table clin.lnk_code2fhx is
'Links codes to family history items.';


select gm.register_notifying_table('clin', 'lnk_code2fhx', 'fhx_code');
select audit.register_table_for_auditing('clin', 'lnk_code2fhx');


grant select on clin.lnk_code2fhx to group "gm-public";
grant insert, update, delete on clin.lnk_code2fhx to group "gm-doctors";
grant usage on clin.lnk_code2fhx_pk_seq to group "gm-doctors";

\unset ON_ERROR_STOP
alter table clin.lnk_code2fhx drop constraint clin_lc2fhx_code_uniq_per_item cascade;
\set ON_ERROR_STOP 1

alter table clin.lnk_code2fhx
	add constraint clin_lc2fhx_code_uniq_per_item
		unique(fk_generic_code, fk_item);

-- --------------------------------------------------------------
-- .fk_item
comment on column clin.lnk_code2fhx.fk_item is
'Foreign key to clin.family_history';


\unset ON_ERROR_STOP
alter table clin.lnk_code2fhx drop constraint lnk_code2fhx_fk_item_fkey cascade;
\set ON_ERROR_STOP 1


alter table clin.lnk_code2fhx
	add foreign key (fk_item)
		references clin.family_history(pk)
		on update cascade				-- update if fhx is updated
		on delete cascade;				-- delete if fhx is deleted


\unset ON_ERROR_STOP
drop index idx_c_lc2fhx_fk_item cascade;
\set ON_ERROR_STOP 1

create index idx_c_lc2fhx_fk_item on clin.lnk_code2fhx(fk_item);

-- --------------------------------------------------------------
-- .fk_generic_code
comment on column clin.lnk_code2fhx.fk_generic_code is
'Custom foreign key to ref.coding_system_root.';


alter table clin.lnk_code2fhx
	alter column fk_generic_code
		set not null;


-- INSERT
create trigger tr_ins_lc2sth_fk_generic_code
	before insert on clin.lnk_code2fhx
		for each row execute procedure clin.trf_ins_lc2sth_fk_generic_code();


-- UPDATE
create trigger tr_upd_lc2sth_fk_generic_code
	before update on clin.lnk_code2fhx
		for each row execute procedure clin.trf_upd_lc2sth_fk_generic_code();

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-clin-lnk_code2fhx-dynamic.sql', '16.0');
