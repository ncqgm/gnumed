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
comment on table ref.lnk_indic2vaccine is 'Links vaccination targets to vaccines.';

--select audit.register_table_for_auditing('ref', 'lnk_indic2vaccine');
select gm.register_notifying_table('ref', 'lnk_indic2vaccine');

grant select on ref.lnk_indic2vaccine to "gm-public";
grant select, insert, update, delete on ref.lnk_indic2vaccine to "gm-staff", "gm-doctors";

-- --------------------------------------------------------------
-- .fk_indication
alter table ref.lnk_indic2vaccine
	add foreign key (fk_indication)
		references ref.vacc_indication(pk)
		on delete restrict
		on update cascade;

alter table ref.lnk_indic2vaccine
	alter column fk_indication
		set not null;

drop index if exists ref.idx__ref__lnk_ind2vacc__fk_ind cascade;
create index idx__ref__lnk_ind2vacc__fk_ind on ref.lnk_indic2vaccine(fk_indication);

-- --------------------------------------------------------------
-- .fk_vaccine
alter table ref.lnk_indic2vaccine
	add foreign key (fk_vaccine)
		references ref.vaccine(pk)
		on delete restrict
		on update cascade;

alter table ref.lnk_indic2vaccine
	alter column fk_vaccine
		set not null;

drop index if exists ref.idx__ref__lnk_ind2vacc__fk_vaccine cascade;
create index idx__ref__lnk_ind2vacc__fk_vaccine on ref.lnk_indic2vaccine(fk_vaccine);

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-ref-lnk_indic2vaccine-dynamic.sql', '23.0');
