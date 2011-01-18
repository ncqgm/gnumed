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
comment on table dem.identity_tag is 'tags attached to this identity';


select gm.register_notifying_table('dem', 'identity_tag');
select audit.register_table_for_auditing('dem', 'identity_tag');


grant select, insert, update, delete on
	dem.identity_tag
to group "gm-doctors";

grant select, select, update on
	dem.identity_tag_pk_seq
to group "gm-doctors";

-- --------------------------------------------------------------
-- .fk_identity
alter table dem.identity_tag
	alter column fk_identity
		set not null;

alter table dem.identity_tag
	add foreign key (fk_identity)
		references dem.identity(pk)
		on update cascade
		on delete restrict;

-- --------------------------------------------------------------
-- .fk_tag
alter table dem.identity_tag
	alter column fk_tag
		set not null;

alter table dem.identity_tag
	add foreign key (fk_tag)
		references ref.person_tag(pk)
		on update cascade
		on delete restrict;

-- --------------------------------------------------------------
-- .comment
\unset ON_ERROR_STOP
alter table dem.identity_tag drop constraint dem_identity_tag_sane_comment cascade;
\set ON_ERROR_STOP 1

alter table dem.identity_tag
	add constraint dem_identity_tag_sane_comment check (
		gm.is_null_or_non_empty_string(comment) is True
	)
;

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view dem.v_identity_tags cascade;
\set ON_ERROR_STOP 1

create view dem.v_identity_tags as

select
	dit.fk_identity
		as pk_identity,
	rpt.description
		as description,
	rpt.short_description
		as short_description,
	dit.comment
		as comment,

	dit.pk
		as pk_identity_tag,
	rpt.pk
		as pk_person_tag,

	dit.xmin
		as xmin_identity_tag
from
	dem.identity_tag dit
		left join ref.person_tag rpt on (dit.fk_tag = rpt.pk)
;

grant select on
	dem.v_identity_tags
to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-dem-identity_tag-dynamic.sql', 'Revision: 1.0');
