-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create table ref.icpc_chapter (
	pk serial primary key,
	chapter char(1),
	description text
);

-- --------------------------------------------------------------
create table ref.icpc_component (
	pk serial primary key,
	component smallint,
	description text,
	typical_soap_cat text[]
);

-- --------------------------------------------------------------
create table ref.icpc (
	pk serial primary key,
	--parent.code -> CODE
	--parent.term -> description
	code_extension text,
	short_description text,
	icd10 text[],
	criteria text,
	inclusions text,
	exclusions text[],
	see_also text[],
	--parent.comment -> NOTE
	fk_component smallint,
	fk_chapter char(1)
) inherits (ref.coding_system_root);

-- --------------------------------------------------------------
create table ref.code_thesaurus_root (
	pk_thesaurus serial primary key,
	fk_code integer,
	synonym text
);

-- --------------------------------------------------------------
create table ref.icpc_thesaurus (
	pk serial primary key
) inherits (ref.code_thesaurus_root);

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-ref-icpc2-static.sql', 'Revision: 1.1');
