-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

set check_function_bodies to on;

--set default_transaction_read_only to off;

-- --------------------------------------------------------------
comment on table ref.provider is
	'This table lists all sorts of medical providers';


revoke all on ref.provider from public;
grant select on ref.provider to "gm-public";
grant insert, update, delete on ref.provider to "gm-staff";
grant usage on ref.provider_pk_seq to "gm-public";

-- --------------------------------------------------------------
-- .fk_identity
comment on column ref.provider.fk_identity is 'the person which represents this provider';

alter table ref.provider drop constraint if exists FK_ref_provider_fk_identity cascade;

alter table ref.provider
	add constraint FK_ref_provider_fk_identity foreign key (fk_identity)
		references dem.identity(pk)
		on update cascade
		on delete restrict
;

alter table ref.provider
	alter column fk_identity
		set not null
;

-- --------------------------------------------------------------
-- .fk_speciality
comment on column ref.provider.fk_speciality is 'the speciality/field of work for this provider';

alter table ref.provider drop constraint if exists FK_ref_provider_fk_speciality cascade;

alter table ref.provider
	add constraint FK_ref_provider_fk_speciality foreign key (fk_speciality)
		references ref.provider_speciality(pk)
		on update cascade
		on delete restrict
;

alter table ref.provider
	alter column fk_speciality
		set not null
;

-- --------------------------------------------------------------
-- table constraints
alter table ref.provider drop constraint if exists ref_provider_uniq_prov_spec cascade;

alter table ref.provider
	add constraint ref_provider_uniq_prov_spec
		unique(fk_identity, fk_speciality)
;

-- --------------------------------------------------------------
comment on table ref.provider_speciality is
	'This table lists all sorts of specialities of providers, "surgeon", "surgery", "physical therapy", "podiatrist", "optometrician", ...';


revoke all on ref.provider_speciality from public;
grant select on ref.provider_speciality to "gm-public";
grant insert, update, delete on ref.provider_speciality to "gm-staff";
grant usage on ref.provider_speciality_pk_seq to "gm-public";

-- --------------------------------------------------------------
-- .description
comment on column ref.provider_speciality.description is 'a speciality/field of work';


alter table ref.provider_speciality drop constraint if exists ref_provider_speciality_uniq_desc cascade;

alter table ref.provider_speciality
	add constraint ref_provider_speciality_uniq_desc
		unique(description)
;


alter table ref.provider_speciality drop constraint if exists ref_provider_speciality_sane_desc cascade;

alter table ref.provider_speciality
	add constraint ref_provider_speciality_sane_desc
		check(gm.is_null_or_blank_string(description) is false)
;

-- --------------------------------------------------------------
-- .icpcs
comment on column ref.provider_speciality.icpcs is 'a list of ICPC codes pertinent to this speciality if appropriate';


create or replace function gm.is_onedimensional_gapless_array(anyarray)
	returns boolean
	language 'plpgsql'
	as '
declare
	_array2test alias for $1;
	_val text;
begin
	if array_ndims(_array2test) <> 1 then
		raise notice ''gm.is_onedimensional_gapless_array(): array is not one-dimensional'' using ERRCODE = ''check_violation'';
		return false;
	end if;

	foreach _val in array _array2test loop
		if _val IS NULL then
			raise notice ''gm.is_onedimensional_gapless_array(): array contains NULL(s)'' using ERRCODE = ''check_violation'';
			return false;
		end if;
	end loop;

	return true;
end;';

comment on function gm.is_onedimensional_gapless_array(anyarray) is
	'checks whether a given array is one-dimensional and does not contain any NULLs';


create or replace function gm.is_textarray_without_blanks(text[])
	returns boolean
	language 'plpgsql'
	as '
declare
	_array2test alias for $1;
	_val text;
begin
	-- assumes is one-dimensional and gapless (no nulls)
	foreach _val in array _array2test loop
		if btrim(_val) = '''' then
			raise notice ''gm.is_textarray_without_blanks(): array contains empty strings'' using ERRCODE = ''check_violation'';
			return false;
		end if;
	end loop;

	return true;
end;';


alter table ref.provider_speciality drop constraint if exists ref_provider_speciality_sane_ICPCs cascade;

alter table ref.provider_speciality
	add constraint ref_provider_speciality_sane_ICPCs
		check (
			(icpcs is NULL)
				or
			(
				(gm.is_onedimensional_gapless_array(icpcs))
					AND
				(gm.is_textarray_without_blanks(icpcs))
			)
		)
;

-- --------------------------------------------------------------
drop view if exists ref.v_providers cascade;

create view ref.v_providers as

select
	r_p.pk
		as pk_provider,
	r_p.fk_identity
		as pk_identity,
	r_ps.description
		as speciality,
	_(r_ps.description)
		as l10n_speciality,
	d_i.title
		as title,
	d_n.firstnames
		as firstnames,
	d_n.lastnames
		as lastnames,
	d_i.dob
		as dob,
	d_i.gender
		as gender,
	r_p.fk_speciality
		as pk_speciality,
	d_n.id
		as pk_name
from
	ref.provider r_p
		inner join ref.provider_speciality r_ps on (r_p.fk_speciality = r_ps.pk)
			left join dem.identity d_i on (r_p.fk_identity = d_i.pk)
				left join dem.names d_n on (r_p.fk_identity = d_n.id_identity)
where
	d_n.active is true
;

-- --------------------------------------------------------------
-- .sample data
insert into ref.provider_speciality (description) select i18n.i18n('GP') where not exists (select 1 from ref.provider_speciality where description = 'GP');
insert into ref.provider_speciality (description) select i18n.i18n('FP') where not exists (select 1 from ref.provider_speciality where description = 'FP');
insert into ref.provider_speciality (description) select i18n.i18n('PC') where not exists (select 1 from ref.provider_speciality where description = 'PC');
insert into ref.provider_speciality (description) select i18n.i18n('Primary Care') where not exists (select 1 from ref.provider_speciality where description = 'Primary Care');
insert into ref.provider_speciality (description) select i18n.i18n('PT') where not exists (select 1 from ref.provider_speciality where description = 'PT');
insert into ref.provider_speciality (description) select i18n.i18n('physiotherapy') where not exists (select 1 from ref.provider_speciality where description = 'physiotherapy');
insert into ref.provider_speciality (description) select i18n.i18n('physical therapy') where not exists (select 1 from ref.provider_speciality where description = 'physical therapy');
insert into ref.provider_speciality (description) select i18n.i18n('infectious diseases') where not exists (select 1 from ref.provider_speciality where description = 'infectious diseases');
insert into ref.provider_speciality (description) select i18n.i18n('psychology') where not exists (select 1 from ref.provider_speciality where description = 'psychology');
insert into ref.provider_speciality (description) select i18n.i18n('radiology') where not exists (select 1 from ref.provider_speciality where description = 'radiology');
insert into ref.provider_speciality (description) select i18n.i18n('neurology') where not exists (select 1 from ref.provider_speciality where description = 'neurology');
insert into ref.provider_speciality (description) select i18n.i18n('optometrician') where not exists (select 1 from ref.provider_speciality where description = 'optometrician');
insert into ref.provider_speciality (description) select i18n.i18n('pediatrician') where not exists (select 1 from ref.provider_speciality where description = 'pediatrician');
insert into ref.provider_speciality (description) select i18n.i18n('midwife') where not exists (select 1 from ref.provider_speciality where description = 'midwife');
insert into ref.provider_speciality (description) select i18n.i18n('obstetrics') where not exists (select 1 from ref.provider_speciality where description = 'obstetrics');
insert into ref.provider_speciality (description) select i18n.i18n('OBS') where not exists (select 1 from ref.provider_speciality where description = 'OBS');
insert into ref.provider_speciality (description) select i18n.i18n('gynecology') where not exists (select 1 from ref.provider_speciality where description = 'gynecology');
insert into ref.provider_speciality (description) select i18n.i18n('GYNE') where not exists (select 1 from ref.provider_speciality where description = 'GYNE');
insert into ref.provider_speciality (description) select i18n.i18n('OBS/GYNE') where not exists (select 1 from ref.provider_speciality where description = 'OBS/GYNE');
insert into ref.provider_speciality (description) select i18n.i18n('ENT') where not exists (select 1 from ref.provider_speciality where description = 'ENT');
insert into ref.provider_speciality (description) select i18n.i18n('orthopedics') where not exists (select 1 from ref.provider_speciality where description = 'orthopedics');
insert into ref.provider_speciality (description) select i18n.i18n('opthalmology') where not exists (select 1 from ref.provider_speciality where description = 'opthalmology');
insert into ref.provider_speciality (description) select i18n.i18n('cardiology') where not exists (select 1 from ref.provider_speciality where description = 'cardiology');
insert into ref.provider_speciality (description) select i18n.i18n('surgery') where not exists (select 1 from ref.provider_speciality where description = 'surgery');
insert into ref.provider_speciality (description) select i18n.i18n('internal medicine') where not exists (select 1 from ref.provider_speciality where description = 'internal medicine');


delete from ref.provider where
	fk_identity = (
		select pk_identity from dem.v_persons where firstnames = 'Leonard Horatio' and lastnames = 'McCoy'
	)
;

insert into ref.provider (
	fk_identity,
	fk_speciality
) values
	(
		(select pk_identity from dem.v_persons where firstnames = 'Leonard Horatio' and lastnames = 'McCoy'),
		(select pk from ref.provider_speciality where description = 'psychology')
	),
	(
		(select pk_identity from dem.v_persons where firstnames = 'Leonard Horatio' and lastnames = 'McCoy'),
		(select pk from ref.provider_speciality where description = 'surgery')
	),
	(
		(select pk_identity from dem.v_persons where firstnames = 'Leonard Horatio' and lastnames = 'McCoy'),
		(select pk from ref.provider_speciality where description = 'internal medicine')
	),
	(
		(select pk_identity from dem.v_persons where firstnames = 'Leonard Horatio' and lastnames = 'McCoy'),
		(select pk from ref.provider_speciality where description = 'infectious diseases')
	)
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-ref-provider-dynamic.sql', '20.0');
