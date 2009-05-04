-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- $Id: v11-clin-current_medication-dynamic.sql,v 1.1 2009-05-04 11:38:55 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
comment on table clin.drug_brand is
'The medicine chest of this praxis. Stores brands of drugs patients
 have been taking regardless of whether that brand still exists or
 in fact ever existed as such (as in lifestyle thingies).';

select gm.add_table_for_notifies('clin', 'drug_brand');
select audit.add_table_for_audit('clin', 'drug_brand');

grant select, insert, update, delete on
	clin.drug_brand
	, clin.drug_brand_pk_seq
to group "gm-doctors";


-- .description
comment on column clin.drug_brand.description is
'The name this brand is marketed under.';

\unset ON_ERROR_STOP
alter table clin.drug_brand drop constraint desc_not_empty;
drop index clin.idx_unique_brand cascade;
\set ON_ERROR_STOP 1

alter table clin.drug_brand
	add constraint desc_not_empty check (
		gm.is_null_or_blank_string(description) is False
	);

create unique index idx_unique_brand on clin.drug_brand (description, preparation);


-- .preparation
comment on column clin.drug_brand.preparation is
'How this drug is delivered, tablet, pill, liquid, cream.';

\unset ON_ERROR_STOP
alter table clin.drug_brand drop constraint prep_not_empty;
\set ON_ERROR_STOP 1

alter table clin.drug_brand
	add constraint prep_not_empty check (
		gm.is_null_or_blank_string(preparation) is False
	);


-- .is_fake
comment on column clin.drug_brand.is_fake is
'Whether this truly is an actual brand of an actual drug
 rather than a fake brand created for documenting a, say,
 lifestyle nutrient or simply a component as opposed to
 a particular actual brand.';

alter table clin.drug_brand
	alter column is_fake
		set not null;

alter table clin.drug_brand
	alter column is_fake
		set default True;

-- --------------------------------------------------------------
comment on table clin.drug_component is
'The (active) component(s) (agents) a drug is composed of.';

select gm.add_table_for_notifies('clin', 'drug_component');
select audit.add_table_for_audit('clin', 'drug_component');

grant select, insert, update, delete on
	clin.drug_component
	, clin.drug_component_pk_seq
to group "gm-doctors";


-- .fk_brand
comment on column clin.drug_component.fk_brand is
'Which brand this component belongs to.';

alter table clin.drug_component
	alter column fk_brand
		set not null;

\unset ON_ERROR_STOP
drop index clin.idx_fk_brand_component cascade;
\set ON_ERROR_STOP 1

create index idx_fk_brand_component on clin.drug_component (fk_brand);


-- .description
comment on column clin.drug_component.description is
'The component as such, say, Metoprolol.';

\unset ON_ERROR_STOP
alter table clin.drug_component drop constraint desc_not_empty;
drop index clin.idx_uniq_comp_per_brand cascade;
\set ON_ERROR_STOP 1

alter table clin.drug_component
	add constraint desc_not_empty check (
		gm.is_null_or_blank_string(description) is False
	);

create unique index idx_uniq_comp_per_brand on clin.drug_component (description, fk_brand);


-- .atc_code
comment on column clin.drug_component.atc_code is
'ATC code, if any.';

\unset ON_ERROR_STOP
alter table clin.drug_component drop constraint sane_atc;
drop index clin.idx_atc cascade;
drop unique index clin.idx_uniq_atc_per_brand cascade;
\set ON_ERROR_STOP 1

alter table clin.drug_component
	add constraint sane_atc check (
		gm.is_null_or_non_empty_string(atc_code) is True
	);

create index idx_atc on clin.drug_component (atc_code);
create unique index idx_uniq_atc_per_brand on clin.drug_component (atc_code, fk_brand);


-- .strength
comment on column clin.drug_component.strength is
'The amount of the component in the drug, often in mg.';

\unset ON_ERROR_STOP
alter table clin.drug_component drop constraint sane_strength;
\set ON_ERROR_STOP 1

alter table clin.drug_component
	add constraint sane_strength check (
		gm.is_null_or_non_empty_string(strength) is True
	);

-- --------------------------------------------------------------
comment on table clin.current_medication is
'The substances a patient is actually currently taking.';

select gm.add_table_for_notifies('clin', 'current_medication');
select audit.add_table_for_audit('clin', 'current_medication');

grant select, insert, update, delete on
	clin.current_medication
	, clin.current_medication_pk_seq
to group "gm-doctors";


-- .fk_brand
comment on column clin.current_medication.fk_brand is
'The brand (may be a fake entry) the patient is taking.';

alter table clin.current_medication
	alter column fk_brand
		set not null;

\unset ON_ERROR_STOP
drop index clin.idx_fk_brand_curr_med cascade;
\set ON_ERROR_STOP 1

create index idx_fk_brand_curr_med on clin.current_medication (fk_brand);


-- .schedule
comment on column clin.current_medication.schedule is
'The schedule, if any, the substance is to be taken by.
 An XML snippet to be interpreted by the middleware.';

\unset ON_ERROR_STOP
alter table clin.current_medication drop constraint sane_schedule;
\set ON_ERROR_STOP 1

alter table clin.current_medication
	add constraint sane_schedule check (
		gm.is_null_or_non_empty_string(schedule) is True
	);


-- .aim
comment on column clin.current_medication.aim is
'The aim of taking this substance.';

\unset ON_ERROR_STOP
alter table clin.current_medication drop constraint sane_aim;
\set ON_ERROR_STOP 1

alter table clin.current_medication
	add constraint sane_aim check (
		gm.is_null_or_non_empty_string(aim) is True
	);


-- .clin_when -> "started"
comment on column clin.current_medication.clin_when is
'When was this substance started.';


-- .duration
comment on column clin.current_medication.duration is
'How long is this substances intended to be taken.';


-- .narrative -> "notes"
comment on column clin.current_medication.narrative is
'Any notes on this substance use.';


-- .fk_encounter
comment on column clin.current_medication.fk_encounter is
'The encounter use of this substance was documented under.';


-- --------------------------------------------------------------
-- views ...

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-clin-current_medication-dynamic.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v11-clin-current_medication-dynamic.sql,v $
-- Revision 1.1  2009-05-04 11:38:55  ncq
-- - new
--
--