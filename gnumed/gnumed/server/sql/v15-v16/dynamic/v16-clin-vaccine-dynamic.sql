-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
\set ON_ERROR_STOP 1

set check_function_bodies to on;

-- --------------------------------------------------------------
-- .is_live
alter table clin.vaccine
	alter column is_live
		drop not null;

alter table clin.vaccine
	alter column is_live
		set default null;


-- .id_route
alter table clin.vaccine
	alter column id_route
		drop not null;

alter table clin.vaccine
	alter column id_route
		set default null;


\unset ON_ERROR_STOP
drop index idx_c_vaccine_id_route cascade;
\set ON_ERROR_STOP 1

create index idx_c_vaccine_id_route on clin.vaccine(id_route);


-- .fk_brand
\unset ON_ERROR_STOP
alter table clin.vaccine drop constraint clin_vaccine_uniq_brand cascade;
\set ON_ERROR_STOP 1

alter table clin.vaccine
	add constraint clin_vaccine_uniq_brand
		unique (fk_brand);


-- --------------------------------------------------------------
-- adjust vaccination routes
UPDATE clin.vacc_route SET description = 'oral' WHERE description = 'orally';
select i18n.upd_tx('de', 'oral', 'oral');


INSERT INTO clin.vacc_route (
	abbreviation,
	description
) SELECT
	'nasal'::text,
	'nasal'::text
  WHERE NOT EXISTS (
	select 1 from clin.vacc_route where description = 'nasal' limit 1
);
select i18n.upd_tx('de', 'nasal', 'nasal');


INSERT INTO clin.vacc_route (
	abbreviation,
	description
) SELECT
	'i.d.'::text,
	'intradermal'::text
  WHERE NOT EXISTS (
	select 1 from clin.vacc_route where description = 'intradermal' limit 1
);
select i18n.upd_tx('de', 'intradermal', 'intradermal');

-- --------------------------------------------------------------
-- add vaccination indication
insert into clin.vacc_indication (
	description,
	atcs_single_indication
) select
	'influenza (H3N2)',
	array['J07BB']
  where not exists (
	select 1 from clin.vacc_indication where description = ''
);

select i18n.upd_tx('de', 'influenza (H3N2)', 'Influenza (H3N2)');

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
				is_live,
				fk_brand
			) values (
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
			is_live,
			fk_brand
		) values (
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

-- ==============================================================
select gm.log_script_insertion('v16-clin-v_vaccines.sql', 'v16');
