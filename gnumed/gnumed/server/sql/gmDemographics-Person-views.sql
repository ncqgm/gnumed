-- project: GNUMed

-- purpose: views for easier identity access
-- author: Karsten Hilbert
-- license: GPL (details at http://gnu.org)

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmDemographics-Person-views.sql,v $
-- $Id: gmDemographics-Person-views.sql,v 1.5 2003-11-23 12:53:20 sjtan Exp $

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

-- IH: 9/3/02
-- trigger function to ensure only one name is active
-- it's behaviour is to set all other names to inactive when
-- a name is made active
\unset ON_ERROR_STOP
drop trigger TR_uniq_active_name on names;
drop function F_uniq_active_name();
\set ON_ERROR_STOP 1

create FUNCTION F_uniq_active_name() RETURNS OPAQUE AS '
DECLARE
BEGIN
	IF NEW.active and NEW.active = true THEN
		-- for the observant: yes this trigger is recursive, but only once
		UPDATE names SET active = false	WHERE id_identity = NEW.id_identity AND active;
	END IF;
	RETURN NEW;
END;' LANGUAGE 'plpgsql';

create TRIGGER TR_uniq_active_name
	BEFORE INSERT OR UPDATE ON names
	FOR EACH ROW EXECUTE PROCEDURE F_uniq_active_name();

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

CREATE TRIGGER TR_delete_names
	BEFORE DELETE ON identity
	FOR EACH ROW EXECUTE PROCEDURE F_delete_names();

-- business functions
\unset ON_ERROR_STOP
drop function add_name(integer, text, text, bool);
\set ON_ERROR_STOP 1

create function add_name(integer, text, text, bool) returns integer as '
DECLARE
	identity_id alias for $1;
	first alias for $2;
	last alias for $3;
	activated alias for $4;

	n_rec record;
BEGIN
	select into n_rec * from names where id_identity = identity_id and firstnames = first and lastnames = last;
	-- exists already
	if FOUND then
		-- set the desired activation state
		update names set active = activated where id = n_rec.id;
		if FOUND then
			return n_rec.id;
		end if;
		return NULL;
	end if;
	-- new name
	insert into names (id_identity, firstnames, lastnames, active) values (identity_id, first, last, activated);
	if FOUND then
		select into n_rec id from names where id_identity = identity_id and firstnames = first and lastnames = last;
		return n_rec.id;
	end if;
	return NULL;
END;' language 'plpgsql';

-- ==========================================================
\unset ON_ERROR_STOP
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
drop view v_basic_person;
\set ON_ERROR_STOP 1

create view v_basic_person as
select
	i.id as id, i.id as i_id, n.id as n_id,
	n.title as title, n.firstnames as firstnames, n.lastnames as lastnames,
	--n.aka as aka,
	i.dob as dob, i.cob as cob, i.gender as gender
from
	identity i, names n
where
	i.deceased is NULL and n.id_identity=i.id and n.active=true;

-- i.id as id is legacy compatibility code, remove it once Archive is updated

-- ----------------------------------------------------------
-- create new name and new identity
create RULE r_insert_basic_person AS
	ON INSERT TO v_basic_person DO INSTEAD (
		INSERT INTO identity (pupic, gender, dob, cob)
					values (new_pupic(), NEW.gender, NEW.dob, NEW.cob);
		INSERT INTO names (title, firstnames, lastnames, id_identity)
					VALUES (NEW.title, NEW.firstnames, NEW.lastnames, currval ('identity_id_seq'));
	)
;

-- rule for name change - add new name to list, making it active
create RULE r_update_basic_person1 AS ON UPDATE TO v_basic_person 
    WHERE NEW.firstnames != OLD.firstnames OR NEW.lastnames != OLD.lastnames 
    OR NEW.title != OLD.title DO INSTEAD 
    INSERT INTO names (title, firstnames, lastnames, id_identity, active)
     VALUES (NEW.title, NEW.firstnames, NEW.lastnames, NEW.i_id, 't');

-- rule for identity change
-- yes, you would use this, think carefully.....
create RULE r_update_basic_person2 AS ON UPDATE TO v_basic_person
    DO INSTEAD UPDATE identity SET dob=NEW.dob, cob=NEW.cob, gender=NEW.gender
    WHERE id=NEW.i_id;

-- deletes names as well by use of a trigger (double rule would be simpler, 
-- but didn't work)
create RULE r_delete_basic_person AS ON DELETE TO v_basic_person DO INSTEAD
       DELETE FROM identity WHERE id=OLD.i_id;

-- ==========================================================
GRANT SELECT ON
	v_basic_person
TO GROUP "gm-doctors";

GRANT SELECT, INSERT, UPDATE, DELETE ON
	v_basic_person
TO GROUP "_gm-doctors";

-- =============================================
-- do simple schema revision tracking
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmDemographics-Person-views.sql,v $', '$Revision: 1.5 $');

-- =============================================
-- $Log: gmDemographics-Person-views.sql,v $
-- Revision 1.5  2003-11-23 12:53:20  sjtan
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
