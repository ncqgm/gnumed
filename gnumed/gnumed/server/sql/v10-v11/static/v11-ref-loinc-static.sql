-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v11-ref-loinc-static.sql,v 1.1 2009-04-19 22:22:24 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
create table ref.loinc_staging (
	loinc_num text,
	component text,
	property text,
	time_aspect text,
	system text,
	scale_type text,
	method_type text,
	related_names_1_old text,
	class text,
	source text,
	dt_last_change text,
	change_type text,
	comments text,
	answer_list text,
	status text,
	map_to text,
	scope text,
	normal_range text,
	ipcc_units text,
	reference text,
	exact_component_synonym text,
	molar_mass text,
	class_type text,
	formula text,
	species text,
	example_answers text,
	acs_synonyms text,
	base_name text,
	final text,
	naa_ccr_id text,
	code_table text,
	is_set_root text,
	panel_elements text,
	survey_question_text text,
	survey_question_source text,
	units_required text,
	submitted_units text,
	related_names_2 text,
	short_name text,
	order_obs text,
	cdisc_common_tests text,
	hl7_field_subfield_id text,
	external_copyright_notice text,
	example_units text,
	inpc_percentage text,
	long_common_name text
);

-- --------------------------------------------------------------
alter table ref.loinc
	add column
		example_units text;

alter table ref.loinc
	add column
		inpc_percentage text;

alter table ref.loinc
	add column
		long_common_name text;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-ref-loinc-static.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v11-ref-loinc-static.sql,v $
-- Revision 1.1  2009-04-19 22:22:24  ncq
-- - new
--
--