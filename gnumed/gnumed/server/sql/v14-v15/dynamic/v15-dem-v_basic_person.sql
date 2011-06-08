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
\unset ON_ERROR_STOP
drop view dem.v_basic_person cascade;
\set ON_ERROR_STOP 1


create view dem.v_basic_person as
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
	i.cob
		as cob,
	i.karyotype
		as karyotype,
	i.pupic
		as pupic,
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
	i.fk_marital_status
		as pk_marital_status,
	n.id
		as pk_active_name,
	i.fk_emergency_contact
		as pk_emergency_contact,
	i.fk_primary_provider
		as pk_primary_provider,
	i.xmin
		as xmin_identity
from
	dem.identity i,
	dem.names n
where
	i.deleted is False
		and
	n.active is true
		and
	n.id_identity = i.pk
;


comment on view dem.v_basic_person is
'This view denormalizes non-deleted persons with their active name.';


revoke all on dem.v_basic_person from public;
grant select on dem.v_basic_person to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v15-dem-v_basic_person.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
