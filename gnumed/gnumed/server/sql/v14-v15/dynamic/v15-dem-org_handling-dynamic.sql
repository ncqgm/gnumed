-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
-- dem.org
select gm.add_table_for_notifies('dem'::name, 'org'::name);
select audit.add_table_for_audit('dem'::name, 'org'::name);


comment on table dem.org is
'Organisations at a conceptual level.';


-- .description
comment on column dem.org.description is
'High-level, conceptual description (= name) of organisation, such as "University of Manchester".';

alter table dem.org
	add constraint org_sane_description check (
		gm.is_null_or_blank_string(description) is false
	)
;


-- .fk_category
-- for now, leave this nullable ;-)
alter table dem.org
	add foreign key (fk_category)
		references dem.org_category(pk)
		on update cascade
		on delete restrict
;

-- --------------------------------------------------------------
-- dem.org_branch
select gm.add_table_for_notifies('dem'::name, 'org_branch'::name);
select audit.add_table_for_audit('dem'::name, 'org_branch'::name);


comment on table dem.org_branch is
'Actual branches/departments/offices/... of organisations.';


-- .description
comment on column dem.org_branch.description is
'Description (= name) of branch of organisation, such as "Elms Street office of Jim Busser Praxis".';

alter table dem.org_branch
	add constraint org_branch_sane_description check (
		gm.is_null_or_blank_string(description) is false
	)
;


-- .fk_org
alter table dem.org_branch
	alter column fk_org
		set not null;

alter table dem.org_branch
	add foreign key (fk_org)
		references dem.org(pk)
		on update cascade
		on delete restrict
;


-- .fk_address
alter table dem.org_branch
	alter column fk_address
		set not null;

alter table dem.org_branch
	add foreign key (fk_address)
		references dem.address(id)
		on update cascade
		on delete restrict
;


-- .fk_category
-- for now, leave this nullable ;-)
alter table dem.org_branch
	add foreign key (fk_category)
		references dem.org_category(pk)
		on update cascade
		on delete restrict
;

-- --------------------------------------------------------------
-- permissions
grant select, insert, update, delete on
	dem.org
	, dem.org_branch
	, dem.org_category
to group "gm-doctors";

-- --------------------------------------------------------------
alter table dem.lnk_org2comm
	add foreign key (fk_org)
		references dem.org(pk)
		on update cascade
		on delete restrict
;


alter table dem.lnk_org2comm
	alter column fk_type
		set not null
;


alter table dem.lnk_org2comm
	add constraint lnk_org2comm_sane_url check (
		gm.is_null_or_blank_string(url) is false
	)
;

-- --------------------------------------------------------------
alter table dem.lnk_org2ext_id
	add foreign key (fk_org)
		references dem.org(pk)
		on update cascade
		on delete restrict
;

-- --------------------------------------------------------------
-- remember to handle dependant objects possibly dropped by CASCADE
--\unset ON_ERROR_STOP
--drop forgot_to_edit_drops cascade;
--\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: zzz-template.sql,v $', '$Revision: 1.10 $');

-- ==============================================================
