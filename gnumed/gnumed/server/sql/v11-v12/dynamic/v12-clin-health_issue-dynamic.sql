-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- $Id: v12-clin-health_issue-dynamic.sql,v 1.2 2009-09-01 22:43:14 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
comment on column clin.health_issue.diagnostic_certainty_classification is
'The certainty at which this issue is believed to be a diagnosis:

A: sign (Symptom)
B: cluster of signs (Symptomkomplex)
C: syndromic diagnosis (Bild einer Diagnose)
D: proven diagnosis (diagnostisch gesichert)'
;


alter table clin.health_issue
	add constraint valid_diagnostic_certainty_classification
		check (diagnostic_certainty_classification in ('A', 'B', 'C', 'D', NULL));

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v12-clin-health_issue-dynamic.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: v12-clin-health_issue-dynamic.sql,v $
-- Revision 1.2  2009-09-01 22:43:14  ncq
-- - diagnostic-certainty -> *-classification
--
-- Revision 1.1  2009/08/28 12:45:26  ncq
-- - add diagnostic certainty
--
--
