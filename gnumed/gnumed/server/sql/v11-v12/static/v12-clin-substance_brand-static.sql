-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- $Id: v12-clin-substance_brand-static.sql,v 1.1 2009-10-21 08:52:09 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
alter table clin.substance_brand
	add column external_code text;

alter table audit.log_substance_brand
	add column external_code text;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v12-clin-substance_brand-static.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v12-clin-substance_brand-static.sql,v $
-- Revision 1.1  2009-10-21 08:52:09  ncq
-- - add external_code
--
--