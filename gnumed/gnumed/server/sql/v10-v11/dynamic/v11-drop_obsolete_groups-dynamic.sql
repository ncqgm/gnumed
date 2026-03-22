-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
-- remove obsolete database groups
drop role if exists "gm-staff_medical";
drop role if exists "gm-staff_office";
drop role if exists "gm-trainees_medical";
drop role if exists "gm-trainees_office";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-drop_obsolete_groups-dynamic.sql,v $', '$Revision: 1.2 $');
