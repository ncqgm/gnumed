-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

set check_function_bodies to on;

-- --------------------------------------------------------------
-- list discussion showed that we do want to be able to document
-- non-conformant and clinically "wrong" vaccinations (such as
-- two tetanus boosters within 1 week) -- but we can still do
-- something about it ...


-- eventually add the trigger to warn on potential dupes
\unset ON_ERROR_STOP
drop function clin.trf_warn_on_duplicate_vaccinations() cascade;
\set ON_ERROR_STOP 1

create function clin.trf_warn_on_duplicate_vaccinations()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_NEW_pk_patient integer;

	_NEW_vaccination record;
	_NEW_vacc_label text;

	_prev_vacc_loop_record record;
	_prev_vaccination record;
	_prev_vacc_label text;

	_indication_collision integer;

	msg text;
	_pk_current_provider integer;
BEGIN
	-- find patient for NEW vaccination
	select fk_patient into _NEW_pk_patient from clin.encounter where pk = NEW.fk_encounter;

	-- load denormalized vaccination corresponding to NEW vaccination
	select * into _NEW_vaccination from clin.v_pat_vaccinations where pk_vaccination = NEW.pk;

	-- generate label for NEW vaccination
	_NEW_vacc_label := to_char(_NEW_vaccination.date_given, ''YYYY-MM-DD'')
		|| '' (#'' || _NEW_vaccination.pk_vaccination || ''): ''
		|| _NEW_vaccination.vaccine
		|| '' ('' || array_to_string(_NEW_vaccination.l10n_indications, '', '') || '')'';

	-- loop over ...
	for _prev_vacc_loop_record in
		-- ... vaccinations ...
		SELECT * FROM clin.vaccination cv
		WHERE
			-- ... of this patient ...
			cv.fk_encounter in (select ce.pk from clin.encounter ce where ce.fk_patient = _NEW_pk_patient)
				AND
			-- ... within 7 days of the vaccination date ...
			cv.clin_when BETWEEN (NEW.clin_when - ''7 days''::interval) AND (NEW.clin_when + ''7 days''::interval)
				AND
			-- ... not the vaccination we just INSERTed/UPDATEed
			cv.pk != NEW.pk
	loop

		select * into _indication_collision from ((
			select fk_indication from clin.lnk_vaccine2inds where fk_vaccine = NEW.fk_vaccine
		) INTERSECT (
			select fk_indication from clin.lnk_vaccine2inds where fk_vaccine = _prev_vacc_loop_record.fk_vaccine
		)) as colliding_indications;

		if FOUND then

			-- retrieve denormalized data corresponding to that previous vaccination
			select * into _prev_vaccination from clin.v_pat_vaccinations where pk_vaccination = _prev_vacc_loop_record.pk;

			-- generate label for that previous vaccination
			_prev_vacc_label := to_char(_prev_vaccination.date_given, ''YYYY-MM-DD'')
				|| '' (#'' || _prev_vaccination.pk_vaccination || ''): ''
				|| _prev_vaccination.vaccine
				|| '' ('' || array_to_string(_prev_vaccination.l10n_indications, '', '') || '')'';

			msg := _prev_vacc_label || E''\n'' || _NEW_vacc_label;

			select pk into _pk_current_provider from dem.staff where db_user = session_user;

			-- create inbox message for current user
			insert into dem.message_inbox (
				fk_staff,
				fk_inbox_item_type,
				comment,
				data,
				importance,
				ufk_context,
				fk_patient
			) values (
				_pk_current_provider,
				(select pk_type from dem.v_inbox_item_type where type = ''review vaccs'' and category = ''clinical''),
				_(''Two vaccinations with overlapping target conditions recorded within one week of each other !''),
				msg,
				1,
				ARRAY[_NEW_vaccination.pk_vaccination,_prev_vaccination.pk_vaccination],
				_NEW_pk_patient
			);

			-- create inbox message for vaccinating provider if known
			if NEW.fk_provider is not NULL then
				-- and not identical to session user
				if NEW.fk_provider != _pk_current_provider then
					insert into dem.message_inbox (
						fk_staff,
						fk_inbox_item_type,
						comment,
						data,
						importance,
						ufk_context,
						fk_patient
					) values (
						NEW.fk_provider,
						(select pk_type from dem.v_inbox_item_type where type = ''review vaccs'' and category = ''clinical''),
						_(''Two vaccinations with overlapping target conditions recorded within one week of each other !''),
						msg,
						1,
						ARRAY[_NEW_vaccination.pk_vaccination,_prev_vaccination.pk_vaccination],
						_NEW_pk_patient
					);
				end if;
			end if;

		end if;

	end loop;

	return NEW;
END;';


comment on function clin.trf_warn_on_duplicate_vaccinations() is
'Sends a notification to the inbox of both current_user and
 clin.vaccination.fk_provider (if not NULL) in case a new or updated
 vaccination falls within 1 week of another vaccination with (even
 partially) overlapping indications.';



create trigger tr_warn_on_duplicate_vaccinations
	after insert or update on clin.vaccination
		for each row execute procedure clin.trf_warn_on_duplicate_vaccinations()
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v14-clin-vaccination-dynamic.sql', 'Revision: 1.1');
