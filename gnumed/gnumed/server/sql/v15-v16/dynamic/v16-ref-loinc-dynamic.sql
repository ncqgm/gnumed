-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- remove those which have been orphaned by the old
-- LOINC updater w/ respect to .fk_data_source
delete from ref.loinc r_l where not exists (
	select 1 from ref.data_source r_ds
	where
		r_ds.pk = r_l.fk_data_source
			and
		r_ds.name_short like '%LOINC%'
);

-- make sure we've got a LOINC data source
insert into ref.data_source (
	name_long,
	name_short,
	version,
	source
) select
	'LOINC® (Logical Observation Identifiers Names and Codes)',
	'LOINC',
	'2.26',
	'http://loinc.org'
 where not exists (
	select 1 from ref.data_source where
		name_long = 'LOINC® (Logical Observation Identifiers Names and Codes)'
			and
		name_short = 'LOINC'
			and
		version = '2.26'
);

-- remove dupes
delete from ref.loinc
where ref.loinc.pk not in (
	select max(rl2.pk)
	from ref.loinc rl2
	group by
--		rl2.fk_data_source,
		rl2.code,
		rl2.term
);

-- ensure fk_data_source points to a LOINC entry
update ref.loinc set
	fk_data_source = (
		select ref.data_source.pk
		from ref.data_source
		where
			name_long = 'LOINC® (Logical Observation Identifiers Names and Codes)'
				and
			name_short = 'LOINC'
				and
			version = '2.26'
		limit 1
	)
where
	fk_data_source not in (
		select pk
		from ref.data_source
		where
			name_short like '%LOINC%'
	)
;

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop trigger tr_upd_ref_code_tbl_check_backlink on ref.loinc;
drop trigger tr_del_ref_code_tbl_check_backlink on ref.loinc;
\set ON_ERROR_STOP 1


-- UPDATE
create trigger tr_upd_ref_code_tbl_check_backlink
	before update on ref.loinc
		for each row execute procedure ref.trf_upd_ref_code_tbl_check_backlink();

-- DELETE
create trigger tr_del_ref_code_tbl_check_backlink
	before update on ref.loinc
		for each row execute procedure ref.trf_del_ref_code_tbl_check_backlink();

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop index idx_ref_loinc_fk_data_src cascade;
drop index idx_ref_loinc_code_unique_per_system cascade;
drop index idx_ref_loinc_term_unique_per_system cascade;
\set ON_ERROR_STOP 1

create index idx_ref_loinc_fk_data_src on ref.loinc(fk_data_source);
create unique index idx_ref_loinc_code_unique_per_system on ref.loinc(fk_data_source, lower(code));
create unique index idx_ref_loinc_term_unique_per_system on ref.loinc(fk_data_source, lower(code), lower(term));

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
alter table ref.loinc drop constraint loinc_fk_data_source_fkey cascade;
\set ON_ERROR_STOP 1

alter table ref.loinc
	add foreign key (fk_data_source)
		references ref.data_source(pk)
		on update cascade
		on delete restrict;

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-ref-loinc-dynamic.sql', '16.0');
