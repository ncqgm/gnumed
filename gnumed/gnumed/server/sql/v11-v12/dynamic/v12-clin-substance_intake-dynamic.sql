-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- $Id: v12-clin-substance_intake-dynamic.sql,v 1.8 2009-12-03 17:52:12 ncq Exp $
-- $Revision: 1.8 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

set check_function_bodies to 1;
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
-- .soap_cat
alter table clin.substance_intake
	alter column soap_cat
		set default 'p';

\unset ON_ERROR_STOP
alter table clin.substance_intake drop constraint medication_is_plan cascade;
\set ON_ERROR_STOP 1

alter table clin.substance_intake
	add constraint medication_is_plan
		check (soap_cat='p');

-- --------------------------------------------------------------
-- .is_long_term
comment on column clin.substance_intake.is_long_term is
	'whether this is expected to be a regular/ongoing/chronic/long-term/repeat/permament/perpetual/life-long substance intake';


alter table clin.substance_intake
	alter column is_long_term
		set default null;

-- --------------------------------------------------------------
-- .fk_episode
alter table clin.substance_intake
	alter column fk_episode
		drop not null;


\unset ON_ERROR_STOP
alter table clin.substance_intake drop constraint sane_fk_episode cascade;
\set ON_ERROR_STOP 1


alter table clin.substance_intake
	add constraint sane_fk_episode
		check (
			(intake_is_approved_of is False)
				OR
			((intake_is_approved_of is TRUE) AND (fk_episode is not NULL))
		);


\unset ON_ERROR_STOP
drop function clin.trf_sanity_check_substance_episode() cascade;
\set ON_ERROR_STOP 1


create or replace function clin.trf_sanity_check_substance_episode()
	returns trigger
	language plpgsql
	as '
declare
	_identity_from_encounter integer;
	_identity_from_episode integer;
begin
	-- episode can only be NULL if intake is not approved of,
	-- IOW, if clinician approves of intake she better know why
	if NEW.intake_is_approved_of is True then
		if NEW.fk_episode is NULL then
			raise exception ''clin.trf_sanity_check_substance_episode(): substance intake is approved of but .fk_episode is NULL'';
			return NULL;
		end if;
	end if;

	-- .fk_episode can be NULL (except in the above case)
	if NEW.fk_episode is NULL then
		return NEW;
	end if;

	-- .fk_episode must belong to the same patient as .fk_encounter
	select fk_patient into _identity_from_encounter from clin.encounter where pk = NEW.fk_encounter;

	select fk_patient into _identity_from_episode from clin.encounter where pk = (
		select fk_encounter from clin.episode where pk = NEW.fk_episode
	);

	if _identity_from_encounter <> _identity_from_episode then
		raise exception ''INSERT/UPDATE into %.%: Sanity check failed. Encounter % patient = %. Episode % patient = %.'',
			TG_TABLE_SCHEMA,
			TG_TABLE_NAME,
			NEW.fk_encounter,
			_identity_from_encounter,
			NEW.fk_episode,
			_identity_from_episode
		;
		return NULL;
	end if;

	return NEW;

end;';


create trigger tr_sanity_check_substance_episode
	before insert or update
	on clin.substance_intake
	for each row
		execute procedure clin.trf_sanity_check_substance_episode();

-- --------------------------------------------------------------
-- .fk_brand
alter table clin.substance_intake
	alter column fk_brand
		drop not null;

-- --------------------------------------------------------------
-- .fk_substance

-- drop old foreign key on consumed substance
\unset ON_ERROR_STOP
alter table clin.substance_intake drop constraint substance_intake_fk_substance_fkey cascade;
\set ON_ERROR_STOP 1

-- re-adjust foreign key data
update clin.substance_intake csi set
	fk_substance = (
		select ccs.pk
		from clin.consumed_substance ccs
		where
			ccs.description = (
				select cas.description
				from clin.active_substance cas
				where cas.pk = csi.fk_substance
			)
	);

-- re-add new foreign key
alter table clin.substance_intake
	add foreign key (fk_substance)
		references clin.consumed_substance(pk)
			on update cascade
			on delete restrict;

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
	csi.is_long_term,
	csi.aim,
	cep.description
		as episode,
	csi.narrative
		as notes,
	rbd.is_fake
		as fake_brand,

	case
		when csi.clin_when is null then false
		-- from here on csi.clin_when cannot be null
		when (csi.clin_when > current_timestamp) is true then false
		-- from here on csi.clin_when must be < current_timestamp and not null
		when is_long_term is true then true
		-- from here on csi.is_long_term must be false or null
		when (csi.clin_when + csi.duration > current_timestamp) is true then true
		when (csi.clin_when + csi.duration < current_timestamp) is true then false
		-- from here on csi.duration must be null
		else null
	end::boolean
		as is_currently_active,

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
			nullif (
				(coalesce(' ' || csi.aim, '')						-- lower RR
				 || coalesce(' (' || csi.narrative || ')', '')		-- report if unwell
				 || E'\n'
				),
				E'\n'
			),
			''
		)

		|| coalesce (' "' || rbd.description || ' ' || rbd.preparation || '"'		-- "MetoPharm tablets"
			|| coalesce(' [' || rbd.atc_code || ']', '')							-- [ATC code]
			|| coalesce(' (' || rbd.external_code || ')', ''),						-- (external code)
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
select gm.log_script_insertion('$RCSfile: v12-clin-substance_intake-dynamic.sql,v $', '$Revision: 1.8 $');

-- ==============================================================
-- $Log: v12-clin-substance_intake-dynamic.sql,v $
-- Revision 1.8  2009-12-03 17:52:12  ncq
-- - improved constraints
--
-- Revision 1.7  2009/11/24 21:08:49  ncq
-- - adjust to new drug tables
--
-- Revision 1.6  2009/11/06 15:34:44  ncq
-- - .is_currently_active and .pk_health_issue in view
--
-- Revision 1.5  2009/10/29 17:27:56  ncq
-- - .is_long_term
-- - sanity check on fk_episode
-- - view adjusted
--
-- Revision 1.4  2009/10/28 21:49:27  ncq
-- - need episode name in view, too :-)
--
-- Revision 1.3  2009/10/28 16:45:32  ncq
-- - slightly better comment
--
-- Revision 1.2  2009/10/27 11:03:37  ncq
-- - better comment
--
-- Revision 1.1  2009/10/21 08:54:32  ncq
-- - foreign key to consumed_substances
-- - rework views
--
--