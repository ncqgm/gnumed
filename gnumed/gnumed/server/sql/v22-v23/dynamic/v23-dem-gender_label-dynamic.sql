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
alter table dem.gender_label
	drop column if exists sort_weight text;

-- --------------------------------------------------------------
alter table dem.gender_label
	drop constraint if exists gender_label_tag_check;

comment on column dem.gender_label.symbol is
	'A symbol to be used for this gender, if desired.';

-- --------------------------------------------------------------
drop view if exists dem.v_gender_labels cascade;

create view dem.v_gender_labels as
select
	d_gl.tag,
	_(d_gl.tag)
		as l10n_tag,
	d_gl.label,
	_(d_gl.label)
		as l10n_label,
	d_gl.comment,
	d_gl.symbol
		as symbol,
	_(d_gl.symbol)
		as l10n_symbol,
	d_gl.pk
		as pk_gender_label
from
	dem.gender_label d_gl
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-dem-gender_label-dynamic.sql', '23.0');
