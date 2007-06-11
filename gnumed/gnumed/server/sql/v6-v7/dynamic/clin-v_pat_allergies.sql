-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v6
-- Target database version: v7
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- $Id: clin-v_pat_allergies.sql,v 1.1 2007-06-11 18:41:31 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_pat_allergies cascade;
\set ON_ERROR_STOP 1

create view clin.v_pat_allergies as
select
	a.pk as pk_allergy,
	vpep.pk_patient as pk_patient,
	a.soap_cat as soap_cat,
	case when coalesce(trim(both from a.allergene), '') = ''
		then a.substance
		else a.allergene
	end as descriptor,
	a.allergene as allergene,
	a.substance as substance,
	a.substance_code as substance_code,
	a.generics as generics,
	a.generic_specific as generic_specific,
	a.atc_code as atc_code,
	at.value as type,
	_(at.value) as l10n_type,
	a.definite as definite,
	a.narrative as reaction,
	a.fk_type as pk_type,
	a.pk_item as pk_item,
	a.clin_when as date,
	vpep.pk_health_issue as pk_health_issue,
	a.fk_episode as pk_episode,
	a.fk_encounter as pk_encounter,
	a.modified_when as modified_when,
	a.modified_by as modified_by,
	a.xmin as xmin_allergy
from
	clin.allergy a,
	clin._enum_allergy_type at,
	clin.v_pat_episodes vpep
where
	vpep.pk_episode = a.fk_episode
		and
	at.pk = a.fk_type
;

comment on view clin.v_pat_allergies is
	'denormalizes clin.allergy';

-- --------------------------------------------------------------
grant select on clin.v_pat_allergies to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: clin-v_pat_allergies.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: clin-v_pat_allergies.sql,v $
-- Revision 1.1  2007-06-11 18:41:31  ncq
-- - new
--
-- Revision 1.7  2007/05/07 16:32:09  ncq
-- - log_script_insertion() now in gm.
--
-- Revision 1.6  2007/01/27 21:16:08  ncq
-- - the begin/commit does not fit into our change script model
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
