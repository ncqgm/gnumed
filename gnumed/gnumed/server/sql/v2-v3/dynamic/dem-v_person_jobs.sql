-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: dem-v_person_jobs.sql,v 1.1 2006-11-19 10:16:20 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view dem.v_person_jobs;
\set ON_ERROR_STOP 1

create view dem.v_person_jobs as

select
	lj2p.fk_identity as pk_identity,
	lj2p.fk_occupation as pk_occupation,
	vbp.firstnames,
	vbp.lastnames,
	vbp.preferred,
	vbp.dob,
	vbp.gender,
	o.name as occupation,
	_(o.name) as l10n_occupation,
	lj2p.activities,
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

comment on view dem.v_person_jobs is
	'denormalizes the jobs a person has';

-- --------------------------------------------------------------
grant select on dem.v_person_jobs to group "gm-doctors";

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: dem-v_person_jobs.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: dem-v_person_jobs.sql,v $
-- Revision 1.1  2006-11-19 10:16:20  ncq
-- - add this view
--
-- Revision 1.5  2006/10/24 13:09:45  ncq
-- - What it does duplicates the change log so axe it
--
-- Revision 1.4  2006/09/28 14:39:51  ncq
-- - add comment template
--
-- Revision 1.3  2006/09/18 17:32:53  ncq
-- - make more fool-proof
--
-- Revision 1.2  2006/09/16 21:47:37  ncq
-- - improvements
--
-- Revision 1.1  2006/09/16 14:02:36  ncq
-- - use this as a template for change scripts
--
--
