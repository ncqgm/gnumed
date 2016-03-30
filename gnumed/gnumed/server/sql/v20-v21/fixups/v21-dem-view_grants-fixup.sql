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
grant select on
	dem.v_region,
	dem.v_urb,
	dem.v_street,
	dem.v_address,
	dem.v_zip2street,
	dem.v_uniq_zipped_urbs,
	dem.v_zip2data,
	dem.v_zip2urb,
	dem.v_basic_address
to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-dem-view_grants-fixup.sql', '21.3');
