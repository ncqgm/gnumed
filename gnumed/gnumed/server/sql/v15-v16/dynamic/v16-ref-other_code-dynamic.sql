-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
comment on table ref.other_code is
	'Holds codes from "other" coding systems for which no specific tables exist just yet.';


\unset ON_ERROR_STOP
drop trigger tr_upd_ref_code_tbl_check_backlink on ref.other_code;
drop trigger tr_del_ref_code_tbl_check_backlink on ref.other_code;
\set ON_ERROR_STOP 1


-- UPDATE
create trigger tr_upd_ref_code_tbl_check_backlink
	before update on ref.other_code
		for each row execute procedure ref.trf_upd_ref_code_tbl_check_backlink();

-- DELETE
create trigger tr_del_ref_code_tbl_check_backlink
	before update on ref.other_code
		for each row execute procedure ref.trf_del_ref_code_tbl_check_backlink();

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop index idx_ref_other_code_fk_data_src cascade;
drop index idx_ref_other_code_code_unique_per_system cascade;
drop index idx_ref_other_code_term_unique_per_system cascade;
\set ON_ERROR_STOP 1

create index idx_ref_other_code_fk_data_src on ref.other_code(fk_data_source);
create unique index idx_ref_other_code_code_unique_per_system on ref.other_code(fk_data_source, lower(code));
create unique index idx_ref_other_code_term_unique_per_system on ref.other_code(fk_data_source, lower(code), lower(term));

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
alter table ref.other_code drop constraint other_code_fk_data_source_fkey cascade;
\set ON_ERROR_STOP 1

alter table ref.other_code
	add foreign key (fk_data_source)
		references ref.data_source(pk)
		on update cascade
		on delete restrict;

-- --------------------------------------------------------------
grant select on ref.other_code to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-ref-other_code-dynamic.sql', '16.0');
