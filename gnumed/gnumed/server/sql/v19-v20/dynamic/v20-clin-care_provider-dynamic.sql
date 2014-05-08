-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
comment on table clin.care_provider is
	'This table lists providers related to care for a given patient.';


revoke all on clin.care_provider from public;
grant select, insert, update, delete on clin.care_provider to "gm-doctors";
grant usage on clin.care_provider_pk_seq to "gm-doctors";

-- --------------------------------------------------------------
-- .fk_identity
comment on column clin.care_provider.fk_identity is 'link to the patient';

alter table clin.care_provider drop constraint if exists FK_clin_care_provider_fk_identity cascade;

alter table clin.care_provider
	add constraint FK_clin_care_provider_fk_identity foreign key (fk_identity)
		references clin.patient(fk_identity)
		on update cascade
		on delete restrict
;

alter table clin.care_provider
	alter column fk_identity
		set not null
;

-- --------------------------------------------------------------
-- .fk_provider
comment on column clin.care_provider.fk_provider is 'link to the provider';

alter table clin.care_provider drop constraint if exists FK_clin_care_provider_fk_provider cascade;

alter table clin.care_provider
	add constraint FK_clin_care_provider_fk_provider foreign key (fk_provider)
		references ref.provider(pk)
		on update cascade
		on delete restrict
;

alter table clin.care_provider
	alter column fk_provider
		set not null
;

-- --------------------------------------------------------------
-- .comment
comment on column clin.care_provider.comment is 'comment on the patient/provider relationship, say role/issues cared for/...';

alter table clin.care_provider drop constraint if exists clin_care_provider_sane_comment cascade;

alter table clin.care_provider
	add constraint clin_care_provider_sane_comment
		check(gm.is_null_or_blank_string(comment) is false)
;

-- --------------------------------------------------------------
-- table constraints
alter table clin.care_provider drop constraint if exists clin_care_provider_uniq_prov_pat cascade;

alter table clin.care_provider
	add constraint clin_care_provider_uniq_prov_pat
		unique(fk_identity, fk_provider)
;

-- --------------------------------------------------------------
delete from clin.care_provider where
	fk_identity = (
		select pk_identity from dem.v_persons where firstnames = 'James Tiberius' and lastnames = 'Kirk'
	)
;

insert into clin.care_provider (fk_identity, fk_provider, comment) values (
	(select pk_identity from dem.v_persons where firstnames = 'James Tiberius' and lastnames = 'Kirk'),
	(select pk from ref.provider where fk_identity = (
		select pk_identity from dem.v_persons where firstnames = 'Leonard Horatio' and lastnames = 'McCoy'
	) limit 1),
	'primary doctor'
);

-- --------------------------------------------------------------
drop view if exists clin.v_care_providers cascade;

create view clin.v_care_providers as
select
	c_cp.fk_identity
		as pk_patient,
	c_cp.fk_provider
		as pk_provider,
	r_vp.title
		as provider_title,
	r_vp.firstnames
		as provider_firstnames,
	r_vp.lastnames
		as provider_lastnames,
	r_vp.gender
		as provider_gender,
	r_vp.speciality,
	r_vp.l10n_speciality,
	c_cp.comment,
	r_vp.pk_speciality
from
	clin.care_provider c_cp
		left join ref.v_providers r_vp on (c_cp.fk_provider = r_vp.pk_provider)
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-clin-care_provider-dynamic.sql', '20.0');
