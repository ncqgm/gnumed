-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

set check_function_bodies to on;

-- --------------------------------------------------------------
-- add an index to dem.address.id_street
\unset ON_ERROR_STOP
drop index idx_dem_address_id_street cascade;
drop index idx_dem_street_id_urb cascade;
drop index idx_dem_urb_id_state cascade;
drop index idx_dem_state_country_code cascade;

alter table dem.urb drop constraint urb_id_state_postcode_name_key cascade;
drop index idx_dem_urb_id_state_postcode_name cascade;

alter table dem.state drop constraint state_code_country_key cascade;
drop index idx_dem_state_code_country cascade;

alter table dem.street drop constraint street_id_urb_name_postcode_key cascade;
drop index idx_dem_street_id_urb_name_postcode cascade;
\set ON_ERROR_STOP 1

create index idx_dem_address_id_street on dem.address(id_street);
create index idx_dem_street_id_urb on dem.street(id_urb);
create index idx_dem_urb_id_state on dem.urb(id_state);
create index idx_dem_state_country_code on dem.state(country);
create unique index idx_dem_urb_id_state_postcode_name on dem.urb(id_state, lower(postcode), lower(name));
create unique index idx_dem_state_code_country on dem.state(lower(code), country);
create unique index idx_dem_street_id_urb_name_postcode on dem.street(id_urb, lower(name), lower(postcode));

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop function dem.address_exists(text, text, text, text, text, text, text) cascade;
\set ON_ERROR_STOP 1


create or replace function dem.address_exists(text, text, text, text, text, text, text)
	returns integer
	language 'plpgsql'
	as '
DECLARE
	_code_country alias for $1;
	_code_state alias for $2;
	_urb alias for $3;
	_postcode alias for $4;
	_street alias for $5;
	_number alias for $6;
	_subunit alias for $7;

	__subunit text;
	_pk_address integer;
	msg text;
BEGIN

	if (_code_country || _code_state || _urb || _postcode || _street || _number) is NULL then
		msg := ''[dem.address_exists]: insufficient or invalid address definition: ''
			|| ''country code <'' || coalesce(_code_country, ''NULL'') || ''>, ''
			|| ''state code <'' || coalesce(_code_state, ''NULL'') || ''>, ''
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
			code_state = trim(_code_state)
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
			code_state = trim(_code_state)
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
	state code,
	urb (location),
	postcode,
	street,
	number,
	subunit (can be NULL)
';

--------------------------------------------------------------
\unset ON_ERROR_STOP
drop function dem.create_address(text, text, text, text, text, text, text);
\set ON_ERROR_STOP 1


create or replace function dem.create_address(text, text, text, text, text, text, text)
	returns integer
	LANGUAGE 'plpgsql'
	AS '
DECLARE
	_number ALIAS FOR $1;
	_street ALIAS FOR $2;
	_postcode ALIAS FOR $3;
	_urb ALIAS FOR $4;
	_state_code ALIAS FOR $5;
	_country_code ALIAS FOR $6;
	_subunit alias for $7;

	_street_id integer;
	_pk_address integer;

	__subunit text;
	msg text;
BEGIN
	select into _pk_address dem.address_exists (
		_country_code,
		_state_code,
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
	-- or else it fails (because state and/or country do not exist)
	select into _street_id dem.create_street(_street, _postcode, _urb, _state_code, _country_code);

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
	state code,
	country code,
	subunit (can be NULL)

If the country or the state do not exist
in the database, the function fails.
';

--------------------------------------------------------------
\unset ON_ERROR_STOP
drop view dem.v_address cascade;
\set ON_ERROR_STOP 1



create view dem.v_address as

select
	adr.id
		as pk_address,
	str.name
		as street,
	coalesce(str.postcode, u.postcode)
		as postcode,
	adr.aux_street
		as notes_street,
	adr.number,
	adr.subunit,
	adr.addendum
		as notes_subunit,
	adr.lat_lon
		as lat_lon_address,
	str.postcode
		as postcode_street,
	str.lat_lon
		as lat_lon_street,
	str.suburb,
	u.name
		as urb,
	u.postcode
		as postcode_urb,
	u.lat_lon
		as lat_lon_urb,
	dst.code
		as code_state,
	dst.name
		as state,
	_(dst.name)
		as l10n_state,
	dst.country
		as code_country,
	c.name
		as country,
	_(c.name)
		as l10n_country,
	c.deprecated
		as country_deprecated,
	adr.id_street
		as pk_street,
	u.id
		as pk_urb,
	dst.id
		as pk_state,
	adr.xmin
		as xmin_address
from
	dem.address adr
		left join dem.street str on (adr.id_street = str.id)
			left join dem.urb u on (str.id_urb = u.id)
				left join dem.state dst on (u.id_state = dst.id)
					left join dem.country c on (c.code = dst.country)

--		left join dem.v_street vstr on (adr.id_street = vstr.pk_street)
;



comment on view dem.v_address is 'fully denormalizes data about addresses as entities in themselves';



grant select on dem.v_address to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-dem-v_address.sql', 'v16');

-- ==============================================================
