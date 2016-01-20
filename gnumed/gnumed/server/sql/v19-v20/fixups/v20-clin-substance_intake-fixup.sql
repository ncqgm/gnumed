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
	_intake_id integer;
	_pseudo_episode_id integer;
BEGIN
	-- loop over intakes w/o episode
	FOR _intake_id, _curr_pat_id IN select pk_substance_intake, pk_patient from clin.v_nonbrand_intakes where pk_episode is null LOOP

		-- add pseudo episode
		insert into clin.episode (description, is_open, fk_encounter)
		select
			''substance use'',
			False,
			-- most recent encounter
			(select pk from clin.encounter where fk_patient = _curr_pat_id order by last_affirmed desc limit 1)
		 where not exists (
			select 1 from clin.v_pat_episodes where description = ''substance use'' and pk_patient = _curr_pat_id
		);

		-- get newly created or preexisting episode
		select pk_episode INTO STRICT _pseudo_episode_id from clin.v_pat_episodes
		where
			description = ''substance use''
				and
			pk_patient = _curr_pat_id;

		-- update intake
		update clin.substance_intake set
			fk_episode = _pseudo_episode_id
		where
			pk = _intake_id;

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
