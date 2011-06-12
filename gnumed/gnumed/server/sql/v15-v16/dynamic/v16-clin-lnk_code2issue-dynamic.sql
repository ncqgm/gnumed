-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
comment on table clin.lnk_code2h_issue is
'Links codes to health issues.';


select gm.register_notifying_table('clin', 'lnk_code2h_issue', 'health_issue_code');
select audit.register_table_for_auditing('clin', 'lnk_code2h_issue');


grant select on clin.lnk_code2h_issue to group "gm-public";
grant insert, update, delete on clin.lnk_code2h_issue to group "gm-doctors";
grant usage on clin.lnk_code2h_issue_pk_seq to group "gm-doctors";

\unset ON_ERROR_STOP
alter table clin.lnk_code2h_issue drop constraint clin_lc2h_issue_code_uniq_per_item cascade;
\set ON_ERROR_STOP 1

alter table clin.lnk_code2h_issue
	add constraint clin_lc2h_issue_code_uniq_per_item
		unique(fk_generic_code, fk_item);

-- --------------------------------------------------------------
-- .fk_item
comment on column clin.lnk_code2h_issue.fk_item is
'Foreign key to clin.health_issue';


\unset ON_ERROR_STOP
alter table clin.lnk_code2h_issue drop constraint lnk_code2h_issue_fk_item_fkey cascade;
\set ON_ERROR_STOP 1


alter table clin.lnk_code2h_issue
	add foreign key (fk_item)
		references clin.health_issue(pk)
		on update cascade				-- update if health_issue is updated
		on delete cascade;				-- delete if health_issue is deleted


\unset ON_ERROR_STOP
drop index idx_c_lc2iss_fk_item cascade;
\set ON_ERROR_STOP 1

create index idx_c_lc2iss_fk_item on clin.lnk_code2h_issue(fk_item);

-- --------------------------------------------------------------
-- .fk_generic_code
comment on column clin.lnk_code2h_issue.fk_generic_code is
'Custom foreign key to ref.coding_system_root.';


alter table clin.lnk_code2h_issue
	alter column fk_generic_code
		set not null;


-- INSERT
create trigger tr_ins_lc2sth_fk_generic_code
	before insert on clin.lnk_code2h_issue
		for each row execute procedure clin.trf_ins_lc2sth_fk_generic_code();


-- UPDATE
create trigger tr_upd_lc2sth_fk_generic_code
	before update on clin.lnk_code2h_issue
		for each row execute procedure clin.trf_upd_lc2sth_fk_generic_code();

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-clin-lnk_code2h_issue-dynamic.sql', '1.0');
