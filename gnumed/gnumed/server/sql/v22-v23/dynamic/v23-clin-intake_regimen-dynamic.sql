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
-- started: .clin_when
comment on column clin.intake_regimen.clin_when is 'When this regimen is started. Can be in the future.';

-- --------------------------------------------------------------
-- .comment_on_start
comment on column clin.intake_regimen.comment_on_start is 'Comment (uncertainty level) on .clin_when = started. "?" = "entirely unknown".';

alter table clin.intake_regimen
	alter column comment_on_start
		set default NULL;

-- --------------------------------------------------------------
-- .fk_substance_intake
comment on column clin.intake_regimen.fk_substance_intake is 'The intake this regimen applies to. Only one regimen per patient must be ongoing at any one time.';

alter table clin.intake_regimen
	alter column fk_substance_intake
		set not NULL;

drop index if exists clin.idx_uniq_open_regimen_per_intake cascade;
create unique index idx_uniq_open_regimen_per_intake on clin.intake_regimen(fk_substance_intake, discontinued) where (discontinued is not null);

-- --------------------------------------------------------------
-- schedule: .narrative
comment on column clin.intake_regimen.narrative is 'The schedule, if any, the substance is to be taken by. An XML snippet to be interpreted by the middleware.';

alter table clin.intake_regimen
	drop constraint if exists clin_intake_regimen_sane_schedule cascade;

alter table clin.intake_regimen
	add constraint clin_intake_regimen_sane_schedule check (
		gm.is_null_or_non_empty_string(narrative) is True
	);

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
		fk_substance_intake with =,
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


grant select, insert, update, delete on ref.substance to "gm-doctors";
grant usage on ref.substance_pk_seq to "gm-doctors" ;

-- --------------------------------------------------------------
-- transfer data
insert into clin.intake_regimen (
	fk_substance_intake,
	fk_encounter,
	fk_episode,
	clin_when,
	comment_on_start,
	discontinued,
	discontinue_reason,
	planned_duration,
	narrative
)
	select
		c_si.pk,
		c_si.fk_encounter,
		c_si.fk_episode,
		c_si.clin_when,
		c_si.comment_on_start,
		c_si.discontinued,
		c_si.discontinue_reason,
		c_si.duration,
		c_si.schedule
	from
		clin.substance_intake c_si
	where not exists (
		select 1 from clin.intake_regimen where fk_substance_intake = c_si.pk
	)
;

-- --------------------------------------------------------------
-- add clin.intake_regiment_journal

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-intake_regimen-dynamic.sql', '23.0');
