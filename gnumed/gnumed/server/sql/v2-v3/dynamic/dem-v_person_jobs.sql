-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: dem-v_person_jobs.sql,v 1.2 2006-11-26 14:19:22 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
drop view if exists dem.v_person_jobs cascade;

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

comment on view dem.v_person_jobs is
	'denormalizes the jobs a person has';

-- --------------------------------------------------------------
grant select on dem.v_person_jobs to group "gm-doctors";

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: dem-v_person_jobs.sql,v $', '$Revision: 1.2 $');
