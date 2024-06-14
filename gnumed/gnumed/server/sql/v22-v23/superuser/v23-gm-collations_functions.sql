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
drop function if exists gm.pg_import_system_collations() cascade;

create function gm.pg_import_system_collations()
	returns void
	language plpgsql
	security definer
	as '
BEGIN
	RAISE NOTICE ''running pg_catalog.pg_import_system_collations(%)'', ''pg_catalog''::regnamespace;
	PERFORM pg_catalog.pg_import_system_collations(''pg_catalog''::regnamespace);
END;';

comment on function gm.pg_import_system_collations() is 'Re-imports collations information from the underlying operating system.';

revoke all on function gm.pg_import_system_collations() from public;

grant execute on function gm.pg_import_system_collations() to "gm-dbo";

alter function gm.pg_import_system_collations() owner to postgres;

-- --------------------------------------------------------------
drop function if exists gm.remove_unneeded_collations() cascade;

create function gm.remove_unneeded_collations()
	returns void
	language plpgsql
	security definer
	as '
DECLARE
	_rec record;
	_db_name text;
	_db_encoding integer;
BEGIN
	SELECT pg_catalog.current_database() INTO _db_name;
	SELECT encoding INTO _db_encoding FROM pg_database WHERE datname = _db_name;
	RAISE NOTICE ''database [%]: removing collations for encodings other than the database encoding [%]'', _db_name, pg_catalog.pg_encoding_to_char(_db_encoding);
	FOR _rec IN (
		SELECT oid, collnamespace, collname, collencoding
		FROM pg_collation
		WHERE
			oid > 1000
				AND
			collencoding IS NOT NULL
				AND
			collencoding <> -1
				AND
			collencoding <> _db_encoding
	) LOOP
		RAISE NOTICE ''dropping collation #% "%.%" (encoding: %)'', _rec.oid, _rec.collnamespace::regnamespace, _rec.collname, pg_catalog.pg_encoding_to_char(_rec.collencoding);
		BEGIN
			EXECUTE ''DROP COLLATION IF EXISTS '' || _rec.collnamespace::regnamespace || ''."'' || _rec.collname || ''"'';
		EXCEPTION
			WHEN undefined_object THEN RAISE NOTICE ''collation does not seem to exist (perhaps for the DB encoding ?)'';
		END;
	END LOOP;
END;';

comment on function gm.remove_unneeded_collations() is 'Remove collations not suitable for the database encoding (thusly not usable in this database).';

revoke all on function gm.remove_unneeded_collations() from public;

grant execute on function gm.remove_unneeded_collations() to "gm-dbo";

alter function gm.remove_unneeded_collations() owner to postgres;

-- --------------------------------------------------------------
drop function if exists gm.refresh_pg_collations_version_information() cascade;

create function gm.refresh_pg_collations_version_information()
	returns void
	language plpgsql
	security definer
	as '
DECLARE
	_rec record;
BEGIN
	RAISE NOTICE ''refreshing collations version information in pg_collation'';
	FOR _rec IN (
		SELECT collnamespace, collname
		FROM pg_collation
		WHERE
			collversion IS DISTINCT FROM NULL
				AND
			collprovider <> ''d''
				AND
			collversion <> pg_catalog.pg_collation_actual_version(oid)
	) LOOP
		RAISE NOTICE ''refreshing collation [%."%"] version information'', _rec.collnamespace::regnamespace, _rec.collname;
		BEGIN
			EXECUTE ''ALTER COLLATION '' || _rec.collnamespace::regnamespace || ''."'' || _rec.collname || ''" REFRESH VERSION'';
		EXCEPTION
			WHEN undefined_object THEN RAISE NOTICE ''collation does not exist, cannot refresh'';
		END;
	END LOOP;
END';

comment on function gm.refresh_pg_collations_version_information() is
'Refresh all collations version information in pg_collations.';

revoke all on function gm.refresh_pg_collations_version_information() from public;

grant execute on function gm.refresh_pg_collations_version_information() to "gm-dbo";

alter function gm.refresh_pg_collations_version_information() owner to postgres;

-- --------------------------------------------------------------
drop function if exists gm.update_pg_collations() cascade;

create function gm.update_pg_collations()
	returns void
	language plpgsql
	security invoker
	as '
BEGIN
	PERFORM gm.pg_import_system_collations();
	PERFORM gm.remove_unneeded_collations();
	PERFORM gm.refresh_pg_collations_version_information();
	RAISE NOTICE ''done refreshing collations'';
END;';

comment on function gm.update_pg_collations() is
'Update all collations version information.
.
See https://www.postgresql.org/message-id/9aec6e6d-318e-4a36-96a4-3b898c3600c9%40manitou-mail.org';

revoke all on function gm.update_pg_collations() from public;

grant execute on function gm.update_pg_collations() to "gm-dbo";

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-gm-collations_functions.sql', '23.0');
