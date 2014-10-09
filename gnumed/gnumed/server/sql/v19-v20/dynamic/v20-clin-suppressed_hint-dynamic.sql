-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

set default_transaction_read_only to off;

-- --------------------------------------------------------------
comment on table clin.suppressed_hint is 'A table to hold hints suppressed per patient';


select gm.register_notifying_table('clin', 'suppressed_hint');
select audit.register_table_for_auditing('clin', 'suppressed_hint');


revoke all on clin.suppressed_hint from "public";
grant select on clin.suppressed_hint to group "gm-staff";
grant select, insert, update, delete on clin.suppressed_hint to group "gm-doctors";


GRANT USAGE ON SEQUENCE
	clin.suppressed_hint_pk_seq
to group "gm-doctors";

-- --------------------------------------------------------------
-- .fk_identity
comment on column clin.suppressed_hint.fk_identity is 'the patient this hint is suppressed in';


drop index if exists clin.idx_suppressed_hint_fk_identity cascade;
create index idx_suppressed_hint_fk_identity on clin.suppressed_hint(fk_identity);


alter table clin.suppressed_hint
	alter column fk_identity
		set not null;


alter table clin.suppressed_hint
	drop constraint if exists FK_clin_suppressed_hint_fk_identity cascade;
alter table clin.suppressed_hint
	add constraint FK_clin_suppressed_hint_fk_identity foreign key (fk_identity)
		references clin.patient(fk_identity)
		on update restrict
		on delete cascade
;

-- --------------------------------------------------------------
-- .fk_hint
comment on column clin.suppressed_hint.fk_hint is 'the hint that is suppressed';


drop index if exists clin.idx_suppressed_hint_fk_hint cascade;
create index idx_suppressed_hint_fk_hint on clin.suppressed_hint(fk_hint);


alter table clin.suppressed_hint
	alter column fk_hint
		set not null;


alter table clin.suppressed_hint
	drop constraint if exists FK_clin_suppressed_hint_fk_hint cascade;
alter table clin.suppressed_hint
	add constraint FK_clin_suppressed_hint_fk_hint foreign key (fk_hint)
		references ref.auto_hint(pk)
		on update restrict
		on delete cascade
;

-- --------------------------------------------------------------
-- .rationale
comment on column clin.suppressed_hint.rationale is 'rationale on why this hint is suppressed in this patient';


alter table clin.suppressed_hint
	drop constraint if exists clin_suppressed_hint_sane_rationale cascade;
alter table clin.suppressed_hint
	add constraint clin_suppressed_hint_sane_rationale
		check(gm.is_null_or_blank_string(rationale) is false)
;

-- --------------------------------------------------------------
-- .md5_sum
comment on column clin.suppressed_hint.md5_sum is 'md5 of relevant fields of this hint';


alter table clin.suppressed_hint
	drop constraint if exists clin_suppressed_hint_sane_md5 cascade;
alter table clin.suppressed_hint
	add constraint clin_suppressed_hint_sane_md5
		check(gm.is_null_or_blank_string(md5_sum) is false)
;

-- --------------------------------------------------------------
-- .suppressed_by
comment on column clin.suppressed_hint.suppressed_by is 'who suppressed this hint';


alter table clin.suppressed_hint
	alter column suppressed_by
		set not null;


alter table clin.suppressed_hint
	alter column suppressed_by
		set default CURRENT_USER;


alter table clin.suppressed_hint
	drop constraint if exists clin_suppressed_hint_sane_by cascade;
alter table clin.suppressed_hint
	add constraint clin_suppressed_hint_sane_by check (
		length(suppressed_by) > 0
	);

-- --------------------------------------------------------------
-- .suppressed_when
comment on column clin.suppressed_hint.suppressed_when is 'when was this hint suppressed';


alter table clin.suppressed_hint
	alter column suppressed_when
		set not null;


alter table clin.suppressed_hint
	alter column suppressed_when
		set default statement_timestamp();

-- --------------------------------------------------------------
alter table clin.suppressed_hint
	drop constraint if exists clin_suppressed_hint_uniq_hint_ident cascade;
alter table clin.suppressed_hint
	add constraint clin_suppressed_hint_uniq_hint_ident unique(fk_hint, fk_identity);

-- --------------------------------------------------------------
drop view if exists clin.v_suppressed_hints cascade;


create view clin.v_suppressed_hints as
select
	c_sh.fk_identity
		as pk_identity,
	c_sh.pk
		as pk_suppressed_hint,
	c_sh.fk_hint
		as pk_hint,
	r_vah.title,
	r_vah.hint,
	r_vah.url,
	r_vah.is_active,
	r_vah.source,
	r_vah.query,
	r_vah.lang,
	c_sh.rationale,
	c_sh.md5_sum
		as md5_suppressed,
	r_vah.md5_sum
		as md5_hint,
	c_sh.suppressed_by,
	c_sh.suppressed_when
from
	clin.suppressed_hint c_sh
		join ref.v_auto_hints r_vah on c_sh.fk_hint = r_vah.pk_auto_hint
;


revoke all on clin.v_suppressed_hints from public;
grant select on clin.v_suppressed_hints to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-clin-suppressed_hint-dynamic.sql', '20.0');
