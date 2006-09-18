-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- What it does:
-- - table ref.document_type
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: ref-document_type.sql,v 1.1 2006-09-18 17:30:43 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
begin;

-- --------------------------------------------------------------
create table ref.document_type (
	pk serial primary key,
	scope text
		default null,
	description text
		not null
);

comment on table ref.document_type is
	'pre-installed document types, do not
	 change these as they will be overwritten
	 during database upgrades at the discretion
	 of the GNUmed team';
comment on column ref.document_type.scope is
	'can be used to group document types according
	 to applicability, say, per country';

-- transfer types making sure they are ready for translation
insert into ref.document_type(description)
	select i18n.i18n(name) from blobs.doc_type where not is_user;
-- add some data
insert into ref.document_type(scope, description) values ('AU', i18n.i18n('referral report PIT (AU)'));

-- --------------------------------------------------------------
grant select, insert, update, delete
	on table ref.document_type
	to group "gm-doctors";

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: ref-document_type.sql,v $', '$Revision: 1.1 $');

-- --------------------------------------------------------------
commit;

-- ==============================================================
-- $Log: ref-document_type.sql,v $
-- Revision 1.1  2006-09-18 17:30:43  ncq
-- - create schema ref and add document_type table
--
-- Revision 1.2  2006/09/16 21:47:37  ncq
-- - improvements
--
-- Revision 1.1  2006/09/16 14:02:36  ncq
-- - use this as a template for change scripts
--
--
