-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- What it does:
-- - fix v_pat_narrative_soap
--
-- License: GPL
-- Author: 
-- 
-- ==============================================================
-- $Id: clin-v_pat_narrative_soap.sql,v 1.2 2006-12-11 17:05:12 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_pat_narrative_soap cascade;
\set ON_ERROR_STOP 1


create view clin.v_pat_narrative_soap as
SELECT
	vpep.pk_patient
		AS pk_patient,
	cn.clin_when
		AS date, 
	coalesce (
		(select short_alias from dem.staff where db_user = cn.modified_by),
		'<' || cn.modified_by || '>'
	) as provider,
	cn.soap_cat
		as soap_cat,
	cn.narrative
		as narrative,
	cn.pk_item
		as pk_item,
	cn.pk
		AS pk_narrative,
	vpep.pk_health_issue
		AS pk_health_issue,
	cn.fk_episode
		AS pk_episode,
	cn.fk_encounter
		AS pk_encounter,
	cn.xmin
		AS xmin_clin_narrative
FROM
	clin.clin_narrative cn,
	clin.v_pat_episodes vpep
WHERE
	vpep.pk_episode = cn.fk_episode
;


comment on view clin.v_pat_narrative_soap is
	'patient SOAP-only narrative;
	 this view aggregates all clin.clin_narrative rows
	 and adds denormalized context';


grant select on clin.v_pat_narrative_soap to group "gm-doctors";

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: clin-v_pat_narrative_soap.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: clin-v_pat_narrative_soap.sql,v $
-- Revision 1.2  2006-12-11 17:05:12  ncq
-- - redo view
--
-- Revision 1.1  2006/09/30 10:33:01  ncq
-- - add missing grants
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
