-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v9-ref-atc-dynamic.sql,v 1.2 2008-03-05 22:31:44 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
delete from audit.audited_tables where schema = 'public' and table_name = 'atc_group';

grant select on
	ref.atc_group,
	ref.atc_group_pk_seq
to group "gm-doctors";


delete from audit.audited_tables where schema = 'public' and table_name = 'atc_substance';

grant select on
	ref.atc_substance,
	ref.atc_substance_pk_seq
to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v9-ref-atc-dynamic.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: v9-ref-atc-dynamic.sql,v $
-- Revision 1.2  2008-03-05 22:31:44  ncq
-- - factor out data_source
--
-- Revision 1.1  2008/01/27 21:06:30  ncq
-- - add new
--
--