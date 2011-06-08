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
		references ref.tag_image(pk)
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
-- table constraints
\unset ON_ERROR_STOP
alter table dem.identity_tag drop constraint dem_identity_tag_uniq_tag cascade;
\set ON_ERROR_STOP 1

alter table dem.identity_tag
	add constraint dem_identity_tag_uniq_tag
		unique(fk_identity, fk_tag)
;

-- --------------------------------------------------------------
-- --------------------------------------------------------------
-- test data
delete from dem.identity_tag where
	fk_identity = (select pk_identity from dem.v_basic_person where lastnames = 'Kirk' and firstnames = 'James Tiberius')
		and
	fk_tag = (select pk from ref.tag_image where description = 'Occupation: astronaut')
;

\unset ON_ERROR_STOP
insert into dem.identity_tag (
	fk_identity,
	fk_tag,
	comment
) values (
	(select pk_identity from dem.v_basic_person where lastnames = 'Kirk' and firstnames = 'James Tiberius'),
	(select pk from ref.tag_image where description = 'Occupation: astronaut'),
	'communicate via intercom only'
);
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view dem.v_identity_tags cascade;
\set ON_ERROR_STOP 1

create view dem.v_identity_tags as

select
	dit.fk_identity
		as pk_identity,
	rti.description
		as description,
	_(rti.description)
		as l10n_description,
	dit.comment
		as comment,
	rti.filename
		as filename,
	octet_length(COALESCE(rti.image, ''::bytea))
		as image_size,
	dit.pk
		as pk_identity_tag,
	rti.pk
		as pk_tag_image,
	dit.xmin
		as xmin_identity_tag
from
	dem.identity_tag dit
		left join ref.tag_image rti on (dit.fk_tag = rti.pk)
;

grant select on
	dem.v_identity_tags
to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-dem-identity_tag-dynamic.sql', 'Revision: 1.0');
