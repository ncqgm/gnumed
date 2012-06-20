-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------

-- we don't use inheritance here since UNIQUE constraints are
-- not automatically enforced across inheritance trees
-- .fk_brand
alter table clin.vaccine
	add column fk_brand integer;

alter table audit.log_vaccine
	add column fk_brand integer;

-- --------------------------------------------------------------
-- prepare for improved check constraints

update clin.vaccine
set
	max_age = '149 years'::interval
where
	max_age = '5555 years':: interval;

-- --------------------------------------------------------------
-- delete a few vaccines

delete from clin.vaccine where
	trade_name = 'diptheria-tetanus-acellular pertussis adult/adolescent formulation';

delete from clin.vaccine where
	trade_name = 'diptheria-tetanus-acellular pertussis infant/child formulation';

delete from clin.vaccine where
	trade_name = 'adult diptheria-tetanus';

delete from clin.vaccine where
	trade_name = 'measles-mumps-rubella vaccine';

delete from clin.vaccine where
	trade_name = 'influenza vaccine';

-- --------------------------------------------------------------
-- add missing indications
insert into clin.lnk_vaccine2inds (
	fk_vaccine,
	fk_indication
) values (
	(select pk from clin.vaccine where short_name = 'PRP-OMP'),
	(select id from clin.vacc_indication where description = 'haemophilus influenzae b')
);

insert into clin.lnk_vaccine2inds (
	fk_vaccine,
	fk_indication
) values (
	(select pk from clin.vaccine where short_name = 'HbOC'),
	(select id from clin.vacc_indication where description = 'haemophilus influenzae b')
);

insert into clin.lnk_vaccine2inds (
	fk_vaccine,
	fk_indication
) values (
	(select pk from clin.vaccine where short_name = 'PRP-T'),
	(select id from clin.vacc_indication where description = 'haemophilus influenzae b')
);


insert into clin.lnk_vaccine2inds (
	fk_vaccine,
	fk_indication
) values (
	(select pk from clin.vaccine where trade_name = 'oral poliomyelitis vaccine'),
	(select id from clin.vacc_indication where description = 'poliomyelitis')
);

insert into clin.lnk_vaccine2inds (
	fk_vaccine,
	fk_indication
) values (
	(select pk from clin.vaccine where trade_name = 'inactivated poliomyelitis vaccine'),
	(select id from clin.vacc_indication where description = 'poliomyelitis')
);


insert into clin.lnk_vaccine2inds (
	fk_vaccine,
	fk_indication
) values (
	(select pk from clin.vaccine where short_name = 'VZV'),
	(select id from clin.vacc_indication where description = 'varicella')
);


insert into clin.lnk_vaccine2inds (
	fk_vaccine,
	fk_indication
) values (
	(select pk from clin.vaccine where short_name = '7vPCV'),
	(select id from clin.vacc_indication where description = 'pneumococcus')
);

insert into clin.lnk_vaccine2inds (
	fk_vaccine,
	fk_indication
) values (
	(select pk from clin.vaccine where short_name = '23vPPV'),
	(select id from clin.vacc_indication where description = 'pneumococcus')
);


insert into clin.lnk_vaccine2inds (
	fk_vaccine,
	fk_indication
) values (
	(select pk from clin.vaccine where short_name = 'menCCV'),
	(select id from clin.vacc_indication where description = 'meningococcus C')
);


-- convert existing vaccines to drugs and adjust clin.vaccines.fk_brand
create or replace function tmp_v13_v14_convert_vaccines_to_drugs()
	returns boolean
	language plpgsql
	as '
DECLARE
	_row record;
	_new_drug_pk integer;
	_new_drug_name text;
	_new_drug_preparation text;
BEGIN
	for _row in select * from clin.vaccine loop

		raise notice ''vaccine: % (% - %)'', _row.pk::text, _row.trade_name, _row.short_name;

		-- generate new name
		if position(lower(_row.short_name) in lower(_row.trade_name)) = 0 then
			_new_drug_name := _row.trade_name || '' ('' || _row.short_name || '')'';
		else
			_new_drug_name := _row.trade_name;
		end if;

		-- generate preparation (this is rather arbitrary)
		IF (_row.id_route = (select id from clin.vacc_route where abbreviation = ''o'')) THEN
			_new_drug_preparation := ''vaccine (oral)'';
		ELSEIF (_row.id_route = (select id from clin.vacc_route where abbreviation = ''i.m.'')) THEN
			_new_drug_preparation := ''vaccine (i.m.)'';
		ELSEIF (_row.id_route = (select id from clin.vacc_route where abbreviation = ''s.c.'')) THEN
			_new_drug_preparation := ''vaccine (s.c.)'';
		ELSE
			_new_drug_preparation := ''vaccine'';
		END IF;

		-- create drug
		insert into ref.branded_drug (
			description,
			preparation,
			is_fake,
			atc_code
		) values (
			_new_drug_name,
			_new_drug_preparation,
			False,
			''J07''
		)
		returning pk
		into _new_drug_pk;

		raise notice ''-> drug: %'', _new_drug_pk::text;

		-- adjust foreign key
		update clin.vaccine set
			fk_brand = _new_drug_pk
		where
			pk = _row.pk;

		-- adjust indications
		perform * from clin.lnk_vaccine2inds where fk_vaccine = _row.pk;
		if FOUND is false then
			insert into clin.lnk_vaccine2inds (
				fk_vaccine,
				fk_indication
			) values (
				_row.pk,
				(SELECT id
				 FROM clin.vacc_indication
				 WHERE
					lower(description) = lower(_row.trade_name)
						OR
					lower(description) = lower(_row.short_name)
				LIMIT 1
				)
			);
		end if;

	end loop;

	return true;
END;';

select tmp_v13_v14_convert_vaccines_to_drugs();

drop function tmp_v13_v14_convert_vaccines_to_drugs() cascade;


-- .trade_name
alter table clin.vaccine
	drop column trade_name cascade;

alter table audit.log_vaccine
	drop column trade_name;


-- .short_name
alter table clin.vaccine
	drop column short_name cascade;

alter table audit.log_vaccine
	drop column short_name;
-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v14-clin-vaccine-static.sql,v $', '$Revision: 1.1 $');
