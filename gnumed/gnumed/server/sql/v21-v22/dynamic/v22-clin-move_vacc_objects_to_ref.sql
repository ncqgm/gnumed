-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
alter table if exists clin.vaccine
	set schema ref;

alter table if exists clin.v_vaccines
	set schema ref;

alter table if exists clin.v_indications4vaccine
	set schema ref;


alter table if exists clin.vacc_route
	set schema ref;


alter table if exists clin.lnk_vaccine2inds
	set schema ref;


alter table if exists clin.vacc_indication
	set schema ref;


update audit.audited_tables set
	schema = 'ref'
where
	schema = 'clin'
		and
	table_name in ('vaccine', 'vacc_route', 'lnk_vaccine2inds', 'vacc_indication');


drop function if exists gm.create_generic_monovalent_vaccines() cascade;
drop function if exists gm.create_generic_combi_vaccines() cascade;

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-clin-move_vacc_objects_to_ref.sql', '22.0');
