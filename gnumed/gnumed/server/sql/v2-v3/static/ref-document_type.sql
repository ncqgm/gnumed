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
-- $Id: ref-document_type.sql,v 1.2 2007-09-24 23:31:17 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create table ref.document_type (
	pk serial primary key,
	scope text
		default null,
	description text
		not null
);

-- transfer types making sure they are ready for translation
insert into ref.document_type(description)
	select i18n.i18n(name) from blobs.doc_type where not is_user;
-- add some data
insert into ref.document_type(scope, description) values ('AU', i18n.i18n('referral report PIT (AU)'));

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: ref-document_type.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: ref-document_type.sql,v $
-- Revision 1.2  2007-09-24 23:31:17  ncq
-- - remove begin; commit; as it breaks the bootstrapper
--
-- Revision 1.1  2006/09/26 14:47:53  ncq
-- - those live here now
--
-- Revision 1.1  2006/09/18 17:30:43  ncq
-- - create schema ref and add document_type table
--
-- Revision 1.2  2006/09/16 21:47:37  ncq
-- - improvements
--
-- Revision 1.1  2006/09/16 14:02:36  ncq
-- - use this as a template for change scripts
--
--
