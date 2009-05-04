-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- $Id: v11-clin-current_medication-dynamic.sql,v 1.2 2009-05-04 15:05:59 ncq Exp $
-- $Revision: 1.2 $

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
alter table clin.substance_brand drop constraint desc_not_empty;
drop index clin.idx_unique_brand cascade;
\set ON_ERROR_STOP 1

alter table clin.substance_brand
	add constraint desc_not_empty check (
		gm.is_null_or_blank_string(description) is False
	);

create unique index idx_unique_brand on clin.substance_brand (description, preparation);


-- .preparation
comment on column clin.substance_brand.preparation is
'How this drug is delivered, tablet, pill, liquid, cream.';

\unset ON_ERROR_STOP
alter table clin.substance_brand drop constraint prep_not_empty;
\set ON_ERROR_STOP 1

alter table clin.substance_brand
	add constraint prep_not_empty check (
		gm.is_null_or_blank_string(preparation) is False
	);


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
comment on table clin.substance_component is
'The (active) component(s) (agents) a drug is composed of.';

select gm.add_table_for_notifies('clin', 'substance_component');
select audit.add_table_for_audit('clin', 'substance_component');

grant select, insert, update, delete on
	clin.substance_component
	, clin.substance_component_pk_seq
to group "gm-doctors";


-- .fk_brand
comment on column clin.substance_component.fk_brand is
'Which brand this component belongs to.';

alter table clin.substance_component
	alter column fk_brand
		set not null;

\unset ON_ERROR_STOP
drop index clin.idx_fk_brand_component cascade;
\set ON_ERROR_STOP 1

create index idx_fk_brand_component on clin.substance_component (fk_brand);


-- .description
comment on column clin.substance_component.description is
'The component as such, say, Metoprolol.';

\unset ON_ERROR_STOP
alter table clin.substance_component drop constraint desc_not_empty;
drop index clin.idx_uniq_comp_per_brand cascade;
\set ON_ERROR_STOP 1

alter table clin.substance_component
	add constraint desc_not_empty check (
		gm.is_null_or_blank_string(description) is False
	);

create unique index idx_uniq_comp_per_brand on clin.substance_component (description, fk_brand);


-- .atc_code
comment on column clin.substance_component.atc_code is
'ATC code, if any.';

\unset ON_ERROR_STOP
alter table clin.substance_component drop constraint sane_atc;
drop index clin.idx_atc cascade;
drop unique index clin.idx_uniq_atc_per_brand cascade;
\set ON_ERROR_STOP 1

alter table clin.substance_component
	add constraint sane_atc check (
		gm.is_null_or_non_empty_string(atc_code) is True
	);

create index idx_atc on clin.substance_component (atc_code);
create unique index idx_uniq_atc_per_brand on clin.substance_component (atc_code, fk_brand);


-- .strength
comment on column clin.substance_component.strength is
'The amount of the component in the drug, often in mg.';

\unset ON_ERROR_STOP
alter table clin.substance_component drop constraint sane_strength;
\set ON_ERROR_STOP 1

alter table clin.substance_component
	add constraint sane_strength check (
		gm.is_null_or_non_empty_string(strength) is True
	);

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


-- .schedule
comment on column clin.substance_intake.schedule is
'The schedule, if any, the substance is to be taken by.
 An XML snippet to be interpreted by the middleware.';

\unset ON_ERROR_STOP
alter table clin.substance_intake drop constraint sane_schedule;
\set ON_ERROR_STOP 1

alter table clin.substance_intake
	add constraint sane_schedule check (
		gm.is_null_or_non_empty_string(schedule) is True
	);


-- .aim
comment on column clin.substance_intake.aim is
'The aim of taking this substance.';

\unset ON_ERROR_STOP
alter table clin.substance_intake drop constraint sane_aim;
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


-- .fk_encounter
comment on column clin.substance_intake.fk_encounter is
'The encounter use of this substance was documented under.';


-- --------------------------------------------------------------
-- views ...

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-clin-current_medication-dynamic.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: v11-clin-current_medication-dynamic.sql,v $
-- Revision 1.2  2009-05-04 15:05:59  ncq
-- - better naming
--
-- Revision 1.1  2009/05/04 11:38:55  ncq
-- - new
--
--