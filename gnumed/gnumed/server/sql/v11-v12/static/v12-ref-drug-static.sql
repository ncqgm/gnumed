-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- $Id: v12-ref-drug-static.sql,v 1.1 2009-11-24 21:12:16 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
alter table clin.substance_brand
	set schema ref;



alter table ref.substance_brand
	rename to branded_drug;

alter table audit.log_substance_brand
	rename to log_branded_drug;


alter table ref.branded_drug
	add column fk_data_source
		integer
		references ref.data_source(pk)
		on update cascade
		on delete restrict;

alter table audit.log_branded_drug
	add column fk_data_source integer;


alter table ref.branded_drug
	add column external_code
		text;

alter table audit.log_branded_drug
	add column external_code text;

-- --------------------------------------------------------------
drop table clin.clin_medication cascade;
drop table audit.log_clin_medication cascade;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v12-ref-drug-static.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v12-ref-drug-static.sql,v $
-- Revision 1.1  2009-11-24 21:12:16  ncq
-- - new drug tables
--
--