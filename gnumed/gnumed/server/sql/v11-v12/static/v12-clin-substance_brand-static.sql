-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- $Id: v12-clin-substance_brand-static.sql,v 1.2 2009-11-06 15:37:03 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
alter table clin.substance_brand
	add column external_code text;

alter table audit.log_substance_brand
	add column external_code text;

-- --------------------------------------------------------------
drop table clin.clin_medication cascade;
drop table audit.log_clin_medication cascade;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v12-clin-substance_brand-static.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: v12-clin-substance_brand-static.sql,v $
-- Revision 1.2  2009-11-06 15:37:03  ncq
-- - drop old clin.medication
--
-- Revision 1.1  2009/10/21 08:52:09  ncq
-- - add external_code
--
--