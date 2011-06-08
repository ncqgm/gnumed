-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- $Id: v11-clin-hospital_stay-static.sql,v 1.1 2009-04-01 15:56:31 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create table clin.hospital_stay (
	pk serial primary key,
	discharge timestamp with time zone
) inherits (clin.clin_root_item);

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-clin-hospital_stay-static.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v11-clin-hospital_stay-static.sql,v $
-- Revision 1.1  2009-04-01 15:56:31  ncq
-- - new
--
--