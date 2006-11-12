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
-- $Id: dem-v_street.sql,v 1.2 2006-11-12 23:26:42 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create view dem.v_street as

select
	st.id as pk_street,
	st.name as street,
	coalesce(st.postcode, vu.postcode_urb) as postcode,
	st.postcode as postcode_street,
	st.lat_lon as lat_lon_street,
	st.suburb as suburb,
	vu.urb,
	vu.postcode_urb,
	vu.lat_lon_urb,
	vu.code_state,
	vu.state,
	vu.l10n_state,
	vu.code_country,
	vu.country,
	vu.l10n_country,
	vu.country_deprecated,
	st.id_urb as pk_urb,
	vu.pk_state,
	st.xmin as xmin_street
from
	dem.street st,
	dem.v_urb vu
where
	st.id_urb = vu.pk_urb
;


comment on view dem.v_street is
	'denormalizes street data';

-- --------------------------------------------------------------
grant select on dem.v_street to group "gm-doctors";

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfiledf: zzz-template.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: dem-v_street.sql,v $
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
