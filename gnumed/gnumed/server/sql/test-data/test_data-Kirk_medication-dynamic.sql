-- =============================================
-- Project GNUmed

-- James T. Kirk current substances list entries

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL v2 or later
--
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/test-data/test_data-Kirk_medication-dynamic.sql,v $
-- $Revision: 1.3 $
-- =============================================

-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

--set default_transaction_read_only to off;

--begin;
-- =============================================

-- delete Kirk's current medication
delete from clin.substance_intake where
	fk_encounter in (
		select pk from clin.encounter where fk_patient = (
			select pk_identity from dem.v_basic_person
			where firstnames = 'James Tiberius' and lastnames = 'Kirk' and date_trunc('day', dob) = '1931-3-21'
		)
	);


-- add MetoPharm comp. brand
delete from clin.substance_brand where
	description = 'MetoPharm comp.'
	and preparation = 'tablets'
;

insert into clin.substance_brand (
	description,
	preparation,
	atc_code,
	is_fake
) values (
	'MetoPharm comp.',
	'tablets',
	'C07BB52',
	False
);

delete from clin.active_substance where description = 'Metoprolol';

insert into clin.active_substance (
	description,
	atc_code
) values (
	'Metoprolol',
	'C07AB02'
);

insert into clin.substance_intake (
	fk_encounter,
	fk_episode,
	fk_brand,
	fk_substance,
	clin_when,
	schedule,
	aim,
	narrative,
	strength,
	preparation,
	duration,
	intake_is_approved_of
) values (
	(select pk from clin.encounter
	 where fk_patient = (
		select pk_identity from dem.v_basic_person
		where firstnames = 'James Tiberius' and lastnames = 'Kirk' and date_trunc('day', dob) = '1931-3-21'
	 )
	 limit 1
	),
	(select pk_episode from clin.v_pat_episodes
	 where pk_patient = (
		select pk_identity from dem.v_basic_person
		where firstnames = 'James Tiberius' and lastnames = 'Kirk' and date_trunc('day', dob) = '1931-3-21'
	 )
	 limit 1
	),
	(select pk from clin.substance_brand where description = 'MetoPharm comp.' and preparation = 'tablets'),
	(select pk from clin.active_substance where description = 'Metoprolol'),
	(now() - '6 years 2 months 4 days'::interval),
	'1-0-0-0',
	'lower CV risk via RR',
	'report pulse < 60',
	'100mg',
	'tablets',
	'10 years'::interval,
	True
);

delete from clin.active_substance where description = 'HCT';

insert into clin.active_substance (
	description,
	atc_code
) values (
	'HCT',
	'C03AA03'
);

insert into clin.substance_intake (
	fk_encounter,
	fk_episode,
	fk_brand,
	fk_substance,
	clin_when,
	schedule,
	aim,
	narrative,
	strength,
	preparation,
	duration,
	intake_is_approved_of
) values (
	(select pk from clin.encounter
	 where fk_patient = (
		select pk_identity from dem.v_basic_person
		where firstnames = 'James Tiberius' and lastnames = 'Kirk' and date_trunc('day', dob) = '1931-3-21'
	 )
	 limit 1
	),
	(select pk_episode from clin.v_pat_episodes
	 where pk_patient = (
		select pk_identity from dem.v_basic_person
		where firstnames = 'James Tiberius' and lastnames = 'Kirk' and date_trunc('day', dob) = '1931-3-21'
	 )
	 limit 1
	),
	(select pk from clin.substance_brand where description = 'MetoPharm comp.' and preparation = 'tablets'),
	(select pk from clin.active_substance where description = 'HCT'),
	(now() - '6 years 2 months 4 days'::interval),
	'1-0-0-0',
	'lower CV risk via RR',
	'report increased nightly bladder activity',
	'12.5mg',
	'tablets',
	'10 years'::interval,
	True
);

-- =============================================
-- do simple schema revision tracking
select gm.log_script_insertion('$RCSfile: test_data-Kirk_medication-dynamic.sql,v $', '$Revision: 1.3 $');

-- comment out the "rollback" if you want to
-- really store the above patient data
--rollback;
--commit;

-- =============================================
-- $Log: test_data-Kirk_medication-dynamic.sql,v $
-- Revision 1.3  2009-07-09 16:50:41  ncq
-- - cleanup
--
-- Revision 1.2  2009/06/04 16:36:15  ncq
-- - use intake-is-approved-of
--
-- Revision 1.1  2009/05/12 12:00:18  ncq
-- - Kirk medication entries
--
--