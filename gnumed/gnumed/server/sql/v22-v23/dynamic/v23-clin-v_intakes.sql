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
drop view if exists clin.v_intakes cascade;

create view clin.v_intakes as
	select * from clin.v_intakes__most_recent_inactive
		union all
	select * from clin.v_intakes__active
;

comment on view clin.v_intakes is
	'Substance intakes, active ones, and the most recent regimen of the inactive ones.';

grant select on clin.v_intakes to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-v_intakes.sql', '23.0');
