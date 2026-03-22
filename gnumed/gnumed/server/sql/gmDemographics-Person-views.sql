-- project: GNUmed

-- purpose: views for easier identity access
-- author: Karsten Hilbert
-- license: GPL v2 or later (details at http://gnu.org)

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmDemographics-Person-views.sql,v $
-- $Id: gmDemographics-Person-views.sql,v 1.55 2006-08-04 05:40:27 ncq Exp $

-- ==========================================================
drop index if exists dem.idx_identity_dob;
drop index if exists dem.idx_names_last_first;
drop index if exists dem.idx_names_firstnames;

create index idx_identity_dob on dem.identity(dob);
create index idx_names_last_first on dem.names(lastnames, firstnames);
-- need this for queries on "first" only - becomes redundant with PG 8.0
create index idx_names_firstnames on dem.names(firstnames);

-- ==========================================================
-- rules/triggers/functions on table "names"

-- allow only unique names
drop index if exists dem.idx_uniq_act_name;

create unique index idx_uniq_act_name on dem.names(id_identity) where active = true;

-- IH: 9/3/02
-- trigger function to ensure only one name is active
-- it's behaviour is to set all other names to inactive when
-- a name is made active
drop trigger if exists tr_uniq_active_name on dem.names;
drop function if exists dem.f_uniq_active_name();

drop trigger if exists tr_always_active_name on dem.names;
drop function if exists dem.f_always_active_name();

-- do not allow multiple active names per person
create or replace function dem.f_uniq_active_name() RETURNS trigger AS '
DECLARE
--	tmp text;
BEGIN
--	tmp := ''identity:'' || NEW.id_identity || '',id:'' || NEW.id || '',name:'' || NEW.firstnames || '' '' || NEW.lastnames;
--	raise notice ''uniq_active_name: [%]'', tmp;
	if NEW.active = true then
		update dem.names set active = false
		where
			id_identity = NEW.id_identity
				and
			active = true;
	end if;
	return NEW;
END;' LANGUAGE 'plpgsql';

--create TRIGGER tr_uniq_active_name
--	BEFORE insert on dem.names
--	FOR EACH ROW EXECUTE PROCEDURE dem.F_uniq_active_name();

-- ensure we always have an active name
create or replace function dem.f_always_active_name() returns trigger as '
BEGIN
	if NEW.active = false then
		raise exception ''Cannot delete/disable active name. Another name must be activated first.'';
		return OLD;
	end if;
	return NEW;
END;
' language 'plpgsql';

--create trigger tr_always_active_name
--	before update or delete on dem.names
--	for each row execute PROCEDURE dem.f_always_active_name();


-- FIXME: we don't actually want this to be available
drop trigger if exists TR_delete_names on dem.identity;
drop function if exists dem.F_delete_names();

create or replace function dem.f_delete_names() RETURNS trigger AS '
DECLARE
BEGIN
	DELETE from dem.names WHERE id_identity=OLD.id;
	RETURN OLD;
END;' LANGUAGE 'plpgsql';

-- only re-enable this once we know how to do it !!
--CREATE TRIGGER TR_delete_names
--	BEFORE DELETE on dem.identity
--	FOR EACH ROW EXECUTE PROCEDURE dem.F_delete_names();

-- business functions

create or replace function dem.add_name(integer, text, text, bool) returns integer as '
DECLARE
	_id_identity alias for $1;
	_first alias for $2;
	_last alias for $3;
	_active alias for $4;

	_id integer;
BEGIN
    -- deactivate all the existing names if this name is to become active
	if _active then
		update dem.names set active = false where id_identity = _id_identity;
	end if;
	-- name already there for this identity ?
	select into _id id from dem.names where id_identity = _id_identity and firstnames = _first and lastnames = _last;
	if FOUND then
		update dem.names set active = _active where id = _id;
		return _id;
	end if;
	-- no, insert new name
	insert into dem.names (id_identity, firstnames, lastnames, active) values (_id_identity, _first, _last, _active);
	if FOUND then
		return currval(''dem.names_id_seq'');
	end if;
	return NULL;
END;' language 'plpgsql';



create or replace function dem.set_nickname(integer, text) returns integer as '
DECLARE
	_id_identity alias for $1;
	_nick alias for $2;

	_names_row record;
	msg text;
BEGIN
	-- 0.1: Just always set the nickname inside the active name
	-- post 0.1: openEHR-like (name: pk, fk_identity, name, fk_type, comment, is_legal, is_active ...)
	-- does name exist ?
	select into _names_row * from dem.names where id_identity = _id_identity and active = true;
	if not found then
		msg := ''Cannot set nickname ['' || _nick || '']. No active <names> row with id_identity ['' || _id_identity || ''] found.'';
		raise exception ''%'', msg;
	end if;
	update dem.names set preferred = _nick where id = _names_row.id;
	return _names_row.id;
END;' language 'plpgsql';

comment on function dem.set_nickname(integer, text) is
	'Setting the nickname only makes sense for the currently active\n
	 name. However, we also want to keep track of previous nicknames.\n
	 Hence we would set the nickname right in the active name if\n
	 it is NULL. It it contains a previous nickname (eg IS NOT NULL)\n
	 we will inactivate the currently active name and copy it into\n
	 a new active name but with the nickname set to the new one.\n
	 Unsetting works the same (IOW *setting* to NULL).';

-- ==========================================================
create or replace function dem.create_occupation(text) RETURNS integer AS '
DECLARE
	_job alias for $1;
	_id integer;
BEGIN
	select into _id id from dem.occupation where name = _job;
	if FOUND then
		return _id;
	end if;
	insert into dem.occupation (name) values (_job);
	return currval(''dem.occupation_id_seq'');
END;' LANGUAGE 'plpgsql';

-- ==========================================================
create or replace function dem.link_person_comm(integer, text, text, bool) RETURNS integer AS '
DECLARE
	_id_identity alias for $1;
	_comm_medium alias for $2;
	_url alias for $3;
	_is_confidential alias for $4;

	_id_comm_type integer;
	_id_lnk_identity2comm integer;

	msg text;
BEGIN
	-- FIXME: maybe need to update is_confidential
	SELECT INTO _id_lnk_identity2comm id from dem.lnk_identity2comm WHERE id_identity = _id_identity AND url ILIKE _url;
	IF FOUND THEN
		RETURN _id_lnk_identity2comm;
	END IF;
	-- does comm_medium exist ?
	SELECT INTO _id_comm_type id from dem.enum_comm_types WHERE description ILIKE _comm_medium;
	IF NOT FOUND THEN
		msg := ''Cannot set person comm ['' || _id_identity || '', '' || _comm_medium || '','' || _url || '']. No enum_comms_types row with description ['' || _comm_medium || ''] found.'';
		RAISE EXCEPTION ''---> %'', msg;
	END IF;
	-- update existing comm. 0.1 Release (FIXME: rewrite later to allow for any number of type entries per identity)
	SELECT INTO _id_lnk_identity2comm id from dem.lnk_identity2comm WHERE id_identity = _id_identity AND id_type = _id_comm_type;
	IF FOUND THEN
		UPDATE dem.lnk_identity2comm SET url = _url, is_confidential = _is_confidential WHERE id = _id_lnk_identity2comm;
		RETURN _id_lnk_identity2comm;
	END IF;
	-- create new communication2identity link
	INSERT INTO dem.lnk_identity2comm (id_identity, url, id_type, is_confidential) values (_id_identity, _url, _id_comm_type, _is_confidential);
	RETURN currval(''dem.lnk_identity2comm_id_seq'');
END;' LANGUAGE 'plpgsql';

drop function if exists dem.new_pupic() cascade;

create or replace function dem.new_pupic() RETURNS char(24) AS '
DECLARE
BEGIN
   -- how does this work? How do we get new ''unique'' numbers?
   RETURN ''0000000000'';
END;' LANGUAGE 'plpgsql';

-- ==========================================================
drop view if exists dem.v_gender_labels;

create view dem.v_gender_labels as
select
	gl.tag,
	_(gl.tag) as l10n_tag,
	gl.label,
	_(gl.label) as l10n_label,
	gl.comment,
	gl.sort_weight as sort_weight,
	gl.pk as pk_gender_label
from
	dem.gender_label gl
;

-- ==========================================================
drop view if exists dem.v_basic_person cascade;

create view dem.v_basic_person as
select
	i.pk as pk_identity,
	n.id as n_id,
	i.title as title,
	n.firstnames as firstnames,
	n.lastnames as lastnames,
	i.dob as dob,
	i.cob as cob,
	i.gender as gender,
	_(i.gender) as l10n_gender,
	i.karyotype as karyotype,
	i.pupic as pupic,
	case when i.fk_marital_status is null
		then 'unknown'
		else (select ms.name from dem.marital_status ms, dem.identity i1 where ms.pk=i.fk_marital_status and i1.pk=i.pk)
	end as marital_status,
	case when i.fk_marital_status is null
		then _('unknown')
		else (select _(ms1.name) from dem.marital_status ms1, dem.identity i1 where ms1.pk=i.fk_marital_status and i1.pk=i.pk)
	end as l10n_marital_status,
	i.fk_marital_status as pk_marital_status,
	n.preferred as preferred,
	i.xmin as xmin_identity
from
	dem.identity i,
	dem.names n
where
	i.deleted is False and
	i.deceased is NULL and
	n.active = true and
	n.id_identity = i.pk
;

-- ----------------------------------------------------------
-- create new name and new identity
create RULE r_insert_basic_person AS
	ON INSERT TO dem.v_basic_person DO INSTEAD (
		INSERT INTO dem.identity (pupic, gender, dob, cob, title)
					values (dem.new_pupic(), NEW.gender, NEW.dob, NEW.cob, NEW.title);
		INSERT INTO dem.names (firstnames, lastnames, id_identity)
					VALUES (NEW.firstnames, NEW.lastnames, currval('dem.identity_pk_seq'));
	)
;

-- rule for name change - add new name to list, making it active
create RULE r_update_basic_person1 AS
	ON UPDATE TO dem.v_basic_person WHERE
		NEW.firstnames != OLD.firstnames OR
		NEW.lastnames != OLD.lastnames OR
		NEW.title != OLD.title
	DO INSTEAD 
		INSERT INTO dem.names (firstnames, lastnames, id_identity, active)
			VALUES (NEW.firstnames, NEW.lastnames, NEW.pk_identity, true);

-- rule for identity change
-- yes, you would use this, think carefully.....
create RULE r_update_basic_person2 AS
	ON UPDATE TO dem.v_basic_person DO INSTEAD
		UPDATE dem.identity SET
			dob=NEW.dob,
			cob=NEW.cob,
			gender=NEW.gender
		WHERE pk=NEW.pk_identity;

create RULE r_delete_basic_person AS
	ON DELETE to dem.v_basic_person DO INSTEAD
		update dem.identity set deleted = True where pk = OLD.pk_identity;

create rule r_del_identity as
	on delete to dem.identity do instead
		update dem.identity set deleted = True where pk = OLD.pk;

-- =============================================
-- staff views
drop view if exists dem.v_staff;

create view dem.v_staff as
select
	vbp.pk_identity as pk_identity,
	s.pk as pk_staff,
	vbp.title as title,
	vbp.firstnames as firstnames,
	vbp.lastnames as lastnames,
	s.short_alias as short_alias,
	_(sr.name) as role,
	vbp.dob as dob,
	vbp.gender as gender,
	s.db_user as db_user,
	s.comment as comment,
	s.is_active as is_active,
	(select (
		select exists (
			SELECT 1
			from pg_group
			where
				(SELECT usesysid from pg_user where usename = s.db_user) = any(grolist) and
				groname=current_database()
		)
	) AND (
		select exists (
			SELECT 1
			from pg_group
			where
				(SELECT usesysid from pg_user where usename = s.db_user) = any(grolist) and
				groname='gm-logins'
		)
	)) as can_login,
	s.xmin as xmin_staff,
	s.fk_role as pk_role
from
	dem.staff s,
	dem.staff_role sr,
	dem.v_basic_person vbp
where
	s.fk_role = sr.pk
		and
	s.fk_identity = vbp.pk_identity
;

-- =========================================================
-- emulate previous structure of address linktables
drop view if exists dem.lnk_person2address;
drop view if exists dem.lnk_org2address;

CREATE VIEW dem.lnk_person2address AS
	SELECT id_identity, id_address, id_type
	from dem.lnk_person_org_address;

CREATE VIEW dem.lnk_org2address AS
	SELECT id_org, id_address
	from dem.lnk_person_org_address;

-- ==========================================================
drop view if exists dem.v_person_comms_flat cascade;

create view dem.v_person_comms_flat as
select
        pk,
        v1.email ,
        v2.fax,
        v3.homephone,
        v4.workphone,
        v5.mobile
from
        (select pk from dem.identity) as i
            left outer join
        (select  url as email, id_identity from dem.lnk_identity2comm  where id_type =1) as v1
            on (pk = v1.id_identity)
                full outer join
            (select  url as fax, id_identity as id_id_fax from dem.lnk_identity2comm  where id_type =2 ) as v2
                on (pk = v2.id_id_fax)
                    full outer join
                (select  url as homephone, id_identity as id_id_homephone from dem.lnk_identity2comm  where id_type =3 ) as v3
                    on (pk = v3.id_id_homephone)
                        full outer join
                    (select url as workphone, id_identity as id_id_workphone from dem.lnk_identity2comm  where id_type =4 ) as v4
                        on (pk = v4.id_id_workphone)
                            full outer join
                        (select url as mobile, id_identity as id_id_mobile from dem.lnk_identity2comm  where id_type =5 ) as v5
                            on (pk = v5.id_id_mobile);

-- =========================================================

-- ==========================================================
drop index if exists dem.idx_lnk_pers2rel;

create index idx_lnk_pers2rel on dem.lnk_person2relative(id_identity, id_relation_type);

-- ==========================================================
-- permissions
-- ==========================================================
GRANT SELECT ON
	dem.v_staff
	, dem.lnk_person2address
	, dem.lnk_org2address
	, dem.v_person_comms_flat
	, dem.v_gender_labels
TO GROUP "gm-doctors";

GRANT SELECT, INSERT, UPDATE, DELETE ON
	dem.v_basic_person
TO GROUP "gm-doctors";

-- =============================================
-- do simple schema revision tracking
delete from gm_schema_revision where filename = '$RCSfile: gmDemographics-Person-views.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmDemographics-Person-views.sql,v $', '$Revision: 1.55 $');
