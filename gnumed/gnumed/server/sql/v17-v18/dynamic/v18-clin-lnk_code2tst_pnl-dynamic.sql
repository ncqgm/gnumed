-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
comment on table clin.lnk_code2tst_pnl is
'Links codes to test panels.';


select gm.register_notifying_table('clin', 'lnk_code2tst_pnl', 'test_panel_code');
select audit.register_table_for_auditing('clin', 'lnk_code2tst_pnl');


grant select on clin.lnk_code2tst_pnl to group "gm-public";
grant insert, update, delete on clin.lnk_code2tst_pnl to group "gm-doctors";
grant usage on clin.lnk_code2tst_pnl_pk_seq to group "gm-doctors";

\unset ON_ERROR_STOP
alter table clin.lnk_code2tst_pnl drop constraint clin_lc2tst_pnl_code_uniq_per_item cascade;
\set ON_ERROR_STOP 1

alter table clin.lnk_code2tst_pnl
	add constraint clin_lc2tst_pnl_code_uniq_per_item
		unique(fk_generic_code, fk_item);

-- --------------------------------------------------------------
-- .fk_item
comment on column clin.lnk_code2tst_pnl.fk_item is
'Foreign key to clin.test_panel';


\unset ON_ERROR_STOP
alter table clin.lnk_code2tst_pnl drop constraint lnk_code2tst_pnl_fk_item_fkey cascade;
\set ON_ERROR_STOP 1


alter table clin.lnk_code2tst_pnl
	add foreign key (fk_item)
		references clin.test_panel(pk)
		on update cascade				-- update if test_panel is updated
		on delete cascade;				-- delete if test_panel is deleted


\unset ON_ERROR_STOP
drop index clin.idx_c_lc2tp_fk_item cascade;
\set ON_ERROR_STOP 1

create index idx_c_lc2tp_fk_item on clin.lnk_code2tst_pnl(fk_item);

-- --------------------------------------------------------------
-- .fk_generic_code
comment on column clin.lnk_code2tst_pnl.fk_generic_code is
'Custom foreign key to ref.coding_system_root.';


alter table clin.lnk_code2tst_pnl
	alter column fk_generic_code
		set not null;


\unset ON_ERROR_STOP
drop trigger tr_ins_lc2tp_fk_generic_code on clin.lnk_code2tst_pnl;
drop trigger tr_upd_lc2tp_fk_generic_code on clin.lnk_code2tst_pnl;
\set ON_ERROR_STOP 1


-- INSERT
create trigger tr_ins_lc2tp_fk_generic_code
	before insert on clin.lnk_code2tst_pnl
		for each row execute procedure clin.trf_ins_lc2sth_fk_generic_code();


-- UPDATE
create trigger tr_upd_lc2tp_fk_generic_code
	before update on clin.lnk_code2tst_pnl
		for each row execute procedure clin.trf_upd_lc2sth_fk_generic_code();

-- --------------------------------------------------------------
select gm.log_script_insertion('v18-clin-lnk_code2tst_pnl-dynamic.sql', '18.0');
