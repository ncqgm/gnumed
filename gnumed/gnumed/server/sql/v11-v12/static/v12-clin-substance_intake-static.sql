-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- $Id: v12-clin-substance_intake-static.sql,v 1.1 2009-10-29 17:13:02 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
alter table clin.substance_intake
	add column is_long_term boolean
		default false;

alter table audit.log_substance_intake
	add column is_long_term boolean;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v12-clin-substance_intake-static.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v12-clin-substance_intake-static.sql,v $
-- Revision 1.1  2009-10-29 17:13:02  ncq
-- - .is_long_term
--
--