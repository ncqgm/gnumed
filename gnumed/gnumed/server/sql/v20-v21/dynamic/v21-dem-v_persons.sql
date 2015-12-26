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

create view dem.v_persons as
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
		as dob_is_estimated
from
	dem.identity d_i
		inner join dem.names d_n on ((d_n.id_identity = d_i.pk) and (d_n.active is true))
			left outer join dem.marital_status d_ms on (d_i.fk_marital_status = d_ms.pk)
;


comment on view dem.v_persons is
	'This view denormalizes persons with their active name.';


revoke all on dem.v_persons from public;
grant select on dem.v_persons to group "gm-public";

-- --------------------------------------------------------------
drop view if exists dem.v_deleted_persons cascade;

create or replace view dem.v_deleted_persons as
select d_vp.*
from dem.v_persons d_vp
where
	d_vp.is_deleted is true
;


comment on view dem.v_deleted_persons is
	'This view denormalizes "deleted" persons with their active name.';


revoke all on dem.v_deleted_persons from public;
grant select on dem.v_deleted_persons to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-dem-v_persons.sql', '21.0');
