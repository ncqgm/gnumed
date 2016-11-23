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
drop view if exists clin.v_suppressed_hints cascade;


create view clin.v_suppressed_hints as
select
	(select fk_patient from clin.encounter where pk = c_sh.fk_encounter)
		as pk_identity,
	c_sh.pk
		as pk_suppressed_hint,
	c_sh.fk_hint
		as pk_hint,
	r_vah.title,
	r_vah.hint,
	r_vah.recommendation,
	r_vah.url,
	r_vah.is_active,
	r_vah.source,
	r_vah.query,
	r_vah.lang,
	c_sh.rationale,
	r_vah.popup_type,
	r_vah.highlight_as_priority,
	c_sh.md5_sum
		as md5_suppressed,
	r_vah.md5_sum
		as md5_hint,
	c_sh.suppressed_by,
	c_sh.suppressed_when,
	c_sh.fk_encounter
		as pk_encounter
from
	clin.suppressed_hint c_sh
		join ref.v_auto_hints r_vah on c_sh.fk_hint = r_vah.pk_auto_hint
;


revoke all on clin.v_suppressed_hints from public;
grant select on clin.v_suppressed_hints to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-clin-v_suppressed_hints.sql', '22.0');
