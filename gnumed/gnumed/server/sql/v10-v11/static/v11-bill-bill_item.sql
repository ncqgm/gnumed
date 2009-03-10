-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v11-bill-bill_item.sql,v 1.1 2009-03-10 14:29:05 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create table bill_item (
	pk serial primary key,
	fk_provider integer
		references dem.provider(pk)
		on update cascade
		on delete restrict,
	fk_encounter_inserted integer
		references clin.encounter(pk)
		on update cascade
		on delete restrict,
	date_completed date
		not null
		default now(),
	fk_encounter_completed integer
		references clin.encounter(pk)
		on update cascade
		on delete restrict,
	description text,
	disposition text,
	amount_to_bill decimal,
	currency text,
	status text
) inherits (audit.audit_fields);

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-bill-bill_item.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v11-bill-bill_item.sql,v $
-- Revision 1.1  2009-03-10 14:29:05  ncq
-- - new
--
--