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
-- .amount
comment on column ref.consumable_substance.amount is
	'The amount of substance.';

\unset ON_ERROR_STOP
alter table ref.consumable_substance drop constraint ref_consumable_sane_amount cascade;
\set ON_ERROR_STOP 1

alter table ref.consumable_substance
	alter column amount
		set not null;

alter table ref.consumable_substance
	add constraint ref_consumable_sane_amount
		check (amount >= 0);

-- --------------------------------------------------------------
-- table constraints
\unset ON_ERROR_STOP
alter table ref.consumable_substance drop constraint ref_consumable_uniq_subst_amount_unit cascade;
\set ON_ERROR_STOP 1

alter table ref.consumable_substance
	add constraint ref_consumable_uniq_subst_amount_unit
		unique(upper(description), amount, unit);

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-ref-consumable_substance-dynamic.sql', 'Revision: v16');

-- ==============================================================
