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
comment on column dem.identity.comment is
	'A free-text comment on this identity.\n
\n
Can be used to to discriminate patients which are otherwise\n
identical regarding name and date of birth.\n
Should be something non-ephemereal and unique to the person\n
itself across time, place and database instance.\n
Good: place of birth\n
Good: maiden name of mother\n
Good: mother of <name>\n
Good: hash of DNA\n
Good (?): hair color of first pet\n
Bad: current address (will change)\n
Bad: primary provider in this praxis (can change, invalid in another GNUmed instance)\n
Bad: nickname (will change, can dupe as well)\n
Bad: favourite food\n
not-quite-so-bad: occupation';

-- --------------------------------------------------------------
drop function if exists dem.new_pupic() cascade;

-- --------------------------------------------------------------
drop function if exists dem.trf_sane_identity_comment() cascade;

-- disable audit trigger for update (because table layout has changed)
alter table dem.identity
	disable trigger zt_upd_identity;

-- de-duplicate
update dem.identity set
	comment = coalesce(comment, '') || '[auto-set by <v21-dem-identity-dynamic.sql>: ' || clock_timestamp() || ']'
where
	pk in (
		select pk_identity
		from dem.v_persons d_vp1
		where exists (
			select 1 from dem.v_persons d_vp2
			where
				d_vp2.firstnames = d_vp1.firstnames
					and
				d_vp2.lastnames = d_vp1.lastnames
					and
				d_vp2.gender = d_vp1.gender
					and
				date_trunc('day', d_vp2.dob) = date_trunc('day', d_vp1.dob)
					and
				d_vp2.pk_identity != d_vp1.pk_identity
		)
	)
;


-- create function and trigger
create function clin.trf_sane_identity_comment()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_identity_row record;
	_names_row record;
BEGIN
	if TG_TABLE_NAME = ''identity'' then
		if TG_OP = ''UPDATE'' then
			if NEW.comment IS NOT DISTINCT FROM OLD.comment then
				return NEW;
			end if;
		end if;
		_identity_row := NEW;
		select * into _names_row from dem.names where id_identity = NEW.pk;
	else
		select * into _identity_row from dem.identity where pk = NEW.id_identity;
		_names_row := NEW;
	end if;

	-- any row with
	PERFORM 1 FROM
		dem.v_all_persons
	WHERE
		-- same firstname
		firstnames = _names_row.firstnames
			and
		-- same lastname
		lastnames = _names_row.lastnames
			and
		-- same gender
		gender is not distinct from _identity_row.gender
			and
		-- same dob (day)
		dob_only is not distinct from _identity_row.dob
			and
		-- same discriminator
		comment is not distinct from _identity_row.comment
			and
		-- but not the currently updated or inserted row
		pk_identity != _identity_row.pk
	;
	if FOUND then
		RAISE EXCEPTION
			''% on %.%: More than one person with (firstnames=%), (lastnames=%), (dob=%), (comment=%)'',
				TG_OP,
				TG_TABLE_SCHEMA,
				TG_TABLE_NAME,
				_names_row.firstnames,
				_names_row.lastnames,
				_identity_row.dob,
				_identity_row.comment
			USING ERRCODE = ''unique_violation''
		;
		RETURN NULL;
	end if;

	return NEW;
END;';

comment on function clin.trf_sane_identity_comment() is
	'Ensures unique(identity.dob, names.firstnames, names.lastnames, identity.comment)';


create trigger tr_sane_identity_comment
	after insert or update on dem.identity
	for each row execute procedure clin.trf_sane_identity_comment();


create trigger tr_sane_identity_comment
	after insert or update on dem.names
	for each row execute procedure clin.trf_sane_identity_comment();


-- tob nullable
-- dob = (dyob + coalesce(tob, 11:11:11.111)) at client_timezone

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-dem-identity-dynamic.sql', '21.0');
