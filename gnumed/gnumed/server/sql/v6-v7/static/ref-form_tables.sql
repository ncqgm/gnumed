-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v6
-- Target database version: v7
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create table ref.form_types (
	name text
		unique
		not null,
	pk serial primary key
);

insert into ref.form_types select * from public.form_types;

select setval(pg_get_serial_sequence('ref.form_types', 'pk'), (select max(pk) from ref.form_types) + 1);

-- --------------------------------------------------------------
create table ref.paperwork_templates (
	pk serial primary key,
	fk_template_type integer
		not null
		references ref.form_types(pk)
		on update cascade
		on delete restrict,
	instance_type text
		default null,
	name_short text
		not null,
	name_long text
		not null,
	external_version text
		not null,
	gnumed_revision float
		default null,
	engine text
		not null
		default 'O'
		check (engine in ('T', 'L', 'H', 'O')),
	in_use boolean
		not null
		default true,
	filename text
		default null,
	data bytea
		default null,
	-- a certain GNUmed internal revision of any given external version of a template can only exist once
	unique (gnumed_revision, external_version, name_long),
	-- a certain form can only ever have one short alias, regardless of revision
	unique (name_long, name_short)
) inherits (audit.audit_fields);

insert into ref.paperwork_templates (fk_template_type, name_short, name_long, external_version, engine, in_use, data)
select
	fk_type,
	name_short,
	name_long,
	revision,
	engine,
	in_use,
	decode(replace(template, E'\\', E'\\\\'), 'escape')
from public.form_defs;

drop table public.form_defs cascade;
drop table audit.log_form_defs cascade;
drop table public.form_types cascade;

delete from audit.audited_tables where schema = 'public' and table_name = 'form_defs';

-- --------------------------------------------------------------
-- '
alter table public.form_fields add foreign key (fk_form) references ref.paperwork_templates(pk);

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: ref-form_tables.sql,v $', '$Revision: 1.8 $');

-- ==============================================================
