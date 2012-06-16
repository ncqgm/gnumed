-- =============================================
-- Project GNUmed

-- James T. Kirk test data

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL v2 or later
--
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/test-data/test_data-Kirk-procedure-dynamic.sql,v $
-- $Revision: 1.2 $
-- =============================================

-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

--set default_transaction_read_only to off;

--begin;
-- =============================================
\unset ON_ERROR_STOP

insert into clin.procedure (
	clin_when,
	fk_encounter,
	fk_episode,
	narrative,
	soap_cat,
	clin_where,
	fk_hospital_stay
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

	'laparoscopic lavage of abdominal cavity',
	'p',
	null,

	(select pk from clin.hospital_stay
	 where
		fk_encounter = (
			select pk from clin.encounter
			where fk_patient = (
				select pk_identity from dem.v_basic_person
				where firstnames = 'James Tiberius' and lastnames = 'Kirk' and date_trunc('day', dob) = '1931-3-21'
	 		)
			limit 1
		) and
		fk_episode = (
			select pk_episode from clin.v_pat_episodes
			where pk_patient = (
				select pk_identity from dem.v_basic_person
				where firstnames = 'James Tiberius' and lastnames = 'Kirk' and date_trunc('day', dob) = '1931-3-21'
				)	and
				description = 'abdominal lap'
					and
				health_issue like '%peritonitis%'
			limit 1
		)
	)

);

\set ON_ERROR_STOP 1

-- =============================================
-- do simple schema revision tracking
select gm.log_script_insertion('$RCSfile: test_data-Kirk-procedure-dynamic.sql,v $', '$Revision: 1.2 $');

-- comment out the "rollback" if you want to
-- really store the above patient data
--rollback;
--commit;

-- =============================================
-- $Log: test_data-Kirk-procedure-dynamic.sql,v $
-- Revision 1.2  2009-10-23 09:43:38  ncq
-- - make optional
--
-- Revision 1.1  2009/09/17 21:50:29  ncq
-- - add a procedure
--
-- Revision 1.1  2009/09/01 22:11:26  ncq
-- - new
--
--