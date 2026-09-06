-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

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
	-- '"' || (_(b_dt.name) || '" '
	(
	'"' || coalesce(tx_exact_doc_type.trans, tx_reduced_doc_type.trans, b_dt.name) || '" '
		|| (select _('with')) || ' ' || (select count(1) from blobs.doc_obj b_do where b_do.fk_doc = b_dm.pk) || ' ' || (select _('part(s)')) || E'\n'
		|| ' ' || to_char(b_dm.clin_when, 'YYYY-MM-DD HH24:MI') || E'\n'
		|| coalesce(' [' || b_dm.ext_ref || ']', '')
		|| (case
			when b_dm.unit_is_receiver
				then coalesce(' ' || (select _('sent to')) || d_ou.description || ' ' || (select _('of')) || ' ' || d_o.description, '')
				else coalesce(' @ ' || d_ou.description || ' ' || (select _('of')) || ' ' || d_o.description, '')
			end
		) || E'\n'
		|| coalesce(' ' || b_dm.comment, '')
	)	as narrative,
	b_dm.fk_encounter
		as pk_encounter,
	b_dm.fk_episode
		as pk_episode,
	c_epi.fk_health_issue
		as pk_health_issue,
	b_dm.pk
		as src_pk,
	'blobs.doc_med'::text
		as src_table,
	b_dm.row_version,

	-- issue
	c_hi.description
		as health_issue,
	c_hi.laterality
		as issue_laterality,
	c_hi.is_active
		as issue_active,
	c_hi.clinically_relevant
		as issue_clinically_relevant,
	c_hi.is_confidential
		as issue_confidential,

	-- episode
	c_epi.description
		as episode,
	c_epi.is_open
		as episode_open,

	-- encounter
	c_enc.started
		as encounter_started,
	c_enc.last_affirmed
		as encounter_last_affirmed,
	c_enc.fk_type AS pk_encounter_type
from
	blobs.doc_med b_dm
		inner join clin.encounter c_enc on (b_dm.fk_encounter = c_enc.pk)

		inner join blobs.doc_type b_dt on (b_dm.fk_type = b_dt.pk)
			LEFT JOIN i18n.translations tx_exact_doc_type ON
				tx_exact_doc_type.orig = b_dt.name
					AND
				tx_exact_doc_type.lang = (SELECT lang FROM i18n.curr_lang WHERE db_user = current_user)
			LEFT JOIN i18n.translations tx_reduced_doc_type ON
				tx_reduced_doc_type.orig = b_dt.name
					AND
				tx_reduced_doc_type.lang = (SELECT regexp_replace(lang, '_.*$', '') FROM i18n.curr_lang WHERE db_user = current_user)

		inner join clin.episode c_epi on (b_dm.fk_episode = c_epi.pk)
			left join clin.health_issue c_hi on (c_epi.fk_health_issue = c_hi.pk)

		left join dem.org_unit d_ou on (b_dm.fk_org_unit = d_ou.pk)
			left join dem.org d_o on (d_ou.fk_org = d_o.pk)
;


grant select on blobs.v_doc_med_journal TO GROUP "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-blobs-v_doc_med_journal.sql', '23.0');
