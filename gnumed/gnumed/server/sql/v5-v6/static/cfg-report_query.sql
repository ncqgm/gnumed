-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v5
-- Target database version: v6
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: cfg-report_query.sql,v 1.3 2007-04-21 19:44:22 ncq Exp $
-- $Revision: 1.3 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create table cfg.report_query (
	pk serial primary key,
	label text
		unique
		not null,
	cmd text
		not null
) inherits (audit.audit_fields);

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: cfg-report_query.sql,v $', '$Revision: 1.3 $');

-- ==============================================================
-- $Log: cfg-report_query.sql,v $
-- Revision 1.3  2007-04-21 19:44:22  ncq
-- - label must be unique, cmd doesn't have to be
--
-- Revision 1.2  2007/04/07 22:29:12  ncq
-- - only this is static
--
-- Revision 1.1  2007/04/06 23:10:54  ncq
-- - store data mining queries
--
--