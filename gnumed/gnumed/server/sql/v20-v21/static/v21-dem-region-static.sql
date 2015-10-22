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
alter table dem.state rename to region;
alter table dem.region rename column id to pk;


alter table audit.log_state rename to log_region;
alter table audit.log_region rename column id to pk;

-- --------------------------------------------------------------
alter table dem.urb rename column id_state to fk_region;

alter table audit.log_urb rename column id_state to fk_region;

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-dem-region-static.sql', '21.0');
