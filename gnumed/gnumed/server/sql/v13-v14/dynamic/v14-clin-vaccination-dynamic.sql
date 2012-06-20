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
-- .narrative
comment on column clin.vaccination.narrative is
	'Used to record a comment on this vaccination.';

\unset ON_ERROR_STOP
alter table clin.vaccination drop constraint vaccination_sane_narrative cascade;
\set ON_ERROR_STOP 1

alter table clin.vaccination
	add constraint vaccination_sane_narrative check (
		gm.is_null_or_non_empty_string(narrative) is true
	);


-- .reaction
comment on column clin.vaccination.reaction is
	'Used to record reactions to this vaccination.';

\unset ON_ERROR_STOP
alter table clin.vaccination drop constraint vaccination_sane_reaction cascade;
\set ON_ERROR_STOP 1

alter table clin.vaccination
	add constraint vaccination_sane_reaction check (
		gm.is_null_or_non_empty_string(reaction) is true
	);


-- .site
comment on column clin.vaccination.site is
	'The site of injection used in this vaccination.';

\unset ON_ERROR_STOP
alter table clin.vaccination drop constraint vaccination_sane_site cascade;
\set ON_ERROR_STOP 1

alter table clin.vaccination
	add constraint vaccination_sane_site check (
		gm.is_null_or_non_empty_string(site) is true
	);

alter table clin.vaccination
	alter column site
		set default null;


-- .batch_no
comment on column clin.vaccination.batch_no is
	'The batch/lot number of the vaccine given.';

alter table clin.vaccination
	alter column batch_no
		drop default;



-- .fk_provider
comment on column clin.vaccination.fk_provider is
	'Who administered this vaccination.';

alter table clin.vaccination
	alter column fk_provider
		drop not null;

alter table clin.vaccination
	add foreign key (fk_provider)
		references dem.staff(pk)
		on update cascade
		on delete restrict;

-- --------------------------------------------------------------
-- list discussion showed that we do want to be able to document
-- non-conformant and clinically "wrong" vaccinations (such as
-- two tetanus boosters within 1 week) -- but we can still do
-- something about it ...


-- we need a suitable inbox message type
grant select on
	dem.v_inbox_item_type
to group "gm-public";

delete from dem.inbox_item_type where description = 'review vaccs';

insert into dem.inbox_item_type (
	fk_inbox_item_category,
	description,
	is_user
) values (
	(select pk from dem.inbox_item_category where description = 'clinical'),
	'review vaccs',
	False
);

select i18n.upd_tx('de_DE', 'review vaccs', 'Impfungen überprüfen');


-- add localized message
select i18n.upd_tx('de_DE', 'Two vaccinations with overlapping target conditions recorded within one week of each other !', 'Zwei Impfungen innerhalb einer Woche haben überlappende Indikationen !');


-- eventually add the trigger to warn on potential dupes
\unset ON_ERROR_STOP
drop function clin.trf_warn_on_duplicate_vaccinations() cascade;
\set ON_ERROR_STOP 1

create function clin.trf_warn_on_duplicate_vaccinations()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_NEW_pk_patient integer;

	_NEW_vaccination record;
	_NEW_vacc_label text;

	_prev_vacc_loop_record record;
	_prev_vaccination record;
	_prev_vacc_label text;

	_indication_collision integer;

	msg text;
	_pk_current_provider integer;
BEGIN
	-- find patient for NEW vaccination
	select fk_patient into _NEW_pk_patient from clin.encounter where pk = NEW.fk_encounter;

	-- load denormalized vaccination corresponding to NEW vaccination
	select * into _NEW_vaccination from clin.v_pat_vaccinations where pk_vaccination = NEW.pk;

	-- generate label for NEW vaccination
	_NEW_vacc_label := to_char(_NEW_vaccination.date_given, ''YYYY-MM-DD'')
		|| '' (#'' || _NEW_vaccination.pk_vaccination || ''): ''
		|| _NEW_vaccination.vaccine
		|| '' ('' || array_to_string(_NEW_vaccination.l10n_indications, '', '') || '')'';

	-- loop over ...
	for _prev_vacc_loop_record in
		-- ... vaccinations ...
		SELECT * FROM clin.vaccination cv
		WHERE
			-- ... of this patient ...
			cv.fk_encounter in (select pk from clin.encounter where fk_patient = _NEW_pk_patient)
				AND
			-- ... within 7 days of the vaccination date ...
			cv.clin_when BETWEEN (NEW.clin_when - ''7 days''::interval) AND (NEW.clin_when + ''7 days''::interval)
				AND
			-- ... not the vaccination we just INSERTed/UPDATEed
			cv.pk != NEW.pk
	loop

		select * into _indication_collision from ((
			select fk_indication from clin.lnk_vaccine2inds where fk_vaccine = NEW.fk_vaccine
		) INTERSECT (
			select fk_indication from clin.lnk_vaccine2inds where fk_vaccine = _prev_vacc_loop_record.fk_vaccine
		)) as colliding_indications;

		if FOUND then

			-- retrieve denormalized data corresponding to that previous vaccination
			select * into _prev_vaccination from clin.v_pat_vaccinations where pk_vaccination = _prev_vacc_loop_record.pk;

			-- generate label for that previous vaccination
			_prev_vacc_label := to_char(_prev_vaccination.date_given, ''YYYY-MM-DD'')
				|| '' (#'' || _prev_vaccination.pk_vaccination || ''): ''
				|| _prev_vaccination.vaccine
				|| '' ('' || array_to_string(_prev_vaccination.l10n_indications, '', '') || '')'';

			msg := _prev_vacc_label || E''\n'' || _NEW_vacc_label;

			select pk into _pk_current_provider from dem.staff where db_user = session_user;

			-- create inbox message for current user
			insert into dem.message_inbox (
				fk_staff,
				fk_inbox_item_type,
				comment,
				data,
				importance,
--				ufk_context,
				fk_patient
			) values (
				_pk_current_provider,
				(select pk_type from dem.v_inbox_item_type where type = ''review vaccs'' and category = ''clinical''),
				_(''Two vaccinations with overlapping target conditions recorded within one week of each other !''),
				msg,
				1,
--				NEW.pk,
				_NEW_pk_patient
			);

			-- create inbox message for vaccinating provider if known
			if NEW.fk_provider is not NULL then
				-- and not identical to session user
				if NEW.fk_provider != _pk_current_provider then
					insert into dem.message_inbox (
						fk_staff,
						fk_inbox_item_type,
						comment,
						data,
						importance,
--						ufk_context,
						fk_patient
					) values (
						NEW.fk_provider,
						(select pk_type from dem.v_inbox_item_type where type = ''review vaccs'' and category = ''clinical''),
						_(''Two vaccinations with overlapping target conditions recorded within one week of each other !''),
						msg,
						1,
--						NEW.pk,
						_NEW_pk_patient
					);
				end if;
			end if;

		end if;

	end loop;

	return NEW;
END;';


comment on function clin.trf_warn_on_duplicate_vaccinations() is
'Sends a notification to the inbox of both current_user and
 clin.vaccination.fk_provider (if not NULL) in case a new or updated
 vaccination falls within 1 week of another vaccination with (even
 partially) overlapping indications.';



create trigger tr_warn_on_duplicate_vaccinations
	after insert or update on clin.vaccination
		for each row execute procedure clin.trf_warn_on_duplicate_vaccinations()
;

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_pat_vaccinations cascade;
\set ON_ERROR_STOP 1

create view clin.v_pat_vaccinations as

select
	cenc.fk_patient
		as pk_patient,
	clv.pk
		as pk_vaccination,
	clv.clin_when
		as date_given,
	rbd.description
		as vaccine,
	(select array_agg(description)
	 from
		clin.lnk_vaccine2inds clvi
			join clin.vacc_indication cvi on (clvi.fk_indication = cvi.id)
	 where
		clvi.fk_vaccine = clv.fk_vaccine
	) as indications,
	(select array_agg(_(description))
	 from
		clin.lnk_vaccine2inds clvi
			join clin.vacc_indication cvi on (clvi.fk_indication = cvi.id)
	 where
		clvi.fk_vaccine = clv.fk_vaccine
	) as l10n_indications,
	clv.site
		as site,
	clv.batch_no
		as batch_no,
	clv.reaction
		as reaction,
	clv.narrative
		as comment,
	clv.soap_cat
		as soap_cat,

	clv.modified_when
		as modified_when,
	clv.modified_by
		as modified_by,
	clv.row_version
		as row_version,

	(select array_agg(clvi.fk_indication)
	 from
		clin.lnk_vaccine2inds clvi
			join clin.vacc_indication cvi on (clvi.fk_indication = cvi.id)
	 where
		clvi.fk_vaccine = clv.pk
	) as pk_indications,
	clv.fk_vaccine
		as pk_vaccine,
	clv.fk_provider
		as pk_provider,
	clv.fk_encounter
		as pk_encounter,
	clv.fk_episode
		as pk_episode,

	clv.xmin
		as xmin_vaccination
from
	clin.vaccination clv
		join clin.encounter cenc on (cenc.pk = clv.fk_encounter)
			join clin.vaccine on (clin.vaccine.pk = clv.fk_vaccine)
				join ref.branded_drug rbd on (clin.vaccine.fk_brand = rbd.pk)

;

comment on view clin.v_pat_vaccinations is
	'Lists vaccinations for patients';

grant select on clin.v_pat_vaccinations to group "gm-doctors";

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_pat_vaccs4indication cascade;
\set ON_ERROR_STOP 1

create view clin.v_pat_vaccs4indication as

select
	cenc.fk_patient
		as pk_patient,
	cv.pk
		as pk_vaccination,
	cv.clin_when
		as date_given,
	cvi4v.vaccine
		as vaccine,
	cvi4v.indication
		as indication,
	cvi4v.l10n_indication
		as l10n_indication,
	cv.site
		as site,
	cv.batch_no
		as batch_no,
	cv.reaction
		as reaction,
	cv.narrative
		as comment,
	cv.soap_cat
		as soap_cat,

	cv.modified_when
		as modified_when,
	cv.modified_by
		as modified_by,
	cv.row_version
		as row_version,

	cv.fk_vaccine
		as pk_vaccine,
	cvi4v.pk_indication
		as pk_indication,
	cv.fk_provider
		as pk_provider,
	cv.fk_encounter
		as pk_encounter,
	cv.fk_episode
		as pk_episode,

	cv.xmin
		as xmin_vaccination
from
	clin.vaccination cv
		join clin.encounter cenc on (cenc.pk = cv.fk_encounter)
			join clin.v_indications4vaccine cvi4v on (cvi4v.pk_vaccine = cv.fk_vaccine)

;

comment on view clin.v_pat_vaccs4indication is
	'Lists vaccinations per indication for patients';

grant select on clin.v_pat_vaccs4indication to group "gm-doctors";

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_pat_last_vacc4indication cascade;
\set ON_ERROR_STOP 1

create view clin.v_pat_last_vacc4indication as

select
	cvpv4i1.*,
	cpi.indication_count
from
	clin.v_pat_vaccs4indication cvpv4i1
		join (
			SELECT
				COUNT(1) AS indication_count,
				pk_patient,
				pk_indication
			FROM clin.v_pat_vaccs4indication
			GROUP BY
				pk_patient,
				pk_indication
		) AS cpi ON (cvpv4i1.pk_patient = cpi.pk_patient AND cvpv4i1.pk_indication = cpi.pk_indication)
where
	cvpv4i1.date_given = (
		select
			max(cvpv4i2.date_given)
		from
			clin.v_pat_vaccs4indication cvpv4i2
		where
			cvpv4i1.pk_patient = cvpv4i2.pk_patient
				and
			cvpv4i1.pk_indication = cvpv4i2.pk_indication
	)
;

comment on view clin.v_pat_last_vacc4indication is
	'Lists *latest* vaccinations with total count per indication.';

grant select on clin.v_pat_last_vacc4indication to group "gm-doctors";

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_pat_vaccinations_journal cascade;
\set ON_ERROR_STOP 1

create view clin.v_pat_vaccinations_journal as

select
	cenc.fk_patient
		as pk_patient,
	cv.modified_when
		as modified_when,
	cv.clin_when
		as clin_when,
	coalesce (
		(select short_alias from dem.staff where db_user = cv.modified_by),
		'<' || cv.modified_by || '>'
	)
		as modified_by,
	cv.soap_cat
		as soap_cat,

	(_('Vaccination') || ': '
		|| rbd.description || ' '
		|| '[' || cv.batch_no || ']'
		|| coalesce(' (' || cv.site || ')', '')
		|| coalesce(E'\n' || _('Reaction') || ': ' || cv.reaction, '')
		|| coalesce(E'\n' || _('Comment') || ': ' || cv.narrative, '')
		|| coalesce (
			(
				E'\n' || _('Indications') || ': '
				|| array_to_string ((
					select
						array_agg(_(description))
		 			from
						clin.lnk_vaccine2inds clvi
							join clin.vacc_indication cvi on (clvi.fk_indication = cvi.id)
					where
						clvi.fk_vaccine = cv.fk_vaccine
					),
					' / '
				)
			),
			''
		)
	)
		as narrative,

	cv.fk_encounter
		as pk_encounter,
	cv.fk_episode
		as pk_episode,
	(select fk_health_issue from clin.episode where pk = cv.fk_episode)
		as pk_health_issue,
	cv.pk
		as src_pk,
	'clin.vaccination'::text
		as src_table,
	cv.row_version
		as row_version
from
	clin.vaccination cv
		join clin.encounter cenc on (cenc.pk = cv.fk_encounter)
			join clin.vaccine on (clin.vaccine.pk = cv.fk_vaccine)
				join ref.branded_drug rbd on (clin.vaccine.fk_brand = rbd.pk)
;

select i18n.upd_tx('de_DE', 'Vaccination', 'Impfung');
select i18n.upd_tx('de_DE', 'Reaction', 'Reaktion');
select i18n.upd_tx('de_DE', 'Comment', 'Kommentar');
select i18n.upd_tx('de_DE', 'Indications', 'Indikationen');


comment on view clin.v_pat_vaccinations_journal is
	'Vaccination data denormalized for the EMR journal.';

grant select on clin.v_pat_vaccinations_journal to group "gm-doctors";


-- --------------------------------------------------------------
select gm.log_script_insertion('v14-clin-vaccination-dynamic.sql', 'Revision: 1.1');
