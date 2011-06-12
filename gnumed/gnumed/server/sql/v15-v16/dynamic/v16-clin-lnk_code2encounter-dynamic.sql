-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- RFE
-- --------------------------------------------------------------
comment on table clin.lnk_code2rfe is
'Links codes to encounters.';


select gm.register_notifying_table('clin', 'lnk_code2rfe', 'rfe_code');
select audit.register_table_for_auditing('clin', 'lnk_code2rfe');


grant select on clin.lnk_code2rfe to group "gm-public";
grant insert, update, delete on clin.lnk_code2rfe to group "gm-doctors";
grant usage on clin.lnk_code2rfe_pk_seq to group "gm-doctors";

\unset ON_ERROR_STOP
alter table clin.lnk_code2rfe drop constraint clin_lc2rfe_code_uniq_per_item cascade;
\set ON_ERROR_STOP 1

alter table clin.lnk_code2rfe
	add constraint clin_lc2rfe_code_uniq_per_item
		unique(fk_generic_code, fk_item);

-- --------------------------------------------------------------
-- .fk_item
comment on column clin.lnk_code2rfe.fk_item is
'Foreign key to clin.encounter';


\unset ON_ERROR_STOP
alter table clin.lnk_code2rfe drop constraint lnk_code2rfe_fk_item_fkey cascade;
\set ON_ERROR_STOP 1


alter table clin.lnk_code2rfe
	add foreign key (fk_item)
		references clin.encounter(pk)
		on update cascade				-- update if encounter is updated
		on delete cascade;				-- delete if encounter is deleted


\unset ON_ERROR_STOP
drop index idx_c_lc2rfe_fk_item cascade;
\set ON_ERROR_STOP 1

create index idx_c_lc2rfe_fk_item on clin.lnk_code2rfe(fk_item);

-- --------------------------------------------------------------
-- .fk_generic_code
comment on column clin.lnk_code2rfe.fk_generic_code is
'Custom foreign key to ref.coding_system_root.';


alter table clin.lnk_code2rfe
	alter column fk_generic_code
		set not null;


-- INSERT
create trigger tr_ins_lc2sth_fk_generic_code
	before insert on clin.lnk_code2rfe
		for each row execute procedure clin.trf_ins_lc2sth_fk_generic_code();


-- UPDATE
create trigger tr_upd_lc2sth_fk_generic_code
	before update on clin.lnk_code2rfe
		for each row execute procedure clin.trf_upd_lc2sth_fk_generic_code();

-- --------------------------------------------------------------
-- AOE
-- --------------------------------------------------------------
comment on table clin.lnk_code2aoe is
'Links codes to encounter.aoe.';


select gm.register_notifying_table('clin', 'lnk_code2aoe', 'aoe_code');
select audit.register_table_for_auditing('clin', 'lnk_code2aoe');


grant select on clin.lnk_code2aoe to group "gm-public";
grant insert, update, delete on clin.lnk_code2aoe to group "gm-doctors";
grant usage on clin.lnk_code2aoe_pk_seq to group "gm-doctors";

\unset ON_ERROR_STOP
alter table clin.lnk_code2aoe drop constraint clin_lc2aoe_code_uniq_per_item cascade;
\set ON_ERROR_STOP 1

alter table clin.lnk_code2aoe
	add constraint clin_lc2aoe_code_uniq_per_item
		unique(fk_generic_code, fk_item);

-- --------------------------------------------------------------
-- .fk_item
comment on column clin.lnk_code2aoe.fk_item is
'Foreign key to clin.encounter';


\unset ON_ERROR_STOP
alter table clin.lnk_code2aoe drop constraint lnk_code2aoe_fk_item_fkey cascade;
\set ON_ERROR_STOP 1


alter table clin.lnk_code2aoe
	add foreign key (fk_item)
		references clin.encounter(pk)
		on update cascade				-- update if encounter is updated
		on delete cascade;				-- delete if encounter is deleted


\unset ON_ERROR_STOP
drop index idx_c_lc2aoe_fk_item cascade;
\set ON_ERROR_STOP 1

create index idx_c_lc2aoe_fk_item on clin.lnk_code2aoe(fk_item);

-- --------------------------------------------------------------
-- .fk_generic_code
comment on column clin.lnk_code2aoe.fk_generic_code is
'Custom foreign key to ref.coding_system_root.';


alter table clin.lnk_code2aoe
	alter column fk_generic_code
		set not null;


-- INSERT
create trigger tr_ins_lc2sth_fk_generic_code
	before insert on clin.lnk_code2aoe
		for each row execute procedure clin.trf_ins_lc2sth_fk_generic_code();


-- UPDATE
create trigger tr_upd_lc2sth_fk_generic_code
	before update on clin.lnk_code2aoe
		for each row execute procedure clin.trf_upd_lc2sth_fk_generic_code();

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-clin-lnk_code2encounter-dynamic.sql', '1.0');
