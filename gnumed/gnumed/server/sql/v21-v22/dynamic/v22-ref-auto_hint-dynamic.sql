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
-- GNUmed now listens to hint changes
select gm.register_notifying_table('ref', 'auto_hint');

-- now that we have user-level editing of hint priorities we better log changes
select audit.register_table_for_auditing('ref', 'auto_hint');

-- --------------------------------------------------------------
-- .popup_priority
comment on column ref.auto_hint.popup_type is
	'0: do not include in any popups (= 0 popups); 1: show an individual popup for this hint (= 1 hint per popup), 2: include in list popups only (= 2 or more hints in popup)';


alter table ref.auto_hint
	alter column popup_type
		set default 1;

-- better safe than sorry for existing hints
update ref.auto_hint set
	popup_type = 1;

alter table ref.auto_hint
	alter column popup_type
		set not null;


alter table ref.auto_hint drop constraint if exists ref_auto_hint_sane_popup_type cascade;

alter table ref.auto_hint
	add constraint ref_auto_hint_sane_popup_type check (
		(popup_type > -1)
			and
		(popup_type < 3)
	);

-- --------------------------------------------------------------
-- .highlight_as_priority
comment on column ref.auto_hint.highlight_as_priority is
	'Whether or not user wants this hint highlighted (possibly among a list of displayed hints), the way of highlighting is up to the application.';


alter table ref.auto_hint
	alter column highlight_as_priority
		set default True;

-- better safe than sorry for existing hints
update ref.auto_hint set
	highlight_as_priority = True;

alter table ref.auto_hint
	alter column highlight_as_priority
		set not null;

-- --------------------------------------------------------------
drop view if exists ref.v_auto_hints cascade;

create view ref.v_auto_hints as
select
	pk
		as pk_auto_hint,
	query
		as query,
	recommendation_query
		as recommendation_query,
	title
		as title,
	hint
		as hint,
	url
		as url,
	is_active
		as is_active,
	source
		as source,
	lang
		as lang,
	popup_type
		as popup_type,
	highlight_as_priority
		as highlight_as_priority,
	-- this column is set from clin.get_hints_for_patient(),
	-- it only exists in this view in order to enable the syntax
	-- "returns setof ref.v_auto_hints" in that function
	null::text
		as rationale4suppression,
	-- this column is set from clin.get_hints_for_patient(),
	-- it only exists in this view in order to enable the syntax
	-- "returns setof ref.v_auto_hints" in that function
	null::text
		as recommendation,
	md5(
		coalesce(query, '')
		|| coalesce(recommendation_query, '')
		|| coalesce(title, '')
		|| coalesce(hint, '')
		|| coalesce(url, '')
	)	as md5_sum,
	xmin
		as xmin_auto_hint
from
	ref.auto_hint
;


revoke all on ref.v_auto_hints from public;
grant select on ref.v_auto_hints to group "gm-staff";

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-ref-auto_hint-dynamic.sql', '22.0');
