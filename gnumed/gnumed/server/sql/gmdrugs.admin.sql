-- DDL structure of auditing system drug database for the gnumed project
-- Copyright 2002 by Ian Haywood
-- This is free software in the sense of the General Public License (GPL)
-- For details regarding GPL licensing see http://gnu.org
--
-- usage:
--	log into psql (database gnumed OR drugs)  as administrator
--	run the script from the prompt with "\i drugs.admin.sql" AFTER gmdrugs.sql
--=====================================================================
-- Revision 0.1 2002/10/28 ihaywood 
--
-- this is a special supplement to gmdrugs to allow editing and auditing.
-- it is seperated to preserve the intregity of gmdrugs.sql
-- tables for auditing. This is a parallel auditing system just for the 
-- drug databases. The users are the creators of the database, 
-- and may have no overlap with the users on deployed databases.

-- NOT FINISHED, don't use use yet.

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1


create table users 
(
	login name,
	public_key text,
	title varchar (100),
	password_expiry date,
	iso_countrycode char (2)
);

comment on table users is 'extra data about database users';
comment on column users.public_key is 'armoured GPG public key of this user';
comment on column users.title is 'full name and qualifications';
comment on column users.password_expiry is 'the date the password expires';
comment on column users.iso_countrycode is 'the users country';

insert into users values ('ian', NULL, 'Dr. Ian Haywood, MBBS', '31 Dec 2002', 'au');

create table audit
(
	id serial primary key,
	table_name name,
	table_row integer,
	stamp datetime default current_timestamp,
	who name default current_user,
	why text, -- general comment on the change
	what text, -- pickled contents of the row
	-- (this is of course a ridiculously inefficient means of storage.)
	action char check (action in ('i', 'u', 'd', 'v')),
	-- i=insert, u=update, d=delete, v=validate
	version integer,
	source integer references info_reference (id),
	signature text 
);

comment on table audit is 'this is a master table of all changes to the database.'; 

comment on column audit.what is 'pickled contents of the row after change made.';

comment on column audit.action is 'action performed on row';
comment on column audit.source is 'source of information for this change';
comment on column audit.signature is 'GPG signature of the what field';
comment on column audit.why is 'explanation of the change';

--A Note on Signatures
--SQL rows cannot be signed, only 'documents': i.e ASCII strings, can be.
--So PL/Python is used to form a pickled dictionary of the row, and 
--this is signed.

--PL/Python trigger to update audit table.
drop trigger element_trig on drug_element;
drop function audit_func ();

create function audit_func () returns opaque as '
import StringIO
import string
if TD["event"] == "INSERT":
 action = "i"
 row = TD["new"]
elif TD["event"] == "UPDATE":
 action = "u"
 row = TD["new"]
elif TD["event"] == "DELETE":
 action = "d"
 row = TD["old"]
else:
 plpy.fatal ("unknown action")
if row.has_key ("id"):
 row_id = row["id"]
else:
 row_id = "NULL"
# the description ("what" field) depends on the underlying table.
# to make this meaningful, references must be looked up.
# certain regularities in the way columns are named can be exploited to do this, this is not 
# a graceful or complete solution, but better than any alternative I could think of.
# what becomes a HTML table of field:value pairs.
f = StringIO.StringIO()
for field in row.keys ():
 if field == "id_drug" or field == "id_component" or field == "id_compound" or field == "id_class" or field == "id_interacts_with":
  value = plpy.execute ("select get_drug_name (%s) as foo" % row[field])[0]["foo"]
  field = field[3:]
 elif field == "id_route":
  value = plpy.execute ("select description from drug_routes where id = %s" % row[field])[0]["description"]
  field = field[3:]
 elif field == "id_formulation":
  value = plpy.execute ("select description from drug_formulations where id = %s" % row[field])[0]["description"]
  field = field[3:]
 elif field == "id_unit" or field == "id_packing_unit":
  value = plpy.execute ("select description from drug_units where id = %s" % row[field])[0]["description"]
  field = field[3:] 
 elif field == "id_adverse_effect":
  value = plpy.execute ("select description from adverse_effects where id = %s" % row[field])[0]["description"]
  field = field[3:]
 elif field == "id_code_system":
  value = plpy.execute ("select name from code_systems where id = %s" % row[field])[0]["name"]
  field = field[3:]
 elif field == "id_info":
  value = plpy.execute ("select title from drug_information di, information_topic it where di.id = %s and id_topic = it.id" % row[field])[0]["title"]
  field = field[3:]
 elif field == "id_interaction":
  value = plpy.execute ("select description from interactions where id = %s" % row[field])[0]["description"]
  field = field[3:]
 elif field == "id_warning":
  value = plpy.execute ("select details from drug_warning where id = %s" % row[field])[0]["details"]
  field = field[3:]
 elif field == "id_product":
  product = plpy.execute ("select get_drug_name (id_drug) as drug_name, df.description as df from product, drug_formulations where id = %s and df.id = id_formulation" % row[field])[0]
  value = "%(drug_name)s %(df)s" % product
  field = field[3:]
 elif field == "id_info_reference":
  value = plpy.execute ("select description from info_reference where id = %s" % row[field])[0]["description"]
  field = field[3:]
 else:
  value = row[field]
 f.write ("<td>%s</td><td>%s</td>" % (field, value))
what = f.getvalue ()
table_name = plpy.execute ("select relname from pg_class where oid = %s" % TD["relid"])[0]["relname"]
plpy.execute ("insert into audit (action, what, table_row, table_name, version) values (''%(action)s'', ''%(what)s'', %(row_id)s, ''%(table_name)s'', (select count (*)+1 from audit where table_name = ''%(table_name)s'' and table_row = %(row_id)s))" % vars ())
' language 'plpython';

comment on function audit_func () is 'Python trigger function to create audit entries';

create trigger element_trig after insert or update or delete on drug_element 
for each row execute procedure audit_func ();

insert into drug_element (description) values ('chop');

-- groups of users
create group contributors;
create group browsers;

grant all on audit to group contributors;
grant all on drug_dosage to group contributors;
grant all on generic_drug_name to group contributors;
grant all on link_compound_generics to group contributors;
grant all on link_drug_adverse_effects to group contributors;
grant all on link_drug_class to group contributors;
grant all on link_drug_disease_interactions to group contributors;
grant all on link_drug_indication to group contributors;
grant all on link_drug_information to group contributors;
grant all on link_drug_interactions to group contributors;
grant all on link_drug_warning to group contributors;
grant all on link_flag_product to group contributors;
grant all on link_product_component to group contributors;
grant all on link_product_manufacturer to group contributors;
grant all on product to group contributors;
grant all on subsidized_products to group contributors;
grant all on substance_dosage to group contributors;
grant all on drug_warning to group contributors;
grant all on drug_information to group contributors;
grant all on drug_element to group contributors;
grant all on conditions to group contributors;
grant all on available to group contributors;
grant all on manufacturer to contributors;
grant all on info_reference to contributors;
grant all on interactions to contributors;
grant all on adverse_effects to contributors;

grant select on audit to group browsers;
grant select on drug_dosage to group browsers;
grant select on generic_drug_name to group browsers;
grant select on link_compound_generics to group browsers;
grant select on link_drug_adverse_effects to group browsers;
grant select on link_drug_class to group browsers;
grant select on link_drug_disease_interactions to group browsers;
grant select on link_drug_indication to group browsers;
grant select on link_drug_information to group browsers;
grant select on link_drug_interactions to group browsers;
grant select on link_drug_warning to group browsers;
grant select on link_flag_product to group browsers;
grant select on link_product_component to group browsers;
grant select on link_product_manufacturer to group browsers;
grant select on product to group browsers;
grant select on subsidized_products to group browsers;
grant select on substance_dosage to group browsers;
grant select on drug_warning to group browsers;
grant select on drug_information to group browsers;
grant select on drug_element to group browsers;
grant select on conditions to group browsers;
grant select on available to group browsers;
grant select on manufacturer to browsers;
grant select on info_reference to browsers;
grant select on interactions to browsers;
grant select on adverse_effects to browsers;

grant select on code_systems to public;
grant select on drug_flags to public;
grant select on drug_formulations to public;
grant select on drug_routes to public;
grant select on drug_units to public;
grant select on information_topic to public;
grant select on drug_warning_categories to public;
grant select on subsidies to public;




