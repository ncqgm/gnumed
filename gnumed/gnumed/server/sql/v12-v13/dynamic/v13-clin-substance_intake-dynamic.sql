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
-- .discontinued
comment on column clin.substance_intake.discontinued is
	'when was this entry discontinued';


alter table clin.substance_intake
	alter column discontinued
		set default NULL;


\unset ON_ERROR_STOP
alter table clin.substance_intake drop constraint discontinued_after_started cascade;
\set ON_ERROR_STOP 1

alter table clin.substance_intake
	add constraint discontinued_after_started
		check (
			(clin_when is null)
				or
			(discontinued is null)
				or
			((discontinued >= clin_when) and (discontinued <= current_timestamp))
		);


-- unset reason if setting discontinued to null
\unset ON_ERROR_STOP
drop function clin.trf_undiscontinue_unsets_reason() cascade;
\set ON_ERROR_STOP 1

create or replace function clin.trf_undiscontinue_unsets_reason()
	returns trigger
	language plpgsql
	as '
declare
	_identity_from_encounter integer;
	_identity_from_issue integer;
begin
	if NEW.discontinued is NULL then
		NEW.discontinue_reason := NULL;
	end if;

	return NEW;
end;';

create trigger tr_undiscontinue_unsets_reason
	before insert or update on clin.substance_intake
	for each row
		execute procedure clin.trf_undiscontinue_unsets_reason();

-- --------------------------------------------------------------
-- .discontinue_reason
comment on column clin.substance_intake.discontinued is
	'why was this entry discontinued';

alter table clin.substance_intake
	alter column discontinue_reason
		set default NULL;

\unset ON_ERROR_STOP
alter table clin.substance_intake drop constraint sane_discontinue_reason cascade;
\set ON_ERROR_STOP 1

alter table clin.substance_intake
	add constraint sane_discontinue_reason
		check (
			((discontinued is null) and (discontinue_reason is null))
				or
			((discontinued is not null) and (gm.is_null_or_non_empty_string(discontinue_reason) is true))
		);

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_pat_substance_intake cascade;
\set ON_ERROR_STOP 1

create view clin.v_pat_substance_intake as
select
	csi.pk
		as pk_substance_intake,
	(select fk_patient from clin.encounter where pk = csi.fk_encounter)
		as pk_patient,
	csi.soap_cat,
	rbd.description
		as brand,
	csi.preparation,
	rbd.atc_code
		as atc_brand,
	rbd.external_code
		as external_code_brand,
	rbd.external_code_type
		as external_code_type_brand,

	ccs.description
		as substance,
	csi.strength,
	ccs.atc_code
		as atc_substance,

	csi.clin_when
		as started,
	csi.intake_is_approved_of,
	csi.schedule,
	csi.duration,
	csi.discontinued,
	csi.discontinue_reason,
	csi.is_long_term,
	csi.aim,
	cep.description
		as episode,
	csi.narrative
		as notes,
	rbd.is_fake
		as fake_brand,
	-- currently active ?
	case
		-- no discontinue date documented so assumed active
		when csi.discontinued is null then true
		-- else not active (constraints guarantee that .discontinued > clin_when and < current_timestamp)
		else false
	end::boolean
		as is_currently_active,
	-- seems inactive ?
	case
		when csi.discontinued is not null then true
		-- from here on discontinued is NULL
		when csi.clin_when is null then
			case
				when csi.is_long_term is true then false
				else null
			end
		-- from here clin_when is NOT null
		when (csi.clin_when > current_timestamp) is true then true
		when ((csi.clin_when + csi.duration) < current_timestamp) is true then true
		when ((csi.clin_when + csi.duration) > current_timestamp) is true then false
		else null
	end::boolean
		as seems_inactive,
	csi.fk_brand
		as pk_brand,
	ccs.pk
		as pk_substance,
	csi.fk_encounter
		as pk_encounter,
	csi.fk_episode
		as pk_episode,
	cep.fk_health_issue
		as pk_health_issue,
	csi.modified_when,
	csi.modified_by,
	csi.row_version
		as row_version,
	csi.xmin
		as xmin_substance_intake
from
	clin.substance_intake csi
		left join ref.branded_drug rbd on (csi.fk_brand = rbd.pk)
			left join clin.consumed_substance ccs on (csi.fk_substance = ccs.pk)
				left join clin.episode cep on (csi.fk_episode = cep.pk)
;

grant select on clin.v_pat_substance_intake to group "gm-doctors";

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_pat_substance_intake_journal cascade;
\set ON_ERROR_STOP 1

create view clin.v_pat_substance_intake_journal as
select
	(select fk_patient from clin.encounter where pk = csi.fk_encounter)
		as pk_patient,
	csi.modified_when
		as modified_when,
	csi.clin_when
		as clin_when,
	coalesce (
		(select short_alias from dem.staff where db_user = csi.modified_by),
		'<' || csi.modified_by || '>'
	)
		as modified_by,
	csi.soap_cat
		as soap_cat,

	(case
		when is_long_term is true then _('long-term') || ' '
		else ''
	 end
	)
		|| _('substance intake') || ' '
		|| (case
				when intake_is_approved_of is true then _('(approved of)')
				when intake_is_approved_of is false then _('(not approved of)')
				else _('(of unknown approval)')
			end)
		|| E':\n'

		|| ' ' || ccs.description								-- Metoprolol
		|| coalesce(' [' || ccs.atc_code || '] ', ' ')			-- [ATC]
		|| csi.strength || ' '									-- 100mg
		|| csi.preparation										-- tab
		|| coalesce(' ' || csi.schedule, '')					-- 1-0-0
		|| ', ' || to_char(csi.clin_when, 'YYYY-MM-DD')			-- 2009-03-01
		|| coalesce(' -> ' || csi.duration, '')					-- -> 6 months
		|| E'\n'

		|| coalesce (
				' ' || _('discontinued') || to_char(csi.discontinued, ': YYYY-MM-DD')
				|| coalesce('(' || csi.discontinue_reason || ')', '')
				|| E'\n',
				''
			)

		|| coalesce (
			nullif (
				(coalesce(' ' || csi.aim, '')						-- lower RR
				 || coalesce(' (' || csi.narrative || ')', '')		-- report if unwell
				 || E'\n'
				),
				E'\n'
			),
			''
		)

		|| coalesce (' "' || rbd.description || ' ' || rbd.preparation || '"'							-- "MetoPharm tablets"
			|| coalesce(' [' || rbd.atc_code || ']', '')												-- [ATC code]
			|| coalesce(' (' || rbd.external_code_type || ': ' || rbd.external_code || ')', ''),		-- (external code)
			'')

	as narrative,

	csi.fk_encounter
		as pk_encounter,
	csi.fk_episode
		as pk_episode,
	(select fk_health_issue from clin.episode where pk = csi.fk_episode)
		as pk_health_issue,
	csi.pk
		as src_pk,
	'clin.substance_intake'::text
		as src_table,
	csi.row_version
		as row_version
from
	clin.substance_intake csi
		left join ref.branded_drug rbd on (csi.fk_brand = rbd.pk)
			left join clin.consumed_substance ccs on (csi.fk_substance = ccs.pk)
;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v13-clin-substance_intake-dynamic.sql,v $', '$Revision: 1.8 $');

-- ==============================================================
