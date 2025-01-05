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
-- trigger to ensure that at the end of a tx a product still has components (doses) left
drop function if exists ref.trf_assert_product_keeps_components() cascade;

create function ref.trf_assert_product_keeps_components()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_msg text;
BEGIN
	-- find components for given drug product
	PERFORM 1 FROM ref.lnk_dose2drug WHERE fk_drug_product = OLD.fk_drug_product LIMIT 1;
	IF FOUND THEN
		RETURN OLD;
	END IF;

	-- perhaps the drug product has been deleted, too ?
	PERFORM 1 FROM ref.drug_product WHERE pk = OLD.fk_drug_product LIMIT 1;
	IF NOT FOUND THEN
		RETURN OLD;
	END IF;

	_msg := ''[ref.trf_assert_product_keeps_components()]: ''
		|| TG_OP
		|| '' failed: no components (doses) linked to drug product [''
		|| OLD.fk_drug_product
		|| ''] anymore.''
	;
	RAISE EXCEPTION integrity_constraint_violation using message = _msg;
	RETURN OLD;
END;';

create constraint trigger tr_del_assert_product_keeps_components
	after
		delete
	on
		ref.lnk_dose2drug
	deferrable
		initially deferred
	for
		each row
	execute procedure
		ref.trf_assert_product_keeps_components()
;

create constraint trigger tr_upd_assert_product_keeps_components
	after
		update
	on
		ref.lnk_dose2drug
	deferrable
		initially deferred
	for
		each row
	when
		(NEW.fk_drug_product is distinct from OLD.fk_drug_product)
	execute procedure
		ref.trf_assert_product_keeps_components()
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-ref-lnk_dose2drug-dynamic.sql', '23.0');
