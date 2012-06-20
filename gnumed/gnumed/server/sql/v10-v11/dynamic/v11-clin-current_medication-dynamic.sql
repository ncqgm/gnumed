-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- $Id: v11-clin-current_medication-dynamic.sql,v 1.4 2009-06-04 16:37:39 ncq Exp $
-- $Revision: 1.4 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
comment on table clin.substance_brand is
'The medicine chest of this praxis. Stores brands of drugs patients
 have been taking regardless of whether that brand still exists or
 in fact ever existed as such (as in lifestyle thingies).';

select gm.add_table_for_notifies('clin', 'substance_brand');
select audit.add_table_for_audit('clin', 'substance_brand');

grant select, insert, update, delete on
	clin.substance_brand
	, clin.substance_brand_pk_seq
to group "gm-doctors";


-- .description
comment on column clin.substance_brand.description is
'The name this brand is marketed under.';

\unset ON_ERROR_STOP
alter table clin.substance_brand drop constraint desc_not_empty cascade;
alter table clin.substance_brand drop constraint unique_brand cascade;
\set ON_ERROR_STOP 1

alter table clin.substance_brand
	add constraint desc_not_empty check (
		gm.is_null_or_blank_string(description) is False
	);

alter table clin.substance_brand
	add constraint unique_brand unique(description, preparation);


-- .preparation
comment on column clin.substance_brand.preparation is
'How this drug is delivered, tablet, pill, liquid, cream.';

\unset ON_ERROR_STOP
alter table clin.substance_brand drop constraint prep_not_empty cascade;
\set ON_ERROR_STOP 1

alter table clin.substance_brand
	add constraint prep_not_empty check (
		gm.is_null_or_blank_string(preparation) is False
	);


-- .atc_code
comment on column clin.substance_brand.atc_code is
'ATC code, if any.';

\unset ON_ERROR_STOP
alter table clin.substance_brand drop constraint sane_atc cascade;
drop index clin.idx_atc_brand cascade;
\set ON_ERROR_STOP 1

alter table clin.substance_brand
	add constraint sane_atc check (
		gm.is_null_or_non_empty_string(atc_code) is True
	);

create index idx_atc_brand on clin.active_substance (atc_code);


-- .is_fake
comment on column clin.substance_brand.is_fake is
'Whether this truly is an actual brand of an actual drug
 rather than a fake brand created for documenting a, say,
 lifestyle nutrient or simply a component as opposed to
 a particular actual brand.';

alter table clin.substance_brand
	alter column is_fake
		set not null;

alter table clin.substance_brand
	alter column is_fake
		set default True;

-- --------------------------------------------------------------
comment on table clin.active_substance is
'(Active) substances (consumables) a patient may be taking.';

select gm.add_table_for_notifies('clin', 'active_substance');
select audit.add_table_for_audit('clin', 'active_substance');

grant select, insert, update, delete on
	clin.active_substance
	, clin.active_substance_pk_seq
to group "gm-doctors";


-- .description
comment on column clin.active_substance.description is
'The substance as such, say, Metoprolol.';

alter table clin.active_substance
	alter column description
		set not null;

\unset ON_ERROR_STOP
alter table clin.active_substance drop constraint unique_desc cascade;
\set ON_ERROR_STOP 1

alter table clin.active_substance
	add constraint unique_desc unique(description);


-- .atc_code
comment on column clin.active_substance.atc_code is
'ATC code, if any.';

\unset ON_ERROR_STOP
alter table clin.active_substance drop constraint sane_atc cascade;
alter table clin.active_substance drop constraint unique_atc cascade;
drop index clin.idx_atc_substance cascade;
\set ON_ERROR_STOP 1

alter table clin.active_substance
	add constraint sane_atc check (
		gm.is_null_or_non_empty_string(atc_code) is True
	);

alter table clin.active_substance
	add constraint unique_atc unique (atc_code);

create index idx_atc_substance on clin.active_substance (atc_code);

-- --------------------------------------------------------------
comment on table clin.substance_intake is
'The substances a patient is actually currently taking.';

select gm.add_table_for_notifies('clin', 'substance_intake');
select audit.add_table_for_audit('clin', 'substance_intake');

grant select, insert, update, delete on
	clin.substance_intake
	, clin.substance_intake_pk_seq
to group "gm-doctors";


-- .fk_brand
comment on column clin.substance_intake.fk_brand is
'The brand (may be a fake entry) the patient is taking.';

alter table clin.substance_intake
	alter column fk_brand
		set not null;

\unset ON_ERROR_STOP
drop index clin.idx_fk_brand_curr_med cascade;
\set ON_ERROR_STOP 1

create index idx_fk_brand_curr_med on clin.substance_intake (fk_brand);


-- .fk_substance
comment on column clin.substance_intake.fk_substance is
'The substance a patient is taking.';

alter table clin.substance_intake
	alter column fk_substance
		set not null;

\unset ON_ERROR_STOP
drop index clin.idx_fk_substance_curr_med cascade;
\set ON_ERROR_STOP 1

create index idx_fk_substance_curr_med on clin.substance_intake (fk_substance);


-- .strength
comment on column clin.substance_intake.strength is
'The amount of the substance, often in mg.';

\unset ON_ERROR_STOP
alter table clin.substance_intake drop constraint sane_strength cascade;
\set ON_ERROR_STOP 1

alter table clin.substance_intake
	add constraint sane_strength check (
		gm.is_null_or_non_empty_string(strength) is True
	);


-- .preparation
comment on column clin.substance_intake.preparation is
'How this substance is delivered, tablet, pill, liquid, cream.';

alter table clin.substance_intake
	alter column preparation
		set not null;


-- .schedule
comment on column clin.substance_intake.schedule is
'The schedule, if any, the substance is to be taken by.
 An XML snippet to be interpreted by the middleware.';

\unset ON_ERROR_STOP
alter table clin.substance_intake drop constraint sane_schedule cascade;
\set ON_ERROR_STOP 1

alter table clin.substance_intake
	add constraint sane_schedule check (
		gm.is_null_or_non_empty_string(schedule) is True
	);


-- .aim
comment on column clin.substance_intake.aim is
'The aim of taking this substance.';

\unset ON_ERROR_STOP
alter table clin.substance_intake drop constraint sane_aim cascade;
\set ON_ERROR_STOP 1

alter table clin.substance_intake
	add constraint sane_aim check (
		gm.is_null_or_non_empty_string(aim) is True
	);


-- .clin_when -> "started"
comment on column clin.substance_intake.clin_when is
'When was this substance started.';


-- .duration
comment on column clin.substance_intake.duration is
'How long is this substances intended to be taken.';


-- .narrative -> "notes"
comment on column clin.substance_intake.narrative is
'Any notes on this substance use.';


-- .soap_cat
alter table clin.substance_intake
	alter column soap_cat
		set default 'p';


-- .fk_encounter
comment on column clin.substance_intake.fk_encounter is
'The encounter use of this substance was documented under.';


-- .intake_is_approved_of
comment on column clin.substance_intake.intake_is_approved_of is
'Whether or not intake of this substance is recommended/approved of by the provider';

alter table clin.substance_intake
	alter column intake_is_approved_of
		set not null;


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
	csb.description
		as brand,
	csb.preparation,
	csb.atc_code
		as atc_brand,

	cas.description
		as substance,
	csi.strength,
	cas.atc_code
		as atc_substance,

	csi.clin_when
		as started,
	csi.intake_is_approved_of,
	csi.schedule,
	csi.duration,
	csi.aim,
	csi.narrative
		as notes,
	csb.is_fake
		as fake_brand,

	csi.fk_brand
		as pk_brand,
	cas.pk
		as pk_substance,
	csi.fk_encounter
		as pk_encounter,
	csi.fk_episode
		as pk_episode,
	csi.modified_when,
	csi.modified_by,
	csi.xmin
		as xmin_substance_intake
from
	clin.substance_intake csi
		left join clin.substance_brand csb on (csi.fk_brand = csb.pk)
			left join clin.active_substance cas on (csi.fk_substance = cas.pk)
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

	_('substance intake') || ' '
		|| (case
				when intake_is_approved_of is true then _('(approved of)')
				when intake_is_approved_of is false then _('(not approved of)')
				else _('[of unknown approval]')
			end)
		|| E':\n'

		|| ' ' || cas.description								-- Metoprolol
		|| coalesce(' [' || cas.atc_code || '] ', ' ')			-- [ATC]
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

		|| coalesce (' "'
			|| csb.description || ' '
			|| csb.preparation || ' '
			|| '[' || csb.atc_code || ']'
			|| '"',
			'')													-- "MetoPharm tablets [ATC code]"

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
		left join clin.substance_brand csb on (csi.fk_brand = csb.pk)
			left join clin.active_substance cas on (csi.fk_substance = cas.pk)
;

grant select on clin.v_pat_substance_intake_journal to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-clin-current_medication-dynamic.sql,v $', '$Revision: 1.4 $');

-- ==============================================================
-- $Log: v11-clin-current_medication-dynamic.sql,v $
-- Revision 1.4  2009-06-04 16:37:39  ncq
-- - .intake-is-approved-of
-- - improved journal view
--
-- Revision 1.3  2009/05/12 12:08:50  ncq
-- - fix table layout
--
-- Revision 1.2  2009/05/04 15:05:59  ncq
-- - better naming
--
-- Revision 1.1  2009/05/04 11:38:55  ncq
-- - new
--
--