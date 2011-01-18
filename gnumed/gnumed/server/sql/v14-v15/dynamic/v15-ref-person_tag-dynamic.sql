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
select gm.register_notifying_table('ref', 'person_tag');
select audit.register_table_for_auditing('ref', 'person_tag');


comment on table ref.person_tag is 'Text/image tags that can be applied to a person for characterization.';


grant select, insert, update, delete on
	ref.person_tag
to group "gm-doctors";

grant select, select, update on
	ref.person_tag_pk_seq
to group "gm-doctors";

-- --------------------------------------------------------------
-- .description
comment on column ref.person_tag.description is 'A textual description of the meaning of the tag.';

\unset ON_ERROR_STOP
alter table ref.person_tag drop constraint ref_person_tag_sane_desc cascade;
alter table ref.person_tag drop constraint ref_person_tag_uniq_desc cascade;
\set ON_ERROR_STOP 1

alter table ref.person_tag
	add constraint ref_person_tag_sane_desc check (
		gm.is_null_or_blank_string(description) is False
	);

alter table ref.person_tag
	add constraint ref_person_tag_uniq_desc
		unique(description);

-- --------------------------------------------------------------
-- .short_description
comment on column ref.person_tag.short_description is 'A (preferably single-word) short description of the meaning of the tag.';

\unset ON_ERROR_STOP
alter table ref.person_tag drop constraint ref_person_tag_sane_short_desc cascade;
alter table ref.person_tag drop constraint ref_person_tag_uniq_short_desc cascade;
\set ON_ERROR_STOP 1

alter table ref.person_tag
	add constraint ref_person_tag_sane_short_desc check (
		gm.is_null_or_blank_string(short_description) is False
	);

alter table ref.person_tag
	add constraint ref_person_tag_uniq_short_desc
		unique(short_description);

-- --------------------------------------------------------------
-- .image
comment on column ref.person_tag.image is 'An image showing the meaning of the tag.';

alter table ref.person_tag
	alter column image
		set not null;

-- --------------------------------------------------------------
-- test data
insert into ref.person_tag (
	description,
	short_description,
	image
) values (
	'Occupation: astronaut',
	'Astronaut',
	'to be imported'
);

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view ref.v_person_tags_no_data cascade;
\set ON_ERROR_STOP 1

create view ref.v_person_tags_no_data as

select
	pk
		as pk_person_tag,
	description,
	short_description,
	xmin
from
	ref.person_tag
;

grant select on
	ref.v_person_tags_no_data
to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-ref-person_tag-dynamic.sql', 'Revision: 1.1');
