-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- $Id: v11-dem-street-dynamic.sql,v 1.1 2009-04-21 16:53:23 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop index dem.idx_street_names cascade;
drop index dem.idx_street_zips cascade;
\set ON_ERROR_STOP 1


create index idx_street_names on dem.street(name);
create index idx_street_zips on dem.street(postcode);

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-dem-street-dynamic.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v11-dem-street-dynamic.sql,v $
-- Revision 1.1  2009-04-21 16:53:23  ncq
-- - add indexe
--
--