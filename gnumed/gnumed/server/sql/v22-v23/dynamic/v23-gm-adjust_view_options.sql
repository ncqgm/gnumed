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
drop function if exists gm.adjust_view_options() cascade;

create function gm.adjust_view_options()
	returns void
	language plpgsql
	security definer
	as '
DECLARE
	_rec record;
BEGIN
	FOR _rec IN (
		SELECT
			n.nspname as view_schema,
			c.relname as view_name
			--,pg_catalog.pg_get_userbyid(c.relowner) as "Owner"
		FROM pg_catalog.pg_class c
			LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
		WHERE c.relkind IN (''v'')
			AND n.nspname OPERATOR(pg_catalog.~) ''^(clin)|(gm)|(blobs)|(ref)|(bill)|(cfg)|(audit)|(dem)|(i18n)|(staging|)(de_de)|(au)$'' COLLATE pg_catalog.default
		ORDER BY
			view_schema, view_name
	) LOOP
		RAISE NOTICE ''setting security_invoker=TRUE on view [%.%]'', _rec.view_schema, _rec.view_name;
		EXECUTE ''ALTER VIEW '' || _rec.view_schema || ''.'' || _rec.view_name || '' SET (security_invoker = TRUE)'';
	END LOOP;
END;';

comment on function gm.adjust_view_options() is 'Adjust all GNUmed views in database as user postgres.';

revoke all on function gm.adjust_view_options() from public;

grant execute on function gm.adjust_view_options() to "gm-dbo";

--select gm.adjust_view_options();

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-gm-adjust_view_options.sql', '23.0');
