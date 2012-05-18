-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
set check_function_bodies to on;
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
comment on table ref.auto_hint is
	'This table stores SQL queries and the associated hints. If the query returns TRUE the client should display the hint.';

select audit.register_table_for_auditing('ref', 'auto_hint');

grant select on ref.auto_hint to group "gm-public";

-- --------------------------------------------------------------
-- .title
comment on column ref.auto_hint.title is 'A short title to summarize and identify the hint.';

\unset ON_ERROR_STOP
alter table ref.auto_hint drop constraint ref_auto_hint_sane_title cascade;
alter table ref.auto_hint drop constraint ref_auto_hint_uniq_title cascade;
\set ON_ERROR_STOP 1

alter table ref.auto_hint
	add constraint ref_auto_hint_sane_title
		check (gm.is_null_or_blank_string(title) is False);

alter table ref.auto_hint
	add constraint ref_auto_hint_uniq_title
		unique(title);

-- --------------------------------------------------------------
-- .query
comment on column ref.auto_hint.query is 'This query is run against the database.';

\unset ON_ERROR_STOP
alter table ref.auto_hint drop constraint ref_auto_hint_sane_query cascade;
alter table ref.auto_hint drop constraint ref_auto_hint_uniq_query cascade;
\set ON_ERROR_STOP 1

alter table ref.auto_hint
	add constraint ref_auto_hint_sane_query
		check (gm.is_null_or_blank_string(query) is False);

alter table ref.auto_hint
	add constraint ref_auto_hint_uniq_query
		unique(query);

-- --------------------------------------------------------------
-- .hint
comment on column ref.auto_hint.hint is 'When the query returns true this is the hint that should be displayed.';

\unset ON_ERROR_STOP
alter table ref.auto_hint drop constraint ref_auto_hint_sane_hint cascade;
\set ON_ERROR_STOP 1

alter table ref.auto_hint
	add constraint ref_auto_hint_sane_hint
		check (gm.is_null_or_blank_string(hint) is False);

-- --------------------------------------------------------------
-- .url
comment on column ref.auto_hint.url is 'An URL relevant to the hint.';

alter table ref.auto_hint
	alter column url
		set default null;

\unset ON_ERROR_STOP
alter table ref.auto_hint drop constraint ref_auto_hint_sane_url cascade;
\set ON_ERROR_STOP 1

alter table ref.auto_hint
	add constraint ref_auto_hint_sane_url
		check (gm.is_null_or_non_empty_string(url));

-- --------------------------------------------------------------
-- .is_active
comment on column ref.auto_hint.is_active is 'Whether or not this query/hint is active.';

alter table ref.auto_hint
	alter column is_active
		set not null;

alter table ref.auto_hint
	alter column is_active
		set default true;

-- --------------------------------------------------------------
-- .source
comment on column ref.auto_hint.source is 'Who provided query and hint.';

\unset ON_ERROR_STOP
alter table ref.auto_hint drop constraint ref_auto_hint_sane_source cascade;
\set ON_ERROR_STOP 1

alter table ref.auto_hint
	add constraint ref_auto_hint_sane_source
		check (gm.is_null_or_blank_string(source) is false);

-- --------------------------------------------------------------
-- .lang
comment on column ref.auto_hint.lang is 'The language the hint is written in.';

\unset ON_ERROR_STOP
alter table ref.auto_hint drop constraint ref_auto_hint_sane_lang cascade;
\set ON_ERROR_STOP 1

alter table ref.auto_hint
	add constraint ref_auto_hint_sane_lang
		check (gm.is_null_or_blank_string(lang) is false);

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
DELETE FROM ref.auto_hint WHERE title = 'Startrek: Denevan neural parasite screening';
\set ON_ERROR_STOP 1

insert into ref.auto_hint(query, title, hint, url, source, lang) values (
	'SELECT EXISTS(SELECT 1 FROM clin.v_family_history WHERE condition ~* ''denevan.*parasit'' AND pk_patient = ID_ACTIVE_PATIENT);',
	'Startrek: Denevan neural parasite screening',
	'Patients with exposure to Denevan Neural Parasite carriers should undergo EEG scanning and brain imaging bi-annually.',
	'http://www.startrek.com/database_article/denevan-neural-parasite',
	'Starfleet Central Preventive Task Force (v17.0)',
	'en'
);


-- --------------------------------------------------------------
\unset ON_ERROR_STOP
DELETE FROM ref.auto_hint WHERE title = 'Kontraindikation: ACE/Sartan <-> Schwangerschaft';
\set ON_ERROR_STOP 1

insert into ref.auto_hint(query, title, hint, url, source, lang) values (
	'SELECT EXISTS (
	SELECT 1 FROM clin.v_pat_substance_intake WHERE
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
create or replace function clin.get_hints_for_patient(integer)
	returns setof ref.auto_hint
	language 'plpgsql'
	as '
DECLARE
	_pk_identity ALIAS FOR $1;
	_r ref.auto_hint%rowtype;
	_query text;
	_applies boolean;
BEGIN
	FOR _r IN SELECT * FROM ref.auto_hint WHERE is_active LOOP
		_query := replace(_r.query, ''ID_ACTIVE_PATIENT'', _pk_identity::text);
		--RAISE NOTICE ''%'', _query;
		EXECUTE _query INTO STRICT _applies;
		--RAISE NOTICE ''Applies: %'', _applies;
		IF _applies THEN
			RETURN NEXT _r;
		END IF;
	END LOOP;
	RETURN;
END;';

-- --------------------------------------------------------------
select gm.log_script_insertion('v17-ref-auto_hint-dynamic.sql', '17.0');
