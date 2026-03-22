-- ===============================================
-- This script creates tables of import of
-- information as provided by the german AMIS database

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/de/gmAMIS.de.sql,v $
-- author: Hilmar Berger, Karsten Hilbert
-- version: $Revision: 1.6 $
-- license: GPL v2 or later
-- TODO: further processing of the data (normalizing)
-- =====================================================================================
reset client_encoding;

-- =====================================================================================
-- amis_praeparate : table of preparations
-- =====================================================================================
drop table if exists amis_praeparate;

create table amis_praeparate (
	connection_id int8 primary key,
	brandname varchar(78),
	drug_presentation char(3),
	combi_package char(1),
	indication_key_1 char(5),
	indication_key_2 char(5),
	manufacturer_key int,
	red_list_key int,
	negative_list_flag char(1),
	sale_regulations_code char(1),
	atc_code char(7),
	drug_descriptive_text_key int8,
	volume_weight_value varchar(7),
	volume_weight_unit varchar(8),
	volume_weight_description varchar(15),
	dose_relation_value char(7),
	dose_relation_description varchar(15),
	package_relation_value char(7),
	package_relation_description varchar(15),
	second_manufacturer_key int
);

-- =====================================================================================
-- amis_praeparate : table of preparations (combinations of more than one drug /package)
-- =====================================================================================
drop table if exists amis_praeparate_combination;

create table amis_praeparate_combination (
	connection_id int8 primary key,
	connection_key_combination int8,
	brandname varchar(78),
	drug_presentation char(3),
	combi_package char(1),
	indication_key_1 char(5),
	indication_key_2 char(5),
	manufacturer_key int,
	red_list_key int,
	negative_list_flag char(1),
	sale_regulations_code char(1),
	atc_code char(7),
	drug_descriptive_text_key int8,
	volume_weight_value varchar(7),
	volume_weight_unit varchar(8),
	volume_weight_description varchar(15),
	dose_relation_value varchar(7),
	dose_relation_description varchar(15),
	package_relation_value varchar(7),
	package_relation_description varchar(15),
	second_manufacturer_key int
);

-- =====================================================================================
-- amis_substances : table of substances
-- =====================================================================================
drop table if exists amis_substances;

create table amis_substances (
	connection_id int8,
	id int,
	dose varchar(20),
	unit varchar(8),
	suffix varchar(100),  -- this is should be different if the same substance appears more
	    	    	    	    -- than once within the same drug
	additive_flag char(2) -- 'j' if this is an additive
);

-- =====================================================================================
-- amis_substances_extended : extended info of substances
-- =====================================================================================
drop table if exists amis_substances_extended;

create table amis_substances_extended (
	connection_id int8,
	id int,
	dose varchar(20),
	unit varchar(8),
	suffix varchar(100),  -- this is should be different if the same substance appears more
	    	    	    	    -- than once within the same drug
	additive_flag char(2), -- 'j' if this is an additive
	primary_substance_info_key int -- the substance the extended information refers to
);

-- =====================================================================================
-- amis_substances_names : names of substances
-- =====================================================================================
drop table if exists amis_substances_names;

create table amis_substances_names (
	substance_id int,
	substance_name varchar(160),
	substance_sort_name varchar(160), -- same as name but lowercase and without spaces
	substance_text_key int,
	substance_classification int8 
);

-- =====================================================================================
-- amis_indications 
-- =====================================================================================
drop table if exists amis_indications;

create table amis_indications (
	indication_key char(5),
	indication_name varchar(95)
);

-- =====================================================================================
-- amis_warnings 
-- =====================================================================================
drop table if exists amis_warnings;

create table amis_warnings (
	connection_id int8,
	warning_id char(4)  	-- refers to amis_warning_text
);

-- =====================================================================================
-- amis_warning_text 
-- =====================================================================================
drop table if exists amis_warning_text;

create table amis_warning_text (
	warning_id char(3),
	warning_text varchar(250)  
);

-- =====================================================================================
-- amis_manufacturer
-- =====================================================================================
drop table if exists amis_manufacturer;

create table amis_manufacturer (
	manufacturer_key int,
	manufacturer_name varchar(50),
	manufacturer_name_long varchar(80),
	manufacturer_postbox varchar(20),
	manufacturer_street varchar(30),
	manufacturer_postcode_postbox char(5),
	manufacturer_postcode_street char(5),
	manufacturer_city varchar(25),
	manufacturer_country varchar(3),
	manufacturer_phone_number varchar(20),
	manufacturer_fax_number varchar(20)
);

-- =====================================================================================
-- amis_manuf_emergency_call
-- =====================================================================================
drop table if exists amis_manuf_emergency_call;

create table amis_manuf_emergency_call (
	manufacturer_key int,
	phone_number varchar(20),
	availability char(1),
	description varchar(76)	
);

-- ===============================================
-- do the same thing with the ATC codes
-- ===============================================
drop table if exists amis_atc;

create table amis_atc (
	code char(7) primary key,
	atc_text text
);

-- ===============================================
-- amis drug descriptions
-- ===============================================
drop table if exists amis_drug_description;

create table amis_drug_description (
	text_key int8,
	type char(1),
	drug_text text
);

-- ===============================================
-- amis substance descriptions
-- ===============================================
drop table if exists amis_substance_description;

create table amis_substance_description (
    text_key int,
	type int,
	substance_text text
);

-- ===============================================
-- amis prices
-- ===============================================
drop table if exists amis_price;

create table amis_price (
	central_pharma_number int,
	connection_id int8,
	brand_name varchar(26),
	preparation_type char(3),
	package_content varchar(9), -- contains value + unit
	package_content_value varchar(6), -- internal use only
	package_content_unit varchar(3), -- internal use only
	package_price varchar(7), -- fixed point (5.2) format
	sale_regulation char(1),
	narcotic char(1),
	commercial_availability char(1),
	negative_list char(1),
   	fixed_price varchar(7),	-- fixed point (5.2) format
	fixed_price_comparison_key int,
	patient_price varchar(7), -- "Zuzahlung"
   	outdated_cpn_1 int,    -- outdated central pharma number
	outdated_cpn_2 int,
	original_cpn int, 	-- used for imported drugs
	price_manufacturer_key int,
	period_of_validity char(9)  -- dd/mm/yy
);

-- =====================================================================================
-- amis_price_manufacturer
-- =====================================================================================
drop table if exists amis_price_manufacturer;

create table amis_price_manufacturer (
	code int primary key,
	manufacturer_name varchar(22),
	name_long varchar(22),
	postbox varchar(6),
	street varchar(22),
	postcode_postbox char(5),
	postcode_street char(5),
	city varchar(23),
	country varchar(3),
	phone_number varchar(17),
	fax_number varchar(17)
);

-- =====================================================================================
-- amis_presentation
-- =====================================================================================
drop table if exists amis_presentation;

create table amis_presentation (
	name_short char(3),
	name_long varchar(50),
	drug_form_code char(1),
	application_form_code char(1),
	application_route_code char(2),
	site_of_action_code char(1)
);

-- =====================================================================================
-- amis_interaction_groups
-- =====================================================================================
drop table if exists amis_interaction_groups;

create table amis_interaction_groups (
	code int primary key,
	first_interaction_group text,
	second_interaction_group text,
	significance_code char(5),
	effect text	
);

-- =====================================================================================
-- amis_documented_interaction
-- =====================================================================================
drop table if exists amis_documented_interaction;

create table amis_documented_interaction (
	code int,
	interaction_group_number char(1), -- group 1 or 2 
	substance_number char(7), -- refers to amis_substances
	connection_id char(11) --refers to amis_praeparate
);

-- =====================================================================================
-- amis_expected_interaction
-- =====================================================================================
drop table if exists amis_expected_interaction;

create table amis_expected_interaction (
	code int,
	interaction_group_number char(1), -- group 1 or 2 
	substance_number char(7), -- refers to amis_substances
	connection_id char(11) --refers to amis_praeparate
);

-- =====================================================================================
-- amis_undecided_interaction
-- =====================================================================================
drop table if exists amis_undecided_interaction;

create table amis_undecided_interaction (
	code int,
	interaction_group_number char(1), -- group 1 or 2 
	substance_number char(7), -- refers to amis_substances
	connection_id char(11) --refers to amis_praeparate
);

-- =====================================================================================
-- amis_unlikely_interaction
-- =====================================================================================
drop table if exists amis_unlikely_interaction;

create table amis_unlikely_interaction (
	code int,
	interaction_group_number char(1), -- group 1 or 2 
	substance_number char(7), -- refers to amis_substances
	connection_id char(11) --refers to amis_praeparate
);

-- =====================================================================================
-- amis_interaction_type
-- =====================================================================================
drop table if exists amis_interaction_type;

create table amis_interaction_type (
	code int,
	type text, 
	type_code char(1),
	mechanism text
);

-- =====================================================================================
-- amis_interaction_text
-- =====================================================================================
drop table if exists amis_interaction_text;

create table amis_interaction_text (
	code int,
	part char(1), 
	text text
);


-- =====================================================================================
-- grant appropriate rights
-- =====================================================================================
GRANT SELECT ON
	amis_praeparate,
	amis_praeparate_combination, 
	amis_substances, 
	amis_substances_extended, 
	amis_substances_names, 
	amis_indications, 
	amis_warnings, 
	amis_warning_text, 
	amis_manufacturer, 
	amis_manuf_emergency_call, 
	amis_atc, 
	amis_drug_description, 
	amis_substance_description, 
	amis_price, 
	amis_price_manufacturer, 
	amis_presentation, 
	amis_interaction_groups, 
	amis_documented_interaction, 
	amis_expected_interaction, 
	amis_undecided_interaction, 
	amis_unlikely_interaction, 
	amis_interaction_type, 
	amis_interaction_text
TO GROUP "gm-public";

-- =============================================                                
-- do simple schema revision tracking                                           
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmAMIS.de.sql,v $', '$Revision: 1.6 $'); 

-- ==========================================================
