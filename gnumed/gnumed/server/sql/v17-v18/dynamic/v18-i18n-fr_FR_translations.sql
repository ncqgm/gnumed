-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
--
-- GNUmed database string translations exported 2013-01-30 20:08
-- - contains translations for each of ['ru_RU', nl_NL, de, es_ES, fr_CA, pap_AN, fr_FR, de_DE]
-- - user language is set to [fr_FR]

--set default_transaction_read_only to off
-- --------------------------------------------------------------

\unset ON_ERROR_STOP

set client_encoding to 'utf8';

select i18n.upd_tx(quote_literal(E'fr'), quote_literal(E'British Columbia'), quote_literal(E'Colombie-Britannique'));
select i18n.upd_tx(quote_literal(E'fr'), quote_literal(E'New Brunswick'), quote_literal(E'Nouveau-Brunswick'));
select i18n.upd_tx(quote_literal(E'fr'), quote_literal(E'Newfoundland and Labrador'), quote_literal(E'Terre-Neuve-et-Labrador'));
select i18n.upd_tx(quote_literal(E'fr'), quote_literal(E'Northwest Territories'), quote_literal(E'Territoires du Nord-Ouest'));
select i18n.upd_tx(quote_literal(E'fr'), quote_literal(E'Nova Scotia'), quote_literal(E'Nouvelle-Écosse'));
select i18n.upd_tx(quote_literal(E'fr'), quote_literal(E'Prince Edward Island'), quote_literal(E'Île-du-Prince-Édouard'));
select i18n.upd_tx(quote_literal(E'fr'), quote_literal(E'Quebec'), quote_literal(E'Québec'));
select i18n.upd_tx(quote_literal(E'fr'), quote_literal(E'Yukon Territory'), quote_literal(E'Territoire du Yukon'));
select i18n.upd_tx(quote_literal(E'fr'), quote_literal(E'adopted daughter'), quote_literal(E'\'belle-fille\''));
select i18n.upd_tx(quote_literal(E'fr'), quote_literal(E'Austria'), quote_literal(E'Autriche'));
select i18n.upd_tx(quote_literal(E'fr'), quote_literal(E'current medication list'), quote_literal(E'liste des médicaments actuelle'));

\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
select gm.log_script_insertion('v18-i18n-fr_FR_translations.sql', '18.0');
