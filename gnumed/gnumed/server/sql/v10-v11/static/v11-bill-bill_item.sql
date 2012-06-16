-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v11-bill-bill_item.sql,v 1.3 2009-04-03 09:58:12 ncq Exp $
-- $Revision: 1.3 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create table bill.bill_item (
	pk serial primary key,
	fk_provider integer
		references dem.staff(pk)
			on update cascade
			on delete restrict,
	fk_encounter integer
		references clin.encounter(pk)
			on update cascade
			on delete restrict,
	date_to_bill date,
	code text,
	system text,
	description text,
	receiver text,
	amount_to_bill numeric,
	currency text,
	locale text,
	status text
) inherits (audit.audit_fields);

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-bill-bill_item.sql,v $', '$Revision: 1.3 $');

-- ==============================================================
-- $Log: v11-bill-bill_item.sql,v $
-- Revision 1.3  2009-04-03 09:58:12  ncq
-- - cleanup
--
-- Revision 1.2  2009/03/16 15:13:38  ncq
-- - columns adjusted
--
-- Revision 1.1  2009/03/10 14:29:05  ncq
-- - new
--
--