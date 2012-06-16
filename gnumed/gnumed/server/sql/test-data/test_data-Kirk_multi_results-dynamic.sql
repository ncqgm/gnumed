-- =============================================
-- Project GNUmed

-- James T. Kirk test data: second CRP result for a particular day

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL v2 or later
--
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/test-data/test_data-Kirk_multi_results-dynamic.sql,v $
-- $Revision: 1.1 $
-- =============================================

-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

--set default_transaction_read_only to off;

--begin;
-- =============================================
-- CRP
insert into clin.test_result (
	clin_when,
	fk_encounter,
	fk_episode,
	fk_type,
	val_num,
	val_unit,
	val_normal_range,
	abnormality_indicator,
	material,
	fk_intended_reviewer
) values (
	'2000-9-17 19:47',

	(select fk_encounter
	from clin.test_result
	where
		fk_type = (select pk from clin.test_type where code = 'CRP-EML')
	and
		date_trunc('day', clin_when) = '2000-9-17'
	limit 1),

	(select fk_episode
	from clin.test_result
	where
		fk_type = (select pk from clin.test_type where code = 'CRP-EML')
	and
		date_trunc('day', clin_when) = '2000-9-17'
	limit 1),

	(select pk from clin.test_type where code='CRP-EML'),

	'14.5',
	'mg/l',
	'0.07-8',
	'++',
	'Serum',

	(select pk_staff from dem.v_staff where firstnames = 'Leonard Horatio' and lastnames = 'McCoy')
);

-- =============================================
-- do simple schema revision tracking
select gm.log_script_insertion('$RCSfile: test_data-Kirk_multi_results-dynamic.sql,v $', '$Revision: 1.1 $');

-- comment out the "rollback" if you want to
-- really store the above patient data
--rollback;
--commit;

-- =============================================
-- $Log: test_data-Kirk_multi_results-dynamic.sql,v $
-- Revision 1.1  2009-07-09 16:40:14  ncq
-- - newly added
--
--