-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- $Id: v11-dem-urb-dynamic.sql,v 1.1 2009-04-21 16:53:23 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
drop index if exists dem.idx_urb_names cascade;
drop index if exists dem.idx_urb_zips cascade;
drop index if exists dem.idx_state_names cascade;


create index idx_urb_names on dem.urb(name);
create index idx_urb_zips on dem.urb(postcode);

create index idx_state_names on dem.state(name);
-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-dem-urb-dynamic.sql,v $', '$Revision: 1.1 $');
