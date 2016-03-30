-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

set check_function_bodies to on;

-- --------------------------------------------------------------
delete from audit.audited_tables where schema = 'dem' and table_name = 'state';

select audit.add_table_for_audit('dem', 'region');

drop function if exists audit.ft_ins_state() cascade;
drop function if exists audit.ft_upd_state() cascade;
drop function if exists audit.ft_del_state() cascade;

COMMENT on table dem.region is
	'region codes (country specific);
	 Richard agreed we should require pre-existence,
	 allow user to mail details for adding a state to developers';
COMMENT on column dem.region.code is
	'region code';

-- --------------------------------------------------------------
alter table dem.urb drop constraint if exists fk_dem_urb_dem_region_pk cascade;
-- remnants of old
alter table dem.urb drop constraint if exists "$1" cascade ;


alter table dem.urb
	add constraint fk_dem_urb_dem_region_pk
		foreign key (fk_region)
		references dem.region(pk)
		on update cascade
		on delete restrict
;

alter table dem.urb
	drop constraint if exists urb_id_state_fkey cascade
;

COMMENT on column dem.urb.fk_region IS
	'reference to information about country and region';

-- --------------------------------------------------------------
COMMENT on column dem.street.id_urb IS
	'reference to information postcode, city, country and region';

-- --------------------------------------------------------------
drop function if exists dem.gm_upd_default_states() cascade;

create or replace function dem.gm_upd_default_regions()
	returns boolean
	language 'plpgsql'
	as '
declare
	_region_code text;
	_region_name text;
	_country_row record;
begin
	_region_code := ''??'';
	_region_name := ''state/territory/province/region not available'';

	-- add default region to countries needing one
	for _country_row in
		select distinct code from dem.country
		where code not in (
			select country from dem.region where code = _region_code
		)
	loop
		raise notice ''adding default region for [%]'', _country_row.code;
		execute ''insert into dem.region (code, country, name) values (''
				|| quote_literal(_region_code) || '', ''
				|| quote_literal(_country_row.code) || '', ''
				|| quote_literal(_region_name) || '');'';
	end loop;
	return true;
end;
';

select dem.gm_upd_default_regions();

-- --------------------------------------------------------------
DROP function if exists dem.create_urb(text, text, text, text);


CREATE function dem.create_urb(text, text, text, text)
	RETURNS integer
	AS '
DECLARE
	_urb ALIAS FOR $1;
	_urb_postcode ALIAS FOR $2;	
	_region_code ALIAS FOR $3;
	_country_code ALIAS FOR $4;

 	_region_pk integer;
	_urb_id integer;

	msg text;
BEGIN
 	-- get region
 	SELECT INTO _region_pk d_r.pk from dem.region d_r WHERE d_r.code = _region_code and d_r.country = _country_code;
 	IF NOT FOUND THEN
		msg := ''combination of region + country not registered [''
			||   ''country:'' || coalesce(_country_code, ''NULL'')
			||  '', region:'' || coalesce(_region_code, ''NULL'')
			||     '', urb:'' || coalesce(_urb, ''NULL'')
			|| '', urb_zip:'' || coalesce(_urb_postcode, ''NULL'')
			|| '']'';
		RAISE EXCEPTION ''=> %'', msg;
 	END IF;
	-- get/create and return urb
	SELECT INTO _urb_id u.id from dem.urb u WHERE u.name ILIKE _urb AND u.fk_region = _region_pk;
	IF FOUND THEN
		RETURN _urb_id;
	END IF;
	INSERT INTO dem.urb (name, postcode, fk_region) VALUES (_urb, _urb_postcode, _region_pk);
	RETURN currval(''dem.urb_id_seq'');
END;' LANGUAGE 'plpgsql';


COMMENT ON function dem.create_urb(text, text, text, text) IS
	'This function takes a parameters the name of the urb,\n
	the postcode of the urb, the name of the region and the\n
	name of the country.\n
	If the country or the region does not exists in the tables,\n
	the function fails.\n
	At first, the urb is tried to be retrieved according to the\n
	supplied information. If the fields do not match exactly an\n
	existing row, a new urb is created and returned.';

-- --------------------------------------------------------------
drop function if exists dem.address_exists(text, text, text, text, text, text, text) cascade;


create or replace function dem.address_exists(text, text, text, text, text, text, text)
	returns integer
	language 'plpgsql'
	as '
DECLARE
	_code_country alias for $1;
	_code_region alias for $2;
	_urb alias for $3;
	_postcode alias for $4;
	_street alias for $5;
	_number alias for $6;
	_subunit alias for $7;

	__subunit text;
	_pk_address integer;
	msg text;
BEGIN

	if (_code_country || _code_region || _urb || _postcode || _street || _number) is NULL then
		msg := ''[dem.address_exists]: insufficient or invalid address definition: ''
			|| ''country code <'' || coalesce(_code_country, ''NULL'') || ''>, ''
			|| ''region code <'' || coalesce(_code_region, ''NULL'') || ''>, ''
			|| ''urb <'' || coalesce(_urb, ''NULL'') || ''>, ''
			|| ''zip <'' || coalesce(_postcode, ''NULL'') || ''>, ''
			|| ''street <'' || coalesce(_street, ''NULL'') || ''>, ''
			|| ''number <'' || coalesce(_number, ''NULL'') || ''>''
		;
		raise exception ''%'', msg;
	end if;

	__subunit := nullif(trim(_subunit), '''');

	if __subunit is null then
		select
			pk_address into _pk_address
		from
			dem.v_address
		where
			code_country = trim(_code_country)
				and
			code_region = trim(_code_region)
				and
			urb = trim(_urb)
				and
			postcode = trim(_postcode)
				and
			street = trim(_street)
				and
			number = trim(_number)
				and
			subunit is null;
	else
		select
			pk_address into _pk_address
		from
			dem.v_address
		where
			code_country = trim(_code_country)
				and
			code_region = trim(_code_region)
				and
			urb = trim(_urb)
				and
			postcode = trim(_postcode)
				and
			street = trim(_street)
				and
			number = trim(_number)
				and
			subunit = __subunit;
	end if;

	return _pk_address;
END;';


comment on function dem.address_exists(text, text, text, text, text, text, text) is
E'This function checks whether a given address exists in
the database and returns the primary key if found.

It takes the following parameters:

	country code,
	region code,
	urb (location),
	postcode,
	street,
	number,
	subunit (can be NULL)
';

--------------------------------------------------------------
drop function if exists dem.create_address(text, text, text, text, text, text, text);


create or replace function dem.create_address(text, text, text, text, text, text, text)
	returns integer
	LANGUAGE 'plpgsql'
	AS '
DECLARE
	_number ALIAS FOR $1;
	_street ALIAS FOR $2;
	_postcode ALIAS FOR $3;
	_urb ALIAS FOR $4;
	_region_code ALIAS FOR $5;
	_country_code ALIAS FOR $6;
	_subunit alias for $7;

	_street_id integer;
	_pk_address integer;

	__subunit text;
	msg text;
BEGIN
	select into _pk_address dem.address_exists (
		_country_code,
		_region_code,
		_urb,
		_postcode,
		_street,
		_number,
		_subunit
	);

	if _pk_address is not null then
		return _pk_address;
	end if;

	-- this either creates dem.street and possible dem.urb rows or
	-- or else it fails (because region and/or country do not exist)
	select into _street_id dem.create_street(_street, _postcode, _urb, _region_code, _country_code);

	-- create address
	__subunit := nullif(trim(_subunit), '''');
	insert into dem.address (
		number,
		id_street,
		subunit
	) values (
		_number,
		_street_id,
		__subunit
	)
	returning id
	into _pk_address;

	return _pk_address;
END;';


comment on function dem.create_address(text, text, text, text, text, text, text) is
E'This function creates an address. It first
checks whether the address already exists.

It takes the following parameters:

	number,
	street,
	postcode,
	urb (location),
	region code,
	country code,
	subunit (can be NULL)

If the country or the region do not exist
in the database, the function fails.
';

-- --------------------------------------------------------------
drop view if exists dem.v_state cascade;
drop view if exists dem.v_region cascade;


create view dem.v_region as
select
	d_r.pk as pk_region,
	d_r.code as code_region,
	d_r.name as region,
	_(d_r.name) as l10n_region,
	d_r.country as code_country,
	c.name as country,
	_(c.name) as l10n_country,
	c.deprecated as country_deprecated,
	d_r.xmin as xmin_region
from
	dem.region as d_r
		left join dem.country c on (d_r.country = c.code)
;


comment on view dem.v_region is 'denormalizes region information';


grant select on dem.v_region to group "gm-public";

-- --------------------------------------------------------------
drop view if exists dem.v_urb cascade;


create view dem.v_urb as
select
	d_u.id as pk_urb,
	d_u.name as urb,
	d_u.postcode as postcode_urb,
	d_u.lat_lon as lat_lon_urb,
	d_vr.code_region,
	d_vr.region,
	d_vr.l10n_region,
	d_vr.code_country,
	d_vr.country,
	d_vr.l10n_country,
	d_vr.country_deprecated,
	d_u.fk_region as pk_region,
	d_u.xmin as xmin_urb
from
	dem.urb d_u
		left join dem.v_region as d_vr on (d_vr.pk_region = d_u.fk_region)
;


comment on view dem.v_urb is 'denormalizes urb data';


grant select on dem.v_urb to group "gm-public";

-- --------------------------------------------------------------
drop view if exists dem.v_street cascade;


create view dem.v_street as
select
	d_st.id as pk_street,
	d_st.name as street,
	coalesce(d_st.postcode, d_vu.postcode_urb) as postcode,
	d_st.postcode as postcode_street,
	d_st.lat_lon as lat_lon_street,
	d_st.suburb as suburb,
	d_vu.urb,
	d_vu.postcode_urb,
	d_vu.lat_lon_urb,
	d_vu.code_region,
	d_vu.region,
	d_vu.l10n_region,
	d_vu.code_country,
	d_vu.country,
	d_vu.l10n_country,
	d_vu.country_deprecated,
	d_st.id_urb as pk_urb,
	d_vu.pk_region,
	d_st.xmin as xmin_street
from
	dem.street d_st
		left join dem.v_urb d_vu on (d_st.id_urb = d_vu.pk_urb)
;


comment on view dem.v_street is 'denormalizes street data';


grant select on dem.v_street to group "gm-public";

-- ------------------------------------------------------------
drop view if exists dem.v_address cascade;


create view dem.v_address as
select
	d_adr.id
		as pk_address,
	d_str.name
		as street,
	coalesce(d_str.postcode, d_u.postcode)
		as postcode,
	d_adr.aux_street
		as notes_street,
	d_adr.number,
	d_adr.subunit,
	d_adr.addendum
		as notes_subunit,
	d_adr.lat_lon
		as lat_lon_address,
	d_str.postcode
		as postcode_street,
	d_str.lat_lon
		as lat_lon_street,
	d_str.suburb,
	d_u.name
		as urb,
	d_u.postcode
		as postcode_urb,
	d_u.lat_lon
		as lat_lon_urb,
	d_r.code
		as code_region,
	d_r.name
		as region,
	_(d_r.name)
		as l10n_region,
	d_r.country
		as code_country,
	d_c.name
		as country,
	_(d_c.name)
		as l10n_country,
	d_c.deprecated
		as country_deprecated,
	d_adr.id_street
		as pk_street,
	d_u.id
		as pk_urb,
	d_r.pk
		as pk_region,
	d_adr.xmin
		as xmin_address
from
	dem.address d_adr
		left join dem.street d_str on (d_adr.id_street = d_str.id)
			left join dem.urb d_u on (d_str.id_urb = d_u.id)
				left join dem.region d_r on (d_u.fk_region = d_r.pk)
					left join dem.country d_c on (d_c.code = d_r.country)
;


comment on view dem.v_address is 'fully denormalizes data about addresses as entities in themselves';


grant select on dem.v_address to group "gm-public";

-- --------------------------------------------------------------
drop view if exists dem.v_zip2street cascade;

create view dem.v_zip2street as
	select
		coalesce (d_str.postcode, d_u.postcode) as postcode,
		d_str.name as street,
		d_str.suburb as suburb,
		d_r.name as region,
		d_r.code as code_region,
		d_u.name as urb,
		d_c.name as country,
		_(d_c.name) as l10n_country,
		d_r.country as code_country
	from
		dem.street d_str,
		dem.urb d_u,
		dem.region d_r,
		dem.country d_c
	where
		d_str.postcode is not null
			and
		d_str.id_urb = d_u.id
			and
		d_u.fk_region = d_r.pk
			and
		d_r.country = d_c.code
;

comment on view dem.v_zip2street is
	'list known data for streets that have a zip code';

grant select on dem.v_zip2street to group "gm-public";

-- --------------------------------------------------------------
drop view if exists dem.v_uniq_zipped_urbs cascade;

create view dem.v_uniq_zipped_urbs as
	-- all the cities that
	select
		d_u.postcode as postcode,
		d_u.name as name,
		d_r.name as region,
		d_r.code as code_region,
		d_c.name as country,
		_(d_c.name) as l10n_country,
		d_r.country as code_country
	from
		dem.urb d_u,
		dem.region d_r,
		dem.country d_c
	where
		-- have a zip code
		d_u.postcode is not null
			and
		-- are not found in "street" with this zip code
		not exists (
			select 1 from
				dem.v_zip2street d_vz2str
			where
				d_vz2str.postcode = d_u.postcode
					and
				d_vz2str.urb = d_u.name
			) and
		d_u.fk_region = d_r.pk
			and
		d_r.country = d_c.code
;

comment on view dem.v_uniq_zipped_urbs is
	'convenience view that selects urbs which:
	 - have a zip code
	 - are not referenced in table "street" with that zip code';

grant select on dem.v_uniq_zipped_urbs to group "gm-public";

-- --------------------------------------------------------------
drop view if exists dem.v_zip2data;

create view dem.v_zip2data as
	select
		d_vz2s.postcode as zip,
		d_vz2s.street,
		d_vz2s.suburb,
		d_vz2s.urb,
		d_vz2s.region,
		d_vz2s.code_region,
		d_vz2s.country,
		d_vz2s.l10n_country,
		d_vz2s.code_country
	from dem.v_zip2street d_vz2s
		union
	select
		d_vuzu.postcode as zip,
		null as street,
		null as suburb,
		d_vuzu.name as urb,
		d_vuzu.region,
		d_vuzu.code_region,
		d_vuzu.country,
		d_vuzu.l10n_country,
		d_vuzu.code_country
	from
		dem.v_uniq_zipped_urbs d_vuzu
;

comment on view dem.v_zip2data is
	'aggregates nearly all known data per zip code';

grant select on dem.v_zip2data to group "gm-public";

-- --------------------------------------------------------------
drop view if exists dem.v_zip2urb cascade;

create view dem.v_zip2urb as
	select
		d_u.postcode as postcode,
		d_u.name as urb,
		d_r.name as region,
		d_r.code as code_region,
		_(d_c.name) as country,
		d_r.country as code_country
	from
		dem.urb d_u,
		dem.region d_r,
		dem.country d_c
	where
		d_u.postcode is not null
			and
		d_u.fk_region = d_r.pk
			and
		d_r.country = d_c.code
;

comment on view dem.v_zip2urb is
	'list known data for urbs that have a zip code';

grant select on dem.v_zip2urb to group "gm-public";

-- --------------------------------------------------------------
drop view if exists dem.v_basic_address cascade;

create view dem.v_basic_address as
select
	d_adr.id as id,
	d_r.country as country_code,
	d_r.code as region_code,
	d_r.name as region,
	d_c.name as country,
	coalesce (d_str.postcode, d_u.postcode) as postcode,
	d_u.name as urb,
	d_adr.number as number,
	d_str.name as street,
	d_adr.addendum as addendum,
	coalesce (d_adr.lat_lon, d_str.lat_lon, d_u.lat_lon) as lat_lon
from
	dem.address d_adr,
	dem.region d_r,
	dem.country d_c,
	dem.urb d_u,
	dem.street d_str
where
	d_r.country = d_c.code
		and
	d_adr.id_street = d_str.id
		and
	d_str.id_urb = d_u.id
		and
	d_u.fk_region = d_r.pk;

grant select on dem.v_basic_address to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-dem-region-dynamic.sql', '21.3');
