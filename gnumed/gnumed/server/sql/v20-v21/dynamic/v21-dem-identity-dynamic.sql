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
-- .duplicates_discriminator
comment on column dem.identity.duplicates_discriminator is
	'A value to discriminate patients which are otherwise\n
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


alter table dem.identity
	drop constraint if exists dem_identity_sane_duplicates_discriminator cascade;

alter table dem.identity
	add constraint dem_identity_sane_duplicates_discriminator check (
		gm.is_null_or_non_empty_string(duplicates_discriminator)
	);

-- --------------------------------------------------------------
drop function if exists dem.trf_sane_identity_duplicates_discriminator() cascade;

-- test inserts to be converted later
insert into dem.identity (dob, gender) values ('1931-03-21', 'm');
insert into dem.names (id_identity, firstnames, lastnames, comment) values (currval(pg_get_serial_sequence('dem.identity', 'pk')), 'James Tiberius', 'Kirk', 'deduplication canary');

-- disable audit trigger for update (because table layout has changed)
alter table dem.identity
	disable trigger zt_upd_identity;

-- de-duplicate
update dem.identity set
	duplicates_discriminator = 'auto-set by <v21-dem-identity-dynamic.sql>: ' || clock_timestamp()
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

-- rename canary to something inauspicious
update dem.names set
	lastnames = 'can-be-deleted ' || clock_timestamp(),
	firstnames = 'can-be-deleted ' || clock_timestamp()
where
	comment = 'deduplication canary'
;

-- create function and trigger
create function clin.trf_sane_identity_duplicates_discriminator()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_identity_row record;
	_names_row record;
BEGIN
	if TG_TABLE_NAME = ''identity'' then
		if TG_OP = ''UPDATE'' then
			if NEW.duplicates_discriminator = OLD.duplicates_discriminator then
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
		dem.v_persons
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
		duplicates_discriminator is not distinct from _identity_row.duplicates_discriminator
			and
		-- but not the currently updated or inserted row
		pk_identity != _identity_row.pk
	;
	if FOUND then
		RAISE EXCEPTION
			''% on %.%: More than one person with (firstnames=%), (lastnames=%), (dob=%), (discriminator=%)'',
				TG_OP,
				TG_TABLE_SCHEMA,
				TG_TABLE_NAME,
				_names_row.firstnames,
				_names_row.lastnames,
				_identity_row.dob,
				_identity_row.duplicates_discriminator
			USING ERRCODE = ''unique_violation''
		;
		RETURN NULL;
	end if;

	return NEW;
END;';

comment on function clin.trf_sane_identity_duplicates_discriminator() is
	'Ensures unique(identity.dob, names.firstnames, names.lastnames, identity.duplicates_discriminator)';


create trigger tr_sane_identity_duplicates_discriminator
	after insert or update on dem.identity
	for each row execute procedure clin.trf_sane_identity_duplicates_discriminator();


create trigger tr_sane_identity_duplicates_discriminator
	after insert or update on dem.names
	for each row execute procedure clin.trf_sane_identity_duplicates_discriminator();



-- tob nullable
-- dob = (dyob + coalesce(tob, 11:11:11.111)) at client_timezone

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-dem-identity-dynamic.sql', '21.0');
