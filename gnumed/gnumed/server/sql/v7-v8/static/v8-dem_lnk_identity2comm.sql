-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v8-dem_lnk_identity2comm.sql,v 1.1 2007-12-02 13:44:33 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table dem.enum_comm_types
	rename column id to pk;

-- --------------------------------------------------------------
alter table dem.lnk_identity2comm
	rename column id to pk;

alter table dem.lnk_identity2comm
	rename column id_identity to fk_identity;

alter table dem.lnk_identity2comm
	rename column id_address to fk_address;

alter table dem.lnk_identity2comm
	rename column id_type to fk_type;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v8-dem_lnk_identity2comm.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v8-dem_lnk_identity2comm.sql,v $
-- Revision 1.1  2007-12-02 13:44:33  ncq
-- - cleanup
--
--