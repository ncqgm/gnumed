-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
drop view if exists clin.v_hospital_stays_journal cascade;


create view clin.v_hospital_stays_journal as

	-- stays w/o discharge date
	select
		(select fk_patient from clin.encounter where pk = c_hs.fk_encounter)
			as pk_patient,
		c_hs.modified_when
			as modified_when,
		c_hs.clin_when
			as clin_when,
		coalesce (
			(select short_alias from dem.staff where db_user = c_hs.modified_by),
			'<' || c_hs.modified_by || '>'
		)
			as modified_by,
		c_hs.soap_cat
			as soap_cat,
		_('hospital stay') || E'\n'
			|| ' ' || _('admitted') || ': ' || to_char(clin_when, 'YYYY-MM-DD') || E'\n'
			|| ' ' || _('hospital') || ': "' || d_ou.description || ' @ ' || d_o.description || '"'
			|| coalesce(E'\n ' || c_hs.narrative, '')
			as narrative,
		c_hs.fk_encounter
			as pk_encounter,
		c_hs.fk_episode
			as pk_episode,
		(select fk_health_issue from clin.episode where pk = c_hs.fk_episode)
			as pk_health_issue,
		c_hs.pk
			as src_pk,
		'clin.hospital_stay'::text
			as src_table,
		c_hs.row_version
			as row_version
	from
		clin.hospital_stay c_hs
			left join dem.org_unit d_ou on (d_ou.pk = c_hs.fk_org_unit)
				left join dem.org d_o on (d_o.pk = d_ou.fk_org)
	where
		(c_hs.discharge is NULL)

union all

	-- one-day stays
	select
		(select fk_patient from clin.encounter where pk = c_hs.fk_encounter)
			as pk_patient,
		c_hs.modified_when
			as modified_when,
		c_hs.clin_when
			as clin_when,
		coalesce (
			(select short_alias from dem.staff where db_user = c_hs.modified_by),
			'<' || c_hs.modified_by || '>'
		)
			as modified_by,
		c_hs.soap_cat
			as soap_cat,
		_('hospital stay') || E'\n'
			|| ' ' || _('admitted/discharged') || ': ' || to_char(clin_when, 'YYYY-MM-DD') || E'\n'
			|| ' ' || _('hospital') || ': "' || d_ou.description || ' @ ' || d_o.description || '"' || E'\n'
			|| coalesce(E'\n ' || c_hs.narrative, '')
			as narrative,
		c_hs.fk_encounter
			as pk_encounter,
		c_hs.fk_episode
			as pk_episode,
		(select fk_health_issue from clin.episode where pk = c_hs.fk_episode)
			as pk_health_issue,
		c_hs.pk
			as src_pk,
		'clin.hospital_stay'::text
			as src_table,
		c_hs.row_version
			as row_version
	from
		clin.hospital_stay c_hs
			left join dem.org_unit d_ou on (d_ou.pk = c_hs.fk_org_unit)
				left join dem.org d_o on (d_o.pk = d_ou.fk_org)
	where
		(c_hs.discharge is not NULL)
			and
		(to_char(c_hs.clin_when, 'YYYYMMDD') = to_char(c_hs.discharge, 'YYYYMMDD'))

union all

	-- several days stays: admission
	select
		(select fk_patient from clin.encounter where pk = c_hs.fk_encounter)
			as pk_patient,
		c_hs.modified_when
			as modified_when,
		c_hs.clin_when
			as clin_when,
		coalesce (
			(select short_alias from dem.staff where db_user = c_hs.modified_by),
			'<' || c_hs.modified_by || '>'
		)
			as modified_by,
		c_hs.soap_cat
			as soap_cat,
		_('hospital stay') || E'\n'
			|| ' ' || _('admitted') || ': ' || to_char(clin_when, 'YYYY-MM-DD') || E'\n'
			|| ' ' || _('discharged') || ': ' || to_char(discharge, 'YYYY-MM-DD') || E'\n'
			|| ' ' || _('hospital') || ': "' || d_ou.description || ' @ ' || d_o.description || '"' || E'\n'
			|| coalesce(E'\n ' || c_hs.narrative, '')
			as narrative,
		c_hs.fk_encounter
			as pk_encounter,
		c_hs.fk_episode
			as pk_episode,
		(select fk_health_issue from clin.episode where pk = c_hs.fk_episode)
			as pk_health_issue,
		c_hs.pk
			as src_pk,
		'clin.hospital_stay'::text
			as src_table,
		c_hs.row_version
			as row_version
	from
		clin.hospital_stay c_hs
			left join dem.org_unit d_ou on (d_ou.pk = c_hs.fk_org_unit)
				left join dem.org d_o on (d_o.pk = d_ou.fk_org)
	where
		(c_hs.discharge is not NULL)
			and
		(to_char(c_hs.clin_when, 'YYYYMMDD') != to_char(c_hs.discharge, 'YYYYMMDD'))

union all

	-- several days stays: discharge
	select
		(select fk_patient from clin.encounter where pk = c_hs.fk_encounter)
			as pk_patient,
		c_hs.modified_when
			as modified_when,
		c_hs.discharge
			as clin_when,
		coalesce (
			(select short_alias from dem.staff where db_user = c_hs.modified_by),
			'<' || c_hs.modified_by || '>'
		)
			as modified_by,
		c_hs.soap_cat
			as soap_cat,
		_('discharged from') || ' "' || d_ou.description || ' @ ' || d_o.description || '"'
			as narrative,
		c_hs.fk_encounter
			as pk_encounter,
		c_hs.fk_episode
			as pk_episode,
		(select fk_health_issue from clin.episode where pk = c_hs.fk_episode)
			as pk_health_issue,
		c_hs.pk
			as src_pk,
		'clin.hospital_stay'::text
			as src_table,
		c_hs.row_version
			as row_version
	from
		clin.hospital_stay c_hs
			left join dem.org_unit d_ou on (d_ou.pk = c_hs.fk_org_unit)
				left join dem.org d_o on (d_o.pk = d_ou.fk_org)
	where
		(c_hs.discharge is not NULL)
			and
		(to_char(c_hs.clin_when, 'YYYYMMDD') != to_char(c_hs.discharge, 'YYYYMMDD'))
;


grant select on clin.v_hospital_stays_journal to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-clin-v_hospital_stays_journal.sql', '21.0');
