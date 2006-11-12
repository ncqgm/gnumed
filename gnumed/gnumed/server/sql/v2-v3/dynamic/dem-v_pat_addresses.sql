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
-- $Id: dem-v_pat_addresses.sql,v 1.1 2006-11-12 23:24:37 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view dem.v_pat_adresses cascade;
\set ON_ERROR_STOP 1

create view dem.v_pat_addresses as
select
	vbp.pk_identity,
	va.pk_address,
	at.name as address_type,
	_(at.name) as l10n_address_type,

	vbp.title,
	vbp.firstnames,
	vbp.lastnames,
	vbp.dob,
	vbp.cob,
	vbp.gender,
	vbp.l10n_gender,
	vbp.preferred,

	va.street,
	va.postcode,
	va.notes_street,
	va.number,
	va.subunit,
	va.notes_subunit,
	va.lat_lon_address,
	va.postcode_street,
	va.lat_lon_street,
	va.suburb,
	va.urb,
	va.postcode_urb,
	va.lat_lon_urb,
	va.code_state,
	va.state,
	va.l10n_state,
	va.code_country,
	va.country,
	va.l10n_country,
	va.country_deprecated,
	va.pk_street,
	va.pk_urb,
	va.pk_state,

	lpoa.id as pk_lnk_person_org_address,
	lpoa.id_type as pk_address_type,

	lpoa.xmin as xmin_lnk_person_org_address
from
	dem.v_address va,
	dem.lnk_person_org_address lpoa,
	dem.v_basic_person vbp,
	dem.address_type at
where
	lpoa.id_identity = vbp.pk_identity and
	lpoa.id_address = va.pk_address and
	lpoa.id_type = at.id
;


comment on view dem.v_pat_addresses is
	'denormalized addressed per patient';

-- --------------------------------------------------------------
-- don't forget appropriate grants
grant select on dem.v_pat_addresses to group "gm-doctors";

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: dem-v_pat_addresses.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: dem-v_pat_addresses.sql,v $
-- Revision 1.1  2006-11-12 23:24:37  ncq
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
