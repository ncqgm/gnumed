-- Project: GNUmed
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/update_db-v1_v2.sql,v $
-- $Revision: 1.1 $
-- license: GPL
-- author: Ian Haywood, Horst Herb, Karsten Hilbert

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- == service default ================================================

\unset ON_ERROR_STOP
-- reload patient data after search even if same patient
insert into cfg_template
	(name, type, description)
values (
	'patient_search.always_reload_new_patient',
	'numeric',
	'1/0, meaning true/false,
	 if true: reload patient data after search even if the new patient is the same as the previous one,
	 if false: do not reload data if new patient matches previous one'
);

insert into cfg_item
	(id_template, owner, workplace)
values (
	currval('cfg_template_id_seq'),
	'xxxDEFAULTxxx',
	'xxxDEFAULTxxx'
);

-- default to false
insert into cfg_numeric
	(id_item, value)
values (
	currval('cfg_item_id_seq'),
	0
);
\set ON_ERROR_STOP 1

-- ===================================================================
\unset ON_ERROR_STOP

-- do simple schema revision tracking
delete from gm_schema_revision where filename='$RCSfile: update_db-v1_v2.sql,v $';
INSERT INTO gm_schema_revision (filename, version, is_core) VALUES('$RCSfile: update_db-v1_v2.sql,v $', '$Revision: 1.1 $', True);

-- =============================================
-- $Log: update_db-v1_v2.sql,v $
-- Revision 1.1  2005-09-13 11:54:47  ncq
-- - initial update of v1 -> v2: config option
--
-- 
