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
DELETE FROM ref.paperwork_templates WHERE name_long = 'Begleitbrief ohne medizinische Daten [K.Hilbert]';

UPDATE ref.paperwork_templates SET
	name_short = 'Begleitbrief [K.Hilbert]',
	name_long = 'Begleitbrief [K.Hilbert]'
WHERE
	name_long = 'Begleitbrief mit Diagnosen [K.Hilbert]';

-- --------------------------------------------------------------
-- invoices
DELETE FROM ref.paperwork_templates WHERE name_long = 'Invoice with VAT (GNUmed default)';

INSERT INTO ref.paperwork_templates (
	fk_template_type,
	instance_type,
	name_short,
	name_long,
	external_version,
	engine,
	filename,
	data
) values (
	(select pk from ref.form_types where name = 'invoice'),
	'invoice',
	'Invoice (VAT)',
	'Invoice with VAT (GNUmed default)',
	'23.0',
	'L',
	'invoice.tex',
	'real template missing'::bytea
);

DELETE FROM ref.paperwork_templates WHERE name_long = 'Invoice without VAT (GNUmed default)';

INSERT INTO ref.paperwork_templates (
	fk_template_type,
	instance_type,
	name_short,
	name_long,
	external_version,
	engine,
	filename,
	data
) values (
	(select pk from ref.form_types where name = 'invoice'),
	'invoice',
	'Invoice (w/o VAT)',
	'Invoice without VAT (GNUmed default)',
	'23.0',
	'L',
	'invoice.tex',
	'real template missing'::bytea
);

-- --------------------------------------------------------------
ALTER TABLE ref.paperwork_templates
	ALTER COLUMN engine
		SET DEFAULT 'L';

--ALTER TABLE ref.paperwork_templates
--	DROP constraint IF EXISTS ref_templates_engine_range;

--ALTER TABLE ref.paperwork_templates
--	DROP constraint IF EXISTS ref__pw_templates__engine__range;

--ALTER TABLE ref.paperwork_templates
--	ADD constraint ref__pw_templates__engine__range CHECK (
--		engine = ANY(ARRAY['T'::text, 'L'::text, 'H'::text, 'I'::text, 'G'::text, 'P'::text, 'A'::text, 'X'::text, 'S'::text])
--	);

-- --------------------------------------------------------------
DELETE FROM audit.audited_tables WHERE
	schema = 'ref'
		AND
	table_name = 'paperwork_templates';

DROP TABLE if exists
	audit.log_paperwork_templates cascade;

DROP function if exists audit.ft_ins_paperwork_templates() cascade;
DROP function if exists audit.ft_upd_paperwork_templates() cascade;
DROP function if exists audit.ft_del_paperwork_templates() cascade;

ALTER TABLE ref.paperwork_templates
	NO INHERIT audit.audit_fields;

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-ref-paperwork_templates.sql', '23.0');
