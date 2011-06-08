-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- $Id: v11-gm-unaccent_string.sql,v 1.1 2009-04-01 15:55:39 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
create or replace function gm.unaccent_string(text)
	returns text
	language sql
	as $$
select
	-- missing slawic umlauts on s, c, z, l (crossed out)
	translate (
		$1,
		-- a,              e,               i,            o,               u,              s,c,n
		'áàâãäåāăąÁÀÂÃÄÅĀĂĄéèêëēĕėęěĒĔĖĘĚÉÈÊíìîïĩīĭÍÌÎÏĨĪĬóôõöøōŏőÓÒÔÕÖØŌŎŐúùûüũūŭůÚÙÛÜŨŪŬŮšßçÇÑñ',
		'aaaaaaaaaAAAAAAAAAeeeeeeeeeeeeeeEEEiiiiiiiIIIIIIIooooooooOOOOOOOOOuuuuuuuuUUUUUUUUsscCNn'
	)
$$;


grant execute on function gm.unaccent_string(text) to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-gm-unaccent_string.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v11-gm-unaccent_string.sql,v $
-- Revision 1.1  2009-04-01 15:55:39  ncq
-- - new
--
--