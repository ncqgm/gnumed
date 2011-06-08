-- =============================================
-- Project GNUmed

-- James T. Kirk test data: vaccinations

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL v2 or later
-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

set default_transaction_read_only to off;

begin;
-- =============================================
\unset ON_ERROR_STOP

insert into clin.vaccination (
	clin_when,
	fk_encounter,
	fk_episode,
	fk_provider,
	fk_vaccine,
	narrative,
	site,
	batch_no,
	reaction
) values (
	now() - '9 years 5 months 8 days'::interval,
	(select pk from clin.encounter
	 where fk_patient = (
		select pk_identity from dem.v_basic_person
		where firstnames = 'James Tiberius' and lastnames = 'Kirk' and date_trunc('day', dob) = '1931-3-21'
	 )
	 limit 1
	),

	(select pk_episode from clin.v_pat_episodes
	 where
	 pk_patient = (
		select pk_identity from dem.v_basic_person
		where firstnames = 'James Tiberius' and lastnames = 'Kirk' and date_trunc('day', dob) = '1931-3-21'
	 )
	 	and
	 description = 'abdominal lap'
	 	and
	 health_issue like '%peritonitis%'
	 limit 1
	),

--	(select pk_staff from dem.v_staff where firstnames='Leonard Horatio' and lastnames='McCoy'),
	-1,
	(select pk_vaccine from clin.v_vaccines where vaccine = 'REPEVAX (Repevax)'),

	'needed a booster shot',
	'left deltoid muscle',
	'AH-07/2-11',
	'atypical swelling of injection site and malaise'
);

\set ON_ERROR_STOP 1

-- =============================================
-- do simple schema revision tracking
select gm.log_script_insertion('$RCSfile: test_data-Kirk-vaccinations.sql,v $', '$Revision: 1.2 $');

-- comment out the "rollback" if you want to
-- really store the above patient data
rollback;
commit;

-- =============================================
