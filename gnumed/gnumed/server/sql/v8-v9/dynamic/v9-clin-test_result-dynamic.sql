-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v9-clin-test_result-dynamic.sql,v 1.7 2008-08-17 10:33:08 ncq Exp $
-- $Revision: 1.7 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
set check_function_bodies to 'on';

--set default_transaction_read_only to off;

-- --------------------------------------------------------------
-- clin.test_result
select gm.add_table_for_notifies('clin', 'test_result');


comment on column clin.test_result.note_test_org is
	'A comment on the test result provided by the tester or testing entity.';


\unset ON_ERROR_STOP
drop function clin.trf_invalidate_review_on_result_change() cascade;
\set ON_ERROR_STOP 1

create function clin.trf_invalidate_review_on_result_change()
	returns trigger
	language 'plpgsql'
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
		-- write note into clin_narrative ? (same with blobs.doc_obj)
	end if;

	return NEW;
END;';

create trigger tr_invalidate_review_on_result_change
	after update on clin.test_result
	for each row execute procedure clin.trf_invalidate_review_on_result_change()
;

-- --------------------------------------------------------------
-- clin.reviewed_test_results
select gm.add_table_for_notifies('clin', 'reviewed_test_results');


alter table clin.reviewed_test_results
	add constraint unique_review_per_row unique(fk_reviewed_row);

-- create rule r_no_del_clin_reviewed_test_results as
--	on delete to clin.reviewed_test_results do instead
--		nothing;

-- comment on rule r_no_del_clin_reviewed_test_results on clin.reviewed_test_results is
-- 'Once a review exists it cannot be deleted anymore.';


revoke delete on clin.reviewed_test_results from public, "gm-doctors", "gm-public" cascade;
grant delete on clin.reviewed_test_results to "gm-dbo";


\unset ON_ERROR_STOP
drop function clin.f_fk_reviewer_default() cascade;
\set ON_ERROR_STOP 1

create function clin.f_fk_reviewer_default()
	returns integer
	language 'plpgsql'
	as '
declare
	_pk_staff integer;
begin
	select pk into _pk_staff from dem.staff where db_user = current_user;
	return _pk_staff;
end;';

alter table clin.reviewed_test_results
	alter column fk_reviewer
		set default clin.f_fk_reviewer_default();


\unset ON_ERROR_STOP
drop function clin.trf_notify_reviewer_of_review_change() cascade;
\set ON_ERROR_STOP 1

create function clin.trf_notify_reviewer_of_review_change()
	returns trigger
	language 'plpgsql'
	as '
declare
	_pk_patient integer;
	_pk_type integer;
begin
	-- disallow change of referenced row
	-- for cleanliness this really *should* be in another trigger
	if NEW.fk_reviewed_row <> OLD.fk_reviewed_row then
		raise exception ''Attaching an existing review to another test result is not allowed (fk_reviewed_row change).'';
		return NEW;
	end if;

	-- change of last reviewer ?
	if NEW.fk_reviewer = OLD.fk_reviewer then
		return NEW;
	end if;

	-- review change ?
	if (NEW.is_technically_abnormal <> OLD.is_technically_abnormal) or
	   (NEW.clinically_relevant <> OLD.clinically_relevant) then

		-- find patient for test result
		select pk_patient into _pk_patient
			from clin.v_test_results
			where pk_test_result = OLD.fk_reviewed_row;

		-- find inbox item type
		select pk_type into _pk_type
			from dem.v_inbox_item_type where
			type = ''results review change'';
		-- create it if necessary
		if not found then
			insert into dem.inbox_item_type (
				fk_inbox_item_category,
				description
			) values (
				(select pk from dem.item_inbox_category where description = ''clinical''),
				''results review change''
			);
			select pk_type into _pk_type
				from dem.v_inbox_item_type where
				type = ''results review change'';
		end if;

		-- already notified ?
		perform 1 from dem.provider_inbox where
			fk_staff = OLD.fk_reviewer
			and fk_inbox_item_type = _pk_type
			and ufk_context = _pk_patient;
		-- nope, so notify now
		if not found then
			insert into dem.provider_inbox (
				fk_staff, fk_inbox_item_type, comment, ufk_context
			) values (
				OLD.fk_reviewer,
				_pk_type,
				(select
					_(''results review changed for patient'') || '' ['' || vpb.lastnames || '', '' || vbp.firstnames || '']''
					from dem.v_basic_person vbp
					where vpb.pk_identity = _pk_patient
				),
				_pk_patient
			);
		end if;
	end if;

	return NEW;
end;';

create trigger tr_notify_reviewer_of_review_change
	before update on clin.reviewed_test_results
	for each row execute procedure clin.trf_notify_reviewer_of_review_change()
;


select i18n.i18n('results review change');
select i18n.i18n('results review changed for patient');

select i18n.upd_tx('de_DE', 'results review change', 'Ergebnisbewertung geändert');
select i18n.upd_tx('de_DE', 'results review changed for patient', 'Bewertung von Testergebnissen änderte sich beim Patienten');

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v9-clin-test_result-dynamic.sql,v $', '$Revision: 1.7 $');

-- ==============================================================
-- $Log: v9-clin-test_result-dynamic.sql,v $
-- Revision 1.7  2008-08-17 10:33:08  ncq
-- - comment out note
--
-- Revision 1.6  2008/08/16 19:35:50  ncq
-- - invalidate existing review if test result value / unit / type changes
--
-- Revision 1.5  2008/06/24 14:03:55  ncq
-- - can't have DO NOTHING ON DELETE rule on reviews table as
--   that will prevent deletes cascaded from test result deletions,
--   instead, revoke DELETE from users
--
-- Revision 1.4  2008/04/22 21:21:03  ncq
-- - function for clin.reviewed_test_results.fk_reviwer default value
--
-- Revision 1.3  2008/04/14 17:14:48  ncq
-- - setup clin.test_result and clin.reviewed_test_results for notification
-- - popular request wants one review per result row, not one per provider per row
-- - notify previous reviewer by trigger of review change
--
-- Revision 1.2  2008/03/02 11:28:18  ncq
-- - renaming col must be done in static
--
-- Revision 1.1  2008/02/26 16:24:01  ncq
-- - note_provider -> note_test_org
-- - fk_test_org -> nullable
--
--
