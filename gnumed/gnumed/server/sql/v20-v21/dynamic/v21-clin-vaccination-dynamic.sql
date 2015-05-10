-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
drop view if exists clin.v_lnk_vaccine2inds cascade;

create view clin.v_lnk_vaccine2inds as
	select
		cv.pk
			as pk_vaccine,

		rbd.description
			as vaccine,
		rbd.preparation
			as preparation,
		rbd.atc_code
			as atc_code,
		rbd.is_fake
			as is_fake_vaccine,

		cvr.abbreviation
			as route_abbreviation,
		cvr.description
			as route_description,

		cv.is_live,
		cv.min_age,
		cv.max_age,
		cv.comment,

		cvi.description
			as indication,
		_(cvi.description)
			as l10n_indication,
		cvi.atcs_single_indication
			as atcs_single_indication,
		cvi.atcs_combi_indication
			as atcs_combi_indication,

		rbd.external_code,
		rbd.external_code_type,

		cv.id_route
			as pk_route,
		cv.fk_brand
			as pk_brand,
		rbd.fk_data_source
			as pk_data_source,
		cvi.id
			as pk_indication,
		cv.xmin
			as xmin_vaccine
	from
		clin.vaccine cv
			left outer join clin.vacc_route cvr on (cvr.id = cv.id_route)
				join ref.branded_drug rbd on (rbd.pk = cv.fk_brand)
					join clin.lnk_vaccine2inds clv2i on (clv2i.fk_vaccine = cv.pk)
						join clin.vacc_indication cvi on (cvi.id = clv2i.fk_indication)

;

comment on view clin.v_lnk_vaccine2inds is
	'Denormalizes indications per vaccine.';

grant select on clin.v_lnk_vaccine2inds to group "gm-public";

-- --------------------------------------------------------------
drop view if exists clin.v_pat_vaccs4indication cascade;

create view clin.v_pat_vaccs4indication as
select
	c_enc.fk_patient
		as pk_patient,
	c_shot.pk
		as pk_vaccination,
	c_shot.clin_when
		as date_given,
	--c_vinds4vcine.vaccine
	c_vlv2i.vaccine
		as vaccine,
	--c_vinds4vcine.indication
	c_vlv2i.indication
		as indication,
	--c_vinds4vcine.l10n_indication
	c_vlv2i.l10n_indication
		as l10n_indication,
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
	--c_vinds4vcine.pk_indication
	c_vlv2i.pk_indication
		as pk_indication,
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
			join clin.v_lnk_vaccine2inds c_vlv2i on (c_vlv2i.pk_vaccine = c_shot.fk_vaccine)
--			join clin.v_indications4vaccine c_vinds4vcine on (c_vinds4vcine.pk_vaccine = c_shot.fk_vaccine)

;

comment on view clin.v_pat_vaccs4indication is
	'Lists vaccinations per indication for patients';

grant select on clin.v_pat_vaccs4indication to group "gm-doctors";

-- --------------------------------------------------------------
drop view if exists clin.v_pat_last_vacc4indication cascade;

create view clin.v_pat_last_vacc4indication as
	SELECT
		c_vpv4i.*,
		shots_per_ind.no_of_shots
	FROM
		clin.v_pat_vaccs4indication c_vpv4i
			join (
				SELECT
					COUNT(1) AS no_of_shots
					,pk_patient,
					pk_indication
				FROM clin.v_pat_vaccs4indication
				GROUP BY
					pk_patient,
					pk_indication
				) AS shots_per_ind
			ON (c_vpv4i.pk_patient = shots_per_ind.pk_patient AND c_vpv4i.pk_indication = shots_per_ind.pk_indication)

	where
		c_vpv4i.date_given = (
			select
				max(c_vpv4i_2.date_given)
			from
				clin.v_pat_vaccs4indication c_vpv4i_2
			where
				c_vpv4i.pk_patient = c_vpv4i_2.pk_patient
					and
				c_vpv4i.pk_indication = c_vpv4i_2.pk_indication
		)

;

comment on view clin.v_pat_last_vacc4indication is
	'Lists *latest* vaccinations with total count per indication.';

grant select on clin.v_pat_last_vacc4indication to group "gm-doctors";

-- --------------------------------------------------------------
drop index if exists clin.idx_clin_lnk_vaccine2inds_fk_vacc cascade;
create index idx_clin_lnk_vaccine2inds_fk_vacc on clin.lnk_vaccine2inds(fk_vaccine);

drop index if exists clin.idx_clin_lnk_vaccine2inds_fk_ind cascade;
create index idx_clin_lnk_vaccine2inds_fk_ind on clin.lnk_vaccine2inds(fk_indication);


drop index if exists clin.idx_clin_vaccination_fk_vaccine cascade;
create index idx_clin_vaccination_fk_vaccine on clin.vaccination(fk_vaccine);

drop index if exists clin.idx_clin_vaccination_fk_provider cascade;
create index idx_clin_vaccination_fk_provider on clin.vaccination(fk_provider);

drop index if exists clin.idx_clin_vaccination_clin_when cascade;
create index idx_clin_vaccination_clin_when on clin.vaccination(clin_when);

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-clin-vaccination-dynamic.sql', '21.0');
