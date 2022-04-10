-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

set check_function_bodies to on;

-- --------------------------------------------------------------
-- .soap_cat
alter table clin.intake_regimen
	alter column soap_cat
		set not NULL;

alter table clin.intake_regimen
	alter column soap_cat
		set default 'p'::text;

-- --------------------------------------------------------------
-- .fk_intake
comment on column clin.intake_regimen.fk_intake is 'The intake this regimen applies to. Only one regimen per patient must be ongoing at any one time.';

alter table clin.intake_regimen
	alter column fk_intake
		set not NULL;

alter table clin.intake_regimen
	add foreign key (fk_intake)
		references clin.intake(pk)
		on delete restrict
		on update cascade;

drop index if exists clin.idx_uniq_open_regimen_per_intake cascade;
create unique index idx_uniq_open_regimen_per_intake on clin.intake_regimen(fk_intake, discontinued) where (discontinued is null);

-- --------------------------------------------------------------
-- .fk_dose
comment on column clin.intake_regimen.fk_dose is 'The dose being taken. Must link to a dose with the same fk_substance as the fk_intake this row points to.';

alter table clin.intake_regimen
	add foreign key (fk_dose)
		references ref.dose(pk)
		on delete restrict
		on update cascade;

-- make unique(.fk_dose, patient):
-- no, because one given dose may be used in different drugs ...

-- --------------------------------------------------------------
-- .fk_drug_product
comment on column clin.intake_regimen.fk_drug_product is 'The drug being taken.';

alter table clin.intake_regimen
	add foreign key (fk_drug_product)
		references ref.drug_product(pk)
		on delete restrict
		on update cascade;

alter table clin.intake_regimen
	drop constraint if exists clin_intake_regimen_fk_drug_product_requires_fk_dose;

alter table clin.intake_regimen
	add constraint clin_intake_regimen_fk_drug_product_requires_fk_dose check (
		(fk_drug_product is NULL)
			OR
		((fk_drug_product is NOT NULL) AND (fk_dose IS NOT NULL))
	);

-- make unique(.fk_drug, patient)
--drop index if exists clin.idx_uniq_drug_per_patient cascade;
--create unique index idx_uniq_drug_per_patient on clin.intake_regimen(fk_drug_product, xxxxxxxxxxx) where (fk_drug_product is not null);

-- --------------------------------------------------------------
-- .narrative = schedule
comment on column clin.intake_regimen.narrative is 'The schedule, if any, the substance is to be taken by. Can be a snippet from a controlled vocabulary to be interpreted by the middleware.';

alter table clin.intake_regimen
	alter column narrative
		set default NULL;

alter table clin.intake_regimen
	alter column narrative
		set not NULL;

-- --------------------------------------------------------------
-- .clin_when = started
comment on column clin.intake_regimen.clin_when is 'When this regimen is started. Can be in the future.';

alter table clin.intake_regimen
	alter column clin_when
		set default NULL;

-- --------------------------------------------------------------
-- .comment_on_start
comment on column clin.intake_regimen.comment_on_start is 'Comment (uncertainty level) on .clin_when. "?" = "entirely unknown".';

alter table clin.intake_regimen
	alter column comment_on_start
		set default NULL;

-- --------------------------------------------------------------
-- .discontinued
comment on column clin.intake_regimen.discontinued is 'When is this intake discontinued ?';

alter table clin.intake_regimen
	drop constraint if exists clin_intake_regimen_sane_discontinued;

alter table clin.intake_regimen
	add constraint clin_intake_regimen_sane_discontinued check (
		(discontinued is NULL)
			or
		(discontinued >= clin_when)
	);

-- --------------------------------------------------------------
-- .discontinue_reason
comment on column clin.intake_regimen.discontinue_reason is 'Why was this intake discontinued ?';

-- --------------------------------------------------------------
-- .planned_duration
comment on column clin.intake_regimen.planned_duration is 'How long is this substance intended to be taken ?';

-- --------------------------------------------------------------
-- table level
comment on table clin.intake_regimen is 'Holds the regimen which substances are consumed by.';


select audit.register_table_for_auditing('clin', 'intake_regimen');
select gm.register_notifying_table('clin', 'intake_regimen');


alter table clin.intake_regimen
	drop constraint if exists clin_intake_regimen_distinct_period cascade;

alter table clin.intake_regimen
	add constraint clin_intake_regimen_distinct_period exclude using GIST (
		fk_intake with =,
		(tstzrange(clin_when, discontinued, '()')) with &&
	);


drop function if exists clin.trf_undiscontinue_unsets_reason() cascade;

create or replace function clin.trf_undiscontinue_unsets_reason()
	returns trigger
	language plpgsql
	as '
begin
	if NEW.discontinued is NULL then
		NEW.discontinue_reason := NULL;
	end if;

	return NEW;
end;';

create trigger tr_undiscontinue_unsets_reason
	before insert or update on clin.intake_regimen
	for each row
		execute procedure clin.trf_undiscontinue_unsets_reason();


grant select, insert, update, delete on clin.intake_regimen to "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-intake_regimen-dynamic.sql', '23.0');
