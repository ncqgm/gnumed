-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
comment on table ref.icpc_chapter is
	'The chapters of the ICPC.';



grant select on
	ref.icpc_chapter
to group "gm-doctors";



-- .chapter
\unset ON_ERROR_STOP
alter table ref.icpc_chapter drop constraint ref_icpc_unique_chapter cascade;
\set ON_ERROR_STOP 1

alter table ref.icpc_chapter
	add constraint ref_icpc_unique_chapter
		unique(chapter);

alter table ref.icpc_chapter
	alter column chapter
		set not null;



-- .description
\unset ON_ERROR_STOP
alter table ref.icpc_chapter drop constraint ref_icpc_chapter_unique_desc cascade;
alter table ref.icpc_chapter drop constraint ref_icpc_chapter_sane_desc cascade;
\set ON_ERROR_STOP 1

alter table ref.icpc_chapter
	add constraint ref_icpc_chapter_unique_desc
		unique(description);

alter table ref.icpc_chapter
	add constraint ref_icpc_chapter_sane_desc check (
		(gm.is_null_or_blank_string(description) is false)
	);



-- data
delete from ref.icpc_chapter;

insert into ref.icpc_chapter(chapter, description) values ('A', i18n.i18n('General and Unspecified'));
insert into ref.icpc_chapter(chapter, description) values ('B', i18n.i18n('Blood, Blood forming organs, Immune mechanism'));
insert into ref.icpc_chapter(chapter, description) values ('D', i18n.i18n('Digestive'));
insert into ref.icpc_chapter(chapter, description) values ('F', i18n.i18n('Eye ("Focal")'));
insert into ref.icpc_chapter(chapter, description) values ('H', i18n.i18n('Ear ("Hearing")'));
insert into ref.icpc_chapter(chapter, description) values ('K', i18n.i18n('Cardivascular'));
insert into ref.icpc_chapter(chapter, description) values ('L', i18n.i18n('Musculoskeletal ("Locomotion")'));
insert into ref.icpc_chapter(chapter, description) values ('N', i18n.i18n('Neurological'));
insert into ref.icpc_chapter(chapter, description) values ('P', i18n.i18n('Psychological'));
insert into ref.icpc_chapter(chapter, description) values ('R', i18n.i18n('Respiratory'));
insert into ref.icpc_chapter(chapter, description) values ('S', i18n.i18n('Skin'));
insert into ref.icpc_chapter(chapter, description) values ('T', i18n.i18n('Endocrine/Metabolic and Nutritional ("Thyroid")'));
insert into ref.icpc_chapter(chapter, description) values ('U', i18n.i18n('Urological'));
insert into ref.icpc_chapter(chapter, description) values ('W', i18n.i18n('Pregnancy, Childbearing, Family planning ("Women")'));
insert into ref.icpc_chapter(chapter, description) values ('X', i18n.i18n('Female genital ("X-chromosome")'));
insert into ref.icpc_chapter(chapter, description) values ('Y', i18n.i18n('Male genital ("Y-chromosome")'));
insert into ref.icpc_chapter(chapter, description) values ('Z', i18n.i18n('Social problems'));

-- --------------------------------------------------------------
comment on table ref.icpc_component is
	'The Components of the ICPC chapters.';



grant select on
	ref.icpc_component
to group "gm-doctors";



-- .component
\unset ON_ERROR_STOP
alter table ref.icpc_component drop constraint ref_icpc_unique_component cascade;
\set ON_ERROR_STOP 1

alter table ref.icpc_component
	add constraint ref_icpc_unique_component
		unique(component);

alter table ref.icpc_component
	alter column component
		set not null;



-- .description
\unset ON_ERROR_STOP
alter table ref.icpc_component drop constraint ref_icpc_component_unique_desc cascade;
alter table ref.icpc_component drop constraint ref_icpc_component_sane_desc cascade;
\set ON_ERROR_STOP 1

alter table ref.icpc_component
	add constraint ref_icpc_component_unique_desc
		unique(description);

alter table ref.icpc_component
	add constraint ref_icpc_component_sane_desc check (
		(gm.is_null_or_blank_string(description) is false)
	);



-- .typical_soap_cat
comment on column ref.icpc_component.typical_soap_cat is
	'An array of SOAP categories which codes from this component are typically used for.';

--\unset ON_ERROR_STOP
--alter table ref.icpc_component drop constraint ref_icpc_component_soap_cat_range cascade;
--\set ON_ERROR_STOP 1

--alter table ref.icpc_component
--	add constraint ref_icpc_component_soap_cat_range check (
--		((typical_soap_cat is NULL) or (lower(soap_cat) in ('s', 'o', 'a', 'p')))
--	);



-- data
delete from ref.icpc_component;

insert into ref.icpc_component(component, description, typical_soap_cat) values ('1', i18n.i18n('Symptoms, complaints'), ARRAY['s','a']);
insert into ref.icpc_component(component, description, typical_soap_cat) values ('2', i18n.i18n('Diagnostic screening, prevention'), ARRAY['o','p']);
insert into ref.icpc_component(component, description, typical_soap_cat) values ('3', i18n.i18n('Treatment, procedures, medication'), ARRAY['p']);
insert into ref.icpc_component(component, description, typical_soap_cat) values ('4', i18n.i18n('Test results'), ARRAY['o']);
insert into ref.icpc_component(component, description, typical_soap_cat) values ('5', i18n.i18n('Administrative'), ARRAY[NULL]);
insert into ref.icpc_component(component, description, typical_soap_cat) values ('6', i18n.i18n('Other (referral etc)'), ARRAY['s','a']);
insert into ref.icpc_component(component, description, typical_soap_cat) values ('7', i18n.i18n('Diagnosis, disease'), ARRAY['s','a']);

-- --------------------------------------------------------------
-- ref.icpc
comment on table ref.icpc is
	'This table holds ICPC2 codes along with local extensions.';



-- grants
grant select, insert, update, delete on
	ref.icpc
to group "gm-doctors";



-- indexe
\unset ON_ERROR_STOP
drop index idx_ref_icpc_code cascade;
drop index idx_ref_icpc_term cascade;
drop index idx_ref_icpc_chapter cascade;
drop index idx_ref_icpc_component cascade;
drop index idx_ref_icpc_pk_coding_system cascade;
\set ON_ERROR_STOP 1

create index idx_ref_icpc_code on ref.icpc(code);
create index idx_ref_icpc_term on ref.icpc(term);
create index idx_ref_icpc_chapter on ref.icpc(fk_chapter);
create index idx_ref_icpc_component on ref.icpc(fk_component);
create unique index idx_ref_icpc_pk_coding_system on ref.icpc(pk_coding_system);



-- .term
\unset ON_ERROR_STOP
alter table ref.icpc drop constraint ref_icpc_sane_term cascade;
\set ON_ERROR_STOP 1

alter table ref.icpc
	add constraint ref_icpc_sane_term check (
		(gm.is_null_or_blank_string(term) is false)
	);



-- .short_description
comment on column ref.icpc.short_description is 
	'A shorter term for this item';

--\unset ON_ERROR_STOP
--alter table ref.icpc drop constraint ref_icpc_sane_short_desc cascade;
--\set ON_ERROR_STOP 1

--alter table ref.icpc
--	add constraint ref_icpc_sane_short_desc check (
--		(gm.is_null_or_blank_string(short_description) is false)
--	);



-- .code_extension
comment on column ref.icpc.code_extension is 
	'An extension to the bare code as defined in, say, the Netherlands or Australia.';

\unset ON_ERROR_STOP
alter table ref.icpc drop constraint ref_icpc_sane_code_ext cascade;
alter table ref.icpc drop constraint ref_icpc_unique_code_ext cascade;
\set ON_ERROR_STOP 1

alter table ref.icpc
	add constraint ref_icpc_sane_code_ext check (
		(gm.is_null_or_non_empty_string(code_extension) is true)
	);

alter table ref.icpc
	add constraint ref_icpc_unique_code_ext
		unique(code, code_extension);

alter table ref.icpc
	alter column code_extension
		set default null;



-- .criteria
comment on column ref.icpc.criteria is 
	'Criteria to guide in selection of the appropriate code.';

\unset ON_ERROR_STOP
alter table ref.icpc drop constraint ref_icpc_sane_criteria cascade;
\set ON_ERROR_STOP 1

alter table ref.icpc
	add constraint ref_icpc_sane_criteria check (
		(gm.is_null_or_non_empty_string(criteria) is true)
	);

alter table ref.icpc
	alter column criteria
		set default null;



-- .inclusions
comment on column ref.icpc.inclusions is 
	'Items included under this code.';

\unset ON_ERROR_STOP
alter table ref.icpc drop constraint ref_icpc_sane_inclusions cascade;
\set ON_ERROR_STOP 1

alter table ref.icpc
	add constraint ref_icpc_sane_inclusions check (
		(gm.is_null_or_non_empty_string(inclusions) is true)
	);

alter table ref.icpc
	alter column inclusions
		set default null;



-- .exclusions
comment on column ref.icpc.exclusions is 
	'Items NOT included under this code because there is another code for them.';

\unset ON_ERROR_STOP
alter table ref.icpc drop constraint ref_icpc_sane_exclusions cascade;
\set ON_ERROR_STOP 1

alter table ref.icpc
	add constraint ref_icpc_sane_exclusions check (
		(exclusions is null)
			or
		(array_length(exclusions, 1) > 0)
	);

alter table ref.icpc
	alter column exclusions
		set default null;



-- .see_also
comment on column ref.icpc.see_also is 
	'See also under these items.';

\unset ON_ERROR_STOP
alter table ref.icpc drop constraint ref_icpc_sane_see_also cascade;
\set ON_ERROR_STOP 1

alter table ref.icpc
	add constraint ref_icpc_sane_see_also check (
		(see_also is null)
			or
		(array_length(see_also, 1) > 0)
	);

alter table ref.icpc
	alter column see_also
		set default null;



-- .icd10
comment on column ref.icpc.icd10 is
	'Array of corresponding ICD-10 codes.';

\unset ON_ERROR_STOP
alter table ref.icpc drop constraint ref_icpc_sane_icd10 cascade;
\set ON_ERROR_STOP 1

alter table ref.icpc
	add constraint ref_icpc_sane_icd10 check (
		(icd10 is null)
			or
		(array_length(icd10, 1) > 0)
	);

alter table ref.icpc
	alter column icd10
		set default null;



-- .fk_component
-- should drop foreign key first
alter table ref.icpc
	add foreign key (fk_component)
		references ref.icpc_component(component)
		on update cascade
		on delete restrict;

alter table ref.icpc
	alter column fk_component
		set not null;



-- .fk_chapter
-- should drop foreign key first
alter table ref.icpc
	add foreign key (fk_chapter)
		references ref.icpc_chapter(chapter)
		on update cascade
		on delete restrict;

alter table ref.icpc
	alter column fk_chapter
		set not null;

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view ref.v_icpc cascade;
\set ON_ERROR_STOP 1


create or replace view ref.v_icpc as

select
	ri.code,
	ri.code_extension,
	ri.code || coalesce(ri.code_extension, '')
		as extended_code,
	term
		as term,
--	_(term)
--		as l10n_term,
	short_description,
--	_(short_description)
--		as l10n_short_description,
	ri.fk_chapter
		as code_chapter,
	rich.description
		as chapter,
	_(rich.description)
		as l10n_chapter,
	ri.fk_component
		as code_component,
	rico.description
		as component,
	_(rico.description)
		as l10n_component,
	rico.typical_soap_cat,
	icd10,
	criteria,
	inclusions,
	exclusions,
	see_also,
	comment,
	rds.name_short,
	rds.name_long,
	rds.version,
	rds.lang,

	ri.pk
		as pk_icpc,
	ri.fk_data_source
		as pk_data_source
from
	ref.icpc as ri
		join ref.data_source rds on (ri.fk_data_source = rds.pk)
			join ref.icpc_chapter rich on (ri.fk_chapter = rich.chapter)
				join ref.icpc_component rico on (ri.fk_component = rico.component)
;


comment on view ref.v_icpc is
	'View over denormalized ICPC2 data.';


grant select on
	ref.v_icpc
to group "gm-doctors";

-- --------------------------------------------------------------
comment on table ref.code_thesaurus_root is
	'Synonyms for coded terms.';



grant select, insert, update, delete on
	ref.code_thesaurus_root
to group "gm-doctors";



-- .fk_code
alter table ref.code_thesaurus_root
	alter column fk_code
		set not null;



-- .synonym
\unset ON_ERROR_STOP
alter table ref.code_thesaurus_root drop constraint ref_code_thes_root_sane_synonym cascade;
\set ON_ERROR_STOP 1

alter table ref.code_thesaurus_root
	add constraint ref_code_thes_root_sane_synonym check (
		(gm.is_null_or_blank_string(synonym) is false)
	);

-- --------------------------------------------------------------
comment on table ref.icpc_thesaurus is
	'Synonyms for ICPC terms.';



grant select, insert, update, delete on
	ref.icpc_thesaurus
to group "gm-doctors";



-- .fk_code
alter table ref.icpc_thesaurus
	add foreign key (fk_code)
		references ref.icpc(pk_coding_system)
		on update cascade
		on delete restrict;

alter table ref.icpc_thesaurus
	alter column fk_code
		set not null;



-- .term
\unset ON_ERROR_STOP
alter table ref.icpc_thesaurus drop constraint ref_icpc_thes_sane_synonym cascade;
\set ON_ERROR_STOP 1

alter table ref.icpc_thesaurus
	add constraint ref_icpc_thes_sane_synonym check (
		(gm.is_null_or_blank_string(synonym) is false)
	);

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view ref.v_icpc_thesaurus cascade;
\set ON_ERROR_STOP 1


create or replace view ref.v_icpc_thesaurus as

select
	rit.pk
		as pk_icpc_thesaurus,
	ri.code,
	ri.term,
	rit.synonym,
	rit.pk_thesaurus
		as pk_thesaurus,
	rit.fk_code
		as pk_coding_system,
	ri.pk
		as pk_icpc
from
	ref.icpc_thesaurus rit
		join ref.icpc ri on (rit.fk_code = ri.pk_coding_system);



comment on view ref.v_icpc_thesaurus is
	'View over denormalized ICPC2 thesaurus.';


grant select on
	ref.v_icpc_thesaurus
to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-ref-icpc2-dynamic.sql', 'Revision: 1.1');
