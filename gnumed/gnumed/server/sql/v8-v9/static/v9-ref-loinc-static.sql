-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v9-ref-loinc-static.sql,v 1.1 2008-03-05 22:36:11 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create table ref.loinc (
	-- code (.code)
	-- term (":".join() of .component to .method_type)
	-- version (.fk_data_source.name_short + version)
	-- comment (.comment)
	pk serial primary key,
	component text,
	property text,
	time_aspect text,
	system text,
	scale_type text,
	method_type text,
	related_names_1_old text,
	grouping_class text,		-- LOINC.CLASS
	loinc_internal_source text,
	dt_last_change text,
	change_type text,
	answer_list text,
	code_status text,
	maps_to text,
	scope text,
	normal_range text,
	ipcc_units text,
	reference text,
	exact_component_synonym text,
	molar_mass text,
	grouping_class_type smallint,
	formula text,
	species text,
	example_answers text,
	acs_synonyms text,
	base_name text,
	final text,
	naa_ccr_id text,
	code_table text,
	is_set_root boolean,
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
	external_copyright_notice text
) inherits (ref.coding_system_root);

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v9-ref-loinc-static.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v9-ref-loinc-static.sql,v $
-- Revision 1.1  2008-03-05 22:36:11  ncq
-- - new
--
--