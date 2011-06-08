-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- $Id: v12-ref-substance_in_drug-static.sql,v 1.1 2009-11-24 21:12:16 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
create table ref.substance_in_brand (
	pk serial primary key,
	fk_brand integer
		not null
		references ref.branded_drug(pk)
		on update cascade
		on delete cascade,
	description text,
	atc_code text
) inherits (audit.audit_fields);

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v12-ref-substance_in_drug-static.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v12-ref-substance_in_drug-static.sql,v $
-- Revision 1.1  2009-11-24 21:12:16  ncq
-- - new drug tables
--
--