-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v10-clin-v_codes4diag.sql,v 1.1 2008-12-01 12:09:42 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_codes4diag cascade;
\set ON_ERROR_STOP 1


create view clin.v_codes4diag as
select distinct on (diagnosis, code, xfk_coding_system)
	cp.term as diagnosis,
	cp.code as code,
	cp.xfk_coding_system as coding_system
from
	clin.coded_phrase cp
where
	exists(select 1 from clin.v_pat_diag vpd where vpd.diagnosis = cp.term)
;


comment on view clin.v_codes4diag is
	'a lookup view for all the codes associated with a
	 diagnosis, a diagnosis can appear several times,
	  namely once per associated code';


grant select on clin.v_codes4diag to group "gm-doctors";
-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-clin-v_codes4diag.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v10-clin-v_codes4diag.sql,v $
-- Revision 1.1  2008-12-01 12:09:42  ncq
-- - new
--
--