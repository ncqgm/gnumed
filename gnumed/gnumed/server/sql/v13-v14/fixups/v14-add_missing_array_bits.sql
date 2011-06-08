-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

set default_transaction_read_only to off;
set check_function_bodies to on;

-- --------------------------------------------------------------
create or replace function gm.add_missing_array_bits()
	returns boolean
	language 'plpgsql'
	as '
DECLARE

BEGIN

	-- array_agg
	perform 1 from pg_catalog.pg_aggregate where aggfnoid::oid = (select oid from pg_catalog.pg_proc where proname = ''array_agg''::name limit 1);

	if FOUND then
		raise NOTICE ''[gm.add_missing_array_bits]: aggregate <array_agg> already exists'';

	else
		raise NOTICE ''[gm.add_missing_array_bits]: aggregate <array_agg> does not exist (probably PostgreSQL <8.4), creating'';
		CREATE AGGREGATE array_agg(anyelement) (
			SFUNC = array_append,
			STYPE = anyarray,
			INITCOND = ''{}''
		);
		comment on aggregate array_agg(anyelement) is
			''Missing on PG 8.3, needed for vaccination handling starting with conversion from gnumed_v13 to gnumed_v14.'';

	end if;

	-- unnest()
	perform 1 from pg_catalog.pg_proc where
		proname = ''array_unnest''::name
			and
		pronamespace = (select oid from pg_namespace where nspname = ''gm''::name)
	;

	if FOUND then
		raise NOTICE ''[gm.add_missing_array_bits]: function "gm.array_unnest()" already exists'';
	else
		raise NOTICE ''[gm.add_missing_array_bits]: function "gm.array_unnest()" does not exist, creating'';

		CREATE OR REPLACE FUNCTION gm.array_unnest(anyarray)
			RETURNS SETOF anyelement
			AS ''
		SELECT $1[i] FROM
			generate_series (
				array_lower($1,1),
				array_upper($1,1)
			) i
		;''
			LANGUAGE ''sql''
			IMMUTABLE
		;

		comment on function gm.array_unnest(anyarray) is
			''Missing on PG 8.3, needed for vaccination handling starting with conversion from gnumed_v13 to gnumed_v14.'';

	end if;

	perform 1 from pg_catalog.pg_proc where
		proname = ''unnest''::name
			and
		pronamespace = (select oid from pg_namespace where nspname = ''pg_catalog''::name)
	;

	if FOUND then
		raise NOTICE ''[gm.add_missing_array_bits]: function "pg_catalog.unnest()" exists'';

		-- also exists in public ?
		perform 1 from pg_catalog.pg_proc where
			proname = ''unnest''::name
				and
			pronamespace = (select oid from pg_namespace where nspname = ''public''::name)
		;

		if FOUND then
			raise NOTICE ''[gm.add_missing_array_bits]: function "unnest()" also exists in schema "public", removing'';
			drop function public.unnest(anyarray) cascade;
		end if;

	else
		raise NOTICE ''[gm.add_missing_array_bits]: function "pg_catalog.unnest()" does not exist (probably PostgreSQL <8.4)'';

		-- exists in public ?
		perform 1 from pg_catalog.pg_proc where
			proname = ''unnest''::name
				and
			pronamespace = (select oid from pg_namespace where nspname = ''public''::name)
		;

		if FOUND then
			raise NOTICE ''[gm.add_missing_array_bits]: function "public.unnest()" already exists'';
		else
			raise NOTICE ''[gm.add_missing_array_bits]: function "public.unnest()" does not exist either, creating'';

			CREATE OR REPLACE FUNCTION public.unnest(anyarray)
				RETURNS SETOF anyelement
				AS ''SELECT gm.array_unnest($1);''
				LANGUAGE ''sql''
				IMMUTABLE
			;

			comment on function public.unnest(anyarray) is
				''Missing on PG 8.3, needed for vaccination handling starting with conversion from gnumed_v13 to gnumed_v14.'';

		end if;

	end if;

	return TRUE;
END;';



comment on function gm.add_missing_array_bits() is
	'Add array aggregate and array unnesting to PostgreSQL versions lacking this functionality (IOW < 8.4).';



SELECT gm.add_missing_array_bits();

-- --------------------------------------------------------------
select gm.log_script_insertion('v14-add_missing_array_bits.sql', 'Revision: 1.1');
