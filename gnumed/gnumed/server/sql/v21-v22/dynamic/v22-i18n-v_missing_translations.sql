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
drop view if exists i18n.v_missing_translations cascade;

create view i18n.v_missing_translations as
select
	i_cl.lang,
	i_k.orig,
	_(i_k.orig, 'en')
		as english
from
	(select distinct on (lang) lang from i18n.curr_lang) as i_cl,
	i18n.keys i_k
where
	i_k.orig not in (
		select i_t.orig from i18n.translations i_t where i_t.lang = i_cl.lang
	)
;

comment on view i18n.v_missing_translations is
	'lists per language which strings are lacking a translation';

-- --------------------------------------------------------------
GRANT SELECT on
	i18n.v_missing_translations
TO group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-i18n-v_missing_translations.sql', '22.0');
