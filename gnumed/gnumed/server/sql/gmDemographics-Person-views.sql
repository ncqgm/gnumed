-- project: GNUMed

-- purpose: views for easier identity access
-- author: Karsten Hilbert
-- license: GPL (details at http://gnu.org)

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmDemographics-Person-views.sql,v $
-- $Id: gmDemographics-Person-views.sql,v 1.43 2005-12-07 16:28:54 ncq Exp $

-- ==========================================================
\unset ON_ERROR_STOP
drop index idx_identity_dob;
drop index idx_names_last_first;
drop index idx_names_firstnames;
\set ON_ERROR_STOP 1

create index idx_identity_dob on identity(dob);
-- useful for queries on "last and first" or "last"
create index idx_names_last_first on names(lastnames, firstnames);
-- need this for queries on "first" only
create index idx_names_firstnames on names(firstnames);

-- ==========================================================
-- rules/triggers/functions on table "names"

-- allow only unique names
\unset ON_ERROR_STOP
drop index idx_uniq_act_name;
create unique index idx_uniq_act_name on names(id_identity) where active = true;
\set ON_ERROR_STOP 1

-- IH: 9/3/02
-- trigger function to ensure only one name is active
-- it's behaviour is to set all other names to inactive when
-- a name is made active
\unset ON_ERROR_STOP
drop trigger tr_uniq_active_name on names;
drop function f_uniq_active_name();

drop trigger tr_always_active_name on names;
drop function f_always_active_name();
\set ON_ERROR_STOP 1

-- do not allow multiple active names per person
create FUNCTION F_uniq_active_name() RETURNS OPAQUE AS '
DECLARE
--	tmp text;
BEGIN
--	tmp := ''identity:'' || NEW.id_identity || '',id:'' || NEW.id || '',name:'' || NEW.firstnames || '' '' || NEW.lastnames;
--	raise notice ''uniq_active_name: [%]'', tmp;
	if NEW.active = true then
		update names set active = false
		where
			id_identity = NEW.id_identity
				and
			active = true;
	end if;
	return NEW;
END;' LANGUAGE 'plpgsql';

--create TRIGGER tr_uniq_active_name
--	BEFORE insert ON names
--	FOR EACH ROW EXECUTE PROCEDURE F_uniq_active_name();

-- ensure we always have an active name
create function f_always_active_name() returns opaque as '
BEGIN
	if NEW.active = false then
		raise exception ''Cannot delete/disable active name. Another name must be activated first.'';
		return OLD;
	end if;
	return NEW;
END;
' language 'plpgsql';

--create trigger tr_always_active_name
--	before update or delete on names
--	for each row execute procedure f_always_active_name();


-- FIXME: we don't actually want this to be available
\unset ON_ERROR_STOP
drop trigger TR_delete_names on identity;
drop function F_delete_names();
\set ON_ERROR_STOP 1

CREATE FUNCTION F_delete_names() RETURNS OPAQUE AS '
DECLARE
BEGIN
	DELETE FROM names WHERE id_identity=OLD.id;
	RETURN OLD;
END;' LANGUAGE 'plpgsql';

-- only re-enable this once we know how to do it !!
--CREATE TRIGGER TR_delete_names
--	BEFORE DELETE ON identity
--	FOR EACH ROW EXECUTE PROCEDURE F_delete_names();

-- business functions

\unset ON_ERROR_STOP
drop function add_name(integer, text, text, bool);
\set ON_ERROR_STOP 1

create function add_name(integer, text, text, bool) returns integer as '
DECLARE
	_id_identity alias for $1;
	_first alias for $2;
	_last alias for $3;
	_active alias for $4;

	_id integer;
BEGIN
	-- name already there for this identity ?
	select into _id id from names where id_identity = _id_identity and firstnames = _first and lastnames = _last;
	if FOUND then
		update names set active = _active where id = _id;
		return _id;
	end if;
	-- no, insert new name
	if _active then
	    -- deactivate all the existing names
		update names set active = false where id_identity = _id_identity;
	end if;
	insert into names (id_identity, firstnames, lastnames, active) values (_id_identity, _first, _last, _active);
	if FOUND then
		return currval(''names_id_seq'');
	end if;
	return NULL;
END;' language 'plpgsql';

\unset ON_ERROR_STOP
drop function set_nickname(integer, text);
\set ON_ERROR_STOP 1

create function set_nickname(integer, text) returns integer as '
DECLARE
	_id_identity alias for $1;
	_nick alias for $2;

	_names_row record;
BEGIN
	-- 0.1: Just always set the nickname inside the active name
	-- post 0.1: openEHR-like (name: pk, fk_identity, name, fk_type, comment, is_legal, is_active ...)
	-- does name exist ?
	select into _names_row * from names where id_identity = _id_identity and active = true;
	if not found then
		msg := ''Cannot set nickname ['' || _nick || '']. No active <names> row with id_identity ['' || _id_identity || ''] found.''
		raise exception msg;
	end if;
	-- can directly set nickname ?
	-- if _names_row.preferred is null then
	update names set preferred = _nick where id = _names_row.id;
	return _names_row.id;
	-- end if;
	-- must create new row
	-- 1) deactivate old row ...
	-- update names set active = false where id = _names_row.id;
	-- 2) insert new row from old row  and new data ...
	--insert into names (id_identity, active, firstnames, lastnames, preferred, comment)
	--	values (_id_identity, true, _names_row.firstnames, _names_row.lastnames, _nick, _names_row.comment);
	--if found then
	--	return currval(''names_id_seq'');
	--end if;
	--return NULL;
END;' language 'plpgsql';

comment on function set_nickname(integer, text) is
	'Setting the nickname only makes sense for the currently active\n
	 name. However, we also want to keep track of previous nicknames.\n
	 Hence we would set the nickname right in the active name if\n
	 it is NULL. It it contains a previous nickname (eg IS NOT NULL)\n
	 we will inactivate the currently active name and copy it into\n
	 a new active name but with the nickname set to the new one.\n
	 Unsetting works the same (IOW *setting* to NULL).';

-- ==========================================================
\unset ON_ERROR_STOP 
drop function create_occupation(text);
\set ON_ERROR_STOP 1

CREATE FUNCTION create_occupation(text) RETURNS integer AS '
DECLARE
	_job alias for $1;
	_id integer;
BEGIN
	select into _id id from occupation where name = _job;
	if FOUND then
		return _id;
	end if;
	insert into occupation (name) values (_job);
	return currval(''occupation_id_seq'');
END;' LANGUAGE 'plpgsql';

-- ==========================================================
\unset ON_ERROR_STOP 
drop function link_person_comm(integer, text, text, bool);
\set ON_ERROR_STOP 1

CREATE FUNCTION link_person_comm(integer, text, text, bool) RETURNS integer AS '
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
	SELECT INTO _id_lnk_identity2comm id FROM lnk_identity2comm WHERE id_identity = _id_identity AND url ILIKE _url;
	IF FOUND THEN
		RETURN _id_lnk_identity2comm;
	END IF;
	-- does comm_medium exist ?
	SELECT INTO _id_comm_type id FROM enum_comm_types WHERE description ILIKE _comm_medium;
	IF NOT FOUND THEN
		msg := ''Cannot set person comm ['' || _id_identity || '', '' || _comm_medium || '','' || _url || '']. No enum_comms_types row with description ['' || _comm_medium || ''] found.'';
		RAISE EXCEPTION ''---> %'', msg;
	END IF;
	-- update existing comm. 0.1 Release (FIXME: rewrite later to allow for any number of type entries per identity)
	SELECT INTO _id_lnk_identity2comm id FROM lnk_identity2comm WHERE id_identity = _id_identity AND id_type = _id_comm_type;
	IF FOUND THEN
		UPDATE lnk_identity2comm SET url = _url, is_confidential = _is_confidential WHERE id = _id_lnk_identity2comm;
		RETURN _id_lnk_identity2comm;
	END IF;
	-- create new communication2identity link
	INSERT INTO lnk_identity2comm (id_identity, url, id_type, is_confidential) values (_id_identity, _url, _id_comm_type, _is_confidential);
	RETURN currval(''lnk_identity2comm_id_seq'');
END;' LANGUAGE 'plpgsql';

\unset ON_ERROR_STOP
drop function new_pupic() cascade;
drop function new_pupic();
\set ON_ERROR_STOP 1

CREATE FUNCTION new_pupic() RETURNS char(24) AS '
DECLARE
BEGIN
   -- how does this work? How do we get new ''unique'' numbers?
   RETURN ''0000000000'';
END;' LANGUAGE 'plpgsql';

-- ==========================================================
\unset ON_ERROR_STOP
drop view v_gender_labels;
\set ON_ERROR_STOP 1

create view v_gender_labels as
select
	gl.tag,
	_(gl.tag) as l10n_tag,
	gl.label,
	_(gl.label) as l10n_label,
	gl.comment,
	gl.sort_weight as sort_weight,
	gl.pk as pk_gender_label
from
	gender_label gl
;

-- ==========================================================
\unset ON_ERROR_STOP
drop view v_basic_person cascade;
\set ON_ERROR_STOP 1

create view v_basic_person as
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
		else (select ms.name from marital_status ms, identity i1 where ms.pk=i.fk_marital_status and i1.pk=i.pk)
	end as marital_status,
	case when i.fk_marital_status is null
		then _('unknown')
		else (select _(ms1.name) from marital_status ms1, identity i1 where ms1.pk=i.fk_marital_status and i1.pk=i.pk)
	end as l10n_marital_status,
	i.fk_marital_status as pk_marital_status,
	n.preferred as preferred,
	i.xmin as xmin_identity
from
	identity i,
	names n
where
	i.deceased is NULL and
	n.active = true and
	n.id_identity = i.pk
;

-- ----------------------------------------------------------
-- create new name and new identity
create RULE r_insert_basic_person AS
	ON INSERT TO v_basic_person DO INSTEAD (
		INSERT INTO identity (pupic, gender, dob, cob, title)
					values (new_pupic(), NEW.gender, NEW.dob, NEW.cob, NEW.title);
		INSERT INTO names (firstnames, lastnames, id_identity)
					VALUES (NEW.firstnames, NEW.lastnames, currval('identity_pk_seq'));
	)
;

-- rule for name change - add new name to list, making it active
create RULE r_update_basic_person1 AS ON UPDATE TO v_basic_person 
    WHERE NEW.firstnames != OLD.firstnames OR NEW.lastnames != OLD.lastnames 
    OR NEW.title != OLD.title DO INSTEAD 
    INSERT INTO names (firstnames, lastnames, id_identity, active)
     VALUES (NEW.firstnames, NEW.lastnames, NEW.pk_identity, true);

-- rule for identity change
-- yes, you would use this, think carefully.....
create RULE r_update_basic_person2 AS ON UPDATE TO v_basic_person
    DO INSTEAD UPDATE identity SET dob=NEW.dob, cob=NEW.cob, gender=NEW.gender
    WHERE pk=NEW.pk_identity;

-- deletes names as well by use of a trigger (double rule would be simpler, 
-- but didn't work)
create RULE r_delete_basic_person AS ON DELETE TO v_basic_person DO INSTEAD
       DELETE FROM identity WHERE pk=OLD.pk_identity;

-- =============================================
-- staff views
\unset ON_ERROR_STOP
drop view v_staff;
\set ON_ERROR_STOP 1

create view v_staff as
select
	vbp.pk_identity as pk_identity,
	s.pk as pk_staff,
	vbp.title as title,
	vbp.firstnames as firstnames,
	vbp.lastnames as lastnames,
	s.sign as sign,
	_(sr.name) as role,
	vbp.dob as dob,
	vbp.gender as gender,
	s.db_user as db_user,
	s.comment as comment
from
	staff s,
	staff_role sr,
	v_basic_person vbp
where
	s.fk_role = sr.pk
		and
	s.fk_identity = vbp.pk_identity
;

-- =========================================================
-- emulate previous structure of address linktables
\unset ON_ERROR_STOP
drop view lnk_person2address;
drop view lnk_org2address;
\set ON_ERROR_STOP 1

CREATE VIEW lnk_person2address AS
	SELECT id_identity, id_address, id_type
	FROM lnk_person_org_address;

CREATE VIEW lnk_org2address AS
	SELECT id_org, id_address
	FROM lnk_person_org_address;

-- ==========================================================
\unset ON_ERROR_STOP
drop view v_person_comms_flat cascade;
drop view v_person_comms_flat;
\set ON_ERROR_STOP 1

create view v_person_comms_flat as
select
        pk,
        v1.email ,
        v2.fax,
        v3.homephone,
        v4.workphone,
        v5.mobile
from
        (select pk from identity) as i
            left outer join
        (select  url as email, id_identity from lnk_identity2comm  where id_type =1) as v1
            on (pk = v1.id_identity)
                full outer join
            (select  url as fax, id_identity as id_id_fax from lnk_identity2comm  where id_type =2 ) as v2
                on (pk = v2.id_id_fax)
                    full outer join
                (select  url as homephone, id_identity as id_id_homephone from lnk_identity2comm  where id_type =3 ) as v3
                    on (pk = v3.id_id_homephone)
                        full outer join
                    (select url as workphone, id_identity as id_id_workphone from lnk_identity2comm  where id_type =4 ) as v4
                        on (pk = v4.id_id_workphone)
                            full outer join
                        (select url as mobile, id_identity as id_id_mobile from lnk_identity2comm  where id_type =5 ) as v5
                            on (pk = v5.id_id_mobile);

-- =========================================================

-- ==========================================================
\unset ON_ERROR_STOP
drop index idx_lnk_pers2rel;
\set ON_ERROR_STOP 1

create index idx_lnk_pers2rel on lnk_person2relative(id_identity, id_relation_type);
-- consider regular "CLUSTER idx_lnk_pers2rel ON lnk_person2relative;"

-- ==========================================================
-- permissions
-- ==========================================================
GRANT SELECT ON
	v_staff
	, lnk_person2address
	, lnk_org2address
	, v_person_comms_flat
	, v_gender_labels
TO GROUP "gm-doctors";

GRANT SELECT, INSERT, UPDATE, DELETE ON
	v_basic_person
TO GROUP "gm-doctors";

-- =============================================
-- do simple schema revision tracking
delete from gm_schema_revision where filename = '$RCSfile: gmDemographics-Person-views.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmDemographics-Person-views.sql,v $', '$Revision: 1.43 $');

-- =============================================
-- $Log: gmDemographics-Person-views.sql,v $
-- Revision 1.43  2005-12-07 16:28:54  ncq
-- - some tightening of column scopes
--
-- Revision 1.42  2005/12/06 13:22:50  ncq
-- - add missing : in front of =
--
-- Revision 1.41  2005/09/19 16:38:51  ncq
-- - adjust to removed is_core from gm_schema_revision
--
-- Revision 1.40  2005/07/14 21:31:42  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.39  2005/06/10 07:21:05  ncq
-- - add v_basic_person.l10n_gender
--
-- Revision 1.38  2005/05/24 19:54:47  ncq
-- - create_person_comm() -> link_person_comm() with some caveat for post-0.1
--
-- Revision 1.37  2005/05/22 21:44:22  cfmoro
-- For 0.1, update set nickname inside the active name
--
-- Revision 1.36  2005/04/24 14:53:51  ncq
-- - add create_person_comm from Carlos
--
-- Revision 1.35  2005/04/20 16:04:58  ncq
-- - 7.1 did not like _name for some strange reason, make it _job
--
-- Revision 1.34  2005/04/17 16:36:45  ncq
-- - improve add_name()
-- - add set_nickname()
-- - improve create_occupation()
--
-- Revision 1.33  2005/04/14 17:45:21  ncq
-- - gender_label.sort_rank -> sort_weight
--
-- Revision 1.32  2005/04/14 16:57:00  ncq
-- - typo fix
--
-- Revision 1.31  2005/02/13 14:41:52  ncq
-- - v_basic_person.i_pk was an exceptionally bad choice, make that pk_identity
-- - remove legacy identity.pk mappings in v_basic_person
--
-- Revision 1.30  2005/02/12 13:49:14  ncq
-- - identity.id -> identity.pk
-- - allow NULL for identity.fk_marital_status
-- - subsequent schema changes
--
-- Revision 1.29  2005/02/02 09:53:01  sjtan
--
-- keep em happy.
--
-- Revision 1.28  2005/01/26 21:29:11  ncq
-- - added missing GRANT
--
-- Revision 1.27  2004/12/21 09:59:40  ncq
-- - comm_channel -> comm else too long on server < 7.3
--
-- Revision 1.26  2004/12/20 19:04:37  ncq
-- - fixes by Ian while overhauling the demographics API
--
-- Revision 1.25  2004/12/15 09:30:48  ncq
-- - correctly pull in martial status in v_basic_person
--   (update/insert rules may be lacking now, though ?)
--
-- Revision 1.24  2004/12/15 04:18:03  ihaywood
-- minor changes
-- pointless irregularity in v_basic_address
-- extended v_basic_person to more fields.
--
-- Revision 1.23  2004/10/19 23:27:11  sjtan
-- this came up as script stopping bug , when run inside a in-order
-- concatenated monolithic sql script.
--
-- Revision 1.22  2004/08/16 19:35:52  ncq
-- - added idx_lnk_pers2rel based on ideas by Aldfaer (Anne v.d.Ploeg)
--
-- Revision 1.21  2004/07/20 07:19:12  ncq
-- - in add_name() only deactivate existing names if new name is to be active
--   or else we'd be able to have patients without an active name ...
--
-- Revision 1.20  2004/07/20 01:01:46  ihaywood
-- changing a patients name works again.
-- Name searching has been changed to query on names rather than v_basic_person.
-- This is so the old (inactive) names are still visible to the search.
-- This is so when Mary Smith gets married, we can still find her under Smith.
-- [In Australia this odd tradition is still the norm, even female doctors
-- have their medical registration documents updated]
--
-- SOAPTextCtrl now has popups, but the cursor vanishes (?)
--
-- Revision 1.19  2004/07/17 20:57:53  ncq
-- - don't use user/_user workaround anymore as we dropped supporting
--   it (but we did NOT drop supporting readonly connections on > 7.3)
--
-- Revision 1.18  2004/06/28 12:16:19  ncq
-- - drop ... cascade; doesn't work on 7.1
--
-- Revision 1.17  2004/06/27 02:39:46  sjtan
--
-- fix-up for lots of empty rows.
--
-- Revision 1.16  2004/06/25 15:19:42  ncq
-- - add v_person_comms_flat by Syan, this isn't really
--   nice since it uses hardcoded comm types
--
-- Revision 1.15  2004/06/25 15:08:57  ncq
-- - v_pat_comms by Syan
--
-- Revision 1.14  2004/04/07 18:16:06  ncq
-- - move grants into re-runnable scripts
-- - update *.conf accordingly
--
-- Revision 1.13  2004/03/27 18:35:56  ncq
-- - cleanup
--
-- Revision 1.12  2004/03/27 04:37:01  ihaywood
-- lnk_person2address now lnk_person_org_address
-- sundry bugfixes
--
-- Revision 1.11  2003/12/29 15:35:15  uid66147
-- - staff views and grants
--
-- Revision 1.10  2003/12/02 02:14:40  ncq
-- - comment out triggers on name.active until we know how to to them :-(
-- - at least we CAN do active names now
-- - ensure unique active name by means of an index, though
--
-- Revision 1.9  2003/12/01 22:11:26  ncq
-- - remove a raise notice
--
-- Revision 1.8  2003/11/26 23:54:51  ncq
-- - lnk_vaccdef2reg does not exist anymore
--
-- Revision 1.7  2003/11/23 23:37:09  ncq
-- - names.title -> identity.title
-- - yet another go at uniq_active_name triggers
--
-- Revision 1.6  2003/11/23 14:05:38  sjtan
--
-- slight debugging of add_names: start off with active=false, and then other attributes won't be affected
-- by trigger side effects.
--
-- Revision 1.5  2003/11/23 12:53:20  sjtan
-- *** empty log message ***
--
-- Revision 1.4  2003/11/23 00:02:47  sjtan
--
-- NEW.active is not the same as NEW.active = true; does it mean 'is there a NEW.active' ?
-- the syntax for n_id variable didn't seem to work; this works?
--
-- Revision 1.3  2003/11/22 13:58:25  ncq
-- - rename constraint for unique active names
-- - add add_name() function
--
-- Revision 1.2  2003/10/19 13:01:20  ncq
-- - add omitted "index"
--
-- Revision 1.1  2003/08/02 10:46:03  ncq
-- - rename schema files by service
--
-- Revision 1.2  2003/05/12 12:43:39  ncq
-- - gmI18N, gmServices and gmSchemaRevision are imported globally at the
--   database level now, don't include them in individual schema file anymore
--
-- Revision 1.1  2003/04/18 13:17:38  ncq
-- - collect views for Identity DB here
--
