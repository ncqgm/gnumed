-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
set default_transaction_read_only to off;

-- --------------------------------------------------------------
-- .brandname
comment on column ref.vaccine.brandname is 'Vaccine brand. If NULL this is a generic vaccine entry.';

alter table ref.vaccine
	alter column brandname
		drop not null;

drop index if exists ref.idx_uniq__ref__vaccine__brandname cascade;
create unique index idx_uniq__ref__vaccine__brandname on ref.vaccine(brandname);

-- we also need a unique constraint ((brandname=NULL), list-of-indications) meaning: single generic vaccines only

-- --------------------------------------------------------------
-- .atc
comment on column ref.vaccine.atc is 'ATC for the vaccine, if any.';

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-ref-vaccine-dynamic.sql', '23.0');
