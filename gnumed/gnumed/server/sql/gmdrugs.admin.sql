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

create table users 
(
	login name,
	public_key text,
	title varcher (100),
	password_refresh date,
);

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
create function audit_func () returns opaque as '
import pickle
import string
if TD["event"] == "INSERT":
 action = "i"
 what = pickle.dumps (TD["new"])
 table_row = TD["new"]["id"]
elif TD["event"] == "UPDATE":
 action = "u"
 what = pickle.dumps (TD["new"])
 table_row = TD["new"]["id"]
elif TD["event"] == "DELETE":
 action = "d"
 table_row = TD["old"]["id"]
 what = pickle.dumps (TD["old"])
else:
 plpy.fatal ("unknown action")
what = string.replace (what, "''", "''''")
table_name = plpy.execute ("select relname from pg_class where oid = %s" % TD["relid"])[0]["relname"]
plpy.execute ("insert into audit (action, what, table_row, table_name, version) values (''%(action)s'', ''%(what)s'', %(table_row)s, ''%(table_name)s'', (select count (*)+1 from audit where table_name = ''%(table_name)s'' and table_row = %(table_row)s))" % vars ())
' language 'plpython';

comment on function audit_func () is 'Python trigger function to create audit entries';

create trigger audit_trig after insert or update or delete on audited_table 
for each row execute procedure audit_func ();


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

grant select on adverse_effects to public;
grant select on code_systems to public;
grant select on drug_flags to public;
grant select on drug_formulations to public;
grant select on drug_routes to public;
grant select on drug_units to public;
grant select on information_topic to public;
grant select on interactions to public;
grant select on info_reference to public;
grant select on drug_warning_categories to public;
grant select on manufacturer to public;
grant select on subsidies to public;




