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
	'Release Notes for GNUmed 1.7.4 (database v22.4)',
	'GNUmed 1.7.4 Release Notes:

	1.7.4

NEW: placeholders now nest with $2<>2$ $3<>3$ rather than $<<>>$ $<<<>>>$

NEW: placeholder $<patient_mcf>$
NEW: placeholder $<praxis_mcf>$
NEW: placehodler $<qrcode>$
NEW: placeholder $<if_debugging>$
NEW: LaTeX letter template example
NEW: Begleitbrief mit Diagnosen (LaTeX)

FIX: map None to '' in address parts placeholder
FIX: export area export-to-media
FIX: $<vaccination_history::%(l10n_indications)s::>$ field
FIX: vaccine creation
FIX: error in closing expired episodes
FIX: date formatting in document tree

IMPROVED: AppStream and desktop metadata
IMPROVED: add "preset" option to $<free_text>$ placeholder
IMPROVED: include MCF in export area metadata
IMPROVED: Begleitbrief template

	22.4

FIX: LaTeX-Template for Begleitbrief
FIX: 2nd/3rd level placeholders in LaTeX templates
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-release_notes-fixup.sql', '22.4');
