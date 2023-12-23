-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
drop view if exists clin.v_pat_allergy_state cascade;


create view clin.v_pat_allergy_state as
select
	(select fk_patient from clin.encounter where pk = a.fk_encounter)
		as pk_patient,
	a.modified_when,
	coalesce (
		(select short_alias from dem.staff where db_user = a.modified_by),
		'<' || a.modified_by || '>'
	)
		as modified_by,
	a.last_confirmed,
	a.has_allergy,
	a.comment,
	a.fk_encounter
		as pk_encounter,
	a.pk as pk_allergy_state,
	a.xmin as xmin_allergy_state
from
	clin.allergy_state a
;

grant select on clin.v_pat_allergy_state to group "gm-doctors";

-- --------------------------------------------------------------
select i18n.i18n('asked, but unknown');

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-v_pat_allergy_state.sql', 'v23');
