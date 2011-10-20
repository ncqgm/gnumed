-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop trigger tr_upd_ref_code_tbl_check_backlink on ref.atc;
drop trigger tr_del_ref_code_tbl_check_backlink on ref.atc;
\set ON_ERROR_STOP 1


-- UPDATE
create trigger tr_upd_ref_code_tbl_check_backlink
	before update on ref.atc
		for each row execute procedure ref.trf_upd_ref_code_tbl_check_backlink();

-- DELETE
create trigger tr_del_ref_code_tbl_check_backlink
	before update on ref.atc
		for each row execute procedure ref.trf_del_ref_code_tbl_check_backlink();

-- --------------------------------------------------------------
-- remove those which have been orphaned by the old
-- ATC updater w/ respect to .fk_data_source
delete from ref.atc r_a where not exists (
	select 1 from ref.data_source r_ds
	where
		r_ds.pk = r_a.fk_data_source
			and
		r_ds.name_short like '%ATC%'
);

-- make sure we've got an ATC data source
insert into ref.data_source (
	name_long,
	name_short,
	version,
	source
) select
	'Anatomical Therapeutic Chemical Classification 1/2009 Deutschland',
	'ATC',
	'2009-01-DE',
	'http://www.dimdi.de'
 where not exists (
	select 1 from ref.data_source where
		name_long = 'Anatomical Therapeutic Chemical Classification 1/2009 Deutschland'
			and
		name_short = 'ATC'
			and
		version = '2009-01-DE'
);

-- remove dupes
delete from ref.atc
where pk not in (
	select max(ra2.pk)
	from ref.atc ra2
	group by
--		ra2.fk_data_source,
		ra2.code,
		lower(ra2.term)
);

-- ensure fk_data_source points to an ATC entry
update ref.atc set
	fk_data_source = (
		select ref.data_source.pk
		from ref.data_source
		where
			name_long = 'Anatomical Therapeutic Chemical Classification 1/2009 Deutschland'
				and
			name_short = 'ATC'
				and
			version = '2009-01-DE'
		limit 1
	)
where
	fk_data_source not in (
		select pk
		from ref.data_source
		where
			name_short like '%ATC%'
	)
;

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop index idx_ref_atc_fk_data_src cascade;
drop index idx_ref_atc_code_unique_per_system cascade;
drop index idx_ref_atc_term_unique_per_system cascade;
\set ON_ERROR_STOP 1

create index idx_ref_atc_fk_data_src on ref.atc(fk_data_source);
create unique index idx_ref_atc_code_unique_per_system on ref.atc(fk_data_source, lower(code));
create unique index idx_ref_atc_term_unique_per_system on ref.atc(fk_data_source, lower(code), lower(term));

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
alter table ref.atc drop constraint atc_fk_data_source_fkey cascade;
\set ON_ERROR_STOP 1

alter table ref.atc
	add foreign key (fk_data_source)
		references ref.data_source(pk)
		on update cascade
		on delete restrict;

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-ref-atc-dynamic.sql', '16.0');
