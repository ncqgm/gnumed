-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v10-clin-trf_invalidate_review_on_result_change-fixup.sql,v 1.2 2009-08-08 10:36:06 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop function clin.trf_invalidate_review_on_result_change() cascade;
\set ON_ERROR_STOP 1


create or replace function clin.trf_invalidate_review_on_result_change()
	returns trigger
	language 'plpgsql'
	security definer
	as '
DECLARE
	is_modified bool;
BEGIN
	is_modified := False;

	-- change of test type
	if NEW.fk_type != OLD.fk_type then
		is_modified := True;
	end if;

	-- change of numeric value
	if NEW.val_num != OLD.val_num then
		is_modified := True;
	end if;

	-- change of alpha value
	if NEW.val_alpha != OLD.val_alpha then
		is_modified := True;
	end if;

	-- change of unit
	if NEW.val_unit != OLD.val_unit then
		is_modified := True;
	end if;

	if is_modified is True then
		delete from clin.reviewed_test_results where fk_reviewed_row = OLD.pk;
	end if;

	return NEW;
END;';

create trigger tr_invalidate_review_on_result_change
	after update on clin.test_result
	for each row execute procedure clin.trf_invalidate_review_on_result_change()
;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-clin-trf_invalidate_review_on_result_change-fixup.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: v10-clin-trf_invalidate_review_on_result_change-fixup.sql,v $
-- Revision 1.2  2009-08-08 10:36:06  ncq
-- - fix review trigger on modifying test data
--
--