-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- $Id: v11-clin-v_pat_hospital_stays.sql,v 1.1 2009-04-01 15:55:40 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_pat_hospital_stays cascade;
\set ON_ERROR_STOP 1

create view clin.v_pat_hospital_stays as
select
	chs.pk
		as pk_hospital_stay,
	(select fk_patient from clin.encounter where pk = chs.fk_encounter)
		as pk_patient,
	chs.narrative
		as hospital,
	chs.clin_when
		as admission,
	chs.discharge,
	chs.soap_cat
		as soap_cat,
	(select description from clin.episode where pk = chs.fk_episode)
		as episode,
	(select description from clin.health_issue where pk = (
		select fk_health_issue from clin.episode where pk = chs.fk_episode
	))
		as health_issue,
	chs.fk_encounter
		as pk_encounter,
	chs.fk_episode
		as pk_episode,
	(select fk_health_issue from clin.episode where pk = chs.fk_episode)
		as pk_health_issue,
	chs.modified_when
		as modified_when,
	coalesce (
		(select short_alias from dem.staff where db_user = chs.modified_by),
		'<' || chs.modified_by || '>'
	)
		as modified_by,
	chs.row_version,
	chs.xmin
		as xmin_hospital_stay
from
	clin.hospital_stay chs
;

-- --------------------------------------------------------------
grant select on clin.v_pat_hospital_stays to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-clin-v_pat_hospital_stays.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
--