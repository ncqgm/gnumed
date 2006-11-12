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
-- $Id: dem-v_address.sql,v 1.2 2006-11-12 23:25:52 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create view dem.v_address as
select
	adr.id as pk_address,
	vstr.street,
	vstr.postcode,
	adr.aux_street as notes_street,
	adr.number,
	adr.subunit,
	adr.addendum as notes_subunit,
	adr.lat_lon as lat_lon_address,
	vstr.postcode_street,
	vstr.lat_lon_street,
	vstr.suburb,
	vstr.urb,
	vstr.postcode_urb,
	vstr.lat_lon_urb,
	vstr.code_state,
	vstr.state,
	vstr.l10n_state,
	vstr.code_country,
	vstr.country,
	vstr.l10n_country,
	vstr.country_deprecated,
	adr.id_street as pk_street,
	vstr.pk_urb,
	vstr.pk_state,
	adr.xmin as xmin_address
from
	dem.address adr,
	dem.v_street vstr
where
	adr.id_street = vstr.pk_street
;


comment on view dem.v_address is
	'fully denormalizes data about addresses as entities in themselves';

-- --------------------------------------------------------------
grant select on dem.v_address to group "gm-doctors";

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: dem-v_address.sql,v $', '$Revision: 1.2 $');


-- ==============================================================
-- $Log: dem-v_address.sql,v $
-- Revision 1.2  2006-11-12 23:25:52  ncq
-- - include l10n_*, postcode
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
