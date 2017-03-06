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
-- back in the days, when GNUmed was still using pre 8.4 PGs
-- we had to manually add a public.array_agg aggregate via
-- v14-add_missing_array_bits.sql
--
-- nowadays (starting with PG 9.2), there's pg_catalog.array_agg
-- for (anyelement), (anyarray), and (anynonarray), which results
-- in, say:
--
--		PG error message: ERROR:  function array_agg(integer) is not unique
--		ZEILE 5:    (SELECT array_agg(seq_idx) FROM blobs.doc_obj b_do WHERE ...
--		TIP:  Could not choose a best candidate function. You might need to add explicit type casts.
--
-- on using array_agg() with integers

-- so, drop old helper aggregate
drop aggregate if exists public.array_agg(anyelement) cascade;

--CREATE AGGREGATE array_agg(anyelement) (
--	SFUNC = array_append,
--	STYPE = anyarray,
--	INITCOND = ''{}''
--);
--comment on aggregate array_agg(anyelement) is
--	''Missing on PG 8.3, needed for vaccination handling starting with conversion from gnumed_v13 to gnumed_v14.'';

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-previously-missing-array_agg-fixup.sql', '21.12');
