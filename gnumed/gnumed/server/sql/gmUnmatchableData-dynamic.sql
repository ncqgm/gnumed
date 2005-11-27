-- =============================================
-- GNUmed - re-runnable objects for unmatchable incoming results
-- =============================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmUnmatchableData-dynamic.sql,v $
-- $Id: gmUnmatchableData-dynamic.sql,v 1.2 2005-11-27 13:00:59 ncq Exp $
-- license: GPL
-- author: Karsten.Hilbert@gmx.net

-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ---------------------------------------------
comment on table clin.incoming_data_unmatchable is
	'this table holds test results that could not be matched
	 to any patient, it is intended to prevent overflow of
	 incoming_data_unmatched with unmatchable data';

-- ---------------------------------------------
grant select, insert, update, delete on
	clin.incoming_data_unmatched
	, clin.incoming_data_unmatched_pk_seq
to group "gm-doctors";

-- =============================================
-- do simple schema revision tracking
select log_script_insertion('$RCSfile: gmUnmatchableData-dynamic.sql,v $1', '$Revision: 1.2 $');

-- =============================================
-- $Log: gmUnmatchableData-dynamic.sql,v $
-- Revision 1.2  2005-11-27 13:00:59  ncq
-- - since schema "clin" exists now we better use it
--
-- Revision 1.1  2005/10/30 21:57:51  ncq
-- - incoming data tables: unmatched/unmatchable
--
--
