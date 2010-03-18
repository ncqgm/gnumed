-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- example form template
\unset ON_ERROR_STOP
insert into ref.form_types (name) values (i18n.i18n('visual progress note'));
\set ON_ERROR_STOP 1

select i18n.upd_tx('de_DE', 'visual progress note', 'Bildnotiz');

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v12-ref-paperwork_templates.sql,v $', '$Revision: 1.3 $');
