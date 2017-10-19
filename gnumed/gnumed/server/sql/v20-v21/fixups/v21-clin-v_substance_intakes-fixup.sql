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
drop view if exists clin.v_nonbrand_intakes cascade;

create view clin.v_nonbrand_intakes as
select
	c_si.pk
		as pk_substance_intake,
	(select fk_patient from clin.encounter where pk = c_si.fk_encounter)
		as pk_patient,
	c_si.soap_cat,
	null::text
		as brand,
	c_si.preparation,
	r_cs.description
		as substance,
	r_cs.amount,
	r_cs.unit
		as unit,
	r_cs.atc_code
		as atc_substance,
	null::text
		as atc_brand,
	null::text
		as external_code_brand,
	null::text
		as external_code_type_brand,

	-- uncertainty of start
	case
		when c_si.comment_on_start = '?' then null
		else c_si.clin_when
	end::timestamp with time zone
		as started,
	c_si.comment_on_start,
	case
		when c_si.comment_on_start = '?' then true
		else false
	end::boolean
		as start_is_unknown,
	case
		when c_si.comment_on_start is null then false
		else true
	end::boolean
		as start_is_approximate,
	c_si.intake_is_approved_of,
	c_si.harmful_use_type,
	CASE
		WHEN c_si.harmful_use_type IS NULL THEN NULL::timestamp with time zone
		ELSE c_enc.started
	END
		AS last_checked_when,
	c_si.schedule,
	c_si.duration,
	c_si.discontinued,
	c_si.discontinue_reason,
	c_si.is_long_term,
	c_si.aim,
	cep.description
		as episode,
	c_hi.description
		as health_issue,
	c_si.narrative
		as notes,
	null::boolean
		as fake_brand,
	-- currently active ?
	case
		-- no discontinue date documented so assumed active
		when c_si.discontinued is null then true
		-- else not active (constraints guarantee that .discontinued > clin_when and < current_timestamp)
		else false
	end::boolean
		as is_currently_active,
	-- seems inactive ?
	case
		when c_si.discontinued is not null then true
		-- from here on discontinued is NULL
		when c_si.clin_when is null then
			case
				when c_si.is_long_term is true then false
				else null
			end
		-- from here clin_when is NOT null
		when (c_si.clin_when > current_timestamp) is true then true
		when ((c_si.clin_when + c_si.duration) < current_timestamp) is true then true
		when ((c_si.clin_when + c_si.duration) > current_timestamp) is true then false
		else null
	end::boolean
		as seems_inactive,
	null::integer
		as pk_brand,
	null::integer
		as pk_data_source,
	r_cs.pk
		as pk_substance,
	null::integer
		as pk_drug_component,
	c_si.fk_encounter
		as pk_encounter,
	c_si.fk_episode
		as pk_episode,
	cep.fk_health_issue
		as pk_health_issue,
	c_si.modified_when,
	c_si.modified_by,
	c_si.row_version
		as row_version,
	c_si.xmin
		as xmin_substance_intake
from
	clin.substance_intake c_si
		inner join ref.consumable_substance r_cs on (c_si.fk_substance = r_cs.pk)
			left join clin.episode cep on (c_si.fk_episode = cep.pk)
				left join clin.health_issue c_hi on (c_hi.pk = cep.fk_health_issue)
					left join clin.encounter c_enc on (c_si.fk_encounter = c_enc.pk)
where
	c_si.fk_drug_component IS NULL
;

grant select on clin.v_nonbrand_intakes to group "gm-doctors";

-- --------------------------------------------------------------
drop view if exists clin.v_substance_intakes cascade;

create view clin.v_substance_intakes as
select * from clin.v_brand_intakes
	union all
select * from clin.v_nonbrand_intakes
;

grant select on clin.v_substance_intakes to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-clin-v_substance_intakes-fixup.sql', '21.15');
