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
drop function if exists dem.get_person_duplicates(IN _dob timestamp with time zone, IN _lastnames text, IN _firstnames text, IN _gender text, IN _comment text, OUT _existing_identities integer[]) cascade;

create function dem.get_person_duplicates(IN _dob timestamp with time zone, IN _lastnames text, IN _firstnames text, IN _gender text, IN _comment text, OUT _existing_identities integer[])
	language 'plpgsql'
	as '
BEGIN
	SELECT coalesce (
		array_agg(pk_identity),
		ARRAY[]::integer[]
	)
	INTO _existing_identities FROM
		dem.v_person_names d_vpn
			JOIN dem.identity d_i ON (d_i.pk = d_vpn.pk_identity)
	WHERE
		-- same firstname
		lower(d_vpn.firstnames) IS NOT DISTINCT FROM lower(_firstnames)
			AND
		-- same lastname
		lower(d_vpn.lastnames) IS NOT DISTINCT FROM lower(_lastnames)
			AND
		-- same gender
		lower(d_i.gender) IS NOT DISTINCT FROM lower(_gender)
			AND
		-- same dob (day)
		date_trunc(''day'', d_i.dob) IS NOT DISTINCT FROM date_trunc(''day'', _dob)
			AND
		-- same discriminator
		lower(d_i.comment) IS NOT DISTINCT FROM lower(_comment)
	;
END;';

comment on function dem.get_person_duplicates(IN _dob timestamp with time zone, IN _lastnames text, IN _firstnames text, IN _gender text, IN _comment text, OUT _existing_identities integer[]) is
	'Look for persons matching (dob [day level], firstnames [case insensitive], lastnames [case insensitive], gender [case insensitive], comment [case insensitive])';

-- --------------------------------------------------------------
drop function if exists dem.assert_unique_named_identity() cascade;
drop function if exists dem.trf_assert_unique_named_identity() cascade;

-- create function and trigger
create function dem.trf_assert_unique_named_identity()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_identity_row record;
	_names_row record;
	_other_identities integer[];
BEGIN
	-- trigger fired on dem.identity: get corresponding dem.names row
	if TG_TABLE_NAME = ''identity'' then
		_identity_row := NEW;
		select * into _names_row from dem.names where id_identity = NEW.pk;
	-- trigger fired on dem.names: get corresponding dem.identity row
	else
		select * into _identity_row from dem.identity where pk = NEW.id_identity;
		_names_row := NEW;
	end if;

	-- there shall not be any combination of identical
	-- (dob, firstname, lastname, identity.comment)
	-- so, look for clashing rows
	SELECT dem.get_person_duplicates (
		_identity_row.dob,
		_names_row.lastnames,
		_names_row.firstnames,
		_identity_row.gender,
		_identity_row.comment
	) INTO _other_identities;

	-- not needed anymore because we now use a BEFORE trigger
	-- but not the currently updated or inserted row
	--	d_i.pk != _identity_row.pk
	--;

	IF coalesce(array_length(_other_identities, 1), 0) > 0 THEN
		RAISE EXCEPTION
			''[dem.assert_unique_named_identity] % on %.%: More than one person with (firstnames=%), (lastnames=%), (dob=%), (gender=%), (comment=%): % & %'',
				TG_OP,
				TG_TABLE_SCHEMA,
				TG_TABLE_NAME,
				_names_row.firstnames,
				_names_row.lastnames,
				_identity_row.dob,
				_identity_row.gender,
				_identity_row.comment,
				_identity_row.pk,
				_other_identities
			USING ERRCODE = ''unique_violation''
		;
		RETURN NULL;
	END IF;

	return NEW;
END;';

comment on function dem.trf_assert_unique_named_identity() is
	'Ensures unique(identity.dob, names.firstnames, names.lastnames, identity.gender, identity.comment)';

-- --------------------------------------------------------------
-- create trigger on dem.identity
--create constraint trigger tr_ins_upd_d_i_assert_unique_named_identity
create trigger tr_ins_upd_d_i_assert_unique_named_identity
	before insert or update on
		dem.identity
	for
		each row
	execute procedure
		dem.trf_assert_unique_named_identity();

-- create trigger on dem.names
--create constraint trigger tr_ins_upd_d_n_assert_unique_named_identity
create trigger tr_ins_upd_d_n_assert_unique_named_identity
	before insert or update on
		dem.names
	for
		each row
	execute procedure
		dem.trf_assert_unique_named_identity();

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-dem-unique_named_identity.sql', '23.0');
