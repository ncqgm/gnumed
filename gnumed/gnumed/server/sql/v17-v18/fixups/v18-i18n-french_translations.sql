-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: anon contributor
--
-- GNUmed database string translations exported 2013-04-01 09:16
-- - user database language is set to [fr_FR]
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- ----------------------------------------------------------------------------------------------
set client_encoding to 'utf-8';

-- remove dupes with extraneous ''-s
delete from i18n.translations tx1 where
	tx1.lang ~ E'\'.+\''
		and
	exists (
		select 1 from i18n.translations tx2 where
			tx2.lang = trim(both E'\'' from tx1.lang)
				and
			tx2.orig = trim(both E'\'' from tx1.orig)
	);

-- remove extraneous ''-s from non-dupes
update i18n.translations set
	lang = trim(both E'\'' from lang),
	orig = trim(both E'\'' from orig),
	trans = trim(both E'\'' from trans)
where
	lang ~ E'\'.+\''
;

\unset ON_ERROR_STOP

select i18n.upd_tx(E'fr', E'adopted daughter', E'belle-fille');
select i18n.upd_tx(E'fr', E'Austria', E'Autriche');
select i18n.upd_tx(E'fr', E'British Columbia', E'Colombie-Britannique');
select i18n.upd_tx(E'fr', E'current medication list', E'liste des médicaments actuelle');
select i18n.upd_tx(E'fr', E'New Brunswick', E'Nouveau-Brunswick');
select i18n.upd_tx(E'fr', E'Newfoundland and Labrador', E'Terre-Neuve-et-Labrador');
select i18n.upd_tx(E'fr', E'Northwest Territories', E'Territoires du Nord-Ouest');
select i18n.upd_tx(E'fr', E'Nova Scotia', E'Nouvelle-Écosse');
select i18n.upd_tx(E'fr', E'Prince Edward Island', E'Île-du-Prince-Édouard');
select i18n.upd_tx(E'fr', E'Quebec', E'Québec');
select i18n.upd_tx(E'fr', E'Yukon Territory', E'Territoire du Yukon');

select i18n.upd_tx(E'fr_FR', E'administrative encounter', E'acte administratif');
select i18n.upd_tx(E'fr_FR', E'consultation', E'consultation au cabinet');
select i18n.upd_tx(E'fr_FR', E'home', E'domicile');
select i18n.upd_tx(E'fr_FR', E'home visit', E'consultation à domicile');
select i18n.upd_tx(E'fr_FR', E'Hospital', E'Hopital');
select i18n.upd_tx(E'fr_FR', E'hospital visit', E'consultation à l\'hopital');
select i18n.upd_tx(E'fr_FR', E'in surgery', E'chirurgie');
select i18n.upd_tx(E'fr_FR', E'nursing home visit', E'infirmière à domicile');

\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
select gm.log_script_insertion('v18-i18n-french_translations.sql', '18.2');
