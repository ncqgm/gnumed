-- =============================================
-- Project GNUmed

-- James T. Kirk test data: second CRP result for a particular day

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL v2 or later
--
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/test-data/test_data-Kirk-diagnostic_certainty-dynamic.sql,v $
-- $Revision: 1.1 $
-- =============================================

-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

--set default_transaction_read_only to off;

--begin;
-- =============================================
update clin.health_issue
set
	diagnostic_certainty_classification = 'D'
where
	description = 'post appendectomy/peritonitis'
		and
	fk_encounter in (select pk from clin.encounter where fk_patient = 12)
;


update clin.health_issue
set
	diagnostic_certainty_classification = 'C'
where
	description = '9/2000 extraterrestrial infection'
		and
	fk_encounter in (select pk from clin.encounter where fk_patient = 12)
;

-- =============================================
-- do simple schema revision tracking
select gm.log_script_insertion('$RCSfile: test_data-Kirk-diagnostic_certainty-dynamic.sql,v $', '$Revision: 1.1 $');

-- comment out the "rollback" if you want to
-- really store the above patient data
--rollback;
--commit;

-- =============================================
-- $Log: test_data-Kirk-diagnostic_certainty-dynamic.sql,v $
-- Revision 1.1  2009-09-01 22:11:26  ncq
-- - new
--
--