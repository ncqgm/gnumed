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
-- .textual_data
comment on column ref.keyword_expansion.textual_data is 'This holds the text of non-binary snippets.';

alter table ref.keyword_expansion
	alter column textual_data
		drop not null;


\unset ON_ERROR_STOP
alter table ref.keyword_expansion drop constraint ref_kwd_exp_sane_text;
\set ON_ERROR_STOP 1

alter table ref.keyword_expansion
	add constraint ref_kwd_exp_sane_text check (
		gm.is_null_or_non_empty_string(textual_data) is True
	);

-- --------------------------------------------------------------
-- .binary_data
comment on column ref.keyword_expansion.binary_data is 'This holds the binary data of non-textual snippets';

\unset ON_ERROR_STOP
alter table ref.keyword_expansion drop constraint ref_kwd_exp_sane_data;
\set ON_ERROR_STOP 1


alter table ref.keyword_expansion
	add constraint ref_kwd_exp_sane_data check (
		(binary_data is NULL)
			or
		(octet_length(binary_data) > 0)
	);

-- --------------------------------------------------------------
-- table constraint
\unset ON_ERROR_STOP
alter table ref.keyword_expansion drop constraint ref_kwd_exp_binary_xor_textual;
\set ON_ERROR_STOP 1


alter table ref.keyword_expansion
	add constraint ref_kwd_exp_binary_xor_textual check (
		((binary_data is NULL) and (textual_data is not NULL))
			or
		((binary_data is not NULL) and (textual_data is NULL))
	);

-- --------------------------------------------------------------
-- .encrypted
comment on column ref.keyword_expansion.encrypted is 'If true the snippet is encrypted with GnuPG.';

alter table ref.keyword_expansion
	alter column encrypted
		set default false;

alter table ref.keyword_expansion
	alter column encrypted
		set not null;

-- --------------------------------------------------------------
-- views
-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_keyword_expansions cascade;
drop view ref.v_keyword_expansions cascade;
\set ON_ERROR_STOP 1

create view ref.v_keyword_expansions as
select
	r_ke.pk
		as pk_expansion,
	r_ke.fk_staff
		as pk_staff,
	r_ke.keyword
		as keyword,
	r_ke.textual_data
		as expansion,
	r_ke.encrypted
		as is_encrypted,
	(binary_data is null)
		as is_textual,
	octet_length(binary_data)
		as data_size,
	(r_ke.fk_staff is null)
		as public_expansion,
	(r_ke.fk_staff is not null)
		as private_expansion,
	r_ke.owner
		as owner,
	r_ke.xmin
		as xmin_expansion
from
	ref.keyword_expansion r_ke
;


comment on view ref.v_keyword_expansions is
	'Just a slightly more convenient view over expansions.';


grant select on
	ref.v_keyword_expansions
to group "gm-doctors";

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_your_keyword_expansions cascade;
drop view ref.v_your_keyword_expansions cascade;
\set ON_ERROR_STOP 1

create view ref.v_your_keyword_expansions as
select distinct on (keyword) *
from (
	select
		r_ke.pk
			as pk_expansion,
		r_ke.fk_staff
			as pk_staff,
		r_ke.keyword
			as keyword,
		r_ke.textual_data
			as expansion,
		r_ke.encrypted
			as is_encrypted,
		(binary_data is null)
			as is_textual,
		octet_length(binary_data)
			as data_size,
		false
			as public_expansion,
		true
			as private_expansion,
		r_ke.owner
			as owner,
		r_ke.xmin
			as xmin_expansion
	from
		ref.keyword_expansion r_ke
	where
		fk_staff = (select pk from dem.staff where db_user = current_user)

		union all

	select
		r_ke.pk
			as pk_expansion,
		r_ke.fk_staff
			as pk_staff,
		r_ke.keyword
			as keyword,
		r_ke.textual_data
			as expansion,
		r_ke.encrypted
			as is_encrypted,
		(binary_data is null)
			as is_textual,
		octet_length(binary_data)
			as data_size,
		true
			as public_expansion,
		false
			as private_expansion,
		r_ke.owner
			as owner,
		r_ke.xmin
			as xmin_expansion
	from
		ref.keyword_expansion r_ke
	where
		fk_staff is null
	order by
		private_expansion desc
) as union_result;


comment on view ref.v_your_keyword_expansions is
'View over the text expansions relevant to the current user:
a private expansion set up for the current user overrides a
public expansion of the same keyword.';


grant select on
	ref.v_your_keyword_expansions
to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v18-ref-keyword_expansion-dynamic.sql', '18.0');
