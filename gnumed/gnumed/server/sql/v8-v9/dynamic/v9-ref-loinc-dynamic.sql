-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v9-ref-loinc-dynamic.sql,v 1.1 2008-03-05 22:35:13 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
grant select, insert, update, delete on
	ref.loinc,
	ref.loinc_pk_seq
to group "gm-doctors";


comment on table ref.loinc is
'Holds LOINC codes old and new. Refer to the LOINC
 documentation for complete column meanings';
comment on column ref.loinc.fk_data_source is
'points to a particular data source which in turn holds the version';

-- format on .code: nnnnn-n
--alter table ref.loinc add check ...;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v9-ref-loinc-dynamic.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v9-ref-loinc-dynamic.sql,v $
-- Revision 1.1  2008-03-05 22:35:13  ncq
-- - added
--
--