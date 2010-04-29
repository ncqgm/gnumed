-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

set check_function_bodies to on;

-- --------------------------------------------------------------
-- .narrative
comment on column clin.vaccination.narrative is
	'Used to record a comment on this vaccination.';

\unset ON_ERROR_STOP
alter table clin.vaccination drop constraint vaccination_sane_narrative cascade;
\set ON_ERROR_STOP 1

alter table clin.vaccination
	add constraint vaccination_sane_narrative check (
		gm.is_null_or_non_empty_string(narrative) is true
	);


-- .reaction
comment on column clin.vaccination.reaction is
	'Used to record reactions to this vaccination.';

\unset ON_ERROR_STOP
alter table clin.vaccination drop constraint vaccination_sane_reaction cascade;
\set ON_ERROR_STOP 1

alter table clin.vaccination
	add constraint vaccination_sane_reaction check (
		gm.is_null_or_non_empty_string(reaction) is true
	);


-- .site
comment on column clin.vaccination.site is
	'The site of injection used in this vaccination.';

\unset ON_ERROR_STOP
alter table clin.vaccination drop constraint vaccination_sane_site cascade;
\set ON_ERROR_STOP 1

alter table clin.vaccination
	add constraint vaccination_sane_site check (
		gm.is_null_or_non_empty_string(site) is true
	);

alter table clin.vaccination
	alter column site
		set default null;

-- --------------------------------------------------------------
-- trigger to ensure that UNIQUE(clin_when, pk_patient, fk_vaccine) holds

\unset ON_ERROR_STOP
drop function clin.trf_sanity_check_no_duplicate_vaccinations() cascade;
\set ON_ERROR_STOP 1

create function clin.trf_sanity_check_no_duplicate_vaccinations()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_NEW_pk_patient integer;
	_row record;
	_indication_collision integer;
BEGIN
	select fk_patient into _NEW_pk_patient from clin.episode where pk = NEW.fk_episode;

	-- loop over ...
	for _row in
		-- ... vaccinations ...
		SELECT * FROM clin.vaccination
		WHERE
			-- ... of this patient ...
			NEW.fk_episode in (select pk from clin.episode where fk_patient = _NEW_pk_patient)
				and
			-- ... within 2 days of the vaccination date
			clin_when BETWEEN (NEW.clin_when - ''2 days''::interval) AND (NEW.clin_when + ''2 days''::interval)
	loop

		select (
			select fk_indication from clin.link_vaccine2inds where fk_vaccine = NEW.fk_vaccine
		) INTERSECT (
			select fk_indication from clin.link_vaccine2inds where fk_vaccine = _row.fk_vaccine
		) into _indication_collision;

		if FOUND then
			raise exception ''[clin.vaccination]: INSERT/UPDATE failed: vaccinations [%] and [%] share the indication [%] within 2 days of each other'', NEW.pk, _row.pk, _indication_collision;
			return NEW;
		end if;

	end loop;

	return NEW;
END;';


create trigger tr_sanity_check_no_duplicate_vaccinations
	before insert or update on clin.vaccination
		for each row execute procedure clin.trf_sanity_check_no_duplicate_vaccinations()
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v14-clin-vaccination-dynamic.sql', 'Revision: 1.1');
