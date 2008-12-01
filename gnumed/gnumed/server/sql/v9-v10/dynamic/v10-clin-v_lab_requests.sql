-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- $Id: v10-clin-v_lab_requests.sql,v 1.1 2008-12-01 12:09:42 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- remember to handle dependant objects possibly dropped by CASCADE
\unset ON_ERROR_STOP
drop clin.v_lab_requests cascade;
\set ON_ERROR_STOP 1


create or replace view clin.v_lab_requests as
select
	vpi.pk_patient as pk_patient,
	lr.pk as pk_request,
	torg.internal_name as lab_name,
	lr.request_id as request_id,
	lr.lab_request_id as lab_request_id,
	lr.clin_when as sampled_when,
	lr.lab_rxd_when as lab_rxd_when,
	lr.results_reported_when as results_reported_when,
	lr.request_status as request_status,
	_(lr.request_status) as l10n_request_status,
	lr.is_pending as is_pending,
	lr.narrative as progress_note,
	lr.fk_test_org as pk_test_org,
	lr.fk_requestor as pk_requestor,
	lr.fk_encounter as pk_encounter,
	lr.fk_episode as pk_episode,
	vpi.pk_health_issue as pk_health_issue,
	lr.pk_item as pk_item,
	lr.modified_when as modified_when,
	lr.modified_by as modified_by,
	lr.soap_cat as soap_cat,
	lr.xmin as xmin_lab_request
from
	clin.lab_request lr,
	clin.test_org torg,
	clin.v_pat_items vpi
where
	lr.fk_test_org = torg.pk
		and
	vpi.pk_item = lr.pk_item
;


comment on view clin.v_lab_requests is
	'denormalizes lab requests per test organization';

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-clin-v_lab_requests.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v10-clin-v_lab_requests.sql,v $
-- Revision 1.1  2008-12-01 12:09:42  ncq
-- - new
--
--