-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

set check_function_bodies to on;

-- --------------------------------------------------------------
comment on table dem.praxis_branch is 'Defines one branch of a praxis (which itself is a dem.org)';


select gm.register_notifying_table('dem', 'praxis_branch');
select audit.register_table_for_auditing('dem', 'praxis_branch');


grant select on dem.praxis_branch to group "gm-public";
grant insert, update, delete on dem.praxis_branch to group "gm-doctors";

GRANT USAGE ON SEQUENCE
	dem.praxis_branch_pk_seq
to group "gm-public";

-- --------------------------------------------------------------
-- .fk_org_unit
alter table dem.praxis_branch
	alter column fk_org_unit
		set not null
;


\unset ON_ERROR_STOP
alter table dem.praxis_branch drop constraint dem_praxis_branch_uniq_fk_org_unit cascade;
\set ON_ERROR_STOP 1

alter table dem.praxis_branch
	add constraint dem_praxis_branch_uniq_fk_org_unit
		unique(fk_org_unit)
;


\unset ON_ERROR_STOP
drop function dem.trf_prevent_multiple_praxi() cascade;
\set ON_ERROR_STOP 1

create or replace function dem.trf_prevent_multiple_praxi()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_branch_count integer;
	_pk_org_existing integer;
	_pk_org_prospective integer;
	_msg text;
BEGIN
	select count(1) into _branch_count from dem.praxis_branch;

	if TG_OP = ''INSERT'' then
		-- first branch ever
		if _branch_count = 0 then
			return NEW;
		end if;
	end if;

	if TG_OP = ''UPDATE'' then
		-- only one branch (which is being updated)
		if _branch_count = 1 then
			return NEW;
		end if;
	end if;

	-- now we have either got an INSERT with at least
	-- one praxis_branch already existing or we are
	-- UPDATEing one of several existing branches

	SELECT fk_org INTO _pk_org_existing FROM dem.org_unit
	WHERE pk = (SELECT fk_org_unit FROM dem.praxis_branch LIMIT 1);

	SELECT fk_org INTO _pk_org_prospective
	FROM dem.org_unit WHERE pk = NEW.fk_org_unit;

	if _pk_org_prospective = _pk_org_existing then
		return NEW;
	end if;

	_msg := ''[dem.trf_prevent_multiple_praxi] ''
			|| TG_OP || '': ''
			|| ''Existing praxis branches (dem.praxis_branch.fk_org->dem.org_unit.pk->dem.org_unit.fk_org) belong to an org with dem.org.pk=''
			|| _pk_org_existing
			|| ''. Cannot link praxis branch (dem.praxis_branch.fk_org=dem.org_unit.pk=''
			|| NEW.fk_org_unit
			||'') to a different org (dem.org.pk=''
			|| _pk_org_prospective
			||''). There can only be one praxis (=dem.org) per database.'';
	raise exception unique_violation using message = _msg;
	return NULL;
END;';

comment on function dem.trf_prevent_multiple_praxi() is
	'Prevent praxis branches to be defined for more than one dem.org.';

create trigger tr_prevent_multiple_praxi
	before insert or update on dem.praxis_branch
	for each row execute procedure dem.trf_prevent_multiple_praxi();

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view dem.v_praxis_branches cascade;
\set ON_ERROR_STOP 1

create view dem.v_praxis_branches as

select
	d_pb.pk
		as pk_praxis_branch,
	d_vou.organization
		as praxis,
	d_vou.unit
		as branch,
	d_vou.organization_category,
	d_vou.l10n_organization_category,
	d_vou.unit_category,
	d_vou.l10n_unit_category,
	d_vou.pk_org,
	d_pb.fk_org_unit
		as pk_org_unit,
	d_vou.pk_category_org,
	d_vou.pk_category_unit,
	d_vou.pk_address,
	d_pb.xmin
		as xmin_praxis_branch,
	d_vou.xmin_org_unit
from
	dem.praxis_branch d_pb
		left join dem.v_org_units d_vou on (d_pb.fk_org_unit = d_vou.pk_org_unit)
;


comment on view dem.v_praxis_branches is 'Denormalized praxis branches with their praxis.';


grant select on
	dem.v_praxis_branches
to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-dem-praxis_branch-dynamic.sql', '19.0');
