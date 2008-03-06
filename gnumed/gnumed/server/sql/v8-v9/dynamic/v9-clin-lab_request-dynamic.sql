-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v9-clin-lab_request-dynamic.sql,v 1.3 2008-03-06 23:20:56 ncq Exp $
-- $Revision: 1.3 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table clin.lab_request
	alter column fk_test_org
		drop not null;


select audit.add_table_for_audit('clin', 'lab_request');


comment on column clin.lab_request.diagnostic_service_section is
'The (section of) the diagnostic service which performed the test.
- HL7 2.3: OBR:24 Diagnostic Service Section ID
- somewhat redundant with fk_test_org, which, however,
  points to more normalized data';


comment on column clin.lab_request.ordered_service is
'The (battery of) test(s)/service(s) ordered.
- HL7 2.3: OBR:4 Universal Service ID';


-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v9-clin-lab_request-dynamic.sql,v $', '$Revision: 1.3 $');

-- ==============================================================
-- $Log: v9-clin-lab_request-dynamic.sql,v $
-- Revision 1.3  2008-03-06 23:20:56  ncq
-- - mark for auditing
--
-- Revision 1.2  2008/03/05 22:31:07  ncq
-- - add comments
--
--
