-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v10-dem-v_person_jobs.sql,v 1.1 2008-12-22 18:55:17 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view dem.v_person_jobs cascade;
\set ON_ERROR_STOP 1


create view dem.v_person_jobs as

select
	lj2p.fk_identity as pk_identity,
	vbp.firstnames,
	vbp.lastnames,
	vbp.preferred,
	vbp.dob,
	vbp.gender,
	o.name as occupation,
	_(o.name) as l10n_occupation,
	lj2p.activities,
	lj2p.modified_when as modified_when,
	lj2p.fk_occupation as pk_occupation,
	lj2p.pk as pk_lnk_job2person,
	lj2p.xmin as xmin_lnk_job2person
from
	dem.lnk_job2person lj2p,
	dem.v_basic_person vbp,
	dem.occupation o
where
	lj2p.fk_identity = vbp.pk_identity and
	lj2p.fk_occupation = o.id
;


comment on view dem.v_person_jobs is 'denormalizes the jobs a person has';


revoke all on dem.v_person_jobs from public;
grant select on dem.v_person_jobs to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-dem-v_person_jobs.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v10-dem-v_person_jobs.sql,v $
-- Revision 1.1  2008-12-22 18:55:17  ncq
-- - were dropped
--
--