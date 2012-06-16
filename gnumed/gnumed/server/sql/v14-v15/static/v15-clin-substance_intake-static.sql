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
-- .fk_drug_component
alter table clin.substance_intake
	add column fk_drug_component integer;

alter table audit.log_substance_intake
	add column fk_drug_component integer;

-- --------------------------------------------------------------
-- .strength: set dummy strength if not set
update clin.substance_intake set
	strength = '99999.1*?*'
where
	(strength is null)
		or
	(trim(strength) = '')
;

-- --------------------------------------------------------------
-- .tmp_unit
alter table clin.substance_intake
	add column tmp_unit text;

-- if not pointing to a drug: extract unit from .strength
update clin.substance_intake set
	tmp_unit = coalesce (
		trim(regexp_replace(trim(strength), E'\\d+[.,]{0,1}\\d*', '')),
		'*?*'
	)
where
	strength is not null;

-- if .unit is empty, set it to default
update clin.substance_intake set
	tmp_unit = '*?*'
where
	trim(tmp_unit) = '';

-- --------------------------------------------------------------
-- .amount
alter table clin.substance_intake
	add column tmp_amount decimal;

-- if not pointing to a drug: extract amount from .strength
update clin.substance_intake set
	tmp_amount = coalesce (
		(select replace(trim((regexp_matches(trim(strength), E'\\d+[.,]{0,1}\\d*'))[1]), ',', '.'))::decimal,
		99999.2
	)
where
	strength is not null;

-- --------------------------------------------------------------
alter table clin.substance_intake
	drop column strength cascade;

alter table audit.log_substance_intake
	drop column strength cascade;

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-ref-lnk_substance2brand-static.sql', 'Revision: 1.1');

-- ==============================================================
