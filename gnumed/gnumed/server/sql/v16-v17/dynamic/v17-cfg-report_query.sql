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
delete from cfg.report_query where label = 'encounters: recently created or modified by the current user';
insert into cfg.report_query (label, cmd) values (
	'encounters: recently created or modified by the current user',
'SELECT DISTINCT ON (pk_encounter)
	to_char(c_e.modified_when,''yyyy.mm.dd hh:mm'') modified,
	d_n.lastnames || '', '' || d_n.firstnames person_encountered,
	c_e.assessment_of_encounter aoe,
	c_e.pk AS pk_encounter,
	c_e.fk_patient pk_patient
FROM
	clin.encounter c_e INNER JOIN dem.names d_n ON c_e.fk_patient = d_n.id_identity
WHERE
	c_e.modified_by = "current_user"()
		AND
	c_e.modified_when > now() - interval ''7 days''
ORDER BY
	pk_encounter, modified_when DESC
;');

-- --------------------------------------------------------------
delete from cfg.report_query where label = 'encounters: recently created or modified by any user';
insert into cfg.report_query (label, cmd) values (
	'encounters: recently created or modified by any user',
'SELECT DISTINCT ON (pk_encounter)
	to_char(c_e.modified_when,''yyyy.mm.dd hh:mm'') modified,
	c_e.modified_by by_user,
	d_n.lastnames || '', '' || d_n.firstnames person_encountered,
	c_e.assessment_of_encounter aoe,
	c_e.pk AS pk_encounter,
	c_e.fk_patient pk_patient
FROM
	clin.encounter c_e INNER JOIN dem.names d_n ON c_e.fk_patient = d_n.id_identity
		AND
	c_e.modified_when > now() - interval ''7 days''
ORDER BY
	pk_encounter, modified_when DESC
;');

-- --------------------------------------------------------------
delete from cfg.report_query where label = 'reminders: list due ones across all patients';
insert into cfg.report_query (label, cmd) values (
	'reminders: list due ones across all patients',
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
	is_due
;');


-- --------------------------------------------------------------
select gm.log_script_insertion('v17-cfg-report_query.sql', '17.0');
