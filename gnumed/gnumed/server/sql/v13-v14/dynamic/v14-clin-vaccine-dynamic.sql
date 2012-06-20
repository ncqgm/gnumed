-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

set check_function_bodies to on;

-- --------------------------------------------------------------
-- trigger to ensure that after an INSERT or UPDATE transaction there
-- ARE indications linked to this vaccine

\unset ON_ERROR_STOP
drop function clin.trf_sanity_check_vaccine_has_indications() cascade;
\set ON_ERROR_STOP 1

create function clin.trf_sanity_check_vaccine_has_indications()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_indication_link_pk integer;
BEGIN
	perform 1 from clin.lnk_vaccine2inds where fk_vaccine = NEW.pk limit 1;

	if FOUND then
		return NEW;
	end if;

	raise exception ''[clin.vaccine]: INSERT/UPDATE failed: no indication linked to vaccine (clin.lnk_vaccine2inds.fk_vaccine <-(%)-> clin.vaccine.pk)'', NEW.pk;

	return NEW;
END;';


create constraint trigger tr_sanity_check_vaccine_has_indications
	after insert or update on clin.vaccine
	deferrable
	initially deferred
		for each row execute procedure clin.trf_sanity_check_vaccine_has_indications()
;


--revoke delete on clin.lnk_vaccine2inds from public, "gm-doctors";

-- --------------------------------------------------------------
-- .fk_brand
comment on column clin.vaccine.fk_brand is
	'The brand of this vaccine, can be a fake entry in ref.branded_drug.';

alter table clin.vaccine
	alter column fk_brand
		set not null;

\unset ON_ERROR_STOP
alter table clin.vaccine drop constraint vaccine_fk_brand_fkey cascade;
\set ON_ERROR_STOP 1

alter table clin.vaccine
	add foreign key (fk_brand)
		references ref.branded_drug(pk)
		on update cascade
		on delete restrict;


-- .min_age
\unset ON_ERROR_STOP
alter table clin.vaccine drop constraint vaccine_min_age_check cascade;
alter table clin.vaccine drop constraint vaccine_sane_min_age cascade;
\set ON_ERROR_STOP 1

alter table clin.vaccine
	alter column min_age
		drop not null;

alter table clin.vaccine
	alter column min_age
		drop default;

alter table clin.vaccine
	add constraint vaccine_sane_min_age
		check (
			(min_age is null)
				or
			(
				((max_age is null) and (min_age < '150 years'::interval))
					or
				((max_age is not null) and (min_age <= max_age))
			)
		);



-- .max_age
\unset ON_ERROR_STOP
alter table clin.vaccine drop constraint vaccine_check cascade;
alter table clin.vaccine drop constraint vaccine_sane_max_age cascade;
\set ON_ERROR_STOP 1

alter table clin.vaccine
	alter column max_age
		drop not null;

alter table clin.vaccine
	alter column max_age
		drop default;

alter table clin.vaccine
	add constraint vaccine_sane_max_age
		check (
			(max_age is null)
				or
			(max_age < '150 years'::interval)
		);

-- --------------------------------------------------------------
-- generic mono-valent vaccines
create or replace function gm.create_generic_monovalent_vaccines()
	returns boolean
	security definer
	language plpgsql
	as '
DECLARE
	_row record;
	_generic_name text;
	_pk_brand integer;
	_pk_vaccine integer;
BEGIN
	for _row in select * from clin.vacc_indication loop

		_generic_name := _row.description || '' - generic vaccine'';
		raise notice ''re-creating [%]'', _generic_name;

		-- retrieve or create ref.branded_drug entry for indication
		select pk into _pk_brand from ref.branded_drug
		where
			is_fake is true
				and
			description = _generic_name;

		if FOUND is false then
			insert into ref.branded_drug (
				description,
				preparation,
				is_fake,
				atc_code
			) values (
				_generic_name,
				''vaccine'',		-- this is rather arbitrary
				True,
				coalesce(_row.atcs_single_indication[1], ''J07'')
			)
			returning pk
			into _pk_brand;
		end if;

		-- retrieve or create clin.vaccine entry for generic brand
		select pk into _pk_vaccine from clin.vaccine
		where fk_brand = _pk_brand;

		if FOUND is false then
			insert into clin.vaccine (
				id_route,
				is_live,
				fk_brand
			) values (
				(select id from clin.vacc_route where abbreviation = ''i.m.''),
				false,
				_pk_brand
			)
			returning pk
			into _pk_vaccine;
		end if;

		-- link indication to vaccine
		delete from clin.lnk_vaccine2inds
		where
			fk_vaccine = _pk_vaccine;

		insert into clin.lnk_vaccine2inds (
			fk_vaccine,
			fk_indication
		) values (
			_pk_vaccine,
			_row.id
		);

	end loop;

	return true;
END;';

select gm.create_generic_monovalent_vaccines();

-- --------------------------------------------------------------
-- create a few typical, generic combi-indication vaccines
create or replace function gm.create_generic_combi_vaccine(text, text[], text, boolean)
	returns boolean
	security definer
	language plpgsql
	as '
DECLARE
	_name alias for $1;
	_indications alias for $2;
	_atc alias for $3;
	_is_live alias for $4;
	_generic_name text;
	_pk_brand integer;
	_pk_vaccine integer;
	_indication text;
BEGIN

	_generic_name := _name || '' - generic vaccine'';
	raise notice ''re-creating [%] (%)'', _generic_name, array_to_string(_indications, ''-'');

	-- retrieve or create ref.branded_drug entry for indication
	select pk into _pk_brand from ref.branded_drug
	where
		is_fake is true
			and
		description = _generic_name;

	if FOUND is false then
		insert into ref.branded_drug (
			description,
			preparation,
			is_fake,
			atc_code
		) values (
			_generic_name,
			''vaccine'',		-- this is rather arbitrary
			True,
			coalesce(_atc, ''J07'')
		)
		returning pk
		into _pk_brand;
	end if;

	-- retrieve or create clin.vaccine entry for generic brand
	select pk into _pk_vaccine from clin.vaccine
	where fk_brand = _pk_brand;

	if FOUND is false then
		insert into clin.vaccine (
			id_route,
			is_live,
			fk_brand
		) values (
			(select id from clin.vacc_route where abbreviation = ''i.m.''),
			_is_live,
			_pk_brand
		)
		returning pk
		into _pk_vaccine;
	end if;

	-- link indications to vaccine
	delete from clin.lnk_vaccine2inds
	where
		fk_vaccine = _pk_vaccine;

	for _indication in select unnest(_indications) loop

		insert into clin.lnk_vaccine2inds (
			fk_vaccine,
			fk_indication
		) values (
			_pk_vaccine,
			(select id from clin.vacc_indication where description = _indication)
		);

	end loop;

	return true;
END;';



create or replace function gm.create_generic_combi_vaccines()
	returns boolean
	language SQL
	as '

select gm.create_generic_combi_vaccine (
	''Td''::text,
	ARRAY[''tetanus''::text,''diphtheria''::text],
	''J07AM51'',
	False
);

select gm.create_generic_combi_vaccine (
	''DT''::text,
	ARRAY[''tetanus''::text,''diphtheria''::text],
	''J07AM51'',
	False
);

select gm.create_generic_combi_vaccine (
	''TdaP''::text,
	ARRAY[''tetanus''::text,''diphtheria''::text,''pertussis''::text],
	''J07CA01'',
	False
);

select gm.create_generic_combi_vaccine (
	''TDaP''::text,
	ARRAY[''tetanus''::text,''diphtheria''::text,''pertussis''::text],
	''J07CA01'',
	False
);

select gm.create_generic_combi_vaccine (
	''TdaP-Pol''::text,
	ARRAY[''tetanus''::text,''diphtheria''::text,''pertussis''::text,''poliomyelitis''::text],
	''J07CA02'',
	False
);

select gm.create_generic_combi_vaccine (
	''TDaP-Pol''::text,
	ARRAY[''tetanus''::text,''diphtheria''::text,''pertussis''::text,''poliomyelitis''::text],
	''J07CA02'',
	False
);

select gm.create_generic_combi_vaccine (
	''TDaP-Pol-HiB''::text,
	ARRAY[''tetanus''::text,''diphtheria''::text,''pertussis''::text,''poliomyelitis''::text,''haemophilus influenzae b''::text],
	''J07CA06'',
	False
);

select gm.create_generic_combi_vaccine (
	''TDaP-Pol-HiB-HepB''::text,
	ARRAY[''tetanus''::text,''diphtheria''::text,''pertussis''::text,''poliomyelitis''::text,''haemophilus influenzae b''::text,''hepatitis B''::text],
	''J07CA09'',
	False
);

select gm.create_generic_combi_vaccine (
	''MMR''::text,
	ARRAY[''measles''::text,''mumps''::text,''rubella''::text],
	''J07BD52'',
	True
);

select gm.create_generic_combi_vaccine (
	''MMRV''::text,
	ARRAY[''measles''::text,''mumps''::text,''rubella''::text,''varicella (chickenpox, shingles)''::text],
	''J07BD54'',
	True
);

select gm.create_generic_combi_vaccine (
	''HepAB''::text,
	ARRAY[''hepatitis A''::text,''hepatitis B''::text],
	''J07BC20'',
	False
);

select True;
';

select gm.create_generic_combi_vaccines();

-- --------------------------------------------------------------
-- improve ATC codes of pre-existing vaccines
update ref.branded_drug set
	atc_code = 'J07AM01'
where
	description = 'Tetasorbat SSW (Tetanus)';

update ref.branded_drug set
	atc_code = 'J07AM51'
where
	description = 'Td-pur (Td)';

update ref.branded_drug set
	atc_code = 'J07BC02'
where
	description = 'Havrix 720 Kinder (HAV)';

update ref.branded_drug set
	atc_code = 'J07BC02'
where
	description = 'Havrix 1440 (HAV)';

update ref.branded_drug set
	atc_code = 'J07BC01'
where
	description = 'HBVAXPRO';

update ref.branded_drug set
	atc_code = 'J07AL02'
where
	description = 'Prevenar';

update ref.branded_drug set
	atc_code = 'J07BB01'
where
	description = 'InfectoVac Flu 2003/2004 (Flu 03)';

update ref.branded_drug set
	atc_code = 'J07BB01'
where
	description = 'InfectoVac Flu 2004/2005 (Flu 04)';

update ref.branded_drug set
	atc_code = 'J07AH07'
where
	description = 'NeisVac-C, Meningokokken-C-Konjugat (NeisVac-C)';

update ref.branded_drug set
	atc_code = 'J07AH07'
where
	description = 'Menjugate, Meningokokken-C-Konjugat (Menjugate)';

update ref.branded_drug set
	atc_code = 'J07AH07'
where
	description = 'Meningitec';

update ref.branded_drug set
	atc_code = 'J07CA02'
where
	description = 'REPEVAX';

update ref.branded_drug set
	atc_code = 'J07CA01'
where
	description = 'REVAXIS';

update ref.branded_drug set
	atc_code = 'J07BA01'
where
	description = 'FSME-IMMUN 0.25ml Junior';

update ref.branded_drug set
	atc_code = 'J07BA01'
where
	description = 'Encepur Kinder';

update ref.branded_drug set
	atc_code = 'J07BD52'
where
	description = 'PRIORIX';

update ref.branded_drug set
	atc_code = 'J07BD01'
where
	description = 'Masern-Impfstoff Mérieux';

update ref.branded_drug set
	atc_code = 'J07CA06'
where
	description = 'INFANRIX-IPV+HIB';

update ref.branded_drug set
	atc_code = 'J07AG01'
where
	description = 'Act-HiB';

update ref.branded_drug set
	atc_code = 'J07CA06'
where
	description = 'PentaVac';

update ref.branded_drug set
	atc_code = 'J07BF03'
where
	description = 'IPV Mérieux';

update ref.branded_drug set
	atc_code = 'J07AP03'
where
	description = 'Typhim Vi (Typhus)';

update ref.branded_drug set
	atc_code = 'J07BC01'
where
	description = 'Hepatitis B (Hep B)';

update ref.branded_drug set
	description = 'Haemophilus influenzae B (PRP-OMP)',
	atc_code = 'J07AG01'
where
	description = 'Haemophilius influenzae type b (PRP-OMP)';

update ref.branded_drug set
	description = 'Haemophilus influenzae B (PRP-T)',
	atc_code = 'J07AG01'
where
	description = 'Haemophilius influenzae type b(PRP-T)';

update ref.branded_drug set
	description = 'Haemophilus influenzae B (HbOC)',
	atc_code = 'J07AG01'
where
	description = 'Haemophilius influenzae type b(HbOC)';

update ref.branded_drug set
	atc_code = 'J07BF03'
where
	description = 'inactivated poliomyelitis vaccine (IPV)';

update ref.branded_drug set
	atc_code = 'J07BK01'
where
	description = 'varicella-zoster vaccine (VZV)';

update ref.branded_drug set
	atc_code = 'J07AL02'
where
	description = '7-valent pneumococcal conjugate vaccine (7vPCV)';

update ref.branded_drug set
	atc_code = 'J07AL02'
where
	description = '23-valent pneumococcal polysaccharide vaccine (23vPPV)';

update ref.branded_drug set
	atc_code = 'J07AH07'
where
	description = 'meningococcal C conjugate vaccine (menCCV)';

update ref.branded_drug set
	atc_code = 'J07BF02'
where
	description = 'oral poliomyelitis vaccine (OPV)';

update ref.branded_drug set
	atc_code = 'J07AM01'
where
	description = 'Tetasorbat (SFCMS) (Tetanus)';

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
				join clin.vacc_route cvr on (cv.id_route = cvr.id)

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
			join clin.vacc_route cvr on (cvr.id = cv.id_route)
				join ref.branded_drug rbd on (rbd.pk = cv.fk_brand)
					join clin.lnk_vaccine2inds clv2i on (clv2i.fk_vaccine = cv.pk)
						join clin.vacc_indication cvi on (cvi.id = clv2i.fk_indication)

;


comment on view clin.v_indications4vaccine is
	'Denormalizes indications per vaccine.';

grant select on clin.v_indications4vaccine to group "gm-public";

-- --------------------------------------------------------------

grant select on clin.vacc_route to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v14-clin-vaccine-dynamic.sql,v $', '$Revision: 1.3 $');
