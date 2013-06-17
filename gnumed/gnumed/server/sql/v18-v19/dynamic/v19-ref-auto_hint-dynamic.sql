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
\unset ON_ERROR_STOP
DELETE FROM ref.auto_hint WHERE title = 'GKV-Checkup überfällig';
\set ON_ERROR_STOP 1

insert into ref.auto_hint(query, title, hint, url, source, lang) values (
	'SELECT (
	SELECT
		d_i.dob is not NULL
	FROM
		dem.identity d_i
	WHERE
		d_i.pk = ID_ACTIVE_PATIENT

) AND (
	SELECT
		age(d_i.dob) >= ''35 years''::interval
	FROM
		dem.identity d_i
	WHERE
		d_i.pk = ID_ACTIVE_PATIENT

) AND (
	SELECT
		d_i.deceased is not NULL
	FROM
		dem.identity d_i
	WHERE
		d_i.pk = ID_ACTIVE_PATIENT

) AND NOT EXISTS (
	SELECT 1 FROM clin.v_emr_journal
	WHERE
		pk_patient = ID_ACTIVE_PATIENT
			AND
		narrative ~* ''.*checkup.*''
			AND
		age(clin_when) < ''2 years''::interval
);',
	'GKV-Checkup überfällig',
	'Der Patient hatte in den letzten 2 Jahren keinen GKV-Checkup.',
	'die üblichen Verdächtigen',
	'GNUmed default',
	'de'
);


-- --------------------------------------------------------------
DELETE FROM ref.auto_hint WHERE title = 'Kontraindikation: ACE/Sartan <-> Schwangerschaft';

insert into ref.auto_hint(query, title, hint, url, source, lang) values (
	'SELECT EXISTS (
	SELECT 1 FROM clin.v_substance_intakes WHERE
		pk_patient = ID_ACTIVE_PATIENT
			AND
		substance ~* ''.*sartan.*''
			OR
		substance ~* ''.*angiotensin.*''
			OR
		substance ~ ''.*ACE.*''
			OR
		substance ~* ''.*pril.*''
			OR
		atc_brand ~* ''^C09.*''
			OR
		atc_substance ~* ''^C09.*''
) AND EXISTS (
	SELECT 1 FROM clin.v_narrative4search WHERE
		pk_patient = ID_ACTIVE_PATIENT
			AND
		narrative ~* ''.*schwanger.*''
);',
	'Kontraindikation: ACE/Sartan <-> Schwangerschaft',
	'ACE-Hemmer und Sartane können im 2. und 3. Trimenon schwere Fetopathien hervorrufen.',
	'http://www.akdae.de/Arzneimittelsicherheit/Bekanntgaben/Archiv/2010/201010151.pdf',
	'GNUmed default (AkdÄ 2012)',
	'de'
);
-- --------------------------------------------------------------
select gm.log_script_insertion('v19-ref-auto_hint-dynamic.sql', '19.0');
