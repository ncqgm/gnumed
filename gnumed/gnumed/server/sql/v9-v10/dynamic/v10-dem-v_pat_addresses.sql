-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v10-dem-v_pat_addresses.sql,v 1.1 2008-12-22 18:55:18 ncq Exp $
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


comment on view dem.v_pat_addresses is 'denormalized addressed per patient';


revoke all on dem.v_pat_addresses from public;
grant select on dem.v_pat_addresses to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-dem-v_pat_addresses.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v10-dem-v_pat_addresses.sql,v $
-- Revision 1.1  2008-12-22 18:55:18  ncq
-- - were dropped
--
--
