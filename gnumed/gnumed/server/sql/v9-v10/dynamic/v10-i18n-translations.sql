set default_transaction_read_only to off;

\unset ON_ERROR_STOP

select i18n.upd_tx('de_DE', 'Central African Republic', 'Zentralafrikanische Republik');

select i18n.upd_tx('de_DE', 'japanese B encephalitis', 'Japanische Enzephalitis B');
select i18n.upd_tx('de_DE', 'varicella', 'Varizellen');
select i18n.upd_tx('de_DE', 'yellow fever', 'Gelbfieber');
select i18n.upd_tx('de_DE', 'female only', 'nur Frauen');

select i18n.upd_tx('de_DE', 'Allergy state', 'Allergiestatus');
select i18n.upd_tx('de_DE', 'no known allergies', 'keine bekannten Allergie');
select i18n.upd_tx('de_DE', 'does have allergies', 'Allergien vorhanden');
select i18n.upd_tx('de_DE', 'unknown, unasked', 'unbekannt, nicht erfragt');
select i18n.upd_tx('de_DE', 'last confirmed', 'zuletzt überprüft');

\set ON_ERROR_STOP 1
