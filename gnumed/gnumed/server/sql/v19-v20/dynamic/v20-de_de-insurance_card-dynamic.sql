-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
drop table if exists de_de.kvk cascade;
drop table if exists de_de.behandlungsfall cascade;
drop table if exists de_de.prax_geb_paid cascade;
drop table if exists de_de.beh_fall_typ cascade;
drop table if exists de_de.zuzahlungsbefreiung cascade;
drop table if exists de_de.payment_method cascade;
drop table if exists de_de.lab_test_gnr cascade;

drop table if exists audit.log_behandlungsfall cascade;
drop table if exists audit.log_prax_geb_paid cascade;
drop table if exists audit.log_beh_fall_typ cascade;
drop table if exists audit.log_lab_test_gnr cascade;

delete from audit.audited_tables where schema = 'de_de';

-- --------------------------------------------------------------
comment on table de_de.insurance_card is
	'Saves data for German insurance cards.';

--select gm.register_notifying_table('clin', 'external_care');
select audit.register_table_for_auditing('de_de', 'insurance_card');

revoke all on de_de.insurance_card from public;
grant select, insert, update, delete on de_de.insurance_card to "gm-staff";
grant usage on de_de.insurance_card_pk_seq to "gm-staff";

-- --------------------------------------------------------------
-- .fk_identity
comment on column de_de.insurance_card.fk_identity is 'link to the patient';

alter table de_de.insurance_card drop constraint if exists FK_clin_ext_care_fk_identity cascade;

alter table de_de.insurance_card
	add constraint FK_clin_ext_care_fk_identity foreign key (fk_identity)
		references dem.identity(pk)
		on update cascade
		on delete restrict
;

alter table de_de.insurance_card
	alter column fk_identity
		set not null;

-- --------------------------------------------------------------
-- .formatted_dob
comment on column de_de.insurance_card.formatted_dob is 'Pre-formatted (dd.mm.yyyy) pseudo (may contain 0s) DOB as found on card, to be used in official forms.';

alter table de_de.insurance_card drop constraint if exists de_de_insurance_card_sane_dob cascade;

alter table de_de.insurance_card
	add constraint de_de_insurance_card_sane_dob
		check(gm.is_null_or_blank_string(formatted_dob) is false)
;

-- --------------------------------------------------------------
-- .valid_until
comment on column de_de.insurance_card.valid_until is 'End-of-validity of card as found on card.';

alter table de_de.insurance_card
	alter column valid_until
		set not null;

-- --------------------------------------------------------------
-- .presented
comment on column de_de.insurance_card.presented is 'When was the card presented (read).';

alter table de_de.insurance_card
	alter column presented
		set default CURRENT_TIMESTAMP;

alter table de_de.insurance_card
	alter column presented
		set not null;

alter table de_de.insurance_card drop constraint if exists de_de_insurance_card_sane_presented cascade;

alter table de_de.insurance_card
	add constraint de_de_insurance_card_sane_presented
		check(presented <= now())
;

-- --------------------------------------------------------------
-- .invalidated
comment on column de_de.insurance_card.valid_until is 'Invalidation date of card (say, switch of insurance companies).';

-- --------------------------------------------------------------
-- .raw_data
comment on column de_de.insurance_card.raw_data is 'Data as read from the card. May include reader specific additional fields.';

alter table de_de.insurance_card
	alter column raw_data
		set not null;

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-de_de-insurance_card-dynamic.sql', '20.0');
