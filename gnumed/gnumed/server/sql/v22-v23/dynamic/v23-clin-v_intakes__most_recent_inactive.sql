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
drop view if exists clin.v_intakes__most_recent_inactive cascade;

create view clin.v_intakes__most_recent_inactive as
select c_vii.* from
	(
		select
			c_ir.fk_intake, max(c_ir.discontinued) as most_recent_discontinued
		from clin.intake_regimen c_ir
		where c_ir.discontinued is not null
		group by c_ir.fk_intake
	) as most_recent_ones
	inner join clin.v_intakes__inactive c_vii on
		c_vii.pk_intake = most_recent_ones.fk_intake
			AND
		c_vii.discontinued = most_recent_ones.most_recent_discontinued
;

comment on view clin.v_intakes__most_recent_inactive is
	'Inactive intakes together with their most recent regimen.';

grant select on clin.v_intakes__most_recent_inactive to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-v_intakes__most_recent_inactive.sql', '23.0');
