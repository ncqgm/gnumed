-- =============================================
-- GNUmed - static tables for unmatched incoming data
-- =============================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmUnmatchedData-static.sql,v $
-- $Id: gmUnmatchedData-static.sql,v 1.2 2005-11-01 08:53:50 ncq Exp $
-- license: GPL
-- author: Karsten.Hilbert@gmx.net

-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ---------------------------------------------
create table incoming_data_unmatched (
	pk serial primary key,
	fk_patient_candidates integer[],
	request_id text,
	firstnames text,
	lastnames text,
	dob date,
	postcode text,
	other_info text,
	type text,
	data bytea
		not null
) inherits (audit_fields);

select add_table_for_audit('incoming_data_unmatched');

-- =============================================
-- do simple schema revision tracking
select log_script_insertion('$RCSfile: gmUnmatchedData-static.sql,v $4', '$Revision: 1.2 $');

-- =============================================
-- $Log: gmUnmatchedData-static.sql,v $
-- Revision 1.2  2005-11-01 08:53:50  ncq
-- - factor out re-runnables
--
-- Revision 1.1  2005/10/30 21:57:51  ncq
-- - incoming data tables: unmatched/unmatchable
--
--
