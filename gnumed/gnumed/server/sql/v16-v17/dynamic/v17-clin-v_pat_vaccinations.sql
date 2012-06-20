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
drop view clin.v_pat_vaccinations cascade;
\set ON_ERROR_STOP 1

create view clin.v_pat_vaccinations as

select
	cenc.fk_patient
		as pk_patient,
	clv.pk
		as pk_vaccination,
	clv.clin_when
		as date_given,
	now() - clv.clin_when
		as interval_since_given,
	rbd.description
		as vaccine,
	(select array_agg(description)
	 from
		clin.lnk_vaccine2inds clvi
			join clin.vacc_indication cvi on (clvi.fk_indication = cvi.id)
	 where
		clvi.fk_vaccine = clv.fk_vaccine
	) as indications,
	(select array_agg(_(description))
	 from
		clin.lnk_vaccine2inds clvi
			join clin.vacc_indication cvi on (clvi.fk_indication = cvi.id)
	 where
		clvi.fk_vaccine = clv.fk_vaccine
	) as l10n_indications,
	clv.site
		as site,
	clv.batch_no
		as batch_no,
	clv.reaction
		as reaction,
	clv.narrative
		as comment,
	clv.soap_cat
		as soap_cat,

	clv.modified_when
		as modified_when,
	clv.modified_by
		as modified_by,
	clv.row_version
		as row_version,

	(select array_agg(clvi.fk_indication)
	 from
		clin.lnk_vaccine2inds clvi
			join clin.vacc_indication cvi on (clvi.fk_indication = cvi.id)
	 where
		clvi.fk_vaccine = clv.pk
	) as pk_indications,
	clv.fk_vaccine
		as pk_vaccine,
	clv.fk_provider
		as pk_provider,
	clv.fk_encounter
		as pk_encounter,
	clv.fk_episode
		as pk_episode,

	clv.xmin
		as xmin_vaccination
from
	clin.vaccination clv
		join clin.encounter cenc on (cenc.pk = clv.fk_encounter)
			join clin.vaccine on (clin.vaccine.pk = clv.fk_vaccine)
				join ref.branded_drug rbd on (clin.vaccine.fk_brand = rbd.pk)

;

comment on view clin.v_pat_vaccinations is
	'Lists vaccinations for patients';

grant select on clin.v_pat_vaccinations to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v17-clin-v_pat_vaccinations.sql', '17.0');
