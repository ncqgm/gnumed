-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- What it does:
-- - create schema "ref"
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: ref-schema.sql,v 1.1 2006-09-18 17:30:43 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
begin;

-- --------------------------------------------------------------
create schema ref authorization "gm-dbo";

comment on schema ref is
	'This schema holds data that is "reference material" which comes
	 pre-installed with a GNUmed database. Examples are:
	 - document types
	 - ICD codes
	 - form templates';

grant usage on schema ref to group "gm-doctors";

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: ref-schema.sql,v $', '$Revision: 1.1 $');

-- --------------------------------------------------------------
commit;

-- ==============================================================
-- $Log: ref-schema.sql,v $
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
