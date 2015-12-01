-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
drop view if exists blobs.v_doc_med_journal cascade;

create view blobs.v_doc_med_journal as
select
	c_enc.fk_patient
		as pk_patient,
	b_dm.modified_when
		as modified_when,
	b_dm.clin_when
		as clin_when,
	coalesce (
		(select short_alias from dem.staff where db_user = b_dm.modified_by),
		'<' || b_dm.modified_by || '>'
	)
		as modified_by,
	null::text
		as soap_cat,
	'"' || (_(b_dt.name) || '" '
		|| _('with') || ' ' || (select count(1) from blobs.doc_obj b_do where b_do.fk_doc = b_dm.pk) || ' ' || _('part(s)') || E'\n'
		|| ' ' || to_char(b_dm.clin_when, 'YYYY-MM-DD HH24:MI') || E'\n'
		|| coalesce(' [' || b_dm.ext_ref || ']', '') || coalesce(' @ ' || d_ou.description || ' ' || _('of') || ' ' || d_o.description, '') || E'\n'
		|| coalesce(' ' || b_dm.comment, '')
	)	as narrative,
	b_dm.fk_encounter
		as pk_encounter,
	b_dm.fk_episode
		as pk_episode,
	(select fk_health_issue from clin.episode where pk = b_dm.fk_episode)
		as pk_health_issue,
	b_dm.pk
		as src_pk,
	'blobs.doc_med'::text
		as src_table
from
	blobs.doc_med b_dm
		inner join clin.encounter c_enc on (b_dm.fk_encounter = c_enc.pk)
			inner join blobs.doc_type b_dt on (b_dm.fk_type = b_dt.pk)
				left join dem.org_unit d_ou on (b_dm.fk_org_unit = d_ou.pk)
					left join dem.org d_o on (d_ou.fk_org = d_o.pk)
;

grant select on blobs.v_doc_med_journal TO GROUP "gm-doctors";

-- --------------------------------------------------------------
select i18n.upd_tx('de', 'part(s)', 'Teil(e)');
select i18n.upd_tx('de', 'with', 'mit');

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-blobs-v_doc_med_journal.sql', '21.0');
