-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- $Id: v11-drop_obsolete_groups-dynamic.sql,v 1.2 2009-08-08 10:43:23 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
-- remove obsolete database groups
\unset ON_ERROR_STOP
drop role "gm-staff_medical";
drop role "gm-staff_office";
drop role "gm-trainees_medical";
drop role "gm-trainees_office";
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-drop_obsolete_groups-dynamic.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: v11-drop_obsolete_groups-dynamic.sql,v $
-- Revision 1.2  2009-08-08 10:43:23  ncq
-- - cleanup
--
-- Revision 1.1  2009/08/06 13:55:19  ncq
-- - new
--
--