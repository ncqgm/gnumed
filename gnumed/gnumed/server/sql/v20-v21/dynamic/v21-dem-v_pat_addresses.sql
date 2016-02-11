-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
drop view if exists dem.v_pat_adresses cascade;


create or replace view dem.v_pat_addresses as
select
	d_vp.pk_identity,
	d_va.pk_address,
	d_at.name as address_type,
	_(d_at.name) as l10n_address_type,

	d_vp.title,
	d_vp.firstnames,
	d_vp.lastnames,
	d_vp.dob,
	d_vp.gender,
	d_vp.l10n_gender,
	d_vp.preferred,

	d_va.street,
	d_va.postcode,
	d_va.notes_street,
	d_va.number,
	d_va.subunit,
	d_va.notes_subunit,
	d_va.lat_lon_address,
	d_va.postcode_street,
	d_va.lat_lon_street,
	d_va.suburb,
	d_va.urb,
	d_va.postcode_urb,
	d_va.lat_lon_urb,
	d_va.code_region,
	d_va.region,
	d_va.l10n_region,
	d_va.code_country,
	d_va.country,
	d_va.l10n_country,
	d_va.country_deprecated,
	d_va.pk_street,
	d_va.pk_urb,
	d_va.pk_region,

	d_lpoa.id as pk_lnk_person_org_address,
	d_lpoa.id_type as pk_address_type,

	d_lpoa.xmin as xmin_lnk_person_org_address
from
	dem.v_address d_va,
	dem.lnk_person_org_address d_lpoa,
	dem.v_all_persons d_vp,
	dem.address_type d_at
where
	d_lpoa.id_identity = d_vp.pk_identity and
	d_lpoa.id_address = d_va.pk_address and
	d_lpoa.id_type = d_at.id
;


comment on view dem.v_pat_addresses is 'denormalized addresses per person';


revoke all on dem.v_pat_addresses from public;
grant select on dem.v_pat_addresses to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-dem-v_pat_addresses.sql', '21.0');
