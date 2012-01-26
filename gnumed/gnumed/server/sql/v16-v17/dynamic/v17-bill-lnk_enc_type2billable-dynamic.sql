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
comment on table bill.lnk_enc_type2billable is 'actual bills';

select audit.register_table_for_auditing('bill', 'bill');
select gm.register_notifying_table('bill', 'bill');

grant select, insert, delete, update on
	bill.lnk_enc_type2billable
to group "gm-doctors";

grant select on
	bill.lnk_enc_type2billable
to group "gm-public";

grant usage on
	bill.lnk_enc_type2billable_pk_seq
to group "gm-public";

-- --------------------------------------------------------------
-- .fk_billable
comment on column bill.lnk_enc_type2billable.fk_billable is
	'Links to the billable item the encounter type is associated with.';

alter table bill.lnk_enc_type2billable
	alter column fk_billable
		set not null;

\unset ON_ERROR_STOP
alter table bill.lnk_enc_type2billable drop constraint lnk_enc_type2billable_fk_billable_fkey cascade;
\set ON_ERROR_STOP 1

alter table bill.lnk_enc_type2billable
	add foreign key (fk_billable)
		references ref.billable(pk)
		on update cascade
		on delete cascade;


\unset ON_ERROR_STOP
drop index idx_lnk_enc_type2billable_fk_billable cascade;
\set ON_ERROR_STOP 1

create index idx_lnk_enc_type2billable_fk_billable on bill.lnk_enc_type2billable(fk_billable);

-- --------------------------------------------------------------
-- .fk_encounter_type
comment on column bill.lnk_enc_type2billable.fk_encounter_type is
	'Links to encounter type this billable is associated with.';

alter table bill.lnk_enc_type2billable
	alter column fk_encounter_type
		set not null;

\unset ON_ERROR_STOP
alter table bill.lnk_enc_type2billable drop constraint lnk_enc_type2billable_fk_encounter_type_fkey cascade;
\set ON_ERROR_STOP 1

alter table bill.lnk_enc_type2billable
	add foreign key (fk_encounter_type)
		references clin.encounter_type(pk)
		on update cascade
		on delete cascade;


\unset ON_ERROR_STOP
drop index idx_lnk_enc_type2billable_fk_encounter_type cascade;
\set ON_ERROR_STOP 1

create index idx_lnk_enc_type2billable_fk_encounter_type on bill.lnk_enc_type2billable(fk_encounter_type);

-- --------------------------------------------------------------
select gm.log_script_insertion('v17-bill-lnk_enc_type2billable-dynamic.sql', '17.0');
