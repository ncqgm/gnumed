-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- $Id: v12-clin-substance_intake-dynamic.sql,v 1.3 2009-10-28 16:45:32 ncq Exp $
-- $Revision: 1.3 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
-- drop foreign key on brand
\unset ON_ERROR_STOP
alter table clin.substance_intake drop constraint substance_intake_fk_brand_fkey cascade;
\set ON_ERROR_STOP 1

alter table clin.substance_intake
	alter column fk_brand
		drop not null;

-- --------------------------------------------------------------
-- drop old foreign key on consumed substance
\unset ON_ERROR_STOP
alter table clin.substance_intake drop constraint substance_intake_fk_substance_fkey cascade;
\set ON_ERROR_STOP 1

-- re-adjust foreign key data
update clin.substance_intake csi set
	fk_substance = (
		select ccs.pk
		from clin.consumed_substance ccs
		where
			ccs.description = (
				select cas.description
				from clin.active_substance cas
				where cas.pk = csi.fk_substance
			)
	);

-- re-add new foreign key
alter table clin.substance_intake
	add foreign key (fk_substance)
		references clin.consumed_substance(pk)
			on update cascade
			on delete restrict;

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_pat_substance_intake cascade;
\set ON_ERROR_STOP 1

create view clin.v_pat_substance_intake as
select
	csi.pk
		as pk_substance_intake,
	(select fk_patient from clin.encounter where pk = csi.fk_encounter)
		as pk_patient,
	csi.soap_cat,
	csb.description
		as brand,
	csi.preparation,
	csb.atc_code
		as atc_brand,
	csb.external_code
		as external_code_brand,

	ccs.description
		as substance,
	csi.strength,
	ccs.atc_code
		as atc_substance,

	csi.clin_when
		as started,
	csi.intake_is_approved_of,
	csi.schedule,
	csi.duration,
	csi.aim,
	csi.narrative
		as notes,
	csb.is_fake
		as fake_brand,

	csi.fk_brand
		as pk_brand,
	ccs.pk
		as pk_substance,
	csi.fk_encounter
		as pk_encounter,
	csi.fk_episode
		as pk_episode,
	csi.modified_when,
	csi.modified_by,
	csi.xmin
		as xmin_substance_intake
from
	clin.substance_intake csi
		left join clin.substance_brand csb on (csi.fk_brand = csb.pk)
			left join clin.consumed_substance ccs on (csi.fk_substance = ccs.pk)
;

grant select on clin.v_pat_substance_intake to group "gm-doctors";

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_pat_substance_intake_journal cascade;
\set ON_ERROR_STOP 1

create view clin.v_pat_substance_intake_journal as
select
	(select fk_patient from clin.encounter where pk = csi.fk_encounter)
		as pk_patient,
	csi.modified_when
		as modified_when,
	csi.clin_when
		as clin_when,
	coalesce (
		(select short_alias from dem.staff where db_user = csi.modified_by),
		'<' || csi.modified_by || '>'
	)
		as modified_by,
	csi.soap_cat
		as soap_cat,

	_('substance intake') || ' '
		|| (case
				when intake_is_approved_of is true then _('(approved of)')
				when intake_is_approved_of is false then _('(not approved of)')
				else _('[of unknown approval]')
			end)
		|| E':\n'

		|| ' ' || ccs.description								-- Metoprolol
		|| coalesce(' [' || ccs.atc_code || '] ', ' ')			-- [ATC]
		|| csi.strength || ' '									-- 100mg
		|| csi.preparation										-- tab
		|| coalesce(' ' || csi.schedule, '')					-- 1-0-0
		|| ', ' || to_char(csi.clin_when, 'YYYY-MM-DD')			-- 2009-03-01
		|| coalesce(' -> ' || csi.duration, '')					-- -> 6 months
		|| E'\n'

		|| coalesce (
			nullif (
				(coalesce(' ' || csi.aim, '')						-- lower RR
				 || coalesce(' (' || csi.narrative || ')', '')		-- report if unwell
				 || E'\n'
				),
				E'\n'
			),
			''
		)

		|| coalesce (' "' || csb.description || ' ' || csb.preparation || '"'		-- "MetoPharm tablets"
			|| coalesce(' [' || csb.atc_code || ']', '')							-- [ATC code]
			|| coalesce(' (' || csb.external_code || ')', ''),						-- (external code)
			'')

	as narrative,

	csi.fk_encounter
		as pk_encounter,
	csi.fk_episode
		as pk_episode,
	(select fk_health_issue from clin.episode where pk = csi.fk_episode)
		as pk_health_issue,
	csi.pk
		as src_pk,
	'clin.substance_intake'::text
		as src_table,
	csi.row_version
		as row_version
from
	clin.substance_intake csi
		left join clin.substance_brand csb on (csi.fk_brand = csb.pk)
			left join clin.consumed_substance ccs on (csi.fk_substance = ccs.pk)
;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v12-clin-substance_intake-dynamic.sql,v $', '$Revision: 1.3 $');

-- ==============================================================
-- $Log: v12-clin-substance_intake-dynamic.sql,v $
-- Revision 1.3  2009-10-28 16:45:32  ncq
-- - slightly better comment
--
-- Revision 1.2  2009/10/27 11:03:37  ncq
-- - better comment
--
-- Revision 1.1  2009/10/21 08:54:32  ncq
-- - foreign key to consumed_substances
-- - rework views
--
--