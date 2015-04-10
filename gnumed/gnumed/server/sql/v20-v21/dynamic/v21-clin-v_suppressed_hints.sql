-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

--set default_transaction_read_only to off;
set check_function_bodies to on;

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
	r_vah.url,
	r_vah.is_active,
	r_vah.source,
	r_vah.query,
	r_vah.lang,
	c_sh.rationale,
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
drop view if exists clin.v_suppressed_hints_journal cascade;


create view clin.v_suppressed_hints_journal as
select
	(select fk_patient from clin.encounter where pk = c_sh.fk_encounter)
		as pk_identity,
	c_sh.modified_when
		as modified_when,
	c_sh.suppressed_when
		as clin_when,
	c_sh.modified_by
		as modified_by,
	'p'::text
		as soap_cat,
	case
		when r_vah.is_active is TRUE then
			_('Active hint')
		else
			_('Inactive hint')
	end
		|| ' #' || c_sh.fk_hint || ' ' || _('suppressed by') || ' ' || c_sh.suppressed_by || E'\n'
		|| coalesce(_('Title: ') || r_vah.title || E'\n', '')
		|| coalesce(_('URL: ') || r_vah.url || E'\n', '')
		|| coalesce(_('Source: ') || r_vah.source || E'\n', '')
		|| coalesce(_('Rationale: ') || c_sh.rationale || E'\n', '')
		|| case when c_sh.md5_sum <> r_vah.md5_sum
			then _('Hint definition has been modified since suppression. Rationale for suppression may no longer apply.') || E'\n'
			else ''
		end
		|| coalesce(_('Hint: ') || r_vah.hint, '')
		as narrative,
	c_sh.fk_encounter
		as fk_encounter,
	NULL::integer
		as pk_episode,
	NULL::integer
		as pk_health_issue,
	c_sh.pk
		as src_pk,
	'clin.suppressed_hint'::text
		as src_table,
	c_sh.row_version
		as row_version
from
	clin.suppressed_hint c_sh
		join ref.v_auto_hints r_vah on c_sh.fk_hint = r_vah.pk_auto_hint
;


revoke all on clin.v_suppressed_hints from public;
grant select on clin.v_suppressed_hints to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-clin-v_suppressed_hints.sql', '21.0');
