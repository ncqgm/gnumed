-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
delete from cfg.report_query where label = 'reminders: list due ones across all patients';
delete from cfg.report_query where label = 'reminders: list overdue ones across all patients';
insert into cfg.report_query (label, cmd) values (
	'reminders: list overdue ones across all patients',
'SELECT
	person.lastnames || '', '' || person.firstnames || coalesce('' ('' || person.preferred || '')'', '''') as patient,
	person.l10n_gender,
	person.dob,
	inbox.*,
	person.deceased,
	person.comment,
	person.emergency_contact
FROM
	dem.v_message_inbox inbox
		join
	dem.v_basic_person person
		on
	(person.pk_identity = inbox.pk_patient)
WHERE
	is_overdue
;');

-- --------------------------------------------------------------
select gm.log_script_insertion('v18-cfg-report_query.sql', '18.0');
