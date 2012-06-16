-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- $Id: v12-clin-consumed_substance-static.sql,v 1.1 2009-10-21 08:51:17 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
create table clin.consumed_substance (
	pk serial primary key,
	description text,
	atc_code text
) inherits (audit.audit_fields);

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v12-clin-consumed_substance-static.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v12-clin-consumed_substance-static.sql,v $
-- Revision 1.1  2009-10-21 08:51:17  ncq
-- - new table
--
--