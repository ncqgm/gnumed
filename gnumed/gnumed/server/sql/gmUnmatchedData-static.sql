-- =============================================
-- GNUmed - static tables for unmatched incoming data
-- =============================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmUnmatchedData-static.sql,v $
-- $Id: gmUnmatchedData-static.sql,v 1.1 2005-10-30 21:57:51 ncq Exp $
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

comment on table incoming_data_unmatched is
	'this table holds incoming data (lab results, documents)
	 that could not be matched to one single patient automatically,
	 it is intended to facilitate manual matching,
	 - use "modified_when" for import time';
comment on column incoming_data_unmatched.fk_patient_candidates is
	'a matching algorithm can be applied to produce
	 a list of likely candidate patients, the question
	 remains whether this should not be done at runtime';
comment on column incoming_data_unmatched.request_id is
	'request ID as found in <data>';
comment on column incoming_data_unmatched.firstnames is
	'first names as found in <data>';
comment on column incoming_data_unmatched.lastnames is
	'last names as found in <data>';
comment on column incoming_data_unmatched.dob is
	'date of birth as found in <data>';
comment on column incoming_data_unmatched.postcode is
	'postcode as found in <data>';
comment on column incoming_data_unmatched.other_info is
	'other identifying information as found in <data>';
comment on column incoming_data_unmatched.type is
	'the type of <data>, eg HL7, LDT, ...,
	 useful for selecting an importer';
comment on column incoming_data_unmatched.data is
	'the raw data';


-- =============================================
-- do simple schema revision tracking
select log_script_insertion('$RCSfile: gmUnmatchedData-static.sql,v $4', '$Revision: 1.1 $');

-- =============================================
-- $Log: gmUnmatchedData-static.sql,v $
-- Revision 1.1  2005-10-30 21:57:51  ncq
-- - incoming data tables: unmatched/unmatchable
--
--
