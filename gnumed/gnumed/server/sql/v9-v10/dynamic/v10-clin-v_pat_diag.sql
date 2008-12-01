-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- $Id: v10-clin-v_pat_diag.sql,v 1.1 2008-12-01 12:09:41 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- remember to handle dependant objects possibly dropped by CASCADE
\unset ON_ERROR_STOP
drop view clin.v_pat_diag cascade;
\set ON_ERROR_STOP 1


create view clin.v_pat_diag as
select
	vpi.pk_patient as pk_patient,
	cn.clin_when as diagnosed_when,
	cn.narrative as diagnosis,
	cd.laterality as laterality,
	cd.is_chronic as is_chronic,
	cd.is_active as is_active,
	cd.is_definite as is_definite,
	cd.clinically_relevant as clinically_relevant,
	cd.pk as pk_diag,
	cd.fk_narrative as pk_narrative,
	cn.fk_encounter as pk_encounter,
	cn.fk_episode as pk_episode,
	cd.xmin as xmin_clin_diag,
	cn.xmin as xmin_clin_narrative
from
	clin.clin_diag cd,
	clin.clin_narrative as cn,
	clin.v_pat_items vpi
where
	cn.soap_cat = 'a'
		and
	cd.fk_narrative = cn.pk
		and
	cn.pk_item = vpi.pk_item
;


comment on view clin.v_pat_diag is
	'denormalizing view over diagnoses per patient';

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-clin-v_pat_diag.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v10-clin-v_pat_diag.sql,v $
-- Revision 1.1  2008-12-01 12:09:41  ncq
-- - new
--
--