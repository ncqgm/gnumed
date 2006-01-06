-- =============================================
-- GNUmed - static tables for unmatchable test results
-- =============================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmUnmatchableData-static.sql,v $
-- $Id: gmUnmatchableData-static.sql,v 1.4 2006-01-06 10:12:02 ncq Exp $
-- license: GPL
-- author: Karsten.Hilbert@gmx.net

-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ---------------------------------------------
create table clin.incoming_data_unmatchable (
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
) inherits (audit.audit_fields);

select audit.add_table_for_audit('clin', 'incoming_data_unmatchable');

-- =============================================
-- do simple schema revision tracking
select log_script_insertion('$RCSfile: gmUnmatchableData-static.sql,v $2', '$Revision: 1.4 $');

-- =============================================
-- $Log: gmUnmatchableData-static.sql,v $
-- Revision 1.4  2006-01-06 10:12:02  ncq
-- - add missing grants
-- - add_table_for_audit() now in "audit" schema
-- - demographics now in "dem" schema
-- - add view v_inds4vaccine
-- - move staff_role from clinical into demographics
-- - put add_coded_term() into "clin" schema
-- - put German things into "de_de" schema
--
-- Revision 1.3  2006/01/05 16:04:37  ncq
-- - move auditing to its own schema "audit"
--
-- Revision 1.2  2005/11/27 13:00:59  ncq
-- - since schema "clin" exists now we better use it
--
-- Revision 1.1  2005/10/30 21:57:51  ncq
-- - incoming data tables: unmatched/unmatchable
--
--
