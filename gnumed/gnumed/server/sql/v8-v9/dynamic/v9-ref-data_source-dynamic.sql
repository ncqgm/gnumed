-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v9-ref-data_source-dynamic.sql,v 1.1 2008-03-05 22:35:14 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
delete from audit.audited_tables where schema = 'public' and table_name = 'ref_source';

grant select, insert, update, delete on
	ref.data_source,
	ref.data_source_pk_seq
to group "gm-doctors";

select audit.add_table_for_audit('ref', 'data_source');

comment on table ref.data_source is
	'lists the available coding systems, classifications, ontologies and term lists';
comment on column ref.data_source.name_short is
	'shorthand for referring to this reference entry';
comment on column ref.data_source.name_long is
	'long, complete (, ?official) name for this reference entry';
comment on column ref.data_source.version is
	'the exact and non-ambigous version for this entry';
comment on column ref.data_source.description is
	'optional arbitrary description, should include external license';
comment on column ref.data_source.source is
'non-ambigous description of source; with this info in hand it
 must be possible to locate a copy of the external data set';

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v9-ref-data_source-dynamic.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v9-ref-data_source-dynamic.sql,v $
-- Revision 1.1  2008-03-05 22:35:14  ncq
-- - added
--
--
