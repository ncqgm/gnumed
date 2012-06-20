-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1
set default_transaction_read_only to off;

-- --------------------------------------------------------------
select i18n.upd_tx('de', 'meningococcus A', 'Meningokokken Typ A');
select i18n.upd_tx('de', 'meningococcus W', 'Meningokokken Typ W');
select i18n.upd_tx('de', 'meningococcus Y', 'Meningokokken Typ Y');

select i18n.upd_tx('de', 'tuberculosis', 'Tuberkulose');
select i18n.upd_tx('de', 'salmonella typhi (typhoid)', 'Salmonella typhi (Typhus)');
select i18n.upd_tx('de', 'influenza (seasonal)', 'Influenza (sais.)');

select i18n.upd_tx('de', 'Deletion of', 'Löschung:');
select i18n.upd_tx('de', 'Medication history', 'Medikamentenanamnese');

select i18n.upd_tx('de', 'smokes', 'raucht');
select i18n.upd_tx('de', 'often late', 'oft zu spät');
select i18n.upd_tx('de', 'Extra care !', 'Vorsicht');
select i18n.upd_tx('de', 'mobility impairment', 'Gehbehinderung');
select i18n.upd_tx('de', 'minor depression', 'depressoid');
select i18n.upd_tx('de', 'major depression', 'Depression');
select i18n.upd_tx('de', 'choleric', 'cholerisch');

select i18n.upd_tx('de', 'prescription', 'Rezept');

-- --------------------------------------------------------------
insert into dem.country (
	code,
	name
) values (
	'RS',
	'Serbia'
);

select i18n.upd_tx('de', 'Serbia', 'Serbien');

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-i18n-de.sql', 'Revision: 1.1');

-- ==============================================================
