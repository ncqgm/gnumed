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
-- $Id: ref-form_tables.sql,v 1.3 2007-08-12 00:19:23 ncq Exp $
-- $Revision: 1.3 $

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
create table ref.form_defs (
	pk serial primary key,
	fk_type integer
		not null
		references ref.form_types(pk)
		on update cascade
		on delete restrict,
	document_type text
		default null,
	name_short text
		not null,
	name_long text
		not null,
	revision text
		not null,
	template bytea,
	engine text
		default 'T'
		not null
		check (engine in ('T', 'L', 'H', 'O')),
	in_use boolean not null
		default true,
	unique (name_long, name_short),
	unique (name_long, revision)
) inherits (audit.audit_fields);

insert into ref.form_defs (fk_type, name_short, name_long, revision, engine, in_use)
	select fk_type, name_short, name_long, revision, engine, in_use from public.form_defs
;

drop table public.form_defs cascade;
drop table audit.log_form_defs cascade;
drop table public.form_types cascade;

delete from audit.audited_tables where schema = 'public' and table_name = 'form_defs';

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: ref-form_tables.sql,v $', '$Revision: 1.3 $');

-- ==============================================================
-- $Log: ref-form_tables.sql,v $
-- Revision 1.3  2007-08-12 00:19:23  ncq
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