-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_pat_vaccs4indication cascade;
\set ON_ERROR_STOP 1

create view clin.v_pat_vaccs4indication as

select
	cenc.fk_patient
		as pk_patient,
	cv.pk
		as pk_vaccination,
	cv.clin_when
		as date_given,
	cvi4v.vaccine
		as vaccine,
	cvi4v.indication
		as indication,
	cvi4v.l10n_indication
		as l10n_indication,
	cv.site
		as site,
	cv.batch_no
		as batch_no,
	cv.reaction
		as reaction,
	cv.narrative
		as comment,
	cv.soap_cat
		as soap_cat,

	cv.modified_when
		as modified_when,
	cv.modified_by
		as modified_by,
	cv.row_version
		as row_version,

	cv.fk_vaccine
		as pk_vaccine,
	cvi4v.pk_indication
		as pk_indication,
	cv.fk_provider
		as pk_provider,
	cv.fk_encounter
		as pk_encounter,
	cv.fk_episode
		as pk_episode,

	cv.xmin
		as xmin_vaccination
from
	clin.vaccination cv
		join clin.encounter cenc on (cenc.pk = cv.fk_encounter)
			join clin.v_indications4vaccine cvi4v on (cvi4v.pk_vaccine = cv.fk_vaccine)

;

comment on view clin.v_pat_vaccs4indication is
	'Lists vaccinations per indication for patients';

grant select on clin.v_pat_vaccs4indication to group "gm-doctors";

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_pat_last_vacc4indication cascade;
\set ON_ERROR_STOP 1

create view clin.v_pat_last_vacc4indication as

select
	cvpv4i1.*,
	cpi.indication_count
from
	clin.v_pat_vaccs4indication cvpv4i1
		join (
			SELECT
				COUNT(1) AS indication_count,
				pk_patient,
				pk_indication
			FROM clin.v_pat_vaccs4indication
			GROUP BY
				pk_patient,
				pk_indication
		) AS cpi ON (cvpv4i1.pk_patient = cpi.pk_patient AND cvpv4i1.pk_indication = cpi.pk_indication)
where
	cvpv4i1.date_given = (
		select
			max(cvpv4i2.date_given)
		from
			clin.v_pat_vaccs4indication cvpv4i2
		where
			cvpv4i1.pk_patient = cvpv4i2.pk_patient
				and
			cvpv4i1.pk_indication = cvpv4i2.pk_indication
	)
;

comment on view clin.v_pat_last_vacc4indication is
	'Lists *latest* vaccinations with total count per indication.';

grant select on clin.v_pat_last_vacc4indication to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-clin-vaccination-dynamic.sql', 'v16');
