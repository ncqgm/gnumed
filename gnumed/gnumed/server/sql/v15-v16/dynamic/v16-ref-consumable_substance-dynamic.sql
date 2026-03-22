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

alter table ref.consumable_substance drop constraint if exists ref_consumable_sane_amount cascade;

alter table ref.consumable_substance
	alter column amount
		set not null;

alter table ref.consumable_substance
	add constraint ref_consumable_sane_amount
		check (amount >= 0);

-- --------------------------------------------------------------
-- table constraints
alter table ref.consumable_substance drop constraint if exists ref_consumable_uniq_subst_amount_unit cascade;

alter table ref.consumable_substance
	add constraint ref_consumable_uniq_subst_amount_unit
		unique(description, amount, unit);

-- --------------------------------------------------------------
update ref.consumable_substance set
	description = 'Chlordiazepoxide'
where
	description = 'Chlodiazepoxide';


update ref.consumable_substance set
	description = 'Enalapril Maleate'
where
	description = 'Enalpril Maleate';


update ref.consumable_substance set
	description = 'Acabose'
where
	description = 'Acarbose';

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-ref-consumable_substance-dynamic.sql', '16.0');
