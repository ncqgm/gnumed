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
-- $Id: dem-v_urb.sql,v 1.2 2006-11-12 23:26:42 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create view dem.v_urb as

select
	u.id as pk_urb,
	u.name as urb,
	u.postcode as postcode_urb,
	u.lat_lon as lat_lon_urb,
	vs.code_state,
	vs.state,
	vs.l10n_state,
	vs.code_country,
	vs.country,
	vs.l10n_country,
	vs.country_deprecated,
	u.id_state as pk_state,
	u.xmin as xmin_urb
from
	dem.urb u,
	dem.v_state vs

where
	vs.pk_state = u.id_state
;


comment on view dem.v_urb is
	'denormalizes urb data';

-- --------------------------------------------------------------
grant select on dem.v_urb to group "gm-doctors";

-- --------------------------------------------------------------
select public.log_script_insertion('asdf$RCSfile: dem-v_urb.sql,v $', '$Revision: 1.2 $');


-- ==============================================================
-- $Log: dem-v_urb.sql,v $
-- Revision 1.2  2006-11-12 23:26:42  ncq
-- - add l10n_* things
--
-- Revision 1.1  2006/11/09 20:21:56  ncq
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
