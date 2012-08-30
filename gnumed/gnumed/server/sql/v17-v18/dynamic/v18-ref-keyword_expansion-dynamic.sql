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
comment on table ref.keyword_expansion is
	'Arbitrary binary or textual snippets of data. Used as text macros or document "ribbons".';

-- --------------------------------------------------------------
-- .keyword
comment on column ref.keyword_expansion.keyword is 'A keyword by which to uniquely identify this snippet. Can only exist once per provider.';

\unset ON_ERROR_STOP
alter table ref.keyword_expansion drop constraint ref_kwd_exp_sane_keyword;
\set ON_ERROR_STOP 1


alter table ref.keyword_expansion
	add constraint ref_kwd_exp_sane_keyword check (
		gm.is_null_or_blank_string(keyword) is False
	);

-- --------------------------------------------------------------
-- .textual_snippet
comment on column ref.keyword_expansion.textual_snippet is 'This holds the text of non-binary snippets.';

alter table ref.keyword_expansion
	alter column textual_snippet
		drop not null;


\unset ON_ERROR_STOP
alter table ref.keyword_expansion drop constraint ref_kwd_exp_sane_text;
\set ON_ERROR_STOP 1

alter table ref.keyword_expansion
	add constraint ref_kwd_exp_sane_text check (
		gm.is_null_or_non_empty_string(textual_snippet) is True
	);

-- --------------------------------------------------------------
-- .binary_snippet
comment on column ref.keyword_expansion.binary_snippet is 'This holds the binary data of non-textual snippets';

\unset ON_ERROR_STOP
alter table ref.keyword_expansion drop constraint ref_kwd_exp_sane_data;
\set ON_ERROR_STOP 1


alter table ref.keyword_expansion
	add constraint ref_kwd_exp_sane_data check (
		(binary_snippet is NULL)
			or
		(octet_length(binary_snippet) > 0)
	);

-- --------------------------------------------------------------
-- table constraint
\unset ON_ERROR_STOP
alter table ref.keyword_expansion drop constraint ref_kwd_exp_binary_xor_textual;
\set ON_ERROR_STOP 1


alter table ref.keyword_expansion
	add constraint ref_kwd_exp_binary_xor_textual check (
		((binary_snippet is NULL) and (textual_snippet is not NULL))
			or
		((binary_snippet is not NULL) and (textual_snippet is NULL))
	);

-- --------------------------------------------------------------
-- .key_id
comment on column ref.keyword_expansion.key_id is 'A GnuPG key ID. If this is set (NOT NULL) then the *_snippet is encrypted';

\unset ON_ERROR_STOP
alter table ref.keyword_expansion drop constraint ref_kwd_exp_sane_key_id;
\set ON_ERROR_STOP 1

alter table ref.keyword_expansion
	add constraint ref_kwd_exp_sane_key_id check (
		gm.is_null_or_non_empty_string(key_id) is True
	);

-- --------------------------------------------------------------
-- views
-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_keyword_expansions cascade;
drop view clin.v_your_keyword_expansions cascade;
\set ON_ERROR_STOP 1


\unset ON_ERROR_STOP
drop view ref.v_keyword_expansions cascade;
\set ON_ERROR_STOP 1

create view ref.v_keyword_expansions as
select
	r_ke.pk
		as pk_keyword_expansion,
	r_ke.fk_staff
		as pk_staff,
	r_ke.keyword
		as keyword,
	r_ke.textual_snippet
		as expansion,
	r_ke.key_id
		as key_id,
	(r_ke.fk_staff is null)
		as public_expansion,
	(r_ke.fk_staff is not null)
		as private_expansion,
	r_ke.owner
		as owner
from
	ref.keyword_expansion r_ke
where
	binary_snippet is null
;


comment on view ref.v_keyword_expansions is
	'Just a slightly more convenient view over expansions, excluding binary ones.';


grant select on
	ref.v_keyword_expansions
to group "gm-doctors";

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view ref.v_your_keyword_expansions cascade;
\set ON_ERROR_STOP 1

create view ref.v_your_keyword_expansions as
select distinct on (keyword) *
from (
	select
		r_ke.pk
			as pk_keyword_expansion,
		r_ke.fk_staff
			as pk_staff,
		r_ke.keyword
			as keyword,
		r_ke.textual_snippet
			as expansion,
		r_ke.key_id
			as key_id,
		false
			as public_expansion,
		true
			as private_expansion,
		r_ke.owner
			as owner
	from
		ref.keyword_expansion r_ke
	where
		fk_staff = (select pk from dem.staff where db_user = current_user)
			and
		binary_snippet is null

		union all

	select
		r_ke.pk
			as pk_keyword_expansion,
		r_ke.fk_staff
			as pk_staff,
		r_ke.keyword
			as keyword,
		r_ke.textual_snippet
			as expansion,
		r_ke.key_id
			as key_id,
		true
			as public_expansion,
		false
			as private_expansion,
		r_ke.owner
			as owner
	from
		ref.keyword_expansion r_ke
	where
		fk_staff is null
			and
		binary_snippet is null
	order by
		private_expansion desc
) as union_result;


comment on view ref.v_your_keyword_expansions is
'View over the text expansions relevant to the current user:
a private expansion set up for the current user overrides a
public expansion of the same keyword. Binary expansions are excluded.';


grant select on
	ref.v_your_keyword_expansions
to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v18-ref-keyword_expansion-dynamic.sql', '18.0');
