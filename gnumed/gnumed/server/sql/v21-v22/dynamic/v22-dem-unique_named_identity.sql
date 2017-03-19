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
drop function if exists dem.trf_sane_identity_comment() cascade;
drop function if exists dem.assert_unique_named_identity() cascade;


-- create function and trigger
create function dem.assert_unique_named_identity()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_identity_row record;
	_names_row record;
	_other_identities integer[];
BEGIN
	-- working on dem.identity
	if TG_TABLE_NAME = ''identity'' then
		_identity_row := NEW;
		select * into _names_row from dem.names where id_identity = NEW.pk;
	-- working on dem.names
	else
		select * into _identity_row from dem.identity where pk = NEW.id_identity;
		_names_row := NEW;
	end if;

	-- there cannot be any combination of identical
	-- (dob, firstname, lastname, identity.comment)
	-- so, look for clashing rows
	SELECT array_agg(pk_identity) INTO _other_identities FROM
		dem.v_person_names d_vpn
			join dem.identity d_i on (d_i.pk = d_vpn.pk_identity)
	WHERE
		-- same firstname
		d_vpn.firstnames = _names_row.firstnames
			AND
		-- same lastname
		d_vpn.lastnames = _names_row.lastnames
			AND
		-- same gender
		d_i.gender is not distinct from _identity_row.gender
			AND
		-- same dob (day)
		date_trunc(''day'', d_i.dob) is not distinct from date_trunc(''day'', _identity_row.dob)
			AND
		-- same discriminator
		d_i.comment is not distinct from _identity_row.comment
			AND
		-- but not the currently updated or inserted row
		d_i.pk != _identity_row.pk
	;

	if coalesce(array_length(_other_identities, 1), 0) > 0 then
		RAISE EXCEPTION
			''[dem.assert_unique_named_identity] % on %.%: More than one person with (firstnames=%), (lastnames=%), (dob=%), (comment=%): % & %'',
				TG_OP,
				TG_TABLE_SCHEMA,
				TG_TABLE_NAME,
				_names_row.firstnames,
				_names_row.lastnames,
				_identity_row.dob,
				_identity_row.comment,
				_identity_row.pk,
				_other_identities
			USING ERRCODE = ''unique_violation''
		;
		RETURN NULL;
	end if;

	return NEW;
END;';


comment on function dem.assert_unique_named_identity() is
	'Ensures unique(identity.dob, names.firstnames, names.lastnames, identity.comment)';


-- attach to dem.identity
create constraint trigger tr_ins_d_i_assert_unique_named_identity
	after insert on
		dem.identity
	deferrable
		initially deferred
	for
		each row
	execute procedure
		dem.assert_unique_named_identity();

create constraint trigger tr_upd_d_i_assert_unique_named_identity
	after update on
		dem.identity
	deferrable
		initially deferred
	for
		each row
	when
		(NEW.comment IS DISTINCT FROM OLD.comment)
	execute procedure
		dem.assert_unique_named_identity();


-- attach to dem.names
create constraint trigger tr_d_n_assert_unique_named_identity
	after insert or update on
		dem.names
	deferrable
		initially deferred
	for
		each row
	execute procedure
		dem.assert_unique_named_identity();

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-dem-unique_named_identity.sql', '22.0');
