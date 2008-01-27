-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v9-ref-static.sql,v 1.1 2008-01-27 21:07:05 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create table ref.data_source (
	pk serial
		primary key,
	name_long text
		unique
		not null,
	name_short text
		unique
		not null,
	version text
		not null,
	description text,
	source text
		not null
) inherits (audit.audit_fields);

insert into ref.data_source
	select pk_audit, row_version, modified_when, modified_by, pk, name_long, name_short, version, description, source from public.ref_source;
select setval('ref.data_source_pk_seq'::text, (select max(pk) from ref.data_source));

drop table public.ref_source cascade;

alter table audit.log_ref_source rename to log_data_source;

drop table public.lnk_tbl2src cascade;

-- clin.v_vaccination_courses
-- test_norm.fk_ref_src

-- --------------------------------------------------------------
create table ref.atc_group (
	pk serial primary key,
	code text
		not null,
	description text
		not null,
	fk_data_source integer
		not null
		references ref.data_source(pk)
		on update cascade
		on delete restrict,
	unique (code, description)
);

insert into ref.atc_group
	select pk, code, description, (select pk from ref.data_source where name_short = 'ATC/DDD-GM-2004')
	from public.atc_group;
select setval('ref.atc_group_pk_seq'::text, (select max(pk) from ref.atc_group));

drop table public.atc_group;


-- --------------------------------------------------------------
create table ref.atc_substance (
	pk serial primary key,
	code text
		not null,
	description text
		not null,
	ddd_amount numeric,
	fk_ddd_unit integer
		references unit(pk)
		on update cascade
		on delete restrict,
	route text,
	comment text,
	fk_data_source integer
		not null
		references ref.data_source(pk)
		on update cascade
		on delete restrict,
	unique (code, description)
);

insert into ref.atc_substance
	select pk, code, name, ddd_amount, fk_ddd_unit, route, comment, (select pk from ref.data_source where name_short = 'ATC/DDD-GM-2004')
	from public.atc_substance;
select setval('ref.atc_substance_pk_seq'::text, (select max(pk) from ref.atc_substance));

drop table public.atc_substance;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v9-ref-static.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v9-ref-static.sql,v $
-- Revision 1.1  2008-01-27 21:07:05  ncq
-- - new
--
--