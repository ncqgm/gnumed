-- project: GNUMed
-- database: PERSON
-- purpose:  unique identifier for a person and a person's relationships
-- author: hherb
-- copyright: Dr. Horst Herb, horst@hherb.com
-- license: GPL (details at http://gnu.org)
-- version: 0.1
-- changelog:
-- 20.10.2001:  (hherb) identity related tables separated from gnumed main database
--              in order to facilitate use of distributed servers.
--
--              All data integrity checking and versioning taken out of this code, now handled
--              by backend driven log mechanism resp. generated automatically by another script.
--
--              In order to simplfy and speed performance, normalization of "names" undone
--
--    All address related items have been moved into a separate database
--    in order to use GIS servers where available
-- 07.03.2002:  (hherb) "title" attribute added to "names" table
-- 07.03.2002:  (hherb) view "v_basic_person" added
-- 09.03.2002:  (ihaywood) Rules for basic_person view.
-- 08.04.2002:	 (hherb) service "personalia" related changes.
--                BRAKES BACKWARDS COMPATIBILITY!
-- ================================================

-- any table that needs auditing MUST inherit audit_identity.
-- A python script (gmhistorian.py) generates automatically all triggers
-- and tables neccessary to allow versioning and audit trail keeping of
-- these tables

create table audit_identity (
	audit_id serial primary key
);

COMMENT ON TABLE audit_identity IS
'not for direct use - must be inherited by all auditable tables';


-- ==========================================================

create table identity (
	id serial primary key,
	pupic char(24),
	gender character(2) DEFAULT '?' check (gender in ('m', 'f', 'h', 'tm', 'tf', '?')),
	karyotype character(10) DEFAULT NULL,
	dob char(10),  -- consider changeing this to a date type, otherwise let it take dd/mm/yyyy 10 chars
	cob char(2),
	deceased date default NULL
) inherits (audit_identity);


COMMENT ON TABLE identity IS
'represents the unique identity of a person';

COMMENT ON COLUMN identity.pupic IS
'Portable Unique Person Identification Code as per gnumed white papers';

COMMENT ON COLUMN identity.gender is
'(m)ale, (f)emale, (h)ermaphrodite, (tm)transsexual phaenotype male, (tf)transsexual phaenotype female, (?)unknown';

COMMENT ON COLUMN identity.dob IS
'date of birth in format yyyymmdd';

COMMENT ON COLUMN identity.cob IS
'country of birth as per date of birth, coded as 2 character ISO code';

COMMENT ON COLUMN identity.deceased IS
'date when a person has died (if so), format yyyymmdd';

-- as opposed to the versioning of all other tables, changed names
-- should not be moved into the audit trail tables. Search functionality
-- must be available at any time for all names a person ever had.
-- we still need a smart and efficient trigger function that ensures that
-- there is only ONE "active" names record for any given identity at any
-- given time

create table names (
	id serial primary key,
	id_identity integer references identity,
	active boolean default 't',
	lastnames varchar (80),
	firstnames varchar(255),
	--aka varchar (80),
	--IMHO, AKAs should be multiple "name" entries
	preferred varchar(80),
	title varchar(80) --yes, there are some incredible rants of titles ...
) inherits (audit_identity);

COMMENT ON TABLE names IS
'all the names an identity is known under';

COMMENT ON COLUMN names.active IS
'true if the name is still in use';

COMMENT ON COLUMN names.firstnames IS
'all first names of an identity in legal order';

COMMENT ON COLUMN names.lastnames IS
'all last names of an identity in legal order';

--COMMENT ON COLUMN names.aka IS
--'also known as ...';

COMMENT ON COLUMN names.preferred IS
'the preferred first name, the name a person is usually called (nickname)';

-- IH: 9/3/02
-- trigger function to ensure one name is active.
-- its behaviour is to set all other names to inactive when
-- a name is made active.

CREATE FUNCTION check_active_name () RETURNS OPAQUE AS '
DECLARE
BEGIN
	IF NEW.active THEN
	   UPDATE names SET active=''f'' WHERE id_identity = NEW.id_identity
	   AND active;
	END IF;
	RETURN NEW;
END;' LANGUAGE 'plpgsql';

CREATE TRIGGER t_check_active_name BEFORE INSERT OR UPDATE ON names
FOR EACH ROW EXECUTE PROCEDURE check_active_name ();

-- for the observant: yes this trigger is recursive, but only once

-- ==========================================================

-- theoretically, the only information needed to establish any kind of
-- biological family tree would be information about parenthood.
-- However, sometimes social family trees are equally important and at
-- other times information about parenthood is not known or uncertain
-- and it is still useful to record whatever information we can gather.
-- Thus, we need a variety of relationship types

create table relation_types (
	id serial primary key,
	biological boolean,
	biol_verified boolean default false,
	description varchar(40)
) inherits (audit_identity);

COMMENT ON TABLE relation_types IS
'types of biological and social relationships between an identities';

COMMENT ON COLUMN relation_types.biological IS
'true id the relationship is biological (proven or reasonable assumption), else false';

COMMENT ON COLUMN relation_types.biol_verified IS
'ONLY set to true if there is genetic proof for this relationship';

COMMENT ON COLUMN relation_types.description IS
'plain text description of relationship';

--!!I18N!!
-- TRANSLATORS: please do NOT alter the sequence or insert anything; just translate!
-- Only that way we will be able to exchange relationship details between multilingual
-- databases. Hopefully, we will soon have an ontology taking care of this problem.

insert into relation_types(biological, description) values('t', 'parent');
insert into relation_types(biological, description) values('t', 'sibling');
insert into relation_types(biological, description) values('t', 'halfsibling');
insert into relation_types(biological, description) values('f', 'stepparent');
insert into relation_types(biological, description) values('f', 'married');
insert into relation_types(biological, description) values('f', 'defacto');
insert into relation_types(biological, description) values('f', 'divorced');
insert into relation_types(biological, description) values('f', 'separated');
insert into relation_types(biological, description) values('f', 'legal_guardian');

-- ==========================================================

create table relation (
	id serial primary key,
	id_identity integer references identity,
	id_relative integer references identity,
	id_relation_type integer references relation_types,
	started date default NULL,
	ended date default NULL
) inherits (audit_identity);

COMMENT ON TABLE relation IS
'biological and social relationships between an identity and other identities';

COMMENT ON COLUMN relation.id_identity IS
'primary identity to whom the relationship applies';

COMMENT ON COLUMN relation.id_relative IS
'referred identity of this relationship (e.g. "child" if id_identity points to the father and id_relation_type points to "parent")';

COMMENT ON COLUMN relation.started IS
'date when this relationship begun';

COMMENT ON COLUMN relation.ended IS
'date when this relationship ended. Biological relationships do not end!';

-- ==========================================================
create view v_basic_person as
select
	i.id as id,
	n.title as title, n.firstnames as firstnames, n.lastnames as lastnames,
	--n.aka as aka,
	i.dob as dob, i.cob as cob, i.gender as gender
from
	identity i, names n
where
	i.deceased is NULL and n.id_identity=i.id and n.active=true;

-- ==========================================================
-- IH 9/3/02 Add some rules
CREATE FUNCTION new_pupic () RETURNS char (24) AS '
DECLARE
BEGIN
   -- how does this work? How do we get new ''unique'' numbers?
   RETURN ''0000000000'';
END;' LANGUAGE 'plpgsql';


-- create new name and new identity.

CREATE RULE r_insert_basic_person AS ON INSERT TO v_basic_person DO INSTEAD
(
	INSERT INTO identity (pupic, gender, dob, cob) values
	       (new_pupic (), NEW.gender, NEW.dob, NEW.cob);
	INSERT INTO names (title, firstnames, lastnames, id_identity)
	VALUES (NEW.title, NEW.firstnames, NEW.lastnames,
	       currval ('identity_id_seq'));
);


-- rule for name change - add new name to list, making it active.
CREATE RULE r_update_basic_person1 AS ON UPDATE TO v_basic_person 
    WHERE NEW.firstnames != OLD.firstnames OR NEW.lastnames != OLD.lastnames 
    OR NEW.title != OLD.title DO INSTEAD 
    INSERT INTO names (title, firstnames, lastnames, id_identity, active)
     VALUES (NEW.title, NEW.firstnames, NEW.lastnames, NEW.id, 't');

-- rule for identity change
-- yes, you would use this, think carefully.....
CREATE RULE r_update_basic_person2 AS ON UPDATE TO v_basic_person
    DO INSTEAD UPDATE identity SET dob=NEW.dob, cob=NEW.cob, gender=NEW.gender
    WHERE id=NEW.id;
       
-- deletes names as well by use of a trigger (double rule would be simpler, 
-- but didn't work)
CREATE RULE r_delete_basic_person AS ON DELETE TO v_basic_person DO INSTEAD
       DELETE FROM identity WHERE id=OLD.id;

CREATE FUNCTION delete_names () RETURNS OPAQUE AS '
DECLARE
BEGIN
	DELETE FROM names WHERE id_identity=OLD.id;
	RETURN OLD;
END;' LANGUAGE 'plpgsql';


CREATE TRIGGER t_delete_names BEFORE DELETE ON identity
FOR EACH ROW EXECUTE PROCEDURE delete_names ();
-- ==========================================================
-- FIXME: until proper permissions system is developed,
-- otherwise new users  can spend hours wrestling with
-- postgres permissions
GRANT SELECT ON names, identity, v_basic_person TO GROUP "gm-doctors";
GRANT SELECT, INSERT, UPDATE, DELETE ON v_basic_person TO "_gm-doctors";

-- ==========================================================
-- insert some example people

insert into v_basic_person (title, firstnames, lastnames, dob, cob, gender) values ('Mr.', 'Ian', 'Haywood', '19/12/77', 'UK', 'm');
insert into v_basic_person (title, firstnames, lastnames, dob, cob, gender) values ('Ms.', 'Cilla', 'Raby', '1/3/79', 'AU', 'f');
insert into v_basic_person (title, firstnames, lastnames, dob, cob, gender) values ('Dr.', 'Horst', 'Herb', '1/1/70', 'DE', 'm');
insert into v_basic_person (title, firstnames, lastnames, dob, cob, gender) values ('Dr.', 'Richard', 'Terry', '1/1/60', 'AU', 'm');
insert into v_basic_person (title, firstnames, lastnames, dob, cob, gender) values ('Dr.', 'Karsten', 'Hilbert', '23/10/74', 'DE', 'm');
insert into v_basic_person (title, firstnames, lastnames, dob, cob, gender) values ('Mr.', 'Sebastian', 'Hilbert', '13/03/79', 'DE', 'm');
