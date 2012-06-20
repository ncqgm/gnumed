-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- .emergency_contact
alter table dem.identity
	add column emergency_contact text;

alter table audit.log_identity
	add column emergency_contact text;


-- .fk_emergency_contact
alter table dem.identity
	add column fk_emergency_contact integer;

alter table audit.log_identity
	add column fk_emergency_contact integer;


-- .comment
alter table dem.identity
	add column comment text;

alter table audit.log_identity
	add column comment text;

-- --------------------------------------------------------------
select gm.log_script_insertion('v14-dem-identity-static.sql', 'Revision: 1.1');

