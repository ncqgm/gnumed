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
-- table level
-- --------------------------------------------------------------
comment on table clin.intake_regimen is
'Holds ongoing and historical regimens by which substances are consumed.
.
There can be any number of discontinued (historic)
and ongoing regimen per intake.
.
Say, a patient takes paracetamol (PCM):
.
	1000mg PCM in the morning
	500mg PCM at noon
	500mg PCM combined with codeine at night (say, as drug "ParaComp")
.
There will be one clin.intake row for PCM and two (or
three) active regimen rows:
.
- regimen "500mg PCM, 0-0-1 pk_drug=ParaComp"
.
	plus either
.
- regimen "PCM, schedule 1000-500-0, pk_dose=NULL"
	or
- regimen "1000mg PCM, schedule 1-0-0, pk_dose=pcm_1000"
- regimen "500mg PCM, schedule 0-1-0, pk_dose=pcm_500"
.
Each way is medically correct. Which one is used
is up to the clinician.';

-- --------------------------------------------------------------
-- .soap_cat
alter table clin.intake_regimen
	alter column soap_cat
		set not NULL;

alter table clin.intake_regimen
	alter column soap_cat
		set default 'p'::text;

-- --------------------------------------------------------------
-- .fk_episode
comment on column clin.intake_regimen.fk_episode is '
The episode this intake regimen was registered under.
.
The episodes of active regimens (.discontinued=NULL) must
correspond to the episode of the intake they link to.
.
Historical regimens may well link to different episodes
(of the same patient that is).';

-- --------------------------------------------------------------
-- .fk_intake
comment on column clin.intake_regimen.fk_intake is
'The intake this regimen applies to.
.
(fk_intake, discontinued=NULL) is not unique. For
the reasoning refer to the table level comment.';

alter table clin.intake_regimen
	alter column fk_intake
		set not NULL;

alter table clin.intake_regimen
	add foreign key (fk_intake)
		references clin.intake(pk)
		on delete restrict		-- set null
		on update cascade;

drop index if exists clin.idx_clin_intake_regimen_fk_intake cascade;
create index idx_clin_intake_regimen_fk_intake on clin.intake_regimen(fk_intake);

-- --------------------------------------------------------------
-- .fk_dose
comment on column clin.intake_regimen.fk_dose is
'The dose being taken.
.
Must link to a dose with the same fk_substance as the fk_intake this row points to.
.
(fk_dose, patient) is not unique because a dose (= substance + strength)
can be linked to several drug products each of which the patient might be taking.';

alter table clin.intake_regimen
	add foreign key (fk_dose)
		references ref.dose(pk)
		on delete restrict
		on update cascade;

drop index if exists clin.idx_clin_intake_regimen_fk_dose cascade;
create index idx_clin_intake_regimen_fk_dose on clin.intake_regimen(fk_dose);

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

drop index if exists clin.idx_clin_intake_regimen_fk_drug_product cascade;
create index idx_clin_intake_regimen_fk_drug_product on clin.intake_regimen(fk_drug_product);

-- make unique(.fk_drug, patient)
--drop index if exists clin.idx_uniq_drug_per_patient cascade;
--create unique index idx_uniq_drug_per_patient on clin.intake_regimen(fk_drug_product, xxxxxxxxxxx) where (fk_drug_product is not null);

-- --------------------------------------------------------------
-- .narrative = schedule
comment on column clin.intake_regimen.narrative is 
'The schedule, if any, the substance is to be taken by.
.
Can be a snippet from a controlled vocabulary to be
interpreted by the middleware.';

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
-- --------------------------------------------------------------
select audit.register_table_for_auditing('clin', 'intake_regimen');
select gm.register_notifying_table('clin', 'intake_regimen');

grant select, insert, update, delete on clin.intake_regimen to "gm-doctors";

-- --------------------------------------------------------------
-- there *can* be overlapping ongoing regimen: see the table
-- comment on clin.intake_regimen
--alter table clin.intake_regimen
--	drop constraint if exists clin_intake_regimen_distinct_period cascade;
--
--alter table clin.intake_regimen
--	add constraint clin_intake_regimen_distinct_period exclude using GIST (
--		fk_intake with =,
--		(tstzrange(clin_when, discontinued, '()')) with &&
--	);

-- --------------------------------------------------------------
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

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-intake_regimen-dynamic.sql', '23.0');
