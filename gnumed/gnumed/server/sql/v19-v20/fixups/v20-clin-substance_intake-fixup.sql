-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

set check_function_bodies to 1;
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
-- .fk_episode
create or replace function gm._add_substance_use_episodes()
	returns boolean
	language plpgsql
	as '
DECLARE
	_curr_pat_id integer;
	_curr_intake_id integer;
	_substance_use_episode_id integer;
BEGIN
	-- loop over intakes w/o episode
	FOR
		_curr_intake_id, _curr_pat_id
	IN
		select pk_substance_intake, pk_patient from clin.v_nonbrand_intakes where pk_episode is null
	LOOP

		-- select substance use episode
		select pk_episode INTO STRICT _substance_use_episode_id from clin.v_pat_episodes
		where
			summary ilike ''%[substance use]%''
				and
			pk_patient = _curr_pat_id;

		--- create substance use episode
		IF NOT FOUND THEN
			insert into clin.episode
				(description, is_open, fk_encounter, summary)
			values (
				''substance use'',
				False,
				-- most recent encounter
				(select pk from clin.encounter where fk_patient = _curr_pat_id order by last_affirmed desc limit 1),
				''[substance use] (auto-added by v20.10 @ '' || clock_timestamp()::text || '')''
			)
			returning pk into strict _substance_use_episode_id;
		END IF;

		-- update intake
		update clin.substance_intake set
			fk_episode = _substance_use_episode_id
		where
			pk = _curr_intake_id;

	END LOOP;
	RETURN true;
END;';

select gm._add_substance_use_episodes();

drop function gm._add_substance_use_episodes() cascade;


alter table clin.substance_intake
	alter column fk_episode
		set not null;


alter table clin.substance_intake
	drop constraint if exists sane_fk_episode cascade;


drop function if exists clin.trf_sanity_check_substance_episode() cascade;

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-clin-substance_intake-fixup.sql', '20.10');
