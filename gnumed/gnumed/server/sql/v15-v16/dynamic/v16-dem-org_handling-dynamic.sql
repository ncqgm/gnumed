-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
-- dem.org.fk_data_source
comment on column dem.org.fk_data_source is 'Source of the organization data.';

\unset ON_ERROR_STOP
alter table dem.org drop constraint org_fk_data_source_fkey cascade;
\set ON_ERROR_STOP 1

alter table dem.org
	add foreign key (fk_data_source)
		references ref.data_source(pk)
		on update cascade
		on delete restrict
;

alter table dem.org
	alter column fk_data_source
		set default null;

-- --------------------------------------------------------------
-- dem.lnk_org_unit2comm

\unset ON_ERROR_STOP
alter table dem.lnk_org_unit2comm drop constraint lnk_org_unit2comm_fk_org_unit_fkey cascade;
alter table dem.lnk_org_unit2comm drop constraint lnk_org_unit2comm_fk_org_unit_fkey1 cascade;
\set ON_ERROR_STOP 1

-- .fk_org_unit
alter table dem.lnk_org_unit2comm
	add foreign key (fk_org_unit)
		references dem.org_unit(pk)
		on update cascade
		on delete restrict
;

-- --------------------------------------------------------------
-- dem.lnk_org_unit2ext_id

\unset ON_ERROR_STOP
alter table dem.lnk_org_unit2comm drop constraint lnk_org_unit2ext_id_fk_org_unit_fkey cascade;
alter table dem.lnk_org_unit2comm drop constraint lnk_org_unit2ext_id_fk_org_unit_fkey1 cascade;
\set ON_ERROR_STOP 1

-- .fk_org_unit
alter table dem.lnk_org_unit2ext_id
	add foreign key (fk_org_unit)
		references dem.org_unit(pk)
		on update cascade
		on delete restrict
;

-- --------------------------------------------------------------
insert into dem.org_category (description) values ('Government Agency');
select i18n.upd_tx('de', 'Government Agency', 'Regierungsabteilung');

update dem.org set
	fk_category = (select pk from dem.org_category where description = 'Government Agency')
where
	fk_category = (select pk from dem.org_category where description = 'Government')
;

update dem.org_unit set
	fk_category = (select pk from dem.org_category where description = 'Government Agency')
where
	fk_category = (select pk from dem.org_category where description = 'Government')
;


\unset ON_ERROR_STOP
alter table dem.org_category drop constraint org_category_description_key cascade;
drop index idx_dem_org_category_description cascade;
\set ON_ERROR_STOP 1

create unique index idx_dem_org_category_description on dem.org_category(lower(description));

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-dem-org_handling-dynamic.sql', '16.0');
