-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v9-ref-atc-dynamic.sql,v 1.1 2008-01-27 21:06:30 ncq Exp $
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
	'shorthand for referrring to this reference entry';
comment on column ref.data_source.name_long is
	'long, complete (, ?official) name for this reference entry';
comment on column ref.data_source.version is
	'the exact and non-ambigous version for this entry';
comment on column ref.data_source.description is
	'optional arbitrary description';
comment on column ref.data_source.source is
	'non-ambigous description of source; with this info in hand
	 it must be possible to locate a copy of the external reference';



delete from audit.audited_tables where schema = 'public' and table_name = 'atc_group';

grant select on
	ref.atc_group,
	ref.atc_group_pk_seq
to group "gm-doctors";


delete from audit.audited_tables where schema = 'public' and table_name = 'atc_substance';

grant select on
	ref.atc_group,
	ref.atc_group_pk_seq
to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v9-ref-atc-dynamic.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v9-ref-atc-dynamic.sql,v $
-- Revision 1.1  2008-01-27 21:06:30  ncq
-- - add new
--
--