-- =============================================
-- Project GNUmed

-- James T. Kirk hospital stays test data

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
--
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/test-data/test_data-Kirk_hospital_stay-dynamic.sql,v $
-- $Revision: 1.1 $
-- =============================================

-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

set default_transaction_read_only to off;

begin;
-- =============================================
-- (select pk_identity from dem.v_basic_person where firstnames = 'James Tiberius' and lastnames = 'Kirk' and date_trunc('day', dob) = '1931-3-21')

delete from clin.episode where
	fk_encounter in (
		select pk from clin.encounter where fk_patient = (
			select pk_identity from dem.v_basic_person
			where firstnames = 'James Tiberius' and lastnames = 'Kirk' and date_trunc('day', dob) = '1931-3-21'
		)
	) and
	description = 'abdominal lap'
;

insert into clin.episode (
	fk_health_issue,
	description,
	is_open,
	fk_encounter
) values (
	1,
	'abdominal lap',
	False,
	(select pk from clin.encounter
	 where fk_patient = (
		select pk_identity from dem.v_basic_person
		where firstnames = 'James Tiberius' and lastnames = 'Kirk' and date_trunc('day', dob) = '1931-3-21'
	 )
	 limit 1
	)
);

delete from clin.hospital_stay where
	fk_encounter in (
		select pk from clin.encounter where fk_patient = (
			select pk_identity from dem.v_basic_person
			where firstnames = 'James Tiberius' and lastnames = 'Kirk' and date_trunc('day', dob) = '1931-3-21'
		)
	);

insert into clin.hospital_stay (
	fk_encounter,
	fk_episode,
	soap_cat,
	narrative,
	clin_when,
	discharge
) values (
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
	 ) and
	 health_issue like '%peritonitis%'
	 limit 1
	),
	null,
	'Enterprise Healthcare Unit',
	now() - '9 years 5 month 10 days'::interval,
	now() - '9 years 5 month 2 days'::interval
);

-- =============================================
-- do simple schema revision tracking
select gm.log_script_insertion('$RCSfile: test_data-Kirk_hospital_stay-dynamic.sql,v $', '$Revision: 1.1 $');

-- comment out the "rollback" if you want to
-- really store the above patient data
--rollback;
commit;

-- =============================================
-- $Log: test_data-Kirk_hospital_stay-dynamic.sql,v $
-- Revision 1.1  2009-05-13 10:34:58  ncq
-- - add a hospital stay
--
--