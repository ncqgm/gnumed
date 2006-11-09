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
-- $Id: dem-v_state.sql,v 1.1 2006-11-09 20:21:56 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create view dem.v_state as

select
	s.id as pk_state,
	s.code as code_state,
	s.name as state,
	s.country as code_country,
	c.name as country,
	c.deprecated as country_deprecated,
	s.xmin as xmin_state
from
	dem.state as s,
	dem.country as c
where
	c.code = s.country
;

comment on view dem.v_state is
	'denormalizes state information';

-- --------------------------------------------------------------
grant select on dem.v_state to group "gm-doctors";

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: dem-v_state.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: dem-v_state.sql,v $
-- Revision 1.1  2006-11-09 20:21:56  ncq
-- - added
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
