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
comment on table ref.lnk_loinc2substance is 'Links LOINC codes to substances (for monitoring).';

select audit.register_table_for_auditing('ref', 'lnk_loinc2substance');
select gm.register_notifying_table('ref', 'lnk_loinc2substance');

-- table constraints
drop index if exists ref.idx_ll2s_uniq_l_per_s cascade;
create unique index idx_ll2s_uniq_l_per_s on ref.lnk_loinc2substance(fk_substance, loinc);

-- grants
grant select on ref.lnk_loinc2substance to "gm-public";
grant select, insert, update, delete on ref.lnk_loinc2substance to "gm-doctors";
grant usage on ref.lnk_loinc2substance_pk_seq to "gm-doctors";

-- --------------------------------------------------------------
-- .fk_substance
comment on column ref.lnk_loinc2substance.fk_substance is 'FK linking the substance';

alter table ref.lnk_loinc2substance
	alter column fk_substance
		set not null;

alter table ref.lnk_loinc2substance drop constraint if exists ref_ll2s_fk_substance cascade;

alter table ref.lnk_loinc2substance
	add constraint ref_ll2s_fk_substance
		foreign key (fk_substance) references ref.substance(pk)
			on update cascade
			on delete restrict
;

-- --------------------------------------------------------------
-- .loinc
comment on column ref.lnk_loinc2substance.loinc is 'LOINC to monitor for substance';

alter table ref.lnk_loinc2substance drop constraint if exists ref_ll2s_sane_loinc cascade;

alter table ref.lnk_loinc2substance
	add constraint ref_ll2s_sane_loinc check (
		gm.is_null_or_blank_string(loinc) is False
	);

-- should be FK match partial, too

-- --------------------------------------------------------------
-- .max_age
comment on column ref.lnk_loinc2substance.max_age is 'maximum recommended age of value of monitored LOINC in a patient,
set this to something like "999 years" if it needs to be monitored just once,
NULL = unspecified';

-- perhaps > 0 ?

-- --------------------------------------------------------------
-- .comment
comment on column ref.lnk_loinc2substance.comment is 'a comment on this monitoring advice';

alter table ref.lnk_loinc2substance drop constraint if exists ref_ll2s_sane_comment cascade;

alter table ref.lnk_loinc2substance
	add constraint ref_ll2s_sane_comment check (
		gm.is_null_or_non_empty_string(comment) is True
	);

-- --------------------------------------------------------------
drop view if exists ref.v_lnk_loincs2substances cascade;

create view ref.v_lnk_loincs2substances as
select
	r_ll2s.pk as pk_lnk_loinc2substance,
	r_s.description as substance,
	r_ll2s.loinc,
	r_ll2s.max_age,
	r_ll2s.comment,
	r_s.atc,
	r_s.pk as pk_substance,

	r_ll2s.xmin as xmin_lnk_loinc2substance
from
	ref.substance r_s
		inner join ref.lnk_loinc2substance r_ll2s on (r_ll2s.fk_substance = r_s.pk)
;

-- grant
grant select on ref.v_lnk_loincs2substances to "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-ref-lnk_loinc2substance-dynamic.sql', '22.0');
