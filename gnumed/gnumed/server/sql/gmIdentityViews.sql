-- project: GNUMed

-- purpose: views for easier identity access
-- author: Karsten Hilbert
-- license: GPL (details at http://gnu.org)

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/Attic/gmIdentityViews.sql,v $
-- $Id: gmIdentityViews.sql,v 1.2 2003-05-12 12:43:39 ncq Exp $

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

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
CREATE RULE r_insert_basic_person AS
	ON INSERT TO v_basic_person DO INSTEAD (
		INSERT INTO identity (pupic, gender, dob, cob)
					values (new_pupic(), NEW.gender, NEW.dob, NEW.cob);
		INSERT INTO names (title, firstnames, lastnames, id_identity)
					VALUES (NEW.title, NEW.firstnames, NEW.lastnames, currval ('identity_id_seq'));
	)
;

-- rule for name change - add new name to list, making it active
CREATE RULE r_update_basic_person1 AS ON UPDATE TO v_basic_person 
    WHERE NEW.firstnames != OLD.firstnames OR NEW.lastnames != OLD.lastnames 
    OR NEW.title != OLD.title DO INSTEAD 
    INSERT INTO names (title, firstnames, lastnames, id_identity, active)
     VALUES (NEW.title, NEW.firstnames, NEW.lastnames, NEW.i_id, 't');

-- rule for identity change
-- yes, you would use this, think carefully.....
CREATE RULE r_update_basic_person2 AS ON UPDATE TO v_basic_person
    DO INSTEAD UPDATE identity SET dob=NEW.dob, cob=NEW.cob, gender=NEW.gender
    WHERE id=NEW.i_id;

-- deletes names as well by use of a trigger (double rule would be simpler, 
-- but didn't work)
CREATE RULE r_delete_basic_person AS ON DELETE TO v_basic_person DO INSTEAD
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
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmIdentityViews.sql,v $', '$Revision: 1.2 $');

-- =============================================
-- $Log: gmIdentityViews.sql,v $
-- Revision 1.2  2003-05-12 12:43:39  ncq
-- - gmI18N, gmServices and gmSchemaRevision are imported globally at the
--   database level now, don't include them in individual schema file anymore
--
-- Revision 1.1  2003/04/18 13:17:38  ncq
-- - collect views for Identity DB here
--
