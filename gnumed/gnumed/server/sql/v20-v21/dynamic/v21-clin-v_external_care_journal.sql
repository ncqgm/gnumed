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
drop view if exists clin.v_external_care_journal cascade;

create view clin.v_external_care_journal as
select
	c_vec.pk_identity
		as pk_patient,
	c_vec.modified_when
		as modified_when,
	c_vec.modified_when
		as clin_when,
	c_vec.modified_by
		as modified_by,
	's'::text
		as soap_cat,
	_('External care')
		|| coalesce(' ' || _('by') || ' ' || c_vec.provider, '')
		|| ' @ ' || c_vec.unit || ' ' || _('of') || ' ' || c_vec.organization || E'\n'
		|| _('Issue:') || ' ' || c_vec.issue || E'\n'
		|| coalesce(_('Comment:') || ' ' || c_vec.comment, '')
		as narrative,
	c_vec.pk_encounter
		as pk_encounter,
	NULL::integer
		as pk_episode,
	c_vec.pk_health_issue
		as pk_health_issue,
	c_vec.pk_external_care
		as src_pk,
	'clin.external_care'::text
		as src_table,
	c_vec.row_version
		as row_version
from
	clin.v_external_care c_vec
;

revoke all on clin.v_external_care_journal from public;
grant select on clin.v_external_care_journal to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-clin-v_external_care_journal.sql', '21.0');
