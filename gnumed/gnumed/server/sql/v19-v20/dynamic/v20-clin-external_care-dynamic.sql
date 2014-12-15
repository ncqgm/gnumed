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
comment on table clin.external_care is
	'lists external care situations for patients';

select gm.register_notifying_table('clin', 'external_care');
select audit.register_table_for_auditing('clin', 'external_care');

revoke all on clin.external_care from public;
grant select, insert, update, delete on clin.external_care to "gm-doctors";
grant usage on clin.external_care_pk_seq to "gm-doctors";

-- --------------------------------------------------------------
-- .fk_encounter
comment on column clin.external_care.fk_encounter is 'the encounter during which this external care item was first documented';

drop index if exists clin.idx_external_care_fk_encounter cascade;
create index idx_external_care_fk_encounter on clin.external_care(fk_encounter);

alter table clin.external_care
	alter column fk_encounter
		set not null;

alter table clin.external_care
	drop constraint if exists FK_clin_external_care_fk_encounter cascade;
alter table clin.external_care
	add constraint FK_clin_external_care_fk_encounter foreign key (fk_encounter)
		references clin.encounter(pk)
		on update restrict
		on delete restrict
;

-- --------------------------------------------------------------
-- .fk_health_issue
comment on column clin.external_care.fk_health_issue is 'link to a health issue, if any';

drop index if exists clin.idx_external_care_fk_health_issue cascade;
create index idx_external_care_fk_health_issue on clin.external_care(fk_health_issue);

alter table clin.external_care drop constraint if exists FK_clin_ext_care_fk_health_issue cascade;

alter table clin.external_care
	add constraint FK_clin_ext_care_fk_health_issue foreign key (fk_health_issue)
		references clin.health_issue(pk)
		on update cascade
		on delete restrict
;

-- --------------------------------------------------------------
-- .issue
comment on column clin.external_care.issue is 'description of the issue of external care';

alter table clin.external_care drop constraint if exists clin_ext_care_sane_issue cascade;

alter table clin.external_care
	add constraint clin_ext_care_sane_issue
		check(gm.is_null_or_non_empty_string(issue) is True)
;

-- --------------------------------------------------------------
-- .fk_org_unit
comment on column clin.external_care.fk_org_unit is 'link to the org unit where care is rendered';

drop index if exists clin.idx_external_care_fk_org_unit cascade;
create index idx_external_care_fk_org_unit on clin.external_care(fk_org_unit);

alter table clin.external_care drop constraint if exists FK_clin_ext_care_fk_org_unit cascade;

alter table clin.external_care
	add constraint FK_clin_ext_care_fk_org_unit foreign key (fk_org_unit)
		references dem.org_unit(pk)
		on update cascade
		on delete restrict
;

alter table clin.external_care
	alter column fk_org_unit
		set not null
;

-- --------------------------------------------------------------
-- .provider
comment on column clin.external_care.provider is 'name of actual provider at .fk_org_unit';

alter table clin.external_care drop constraint if exists clin_ext_care_sane_provider cascade;

alter table clin.external_care
	add constraint clin_ext_care_sane_provider
		check(gm.is_null_or_non_empty_string(provider) is true)
;

-- --------------------------------------------------------------
-- .comment
comment on column clin.external_care.comment is 'comment on the patient/provider relationship, say role/issues cared for/...';

alter table clin.external_care drop constraint if exists clin_ext_care_sane_comment cascade;

alter table clin.external_care
	add constraint clin_ext_care_sane_comment
		check(gm.is_null_or_non_empty_string(comment) is true)
;

-- --------------------------------------------------------------
-- table constraints:
-- explicit issue XOR linked issue
alter table clin.external_care drop constraint if exists clin_ext_care_issue_xor_fk_issue cascade;

alter table clin.external_care
	add constraint clin_ext_care_issue_xor_fk_issue
		check (
			(
				(fk_health_issue is null) and (issue is not null)
			)	or	(
				(fk_health_issue is not null) and (issue is null)
			)
		)
;


-- linked issue and encounter must belong to same patient
create or replace function clin.trf_sanity_check_enc_issue_ins_upd()
	returns trigger
	 language 'plpgsql'
	as '
declare
	_enc_pk integer;
	_epi_pk integer;
	_identity_from_encounter integer;
	_identity_from_issue integer;
	_cmd text;
begin
	select fk_patient into _identity_from_encounter from clin.encounter where pk = NEW.fk_encounter;
--	raise notice ''%: % -> %'', _cmd, _enc_pk, _identity_from_encounter;
	select fk_patient into _identity_from_issue
	from clin.encounter where pk = (
		select fk_encounter from clin.health_issue where pk = NEW.fk_health_issue
	);

	IF _identity_from_encounter <> _identity_from_issue THEN
		RAISE EXCEPTION ''% into clin.external_care: Sanity check failed. fk_encounter=% -> patient=%. fk_health_issue=% -> patient=%.'',
			TG_OP,
			NEW.fk_encounter,
			_identity_from_encounter,
			NEW.fk_health_issue,
			_identity_from_issue
			USING ERRCODE = ''check_violation''
		;
		return NULL;
	END IF;

	return NEW;
end;
';

DROP TRIGGER IF EXISTS tr_sanity_check_enc_issue_ins_upd ON clin.external_care CASCADE;

CREATE CONSTRAINT TRIGGER tr_sanity_check_enc_issue_ins_upd
	AFTER INSERT OR UPDATE ON clin.external_care
	DEFERRABLE INITIALLY DEFERRED
	FOR EACH ROW WHEN (NEW.fk_health_issue IS NOT NULL)
	EXECUTE PROCEDURE clin.trf_sanity_check_enc_issue_ins_upd();


-- linked issue (= linked patient) can only exist once per org unit
alter table clin.external_care drop constraint if exists clin_ext_care_uniq_fk_issue_per_unit cascade;

alter table clin.external_care
	add constraint clin_ext_care_uniq_fk_issue_per_unit
		unique(fk_health_issue, fk_org_unit)
;


-- explicit issue only once per (patient, org_unit)
create or replace function clin.trf_check_ext_care_uniq_issue_per_enc_and_unit_ins_upd()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_issue_count integer;
BEGIN
	SELECT COUNT(1) INTO STRICT _issue_count
	FROM clin.external_care
	WHERE
		issue = NEW.issue
			AND
		fk_org_unit = NEW.fk_org_unit
			AND
		fk_encounter IN (
			SELECT pk FROM clin.encounter WHERE fk_patient = (
				SELECT fk_patient FROM clin.encounter WHERE pk = NEW.fk_encounter
			)
		)
	;
	IF _issue_count > 1 THEN
		RAISE EXCEPTION ''% into clin.external_care: Sanity check failed. Cannot insert issue [%] more than once for patient of encounter [%] at org unit [%].'',
			TG_OP,
			NEW.issue,
			NEW.fk_encounter,
			NEW.fk_org_unit
			USING ERRCODE = ''check_violation'';
		return NULL;
	END IF;
	RETURN NEW;
END;
';

DROP TRIGGER IF EXISTS tr_clin_ext_care_uniq_issue_per_enc_and_unit_ins_upd ON clin.external_care CASCADE;

CREATE CONSTRAINT TRIGGER tr_clin_ext_care_uniq_issue_per_enc_and_unit_ins_upd
	AFTER INSERT OR UPDATE ON clin.external_care
	DEFERRABLE INITIALLY DEFERRED
	FOR EACH ROW WHEN (NEW.fk_health_issue IS NULL)
	EXECUTE PROCEDURE clin.trf_check_ext_care_uniq_issue_per_enc_and_unit_ins_upd();

-- --------------------------------------------------------------
drop view if exists clin.v_external_care cascade;

create view clin.v_external_care as

select
	c_ec.pk
		as pk_external_care,
	(select fk_patient from clin.encounter where pk = c_ec.fk_encounter)
		as pk_identity,
	coalesce (
		c_ec.issue,
		c_hi.description
	)
		as issue,
	c_ec.provider
		as provider,
	d_ou.description
		as unit,
	d_o.description
		as organization,
	c_ec.comment
		as comment,
	c_ec.fk_health_issue
		as pk_health_issue,
	c_ec.fk_org_unit
		as pk_org_unit,
	c_ec.fk_encounter
		as pk_encounter,
	c_ec.xmin
		as xmin_external_care,
	c_ec.modified_when,
	c_ec.modified_by,
	c_ec.row_version
from
	clin.external_care c_ec
		left join clin.health_issue c_hi on (c_hi.pk = c_ec.fk_health_issue)
			left join dem.org_unit d_ou on (c_ec.fk_org_unit = d_ou.pk)
				left join dem.org d_o on (d_ou.fk_org = d_o.pk)
;

revoke all on clin.v_external_care from public;
grant select on clin.v_external_care to group "gm-doctors";

-- --------------------------------------------------------------
drop view if exists clin.v_external_care_journal cascade;

create view clin.v_external_care_journal as
select
	c_vec.pk_identity
		as pk_patient,
	c_vec.modified_when
		as modified_when,
	c_vec.modified_when
		as clin_when,
	c_vec.modified_by
		as modified_by,
	's'::text
		as soap_cat,
	_('External care')
		|| coalesce(' ' || _('by') || ' ' || c_vec.provider, '')
		|| ' @ ' || c_vec.unit || ' ' || _('of') || ' ' || c_vec.organization || E'\n'
		|| _('Issue:') || ' ' || c_vec.issue || E'\n'
		|| coalesce(_('Comment:') || ' ' || c_vec.comment, '')
		as narrative,
	c_vec.pk_encounter
		as pk_encounter,
	NULL::integer
		as pk_episode,
	c_vec.pk_health_issue
		as pk_health_issue,
	c_vec.pk_external_care
		as src_pk,
	'clin.v_external_care'::text
		as src_table,
	c_vec.row_version
		as row_version
from
	clin.v_external_care c_vec
;

revoke all on clin.v_external_care_journal from public;
grant select on clin.v_external_care_journal to group "gm-doctors";

-- --------------------------------------------------------------
delete from clin.external_care where
	fk_encounter in (
		select pk from clin.encounter where fk_patient = (
			select pk_identity from dem.v_persons where firstnames = 'James Tiberius' and lastnames = 'Kirk'
		)
	)
;

insert into clin.external_care (
	fk_encounter,
	issue,
	fk_org_unit,
	provider,
	comment
)
select
	(select pk
	 from clin.encounter
	 where fk_patient = (select pk_identity from dem.v_persons where firstnames = 'James Tiberius' and lastnames = 'Kirk')
	limit 1
	),
	'intermittent mental disturbance',
	(select pk from dem.org_unit where description = 'Enterprise Sickbay'),
	'Spock',
	'needs copious doses of rationality'
where
		exists (
	(select pk_identity from dem.v_persons where firstnames = 'James Tiberius' and lastnames = 'Kirk')
		) and exists (
	(select pk from dem.org_unit where description = 'Enterprise Sickbay')
);


insert into clin.external_care (
	fk_encounter,
	fk_health_issue,
	fk_org_unit,
	provider,
	comment
)
select
	(select pk
	 from clin.encounter
	 where fk_patient = (select pk_identity from dem.v_persons where firstnames = 'James Tiberius' and lastnames = 'Kirk')
	limit 1
	),
	(select pk_health_issue from clin.v_health_issues where description = '9/2000 extraterrestrial infection' and pk_patient = (select pk_identity from dem.v_persons where firstnames = 'James Tiberius' and lastnames = 'Kirk')),
	(select pk from dem.org_unit where description = 'Enterprise Sickbay'),
	'RN Chapel',
	'in-mission wound care'
where
		exists (
	(select pk_health_issue from clin.v_health_issues where description = '9/2000 extraterrestrial infection' and pk_patient = (select pk_identity from dem.v_persons where firstnames = 'James Tiberius' and lastnames = 'Kirk'))
		) and exists (
	(select pk from dem.org_unit where description = 'Enterprise Sickbay')
);

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-clin-external_care-dynamic.sql', '20.0');
