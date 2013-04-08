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
		as dob_is_estimated
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
select gm.log_script_insertion('v19-dem-v_persons.sql', '19.0');
