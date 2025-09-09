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
INSERT INTO dem.message_inbox (
	fk_staff,
	fk_inbox_item_type,
	comment,
	data
) VALUES (
	(select pk from dem.staff where db_user = 'any-doc'),
	(select pk_type from dem.v_inbox_item_type where type = 'memo' and category = 'administrative'),
	'Release Notes for GNUmed 1.8.22 (database v22.32)',
	'GNUmed 1.8.22 Release Notes:

	1.8.22

FIX: SOAP: auto-resizing input text field [thanks Maria]
FIX: SOAP: tabbing in auto-resizing STC [thanks Maria]
FIX: medication: adding substance dose [thanks Maria]
FIX: medication: adding intake [thanks vboxuser]
FIX: backport mailcap import on Python 3.13 [thanks María]
FIX: backport packaging.version import on Python 3.13 [thanks María]
FIX: PACS plugin: better connect handling

IMPROVED: EMR presentations naming (tabs/menu items) [thanks Maria]
IMPROVED: i18n: added translatable strings [thanks Maria]
IMPROVED: GUI: detection of dark theme [thanks Maria]
IMPROVED: dependancy checker
IMPROVED: PACS: support SSL connection with Orthanc PACS

	22.32

FIX: crash on bootstrapping v15+ servers [thanks Maria]
FIX: bootstrapping: add WITH ADMIN to gm-dbo [thanks Maria]
FIX: upgrade: add WITH ADMIN to gm-dbo [thanks Maria]
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-release_notes-fixup.sql', '22.32@1.8.22');
