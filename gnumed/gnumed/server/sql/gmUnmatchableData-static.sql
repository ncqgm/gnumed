-- =============================================
-- GNUmed - static tables for unmatchable test results
-- =============================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmUnmatchableData-static.sql,v $
-- $Id: gmUnmatchableData-static.sql,v 1.1 2005-10-30 21:57:51 ncq Exp $
-- license: GPL
-- author: Karsten.Hilbert@gmx.net

-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ---------------------------------------------
create table incoming_data_unmatchable (
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

select add_table_for_audit('incoming_data_unmatchable');

-- =============================================
-- do simple schema revision tracking
select log_script_insertion('$RCSfile: gmUnmatchableData-static.sql,v $2', '$Revision: 1.1 $');

-- =============================================
-- $Log: gmUnmatchableData-static.sql,v $
-- Revision 1.1  2005-10-30 21:57:51  ncq
-- - incoming data tables: unmatched/unmatchable
--
--
