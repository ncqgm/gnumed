-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
drop view if exists dem.v_persons cascade;

create or replace view dem.v_persons as
select
	i.pk
		as pk_identity,
	i.title
		as title,
	n.firstnames
		as firstnames,
	n.preferred
		as preferred,
	n.lastnames
		as lastnames,
	i.gender
		as gender,
	_(i.gender)
		as l10n_gender,
	i.dob
		as dob_only,
	(date_trunc('day', i.dob) + coalesce(i.tob, dob::time))
		as dob,
	i.tob
		as tob,
	i.deceased
		as deceased,
	case when i.fk_marital_status is null
		then 'unknown'
		else (select ms.name from dem.marital_status ms, dem.identity i1 where ms.pk = i.fk_marital_status and i1.pk = i.pk)
	end
		as marital_status,
	case when i.fk_marital_status is null
		then _('unknown')
		else (select _(ms1.name) from dem.marital_status ms1, dem.identity i1 where ms1.pk = i.fk_marital_status and i1.pk = i.pk)
	end
		as l10n_marital_status,
	i.emergency_contact
		as emergency_contact,
	i.comment
		as comment,
	i.deleted
		as is_deleted,
	i.fk_marital_status
		as pk_marital_status,
	n.id
		as pk_active_name,
	i.fk_emergency_contact
		as pk_emergency_contact,
	i.fk_primary_provider
		as pk_primary_provider,
	i.xmin
		as xmin_identity,
	i.dob_is_estimated
		as dob_is_estimated,
	i.aux_info
		as aux_info
from
	dem.identity i,
	dem.names n
where
	n.active is true
		and
	n.id_identity = i.pk
;


comment on view dem.v_persons is
'This view denormalizes persons with their active name.';


revoke all on dem.v_persons from public;
grant select on dem.v_persons to group "gm-public";

-- --------------------------------------------------------------
drop view if exists dem.v_all_persons cascade;

create view dem.v_all_persons as
select
	d_i.pk
		as pk_identity,
	d_i.title
		as title,
	d_n.firstnames
		as firstnames,
	d_n.preferred
		as preferred,
	d_n.lastnames
		as lastnames,
	d_i.gender
		as gender,
	_(d_i.gender)
		as l10n_gender,
	d_i.dob
		as dob_only,
	(date_trunc('day', d_i.dob) + coalesce(d_i.tob, dob::time))
		as dob,
	d_i.tob
		as tob,
	d_i.deceased
		as deceased,
	coalesce(d_ms.name, 'unknown')
		as marital_status,
	_(coalesce(d_ms.name, 'unknown'))
		as l10n_marital_status,
	d_i.emergency_contact
		as emergency_contact,
	d_i.comment
		as comment,
	d_i.deleted
		as is_deleted,
	d_i.fk_marital_status
		as pk_marital_status,
	d_n.id
		as pk_active_name,
	d_i.fk_emergency_contact
		as pk_emergency_contact,
	d_i.fk_primary_provider
		as pk_primary_provider,
	d_i.xmin
		as xmin_identity,
	d_i.dob_is_estimated
		as dob_is_estimated,
	d_i.aux_info
		as aux_info
from
	dem.identity d_i
		inner join dem.names d_n on ((d_n.id_identity = d_i.pk) and (d_n.active is true))
			left outer join dem.marital_status d_ms on (d_i.fk_marital_status = d_ms.pk)
;

comment on view dem.v_all_persons is
	'This view denormalizes persons with their active name.';

revoke all on dem.v_all_persons from public;
grant select on dem.v_all_persons to group "gm-public";

-- --------------------------------------------------------------
drop view if exists dem.v_deleted_persons cascade;

create or replace view dem.v_deleted_persons as
select d_vp.*
from dem.v_all_persons d_vp
where
	d_vp.is_deleted is true
;

comment on view dem.v_deleted_persons is
	'This view denormalizes "deleted" persons with their active name.';

revoke all on dem.v_deleted_persons from public;
grant select on dem.v_deleted_persons to group "gm-doctors";

-- --------------------------------------------------------------
drop view if exists dem.v_active_persons cascade;

create or replace view dem.v_active_persons as
select d_vp.*
from dem.v_all_persons d_vp
where
	d_vp.is_deleted is false
;

comment on view dem.v_active_persons is
	'This view denormalizes non-deleted persons with their active name.';

revoke all on dem.v_active_persons from public;
grant select on dem.v_active_persons to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-dem-person_views.sql', '23.0');
