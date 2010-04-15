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
BEGIN
	for _row in select * from clin.vaccine loop

		raise notice ''vaccine: %'', _row.pk::text;

		-- create drug
		case
			when _row.id_route = (select id from clin.vacc_route where abbreviation = ''o'') then
				insert into ref.branded_drug (
					description,
					preparation,
					is_fake,
					atc_code
					--, fk_data_source
					--, external_code
					--, external_code_type
				) values (
					_row.trade_name || '' ('' || _row.short_name || '')'',
					''oral vaccine'',			-- this is rather arbitrary
					False,
					''J07''
				)
				returning pk
				into _new_drug_pk;

			when _row.id_route = (select id from clin.vacc_route where abbreviation = ''i.m.'') then
				insert into ref.branded_drug (
					description,
					preparation,
					is_fake,
					atc_code
					--, fk_data_source
					--, external_code
					--, external_code_type
				) values (
					_row.trade_name || '' ('' || _row.short_name || '')'',
					''injection (i.m.)'',		-- this is rather arbitrary
					False,
					''J07''
				)
				returning pk
				into _new_drug_pk;

			when _row.id_route = (select id from clin.vacc_route where abbreviation = ''s.c.'') then
				insert into ref.branded_drug (
					description,
					preparation,
					is_fake,
					atc_code
					--, fk_data_source
					--, external_code
					--, external_code_type
				) values (
					_row.trade_name || '' ('' || _row.short_name || '')'',
					''injection (s.c.)'',		-- this is rather arbitrary
					False,
					''J07''
				)
				returning pk
				into _new_drug_pk;

			else
				insert into ref.branded_drug (
					description,
					preparation,
					is_fake,
					atc_code
					--, fk_data_source
					--, external_code
					--, external_code_type
				) values (
					_row.trade_name || '' ('' || _row.short_name || '')'',
					''vaccine'',				-- this is rather arbitrary
					False,
					''J07''
				)
				returning pk
				into _new_drug_pk;

		end case;

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
