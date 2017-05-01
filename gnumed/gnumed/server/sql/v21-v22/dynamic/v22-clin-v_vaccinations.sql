-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
drop view if exists clin.v_pat_vaccinations cascade;
drop view if exists clin.v_vaccinations cascade;

create view clin.v_vaccinations as
select
	c_enc.fk_patient
		as pk_patient,
	c_shot.pk
		as pk_vaccination,
	c_shot.clin_when
		as date_given,
	now() - c_shot.clin_when
		as interval_since_given,
	r_dp.description
		as vaccine,
	ARRAY (
		select row_to_json(indication_row) from (
			select
				_(r_s.atc || '-target', 'en')
					as indication,
				case
					when _(r_s.atc || '-target') = (r_s.atc || '-target') then _(r_s.atc || '-target', 'en')
					else _(r_s.atc || '-target')
				end
					as l10n_indication,
				r_s.atc
					as atc_indication
			from
				ref.lnk_dose2drug r_ld2d
					inner join ref.dose r_d on (r_d.pk = r_ld2d.fk_dose)
						inner join ref.substance r_s on (r_d.fk_substance = r_s.pk)
			where
				r_ld2d.fk_drug_product = r_dp.pk
		) as indication_row
	) as indications,
	c_shot.site
		as site,
	c_shot.batch_no
		as batch_no,
	c_shot.reaction
		as reaction,
	c_shot.narrative
		as comment,
	c_shot.soap_cat
		as soap_cat,

	c_shot.modified_when
		as modified_when,
	c_shot.modified_by
		as modified_by,
	c_shot.row_version
		as row_version,
	c_shot.fk_vaccine
		as pk_vaccine,
	c_shot.fk_provider
		as pk_provider,
	c_shot.fk_encounter
		as pk_encounter,
	c_shot.fk_episode
		as pk_episode,

	c_shot.xmin
		as xmin_vaccination
from
	clin.vaccination c_shot
		join clin.encounter c_enc on (c_enc.pk = c_shot.fk_encounter)
		join ref.vaccine r_v on (r_v.pk = c_shot.fk_vaccine)
			join ref.drug_product r_dp on (r_v.fk_drug_product = r_dp.pk)

;

comment on view clin.v_vaccinations is
	'Lists vaccinations for patients';

grant select on clin.v_vaccinations to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-clin-v_vaccinations.sql', '22.0');
