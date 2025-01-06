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
comment on table ref.vacc_indication is 'List of target diseases which can be vaccinated against.';

select audit.register_table_for_auditing('ref', 'vacc_indication');
select gm.register_notifying_table('ref', 'vacc_indication');

grant select on ref.vacc_indication to "gm-public";
grant select, insert, update, delete on ref.vacc_indication to "gm-staff", "gm-doctors";

-- --------------------------------------------------------------
-- .target
comment on column ref.vacc_indication.target is 'Name of the target disease/pathogen.';

alter table ref.vacc_indication
	alter column target
		set not null;

drop index if exists ref.idx_uniq__ref__vacc_indication__target cascade;
create unique index idx_uniq__ref__vacc_indication__target on ref.vacc_indication(target);

-- --------------------------------------------------------------
-- .atc
comment on column ref.vacc_indication.atc is 'ATC for the target vaccine, if any. Single-target ATCs only.';

drop index if exists ref.idx_uniq__ref__vacc_indication__atc cascade;
create unique index idx_uniq__ref__vacc_indication__atc on ref.vacc_indication(atc);

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-ref-vacc_indication-dynamic.sql', '23.0');
