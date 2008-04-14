-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v9-clin-test_result-dynamic.sql,v 1.3 2008-04-14 17:14:48 ncq Exp $
-- $Revision: 1.3 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
set check_function_bodies to 'on';

-- --------------------------------------------------------------
-- clin.test_result
select gm.add_table_for_notifies('clin', 'test_result');

comment on column clin.test_result.note_test_org is
	'A comment on the test result provided by the tester or testing entity.';


-- clin.reviewed_test_results
select gm.add_table_for_notifies('clin', 'reviewed_test_results');

alter table clin.reviewed_test_results
	add constraint unique_review_per_row unique(fk_reviewed_row);

create rule r_no_del_clin_reviewed_test_results as
	on delete to clin.reviewed_test_results do instead
		nothing;

comment on rule r_no_del_clin_reviewed_test_results on clin.reviewed_test_results is
'Once a review exists it cannot be deleted anymore.';

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
select gm.log_script_insertion('$RCSfile: v9-clin-test_result-dynamic.sql,v $', '$Revision: 1.3 $');

-- ==============================================================
-- $Log: v9-clin-test_result-dynamic.sql,v $
-- Revision 1.3  2008-04-14 17:14:48  ncq
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
