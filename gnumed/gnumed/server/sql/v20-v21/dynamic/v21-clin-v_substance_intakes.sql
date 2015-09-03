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
comment on column clin.substance_intake.comment_on_start is 'Comment (uncertainty level) on .clin_when = started. "?" = "entirely unknown".';

alter table clin.substance_intake
	alter column comment_on_start
		set default NULL;

alter table clin.substance_intake
	drop constraint if exists clin_substance_intake_sane_start_comment;

alter table clin.substance_intake
	add constraint clin_substance_intake_sane_start_comment check (
		gm.is_null_or_non_empty_string(comment_on_start)
	);

-- --------------------------------------------------------------
comment on column clin.substance_intake.harmful_use_type is
	'NULL=not considered=medication, 0=no or not considered harmful, 1=presently harmful use, 2=presently addicted, 3=previously addicted';


alter table clin.substance_intake
	drop constraint if exists clin_patient_sane_use_type;

alter table clin.substance_intake
	add constraint clin_patient_sane_use_type check (
		(harmful_use_type IS NULL)
			OR
		(harmful_use_type between 0 and 3)
	);

-- --------------------------------------------------------------
drop view if exists clin.v_brand_intakes cascade;

create view clin.v_brand_intakes as
select
	c_si.pk
		as pk_substance_intake,
	(select fk_patient from clin.encounter where pk = c_si.fk_encounter)
		as pk_patient,
	c_si.soap_cat,
	r_bd.description
		as brand,
	r_bd.preparation,
	r_cs.description
		as substance,
	r_cs.amount,
	r_cs.unit
		as unit,

	r_cs.atc_code
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
	NULL::timestamp with time zone
		as last_checked_when,
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
	r_ls2b.fk_brand
		as pk_brand,
	r_bd.fk_data_source
		as pk_data_source,
	r_ls2b.fk_substance
		as pk_substance,
	r_ls2b.pk
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
		inner join ref.lnk_substance2brand r_ls2b on (c_si.fk_drug_component = r_ls2b.pk)
			inner join ref.branded_drug r_bd on (r_ls2b.fk_brand = r_bd.pk)
			inner join ref.consumable_substance r_cs on (r_ls2b.fk_substance = r_cs.pk)
				left join clin.episode cep on (c_si.fk_episode = cep.pk)
					left join clin.health_issue c_hi on (c_hi.pk = cep.fk_health_issue)
where
	c_si.fk_drug_component IS NOT NULL

;

grant select on clin.v_brand_intakes to group "gm-doctors";

-- --------------------------------------------------------------
drop view if exists clin.v_nonbrand_intakes cascade;

create view clin.v_nonbrand_intakes as
select
	c_si.pk
		as pk_substance_intake,
	(select fk_patient from clin.encounter where pk = c_si.fk_encounter)
		as pk_patient,
	c_si.soap_cat,
	null
		as brand,
	c_si.preparation,
	r_cs.description
		as substance,
	r_cs.amount,
	r_cs.unit
		as unit,
	r_cs.atc_code
		as atc_substance,
	null
		as atc_brand,
	null
		as external_code_brand,
	null
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
	null
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
	null
		as pk_brand,
	null
		as pk_data_source,
	r_cs.pk
		as pk_substance,
	null
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
-- DELETE substance intake
drop function if exists clin.trf_delete_intake_document_deleted() cascade;

create function clin.trf_delete_intake_document_deleted()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_row record;
	_pk_episode integer;
BEGIN
	select
		* into _row
	from
		clin.v_substance_intake_journal
	where
		src_pk = OLD.pk;

	_pk_episode := _row.pk_episode;

	-- create episode if needed
	if _pk_episode is null then
		select pk into _pk_episode
		from clin.episode
		where
			description = _(''Medication history'')
				and
			fk_encounter in (
				select pk from clin.encounter where fk_patient = _row.pk_patient
			);
		if not found then
			insert into clin.episode (
				description,
				is_open,
				fk_encounter
			) values (
				_(''Medication history''),
				FALSE,
				OLD.fk_encounter
			) returning pk into _pk_episode;
		end if;
	end if;

	insert into clin.clin_narrative (
		fk_encounter,
		fk_episode,
		soap_cat,
		narrative
	) values (
		_row.pk_encounter,
		_pk_episode,
		NULL,
		_(''Deletion of'') || '' '' || _row.narrative
	);

	return OLD;
END;';

comment on function clin.trf_delete_intake_document_deleted() is
	'Document the deletion of a substance intake.';

create trigger tr_delete_intake_document_deleted
	before delete on clin.substance_intake
	for each row execute procedure clin.trf_delete_intake_document_deleted();

-- --------------------------------------------------------------
INSERT INTO ref.consumable_substance (
	description,
	atc_code,
	amount,
	unit
)	SELECT
		'nicotine',
		'N07BA01',
		'1',
		'piece'
	WHERE
		NOT EXISTS (SELECT 1 FROM ref.consumable_substance WHERE atc_code = 'N07BA01' and description = 'nicotine')
;

INSERT INTO clin.substance_intake (
	clin_when,
	comment_on_start,
	fk_encounter,
	fk_substance,
	preparation,
	narrative,
	intake_is_approved_of,
	harmful_use_type
)	SELECT
		'20051111'::timestamp,
		'?',
		(select pk from clin.encounter where fk_patient = (
			select pk_identity from dem.v_persons where firstnames = 'James Tiberius' and lastnames = 'Kirk'
		) limit 1),
		(select pk from ref.consumable_substance where atc_code = 'N07BA01' limit 1),
		'tobacco',
		'enjoys an occasional pipe of Old Toby',
		FALSE,
		0
;

INSERT INTO ref.consumable_substance (
	description,
	atc_code,
	amount,
	unit
)	SELECT
		'ethanol',
		'V03AB16',
		'1',
		'l'
	WHERE
		NOT EXISTS (SELECT 1 FROM ref.consumable_substance WHERE atc_code = 'V03AB16' and description = 'ethanol')
;

INSERT INTO clin.substance_intake (
	clin_when,
	comment_on_start,
	fk_encounter,
	fk_substance,
	preparation,
	narrative,
	intake_is_approved_of,
	harmful_use_type
)	SELECT
		'20051111'::timestamp,
		'?',
		(select pk from clin.encounter where fk_patient = (
			select pk_identity from dem.v_persons where firstnames = 'James Tiberius' and lastnames = 'Kirk'
		) limit 1),
		(select pk from ref.consumable_substance where atc_code = 'V03AB16' limit 1),
		'liquid',
		'occasionally relishes a fine glass of Saurian Brandy and will not forego a pint of Romulan Ale',
		FALSE,
		3
;

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'other drugs',
		'1',
		'/1'
	WHERE
		NOT EXISTS (SELECT 1 FROM ref.consumable_substance WHERE description = 'other drugs')
;

INSERT INTO clin.substance_intake (
	clin_when,
	comment_on_start,
	fk_encounter,
	fk_substance,
	preparation,
	narrative,
	intake_is_approved_of,
	harmful_use_type
)	SELECT
		'20051111'::timestamp,
		'?',
		(select pk from clin.encounter where fk_patient = (
			select pk_identity from dem.v_persons where firstnames = 'James Tiberius' and lastnames = 'Kirk'
		) limit 1),
		(select pk from ref.consumable_substance where description = 'other drugs' limit 1),
		'piece',
		'possibly experimented with cordrazine at one point',
		FALSE,
		0
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-clin-v_substance_intakes.sql', '21.0');
