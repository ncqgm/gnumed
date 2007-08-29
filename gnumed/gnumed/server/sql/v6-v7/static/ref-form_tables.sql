-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v6
-- Target database version: v7
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- $Id: ref-form_tables.sql,v 1.6 2007-08-29 14:47:17 ncq Exp $
-- $Revision: 1.6 $

-- --------------------------------------------------------------
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
		default 'T'
		not null
		check (engine in ('T', 'L', 'H', 'O')),
	in_use boolean
		not null
		default true,
	filename text
		default null,
	data bytea
		not null,
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
	decode(replace(template, '\\', '\\\\'), 'escape')
from public.form_defs;

drop table public.form_defs cascade;
drop table audit.log_form_defs cascade;
drop table public.form_types cascade;

delete from audit.audited_tables where schema = 'public' and table_name = 'form_defs';

-- --------------------------------------------------------------
-- '
alter table public.form_fields add foreign key (fk_form) references ref.paperwork_templates(pk);

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: ref-form_tables.sql,v $', '$Revision: 1.6 $');

-- ==============================================================
-- $Log: ref-form_tables.sql,v $
-- Revision 1.6  2007-08-29 14:47:17  ncq
-- - revision -> external_version
-- - add gnumed_revision
-- - fix UNIQUE constraints
-- - add foreign key to public.form_fields
--
-- Revision 1.5  2007/08/20 14:38:42  ncq
-- - public.form_defs -> ref.paperwork_templates, move full data
-- - rename cols
--
-- Revision 1.4  2007/08/13 22:07:50  ncq
-- - add ref.form_defs.filename
--
-- Revision 1.3  2007/08/12 00:19:23  ncq
-- - add document_type field
--
-- Revision 1.2  2007/07/22 09:29:53  ncq
-- - need to adjust ref.form_types sequences
-- - drop audit table of ref.form_defs, too
--
-- Revision 1.1  2007/07/18 14:28:23  ncq
-- - we are now really getting into forms handling
--
--