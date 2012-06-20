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
INSERT INTO clin.encounter_type(description)
	SELECT
		i18n.i18n('phone w/ patient')
	where not exists (
		select 1 from clin.encounter_type
		where description = 'phone w/ patient'
	);

INSERT INTO clin.encounter_type(description)
	SELECT
		i18n.i18n('phone w/ provider')
	where not exists (
		select 1 from clin.encounter_type
		where description = 'phone w/ provider'
	);

INSERT INTO clin.encounter_type(description)
	SELECT
		i18n.i18n('phone w/ caregiver')
	where not exists (
		select 1 from clin.encounter_type
		where description = 'phone w/ caregiver'
	);


select i18n.upd_tx('de', 'phone w/ patient', 'Telefonat mit Patient');
select i18n.upd_tx('de', 'phone w/ provider', 'Telefonat mit Arzt/Behandler');
select i18n.upd_tx('de', 'phone w/ caregiver', 'Telefonat mit Pflegeperson');

select i18n.upd_tx('de', 'Privacy notice', 'Datenschutzhinweis');

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-clin-encounter_types.sql', 'Revision 1');

-- ==============================================================
