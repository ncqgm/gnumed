-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
set default_transaction_read_only to off;

-- --------------------------------------------------------------
drop function if exists gm.revalidate_all_constraints() cascade;

create function gm.revalidate_all_constraints()
	returns void
	language plpgsql
	security definer
	as '
DECLARE
	_rec record;
BEGIN
	FOR _rec IN (
		select con.connamespace, nsp.nspname, con.conname, con.conrelid, rel.relname
		from pg_constraint con
			join pg_namespace nsp on nsp.oid = con.connamespace
			join pg_class rel on rel.oid = con.conrelid
		where contype in (''c'',''f'')
	) LOOP
		RAISE NOTICE ''validating [%] on [%.%]'', _rec.conname, _rec.nspname, _rec.relname;
		EXECUTE ''UPDATE pg_constraint SET convalidated=false WHERE conname=$1 AND connamespace=$2 AND conrelid=$3'' USING _rec.conname, _rec.connamespace, _rec.conrelid;
		-- EXECUTE ''ALTER TABLE $1.$2 VALIDATE CONSTRAINT "$3"'' USING _rec.nspname, _rec.relname, _rec.conname;
		EXECUTE ''ALTER TABLE '' || _rec.nspname || ''.'' || _rec.relname || '' VALIDATE CONSTRAINT "'' || _rec.conname || ''"'';
	END LOOP;
END;';

comment on function gm.revalidate_all_constraints() is 'Revalidates all constraints in database as user postgres.';

revoke all on function gm.revalidate_all_constraints() from public;

grant execute on function gm.revalidate_all_constraints() to "gm-dbo";

alter function gm.revalidate_all_constraints() owner to postgres;

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-gm-revalidate_all_constraints.sql', '23.0');
