-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

set check_function_bodies to on;
-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop function gm.strip_allzeros_fraction(numeric) cascade;
\set ON_ERROR_STOP 1

create or replace function gm.strip_allzeros_fraction(numeric)
	returns numeric
	language 'plpgsql'
	returns null on null input
	as '
DECLARE
	_numeric_value alias for $1;
	_fraction numeric;
	_msg text;
BEGIN
	_fraction := _numeric_value - trunc(_numeric_value);
	if _fraction <> 0 then
		return _numeric_value;
	end if;
	BEGIN
		return _numeric_value::bigint::numeric;
	EXCEPTION
		WHEN numeric_value_out_of_range THEN
			RAISE NOTICE ''[gm.strip_allzeros_fraction]: cannot strip from %'', _numeric_value;
			RETURN _numeric_value;
	END;
END;';


comment on function gm.strip_allzeros_fraction(numeric) is
	'Remove fractions containing only zeros (n.000...) from NUMERICs/DECIMALs.';


-- apply to ref.consumable_substance
update ref.consumable_substance set
	amount = gm.strip_allzeros_fraction(amount);

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop function ref.trf_consumable_subst_normalize_amount() cascade;
\set ON_ERROR_STOP 1

create or replace function ref.trf_consumable_subst_normalize_amount()
	returns trigger
	language 'plpgsql'
	as '
BEGIN
	NEW.amount := gm.strip_allzeros_fraction(NEW.amount);
	return NEW;
END;';


comment on function ref.trf_consumable_subst_normalize_amount() is
	'On INSERT/UPDATE drop .000 all-zero fractions from amounts.';

create trigger tr_consumable_subst_normalize_amount
	before insert or update on ref.consumable_substance
	for each row execute procedure ref.trf_consumable_subst_normalize_amount();


-- --------------------------------------------------------------
select gm.log_script_insertion('v17-ref-consumable_substance-fixup.sql', '17.4');
