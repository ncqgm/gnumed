-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- GNUmed database string translations exported 2012-01-28 20:56
-- - contains translations for each of [de_DE, nl_NL, de, ru_RU, es_ES, fr_CA, pap_AN]
-- - user language is set to [ru_RU]
--
-- Please email this file to <gnumed-devel@gnu.org>.
-- ==============================================================
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP

select i18n.upd_tx(quote_literal(E'ru_RU'), quote_literal(E'Abakan'), quote_literal(E'Абакан'));
select i18n.upd_tx(quote_literal(E'ru_RU'), quote_literal(E'Aberdeen'), quote_literal(E'Аберден'));
select i18n.upd_tx(quote_literal(E'ru_RU'), quote_literal(E'aboriginal/tsi only'), quote_literal(E'только aboriginal/tsi'));
select i18n.upd_tx(quote_literal(E'ru_RU'), quote_literal(E'active'), quote_literal(E'активно'));
select i18n.upd_tx(quote_literal(E'ru_RU'), quote_literal(E'administrative'), quote_literal(E'административно'));
select i18n.upd_tx(quote_literal(E'ru_RU'), quote_literal(E'Administrative'), quote_literal(E'Административно'));
select i18n.upd_tx(quote_literal(E'ru_RU'), quote_literal(E'administrative encounter'), quote_literal(E'обращение администрации'));
select i18n.upd_tx(quote_literal(E'ru_RU'), quote_literal(E'adopted daughter'), quote_literal(E'удочеренная'));
select i18n.upd_tx(quote_literal(E'ru_RU'), quote_literal(E'adopted son'), quote_literal(E'усыновленный'));
select i18n.upd_tx(quote_literal(E'ru_RU'), quote_literal(E'adoptive father'), quote_literal(E'отчим'));
select i18n.upd_tx(quote_literal(E'ru_RU'), quote_literal(E'adoptive mother'), quote_literal(E'мачеха'));
select i18n.upd_tx(quote_literal(E'ru_RU'), quote_literal(E'chart review'), quote_literal(E'просмотр и/б'));
select i18n.upd_tx(quote_literal(E'ru_RU'), quote_literal(E'clinical'), quote_literal(E'клинический'));
select i18n.upd_tx(quote_literal(E'ru_RU'), quote_literal(E'clinically not relevant'), quote_literal(E'клинически незначимо'));
select i18n.upd_tx(quote_literal(E'ru_RU'), quote_literal(E'clinically relevant'), quote_literal(E'клинически значимо'));
select i18n.upd_tx(quote_literal(E'ru_RU'), quote_literal(E'closed'), quote_literal(E'закрытый'));
select i18n.upd_tx(quote_literal(E'ru_RU'), quote_literal(E'emergency encounter'), quote_literal(E'экстренное'));
select i18n.upd_tx(quote_literal(E'ru_RU'), quote_literal(E'fax consultation'), quote_literal(E'консультация по факсу'));
select i18n.upd_tx(quote_literal(E'ru_RU'), quote_literal(E'home visit'), quote_literal(E'посещение на дому'));
select i18n.upd_tx(quote_literal(E'ru_RU'), quote_literal(E'hospital visit'), quote_literal(E'посещение в больницу'));
select i18n.upd_tx(quote_literal(E'ru_RU'), quote_literal(E'in surgery'), quote_literal(E'в хирургию'));
select i18n.upd_tx(quote_literal(E'ru_RU'), quote_literal(E'nursing home visit'), quote_literal(E'медсестра на дому'));
select i18n.upd_tx(quote_literal(E'ru_RU'), quote_literal(E'other encounter'), quote_literal(E'прочие'));
select i18n.upd_tx(quote_literal(E'ru_RU'), quote_literal(E'patient photograph'), quote_literal(E'фотография пациента'));
select i18n.upd_tx(quote_literal(E'ru_RU'), quote_literal(E'phone consultation'), quote_literal(E'консультация по телефону'));
select i18n.upd_tx(quote_literal(E'ru_RU'), quote_literal(E'phone w/ caregiver'), quote_literal(E'звонок от сиделки'));
select i18n.upd_tx(quote_literal(E'ru_RU'), quote_literal(E'phone w/ patient'), quote_literal(E'звонок от пациента'));
select i18n.upd_tx(quote_literal(E'ru_RU'), quote_literal(E'phone w/ provider'), quote_literal(E'звонок от специалиста'));
select i18n.upd_tx(quote_literal(E'ru_RU'), quote_literal(E'proxy encounter'), quote_literal(E'обращение доверенного лица'));
select i18n.upd_tx(quote_literal(E'ru_RU'), quote_literal(E'referral report other'), quote_literal(E'другое сообщение о направлении'));
select i18n.upd_tx(quote_literal(E'ru_RU'), quote_literal(E'repeat script'), quote_literal(E'дублирование'));
select i18n.upd_tx(quote_literal(E'ru_RU'), quote_literal(E'video conference'), quote_literal(E'видеоконференция'));

\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-russian_translations.sql', '16.11');
