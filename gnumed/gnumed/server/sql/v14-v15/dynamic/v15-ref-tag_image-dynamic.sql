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
select gm.register_notifying_table('ref', 'tag_image');
select audit.register_table_for_auditing('ref', 'tag_image');


comment on table ref.tag_image is 'Text+image tags that can be applied to a person for characterization.';


grant select, insert, update, delete on
	ref.tag_image
to group "gm-doctors";

grant select, select, update on
	ref.tag_image_pk_seq
to group "gm-doctors";

-- --------------------------------------------------------------
-- .description
comment on column ref.tag_image.description is 'A textual description of the meaning of the tag. Keep this reasonably short.';

\unset ON_ERROR_STOP
alter table ref.tag_image drop constraint ref_tag_image_sane_desc cascade;
alter table ref.tag_image drop constraint ref_tag_image_uniq_desc cascade;
\set ON_ERROR_STOP 1

alter table ref.tag_image
	add constraint ref_tag_image_sane_desc check (
		gm.is_null_or_blank_string(description) is False
	);

alter table ref.tag_image
	add constraint ref_tag_image_uniq_desc
		unique(description);

-- --------------------------------------------------------------
-- .filename
comment on column ref.tag_image.filename is 'An example filename, mainly for preserving the file suffix. Set during import, suffix used during export.';

\unset ON_ERROR_STOP
alter table ref.tag_image drop constraint ref_tag_image_sane_filename cascade;
\set ON_ERROR_STOP 1

alter table ref.tag_image
	add constraint ref_tag_image_sane_filename check (
		gm.is_null_or_non_empty_string(filename) is True
	);

-- --------------------------------------------------------------
-- .image
comment on column ref.tag_image.image is 'An image showing the meaning of the tag.';

alter table ref.tag_image
	alter column image
		set not null;

-- --------------------------------------------------------------
-- test data
insert into ref.tag_image (
	description,
	filename,
	image
) values (
	'Occupation: astronaut',
	'astronaut.png',
	''
);

insert into ref.tag_image (
	description,
	filename,
	image
) values (
	'smokes',
	'Anonymous_aiga_smoking.png',
	''
);

insert into ref.tag_image (
	description,
	filename,
	image
) values (
	'often late',
	'CoD_fsfe_Pocket_watch_icon.png',
	''
);

insert into ref.tag_image (
	description,
	filename,
	image
) values (
	'Extra care !',
	'eastshores_Warning_Notification.png',
	''
);

insert into ref.tag_image (
	description,
	filename,
	image
) values (
	'mobility impairment',
	'schoolfreeware_WheelChair_Sign.png',
	''
);

insert into ref.tag_image (
	description,
	filename,
	image
) values (
	'minor depression',
	'weather-few-clouds.png',
	''
);

insert into ref.tag_image (
	description,
	filename,
	image
) values (
	'major depression',
	'weather-showers-scattered.png',
	''
);

insert into ref.tag_image (
	description,
	filename,
	image
) values (
	'choleric',
	'weather-storm.png',
	''
);

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view ref.v_tag_images_no_data cascade;
\set ON_ERROR_STOP 1

create view ref.v_tag_images_no_data as

select
	rti.pk
		as pk_tag_image,
	rti.description,
	_(rti.description)
		as l10n_description,
	rti.filename,
	octet_length(COALESCE(rti.image, ''::bytea))
		as size,
	exists (select 1 from dem.identity_tag dit where dit.fk_tag = rti.pk limit 1)
		as is_in_use,
	rti.xmin
		as xmin_tag_image
from
	ref.tag_image rti
;

grant select on
	ref.v_tag_images_no_data
to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-ref-tag_image-dynamic.sql', 'Revision: 1.1');
