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
drop function if exists clin.trf_sane_identity_comment() cascade;
drop function if exists dem.trf_sane_identity_comment() cascade;


-- create function and trigger
create function dem.trf_sane_identity_comment()
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
		-- UPDATEs ...
		if TG_OP = ''UPDATE'' then
			-- ... which do NOT change .comment ...
			if NEW.comment IS NOT DISTINCT FROM OLD.comment then
				-- ... are safe because they were successfully INSERTed before
				return NEW;
			end if;
		end if;
		-- but INSERTs need checking
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
			''% on %.%: More than one person with (firstnames=%), (lastnames=%), (dob=%), (comment=%): % & %'',
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


comment on function dem.trf_sane_identity_comment() is
	'Ensures unique(identity.dob, names.firstnames, names.lastnames, identity.comment)';


create trigger tr_sane_identity_comment
	after insert or update on dem.identity
	for each row execute procedure dem.trf_sane_identity_comment();


create trigger tr_sane_identity_comment
	after insert or update on dem.names
	for each row execute procedure dem.trf_sane_identity_comment();

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-dem-identity-fixup.sql', '21.12');
