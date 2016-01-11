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
-- .fk_org_unit
comment on column blobs.doc_med.fk_org_unit is
'Optional link to the org unit this document originates from.\n
Note that the document may contain data from several units but\n
there will always be one "sender".';

alter table blobs.doc_med
	drop constraint if exists fk_blobs_doc_med_dem_org_unit_pk cascade
;

alter table blobs.doc_med
	add constraint fk_blobs_doc_med_dem_org_unit_pk
		foreign key (fk_org_unit)
		references dem.org_unit(pk)
		on update cascade
		on delete restrict
;

-- --------------------------------------------------------------
drop view if exists blobs.v_doc_med cascade;

create or replace view blobs.v_doc_med as
select
	--(select fk_patient from clin.encounter where pk = b_dm.fk_encounter)
	c_enc.fk_patient
		as pk_patient,
	b_dm.pk
		as pk_doc,
	b_dm.clin_when
		as clin_when,
	b_dt.name
		as type,
	_(b_dt.name)
		as l10n_type,
	b_dm.ext_ref
		as ext_ref,
	b_dm.comment
		as comment,
	c_epi.description
		as episode,
	c_hi.description
		as health_issue,
	c_epi.is_open
		as episode_open,
	d_ou.description
		as unit,
	d_o.description
		as organization,
	b_dm.fk_type
		as pk_type,
	b_dm.fk_encounter
		as pk_encounter,
	b_dm.fk_episode
		as pk_episode,
	c_epi.fk_health_issue
		as pk_health_issue,
	b_dm.fk_org_unit
		as pk_org_unit,
	d_ou.fk_org
		as pk_org,
	b_dm.modified_when
		as modified_when,
	b_dm.modified_by
		as modified_by,
	b_dm.xmin
		as xmin_doc_med
from
	blobs.doc_med b_dm
		inner join blobs.doc_type b_dt on (b_dm.fk_type = b_dt.pk)
		inner join clin.encounter c_enc on (b_dm.fk_encounter = c_enc.pk)
		inner join clin.episode c_epi on (b_dm.fk_episode = c_epi.pk)
			-- there are episodes w/o issue link so LEFT join is needed
			left join clin.health_issue c_hi on (c_hi.pk = c_epi.fk_health_issue)
		left join dem.org_unit d_ou on (b_dm.fk_org_unit = d_ou.pk)
			left join dem.org d_o on (d_ou.fk_org = d_o.pk)
;

GRANT SELECT ON blobs.v_doc_med TO GROUP "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-blobs-doc_med-dynamic.sql', '21.0');
