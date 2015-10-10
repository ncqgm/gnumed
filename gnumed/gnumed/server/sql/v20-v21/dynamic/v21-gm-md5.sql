-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
create or replace function gm.lo_chunked_md5(oid, int)
	returns text
	language 'plpgsql'
	stable strict
	as '
DECLARE
	lo_id alias for $1;
	chunk_size alias for $2;
	_lo_fd integer;
	_lo_size integer;
	_chunk_count integer;
	_remainder integer;
	_md5_concat text;
	INV_READ constant integer := x''40000''::integer;
	SEEK_SET constant integer := 0;
	SEEK_END constant integer := 2;
BEGIN
	-- check for existence of lo_id ?

	_lo_fd := lo_open(lo_id, INV_READ);
	-- get size
	_lo_size := lo_lseek(_lo_fd, 0, SEEK_END);
	PERFORM lo_close(_lo_fd);						-- move further down if loread() proves faster

	-- calculate chunks and remainder
	_chunk_count := _lo_size / chunk_size;
	_remainder := _lo_size % chunk_size;

	-- loop over chunks
	_md5_concat := '''';
	FOR _chunk_id in 1.._chunk_count LOOP
		_md5_concat := _md5_concat || md5(lo_get(lo_id, (_chunk_id - 1) * chunk_size, chunk_size));
		-- using loread() may be faster (as it directly accesses the
		-- existing lo_fd and thusly does not need to re-open the LO
		-- each round)
	END LOOP;
	-- add remainder
	_md5_concat := _md5_concat || md5(lo_get(lo_id, _chunk_count * chunk_size, _remainder));

	return md5(_md5_concat);
END;';

comment on function gm.lo_chunked_md5(oid, int) is 'Function to create a chunked md5 sum on arbitrarily large LARGE OBJECTs.';

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-gm-md5.sql', '21.0');
