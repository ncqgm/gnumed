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
DELETE FROM ref.paperwork_templates WHERE name_long = 'Begleitbrief ohne medizinische Daten [K.Hilbert]';

UPDATE ref.paperwork_templates SET
	name_short = 'Begleitbrief [K.Hilbert]',
	name_long = 'Begleitbrief [K.Hilbert]'
WHERE
	name_long = 'Begleitbrief mit Diagnosen [K.Hilbert]';

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-ref-paperwork_templates.sql', '23.0');
