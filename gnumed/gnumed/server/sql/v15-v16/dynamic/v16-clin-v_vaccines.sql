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
drop view clin.v_vaccines cascade;
\set ON_ERROR_STOP 1

create view clin.v_vaccines as

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

		(select array_agg(description)
		 from
			clin.lnk_vaccine2inds clvi
				join clin.vacc_indication cvi on (clvi.fk_indication = cvi.id)
		 where
			clvi.fk_vaccine = cv.pk
		) as indications,

		(select array_agg(_(description))
		 from
			clin.lnk_vaccine2inds clvi
				join clin.vacc_indication cvi on (clvi.fk_indication = cvi.id)
		 where
			clvi.fk_vaccine = cv.pk
		) as l10n_indications,

		rbd.external_code,
		rbd.external_code_type,

		(select array_agg(clvi.fk_indication)
		 from
			clin.lnk_vaccine2inds clvi
				join clin.vacc_indication cvi on (clvi.fk_indication = cvi.id)
		 where
			clvi.fk_vaccine = cv.pk
		) as pk_indications,

		cv.id_route
			as pk_route,
		cv.fk_brand
			as pk_brand,

		rbd.fk_data_source
			as pk_data_source,

		cv.xmin
			as xmin_vaccine

	from
		clin.vaccine cv
			join ref.branded_drug rbd on (cv.fk_brand = rbd.pk)
				left outer join clin.vacc_route cvr on (cv.id_route = cvr.id)

;

comment on view clin.v_vaccines is
	'A list of vaccines.';

grant select on clin.v_vaccines to group "gm-public";

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_indications4vaccine cascade;
\set ON_ERROR_STOP 1

create view clin.v_indications4vaccine as

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

		(select array_agg(cvi2.description)
		 from
			clin.lnk_vaccine2inds clv2i_2
				join clin.vacc_indication cvi2 on (clv2i_2.fk_indication = cvi2.id)
		 where
			clv2i_2.fk_vaccine = cv.pk
		) as indications,

		(select array_agg(_(cvi2.description))
		 from
			clin.lnk_vaccine2inds clv2i_2
				join clin.vacc_indication cvi2 on (clv2i_2.fk_indication = cvi2.id)
		 where
			clv2i_2.fk_vaccine = cv.pk
		) as l10n_indications,

		(select array_agg(clv2i_2.fk_indication)
		 from
			clin.lnk_vaccine2inds clv2i_2
				join clin.vacc_indication cvi2 on (clv2i_2.fk_indication = cvi2.id)
		 where
			clv2i_2.fk_vaccine = cv.pk
		) as pk_indications,

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


comment on view clin.v_indications4vaccine is
	'Denormalizes indications per vaccine.';

grant select on clin.v_indications4vaccine to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-clin-v_vaccines-dynamic.sql', 'v16');
