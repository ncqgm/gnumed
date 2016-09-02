-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
set check_function_bodies to on;
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
drop function if exists _tmp_convert_substance_intakes() cascade;

-- --------------------------------------------------------------
-- recreate FK
alter table clin.substance_intake
	alter column fk_drug_component
		set not null;

alter table clin.substance_intake
	add constraint clin_substance_intake_fk_drug_component
		foreign key (fk_drug_component) references ref.lnk_dose2drug(pk)
			on update cascade
			on delete restrict
;

-- --------------------------------------------------------------
-- drop leftovers
alter table clin.substance_intake drop column fk_substance cascade;
alter table clin.substance_intake drop column preparation cascade;

drop view if exists clin.v_brand_intakes cascade;
drop view if exists clin.v_nonbrand_intakes cascade;
drop view if exists clin.v_substance_intakes cascade;

drop table if exists ref.consumable_substance cascade;
delete from audit.audited_tables where schema = 'ref' and table_name = 'consumable_substance';
delete from gm.notifying_tables where schema_name = 'ref' and table_name = 'consumable_substance';

drop table if exists ref.lnk_substance2drug cascade;
delete from audit.audited_tables where schema = 'ref' and table_name = 'lnk_substance2drug';

drop function if exists clin.trf_ins_intake_set_substance_from_component() cascade;

drop function if exists clin.trf_ins_upd_intake_prevent_duplicate_substance_links() cascade;

-- --------------------------------------------------------------
-- recreate views
drop view if exists clin.v_substance_intakes cascade;

create view clin.v_substance_intakes as
select
	c_si.pk
		as pk_substance_intake,
	c_enc.fk_patient
		as pk_patient,
	c_si.soap_cat,
	r_bd.description
		as brand,
	r_bd.preparation,
	r_s.description
		as substance,
	r_d.amount,
	r_d.unit,
	r_d.dose_unit,

	r_s.atc
		as atc_substance,
	r_bd.atc_code
		as atc_brand,
	r_bd.external_code
		as external_code_brand,
	r_bd.external_code_type
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
	r_s.intake_instructions,
	cep.description
		as episode,
	c_hi.description
		as health_issue,
	c_si.narrative
		as notes,
	r_bd.is_fake
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
	r_ld2d.fk_brand
		as pk_brand,
	r_bd.fk_data_source
		as pk_data_source,
	r_ld2d.fk_dose
		as pk_dose,
	r_ld2d.pk
		as pk_drug_component,
	r_d.fk_substance
		as pk_substance,
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
		inner join ref.lnk_dose2drug r_ld2d on (c_si.fk_drug_component = r_ld2d.pk)
			inner join ref.branded_drug r_bd on (r_ld2d.fk_brand = r_bd.pk)
			inner join ref.dose r_d on (r_ld2d.fk_dose = r_d.pk)
				inner join ref.substance r_s on (r_d.fk_substance = r_s.pk)
		left join clin.episode cep on (c_si.fk_episode = cep.pk)
			left join clin.health_issue c_hi on (c_hi.pk = cep.fk_health_issue)
		left join clin.encounter c_enc on (c_si.fk_encounter = c_enc.pk)
;

grant select on clin.v_substance_intakes to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-clin-substance_intake-dynamic.sql', '22.0');
