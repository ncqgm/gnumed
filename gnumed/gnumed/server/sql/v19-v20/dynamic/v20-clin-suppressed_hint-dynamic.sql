-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

--set default_transaction_read_only to off;
set check_function_bodies to on;

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
-- .fk_encounter
comment on column clin.suppressed_hint.fk_encounter is 'the encounter during which this hint was first suppressed';


drop index if exists clin.idx_suppressed_hint_fk_encounter cascade;
create index idx_suppressed_hint_fk_encounter on clin.suppressed_hint(fk_encounter);


alter table clin.suppressed_hint
	alter column fk_encounter
		set not null;


alter table clin.suppressed_hint
	drop constraint if exists FK_clin_suppressed_hint_fk_encounter cascade;
alter table clin.suppressed_hint
	add constraint FK_clin_suppressed_hint_fk_encounter foreign key (fk_encounter)
		references clin.encounter(pk)
		on update restrict
		on delete restrict
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
create or replace function clin.trf_sanity_check_uniq_hint_per_pat_ins_upd()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_suppression_count integer;
BEGIN
	-- the count of suppressions for this hint in this patient
	SELECT COUNT(1) INTO STRICT _suppression_count
	FROM clin.suppressed_hint
	WHERE
		fk_hint = NEW.fk_hint
			AND
		fk_encounter IN (
			SELECT pk FROM clin.encounter WHERE fk_patient = (
				SELECT fk_patient FROM clin.encounter WHERE pk = NEW.fk_encounter
			)
		)
	;
	IF _suppression_count > 1 THEN
		RAISE EXCEPTION ''% into clin.suppressed_hint: Sanity check failed. Hint [%] suppressed more than once for patient of encounter [%].'',
			TG_OP,
			NEW.pk,
			NEW.fk_encounter
			USING ERRCODE = ''check_violation'';
		return NULL;
	END IF;
	return NEW;
END;
';


DROP TRIGGER IF EXISTS tr_sanity_check_uniq_hint_per_pat_ins_upd ON clin.suppressed_hint CASCADE;


CREATE CONSTRAINT TRIGGER tr_sanity_check_uniq_hint_per_pat_ins_upd
	AFTER INSERT OR UPDATE ON clin.suppressed_hint
	DEFERRABLE INITIALLY DEFERRED
	FOR EACH ROW EXECUTE PROCEDURE clin.trf_sanity_check_uniq_hint_per_pat_ins_upd();

-- --------------------------------------------------------------
drop view if exists clin.v_suppressed_hints cascade;


create view clin.v_suppressed_hints as
select
	(select fk_patient from clin.encounter where pk = c_sh.fk_encounter)
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
	c_sh.suppressed_when,
	c_sh.fk_encounter
		as pk_encounter
from
	clin.suppressed_hint c_sh
		join ref.v_auto_hints r_vah on c_sh.fk_hint = r_vah.pk_auto_hint
;


revoke all on clin.v_suppressed_hints from public;
grant select on clin.v_suppressed_hints to group "gm-doctors";

-- --------------------------------------------------------------
drop view if exists clin.v_suppressed_hints_journal cascade;


create view clin.v_suppressed_hints_journal as
select
	(select fk_patient from clin.encounter where pk = c_sh.fk_encounter)
		as pk_identity,
	c_sh.modified_when
		as modified_when,
	c_sh.suppressed_when
		as clin_when,
	c_sh.modified_by
		as modified_by,
	'p'::text
		as soap_cat,
	case
		when r_vah.is_active is TRUE then
			_('Active hint')
		else
			_('Inactive hint')
	end
		|| ' #' || c_sh.fk_hint || ' ' || _('suppressed by') || ' ' || c_sh.suppressed_by || E'\n'
		|| coalesce(_('Title: ') || r_vah.title || E'\n', '')
		|| coalesce(_('URL: ') || r_vah.url || E'\n', '')
		|| coalesce(_('Source: ') || r_vah.source || E'\n', '')
		|| coalesce(_('Rationale: ') || c_sh.rationale || E'\n', '')
		|| case when c_sh.md5_sum <> r_vah.md5_sum
			then _('Hint definition has been modified since suppression. Rationale for suppression may no longer apply.') || E'\n'
			else ''
		end
		|| coalesce(_('Hint: ') || r_vah.hint, '')
		as narrative,
	c_sh.fk_encounter
		as fk_encounter,
	NULL::integer
		as pk_episode,
	NULL::integer
		as pk_health_issue,
	c_sh.pk
		as src_pk,
	'clin.suppressed_hint'::text
		as src_table,
	c_sh.row_version
		as row_version
from
	clin.suppressed_hint c_sh
		join ref.v_auto_hints r_vah on c_sh.fk_hint = r_vah.pk_auto_hint
;


revoke all on clin.v_suppressed_hints from public;
grant select on clin.v_suppressed_hints to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-clin-suppressed_hint-dynamic.sql', '20.0');
