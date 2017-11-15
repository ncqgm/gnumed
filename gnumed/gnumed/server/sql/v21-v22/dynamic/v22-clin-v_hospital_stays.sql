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
-- rewrite views + grants
drop view if exists clin.v_hospital_stays cascade;

create view clin.v_hospital_stays as
select
	c_hs.pk
		as pk_hospital_stay,
	(select fk_patient from clin.encounter where pk = c_hs.fk_encounter)
		as pk_patient,
	d_o.description
		as hospital,
	d_ou.description
		as ward,
	c_hs.narrative
		as comment,
	c_hs.clin_when
		as admission,
	c_hs.discharge,
	c_hs.soap_cat
		as soap_cat,
	c_e.description
		as episode,
	c_hi.description
		as health_issue,
	c_hs.fk_encounter
		as pk_encounter,
	c_hs.fk_episode
		as pk_episode,
	c_hi.pk
		as pk_health_issue,
	c_hs.fk_org_unit
		as pk_org_unit,
	d_o.pk
		as pk_org,
	COALESCE (
		(SELECT array_agg(pk) FROM blobs.doc_med b_dm WHERE b_dm.fk_hospital_stay = c_hs.pk),
		ARRAY[]::integer[]
	)
		AS pk_documents,

	c_hs.modified_when
		as modified_when,
	coalesce (
		(select short_alias from dem.staff where db_user = c_hs.modified_by),
		'<' || c_hs.modified_by || '>'
	)
		as modified_by,
	c_hs.row_version,
	c_hs.xmin
		as xmin_hospital_stay
from
	clin.hospital_stay c_hs
		left join clin.episode c_e on (c_e.pk = c_hs.fk_episode)
			left join clin.health_issue c_hi on (c_hi.pk = c_e.fk_health_issue)
				left join dem.org_unit d_ou on (d_ou.pk = c_hs.fk_org_unit)
					left join dem.org d_o on (d_o.pk = d_ou.fk_org)
;

grant select on clin.v_hospital_stays to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-clin-v_hospital_stays.sql', '22.0');
