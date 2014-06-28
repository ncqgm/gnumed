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
-- .fk_identity
comment on column clin.external_care.fk_identity is 'link to the patient';

alter table clin.external_care drop constraint if exists FK_clin_ext_care_fk_identity cascade;

alter table clin.external_care
	add constraint FK_clin_ext_care_fk_identity foreign key (fk_identity)
		references clin.patient(fk_identity)
		on update cascade
		on delete restrict
;

-- --------------------------------------------------------------
-- .fk_health_issue
comment on column clin.external_care.fk_health_issue is 'link to a health issue, if any';

alter table clin.external_care drop constraint if exists FK_clin_ext_care_fk_health_issue cascade;

alter table clin.external_care
	add constraint FK_clin_ext_care_fk_health_issue foreign key (fk_health_issue)
		references clin.health_issue(pk)
		on update cascade
		on delete restrict
;

alter table clin.external_care drop constraint if exists clin_ext_care_uniq_fk_issue cascade;

alter table clin.external_care
	add constraint clin_ext_care_uniq_fk_issue
		unique(fk_health_issue)
;

-- --------------------------------------------------------------
-- .issue
comment on column clin.external_care.issue is 'description of the issue of external care';

alter table clin.external_care drop constraint if exists clin_ext_care_sane_issue cascade;

alter table clin.external_care
	add constraint clin_ext_care_sane_issue
		check(gm.is_null_or_non_empty_string(issue) is True)
;

alter table clin.external_care drop constraint if exists clin_ext_care_uniq_issue cascade;

alter table clin.external_care
	add constraint clin_ext_care_uniq_issue
		unique(issue)
;

-- --------------------------------------------------------------
-- .fk_org_unit
comment on column clin.external_care.fk_org_unit is 'link to the org unit where care is rendered';

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
-- table constraints
alter table clin.external_care drop constraint if exists clin_ext_care_issue_xor_identity_fk cascade;

alter table clin.external_care
	add constraint clin_ext_care_issue_xor_identity_fk
		check (
			(
				(fk_health_issue is null) and (fk_identity is not null)
			)	or	(
				(fk_health_issue is not null) and (fk_identity is null)
			)
		)
;


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


alter table clin.external_care drop constraint if exists clin_ext_care_uniq_issue_per_identity_and_org cascade;

alter table clin.external_care
	add constraint clin_ext_care_uniq_issue_per_identity_and_org
		unique(fk_identity, issue, fk_org_unit)
;


alter table clin.external_care drop constraint if exists clin_ext_care_uniq_fk_issue_per_identity_and_org cascade;

alter table clin.external_care
	add constraint clin_ext_care_uniq_fk_issue_per_identity_and_org
		unique(fk_identity, fk_health_issue, fk_org_unit)
;

-- --------------------------------------------------------------
drop view if exists clin.v_external_care cascade;

create view clin.v_external_care as

select
	c_ec.pk
		as pk_external_care,
	coalesce (
		c_ec.fk_identity,
		(select fk_patient from clin.encounter where pk = (select fk_encounter from clin.health_issue where pk = c_ec.fk_health_issue))
	)
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
	c_ec.xmin
		as xmin_external_care
from
	clin.external_care c_ec
		left join clin.health_issue c_hi on (c_hi.pk = c_ec.fk_health_issue)
			left join dem.org_unit d_ou on (c_ec.fk_org_unit = d_ou.pk)
				left join dem.org d_o on (d_ou.fk_org = d_o.pk)
;

revoke all on clin.v_external_care from public;
grant select on clin.v_external_care to group "gm-doctors";

-- --------------------------------------------------------------
delete from clin.external_care where
	fk_identity = (
		select pk_identity from dem.v_persons where firstnames = 'James Tiberius' and lastnames = 'Kirk'
	)
;

insert into clin.external_care (
	fk_identity,
	issue,
	fk_org_unit,
	provider,
	comment
)
select
	(select pk_identity from dem.v_persons where firstnames = 'James Tiberius' and lastnames = 'Kirk'),
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
	fk_health_issue,
	fk_org_unit,
	provider,
	comment
)
select
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
