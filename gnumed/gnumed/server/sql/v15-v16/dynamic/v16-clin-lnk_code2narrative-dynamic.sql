-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
comment on table clin.lnk_code2narrative is
'Links codes to SOAP narrative.';


select gm.register_notifying_table('clin', 'lnk_code2narrative', 'narrative_code');
select audit.register_table_for_auditing('clin', 'lnk_code2narrative');


grant select on clin.lnk_code2narrative to group "gm-public";
grant insert, update, delete on clin.lnk_code2narrative to group "gm-doctors";
grant usage on clin.lnk_code2narrative_pk_seq to group "gm-doctors";

\unset ON_ERROR_STOP
alter table clin.lnk_code2narrative drop constraint clin_lc2narr_code_uniq_per_item cascade;
\set ON_ERROR_STOP 1

alter table clin.lnk_code2narrative
	add constraint clin_lc2narr_code_uniq_per_item
		unique(fk_generic_code, fk_item);

-- --------------------------------------------------------------
-- .fk_item
comment on column clin.lnk_code2narrative.fk_item is
'Foreign key to clin.clin_narrative';


\unset ON_ERROR_STOP
alter table clin.lnk_code2narrative drop constraint lnk_code2narrative_fk_item_fkey cascade;
\set ON_ERROR_STOP 1


alter table clin.lnk_code2narrative
	add foreign key (fk_item)
		references clin.clin_narrative(pk)
		on update cascade				-- update if narrative is updated
		on delete cascade;				-- delete if narrative is deleted


\unset ON_ERROR_STOP
drop index idx_c_lc2narr_fk_item cascade;
\set ON_ERROR_STOP 1

create index idx_c_lc2narr_fk_item on clin.lnk_code2narrative(fk_item);

-- --------------------------------------------------------------
-- .fk_generic_code
comment on column clin.lnk_code2narrative.fk_generic_code is
'Custom foreign key to ref.coding_system_root.';


alter table clin.lnk_code2narrative
	alter column fk_generic_code
		set not null;


-- INSERT
create trigger tr_ins_lc2sth_fk_generic_code
	before insert on clin.lnk_code2narrative
		for each row execute procedure clin.trf_ins_lc2sth_fk_generic_code();


-- UPDATE
create trigger tr_upd_lc2sth_fk_generic_code
	before update on clin.lnk_code2narrative
		for each row execute procedure clin.trf_upd_lc2sth_fk_generic_code();

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-clin-lnk_code2narrative-dynamic.sql', '1.0');
