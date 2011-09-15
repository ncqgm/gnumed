-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table clin.vaccine
	alter column is_live
		set default true;

-- --------------------------------------------------------------
-- .fk_brand/id_route
\unset ON_ERROR_STOP
alter table clin.vaccine drop constraint clin_vaccine_sane_brand_route cascade;
\set ON_ERROR_STOP 1

alter table clin.vaccine
	add constraint clin_vaccine_uniq_brand_route
		unique (fk_brand, id_route);

-- --------------------------------------------------------------
-- .is_live
alter table clin.vaccine
	alter column is_live
		drop not null;

-- --------------------------------------------------------------
-- adjust vaccination routes
UPDATE clin.vacc_route SET description = 'oral' WHERE description = 'orally';
select i18n.upd_tx('de', 'oral', 'oral');


INSERT INTO clin.vacc_route (
	abbreviation,
	description
) SELECT
	'nasal'::text,
	'nasal'::text
  WHERE NOT EXISTS (
	select 1 from clin.vacc_route where description = 'nasal' limit 1
);
select i18n.upd_tx('de', 'nasal', 'nasal');


INSERT INTO clin.vacc_route (
	abbreviation,
	description
) SELECT
	'i.d.'::text,
	'intradermal'::text
  WHERE NOT EXISTS (
	select 1 from clin.vacc_route where description = 'intradermal' limit 1
);
select i18n.upd_tx('de', 'intradermal', 'intradermal');

-- --------------------------------------------------------------
-- add vaccination indication
insert into clin.vacc_indication (
	description,
	atcs_single_indication
) select
	'influenza (H3N2)',
	array['J07BB']
  where not exists (
	select 1 from clin.vacc_indication where description = ''
);

select i18n.upd_tx('de', 'influenza (H3N2)', 'Influenza (H3N2)');

select gm.create_generic_monovalent_vaccines();

-- ==============================================================
select gm.log_script_insertion('v16-clin-vaccine-dynamic.sql', 'v16');
