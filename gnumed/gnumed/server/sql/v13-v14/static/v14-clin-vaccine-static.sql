-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- .fk_brand
alter table clin.vaccine
	add column fk_brand integer;

alter table audit.log_vaccine
	add column fk_brand integer;


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
