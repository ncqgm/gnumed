#Create one large string from string lines from fileinput.
#simple tables
# audit_clinical
# enum_clinical_encounters
# enum_clinical_history
# enum_info_sources
# enum_coding_systems
# enum_confidentiality_level
# episode
# drug_units
# drug_formulations
# drug_routes
# databases
# enum_immunities


#complex tables
# clinical_transaction
# clinical_history
# coding_systems
# diagnosis_code_text
# clinical_diagnosis
# clinical_diagnosis_extra
# script_drug
# constituents
# script
# link_script_drug


#looking at table  audit_clinical
#a primary key (?) is  	audit_id serial


#looking at table  enum_clinical_encounters
#a primary key (?) is  	id SERIAL primary key,
#User Data Line is (?)  	description text


#looking at table  enum_clinical_history
#a primary key (?) is  	id SERIAL primary key,
#User Data Line is (?)  	description text


#looking at table  enum_info_sources
#a primary key (?) is  	id serial primary key,
#User Data Line is (?)  	description varchar (100)


#looking at table  enum_coding_systems
#a primary key (?) is  	id SERIAL primary key,
#User Data Line is (?)  	description text


#looking at table  enum_confidentiality_level
#a primary key (?) is  	id SERIAL primary key,
#User Data Line is (?)  	description text


#looking at table  episode
#a primary key (?) is  	id serial primary key,
#User Data Line is (?)  	id_patient integer not null,
#User Data Line is (?)  	name varchar(128) default 'unspecified'


#looking at table  drug_units
#a primary key (?) is  	id serial primary key,
#User Data Line is (?)  	unit varchar(30)


#looking at table  drug_formulations
#a primary key (?) is  	id serial primary key,
#User Data Line is (?)  	description varchar(60),
#User Data Line is (?)  	comment text


#looking at table  drug_routes
#a primary key (?) is  	id serial primary key,
#User Data Line is (?)  	description varchar(60),
#User Data Line is (?)  	abbreviation varchar(10),
#User Data Line is (?)  	comment text


#looking at table  databases
#a primary key (?) is  	id serial primary key,
#User Data Line is (?)  	name varchar (50),
#User Data Line is (?)  	published date


#looking at table  enum_immunities
#a primary key (?) is  	id serial primary key,
#User Data Line is (?)  	name text


#looking at table  clinical_transaction
#a primary key (?) is  	id SERIAL primary key,
#User Data Line is (?)  	stamp timestamp with time zone,
#User Data Line is (?)  	duration interval,
#User Data Line is (?)  	id_location int,
#User Data Line is (?)  	id_provider int,  
#User Data Line is (?)  	id_patient int, 
#User Data Line is (?)  	id_enum_clinical_encounters int REFERENCES enum_clinical_encounters (id)


#looking at table  clinical_history
#a primary key (?) is  	id SERIAL primary key,
#User Data Line is (?)  	id_enum_clinical_history int REFERENCES enum_clinical_history (id),
#User Data Line is (?)  	id_clinical_transaction int  REFERENCES clinical_transaction (id),
#User Data Line is (?)  	id_info_sources int REFERENCES enum_info_sources (id),
#User Data Line is (?)  	text text


#looking at table  coding_systems
#a primary key (?) is  	id SERIAL primary key,
#User Data Line is (?)  	id_enum_coding_systems int REFERENCES enum_coding_systems (id),
#User Data Line is (?)  	description text,
#User Data Line is (?)  	deprecated timestamp


#looking at table  diagnosis_code_text
#a primary key (?) is  create table diagnosis_code_text( code char(16) not null, id_coding_system int references coding_systems, text text, primary key(code, id_coding_system))


#looking at table  clinical_diagnosis
#a primary key (?) is  	id SERIAL primary key,
#User Data Line is (?)  	id_clinical_transaction int  REFERENCES clinical_transaction (id),
#User Data Line is (?)  	approximate_start text DEFAULT null,
#User Data Line is (?)  	id_coding_systems int REFERENCES coding_systems (id),
#User Data Line is (?)  	text text


#looking at table  clinical_diagnosis_extra
#a primary key (?) is  	id SERIAL primary key,
#User Data Line is (?)  	id_clinical_diagnosis int REFERENCES clinical_diagnosis (id),
#User Data Line is (?)  	id_enum_confidentiality_level int REFERENCES enum_confidentiality_level (id)


#looking at table  script_drug
#a primary key (?) is  	id serial primary key,
#User Data Line is (?)  	name varchar (200) default 'GENERIC',
#User Data Line is (?)  	directions text,
#User Data Line is (?)  	adjuvant text,
#User Data Line is (?)  	xref_id varchar (100),
#User Data Line is (?)  	source integer references databases (id),
#User Data Line is (?)  	fluid_amount float,
#User Data Line is (?)  	amount_unit integer references drug_units (id),
#User Data Line is (?)  	amount integer,
#User Data Line is (?)  	id_route integer references drug_routes (id),
#User Data Line is (?)  	id_form integer references drug_formulations (id),
#User Data Line is (?)  	frequency integer


#looking at table  constituents
#a primary key (?) is  	id serial primary key,
#User Data Line is (?)  	name varchar (100),
#User Data Line is (?)  	dose float,
#User Data Line is (?)  	dose_unit integer references drug_units (id),
#User Data Line is (?)  	id_drug integer references script_drug (id)


#looking at table  script
#a primary key (?) is  	id serial primary key,
#User Data Line is (?)  	id_transaction integer references clinical_transaction (id)


#looking at table  link_script_drug
#User Data Line is (?)  	id_drug integer references script_drug (id),
#User Data Line is (?)  	id_script integer references script (id),
#User Data Line is (?)  	comment text
# {'clinical_diagnosis_extra': ['id', ['id_clinical_diagnosis', 'id_enum_confidentiality_level']], 'link_script_drug': [None, ['id_drug', 'id_script', 'comment']], 'script_drug': ['id', ['name', 'directions', 'adjuvant', 'xref_id', 'source', 'fluid_amount', 'amount_unit', 'amount', 'id_route', 'id_form', 'frequency']], 'clinical_transaction': ['id', ['stamp', 'duration', 'id_location', 'id_provider', 'id_patient', 'id_enum_clinical_encounters']], 'coding_systems': ['id', ['id_enum_coding_systems', 'description', 'deprecated']], 'constituents': ['id', ['name', 'dose', 'dose_unit', 'id_drug']], 'script': ['id', ['id_transaction']], 'clinical_history': ['id', ['id_enum_clinical_history', 'id_clinical_transaction', 'id_info_sources', 'text']], 'clinical_diagnosis': ['id', ['id_clinical_transaction', 'approximate_start', 'id_coding_systems', 'text']]}
from  SimpleXMLRPCServer import *
from pyPgSQL.PgSQL import *
from analyse_script import *
class ExportFunc:

		def __init__(self, database_name_str):
			self.conn = None
			self.dns = database_name_str
			self.statements = None

		def _get_conn(self):
			if self.conn == None:
				self.conn = connect( self.dns)
			return self.conn
	    	
			   
		def _close_conn(self):
			if self.conn <> None:
				self.conn.close()
				self.conn = None
		
		def _execute_cmd( self, cmd):
		    conn = self._get_conn()
		    cursor = conn.cursor()
		    cursor.execute(cmd)
		    return cursor	

	
		def _do_query( self, query, offset = 0, length = 100 ):
			cmd = '%s LIMIT %s OFFSET %d' % ( query, length, offset)
			cursor = self._execute_cmd( cmd)
			return cursor.fetchall()

		def get_description(self,  tablename):
			cmd = "select * from "+tablename+" where false"
			conn = self._get_conn()
			cursor = conn.cursor()
			cursor.execute(cmd)
			d  =  cursor.description
			l = []
			for x in d:
				l.append( [x[0], x[1]])
			return l
			
		
		def _do_update( self, cmd):
		    print "before _do_update ", cmd	
	    	    cursor = self._execute_cmd(cmd)   	
		    cursor.execute("commit")
		    self._close_conn()

	   

		def convert_result(self, result):
			list = []
			for x in result:
				l = []
				l.extend(x)
				list.append(l)
			return list	
		

		def _get_statements(self):
			if self.statements == None:
				self.statements = []
			
				self.statements.append("""-- Project: GnuMed
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/sjtan/Attic/server2.py,v $
-- $Revision: 1.1 $
-- license: GPL
-- author: Ian Haywood, Horst Herb

-- ===================================================================
-- This database is internationalised!

-- do fixed string i18n()ing
--\i gmI18N.sql

create function i18n(text) returns text as '
begin
	return $1""")
				self.statements.append("""
end""")
				self.statements.append(""" ' language 'plpgsql'""")
				self.statements.append("""


-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
-- \set ON_ERROR_STOP 1

-- ===================================================================
create table audit_clinical (
	audit_id serial
)""")
				self.statements.append("""

comment on table audit_clinical is 
'ancestor table for auditing. Marks tables for automatic trigger generation'""")
				self.statements.append("""

create table enum_clinical_encounters(
	id SERIAL primary key,
	description text
)inherits (audit_clinical)""")
				self.statements.append("""


INSERT INTO enum_clinical_encounters (description)
	values (i18n('surgery consultation'))""")
				self.statements.append("""
INSERT INTO enum_clinical_encounters (description)
	values (i18n('phone consultation'))""")
				self.statements.append("""
INSERT INTO enum_clinical_encounters (description)
	values (i18n('fax consultation'))""")
				self.statements.append("""
INSERT INTO enum_clinical_encounters (description)
	values (i18n('home visit'))""")
				self.statements.append("""
INSERT INTO enum_clinical_encounters (description)
	values (i18n('nursing home visit'))""")
				self.statements.append("""
INSERT INTO enum_clinical_encounters (description)
	values (i18n('repeat script'))""")
				self.statements.append("""
INSERT INTO enum_clinical_encounters (description)
	values (i18n('hospital visit'))""")
				self.statements.append("""
INSERT INTO enum_clinical_encounters (description)
	values (i18n('video conference'))""")
				self.statements.append("""
INSERT INTO enum_clinical_encounters (description)
	values (i18n('proxy encounter'))""")
				self.statements.append("""
INSERT INTO enum_clinical_encounters (description)
	values (i18n('emergency encounter'))""")
				self.statements.append("""
INSERT INTO enum_clinical_encounters (description)
	values (i18n('other encounter'))""")
				self.statements.append("""

COMMENT ON TABLE enum_clinical_encounters is
'these are the types of encounter'""")
				self.statements.append("""


create table clinical_transaction(
	id SERIAL primary key,
	stamp timestamp with time zone,
	duration interval,
	id_location int,
	id_provider int,  
	id_patient int, 
	id_enum_clinical_encounters int REFERENCES enum_clinical_encounters (id)
) inherits (audit_clinical)""")
				self.statements.append("""

COMMENT ON TABLE clinical_transaction is
'unique identifier for clinical encounter'""")
				self.statements.append("""

COMMENT ON COLUMN clinical_transaction.stamp is 
'Date, time and timezone of the transaction.'""")
				self.statements.append(""" 

COMMENT ON COLUMN clinical_transaction.id_location is 
'Location ID, in ?? gmoffice'""")
				self.statements.append("""

COMMENT ON COLUMN clinical_transaction.id_provider is 
'ID of doctor/nurse/patient/..., in ?? gmoffice'""")
				self.statements.append("""

COMMENT ON COLUMN clinical_transaction.id_patient is 
'Patient''s ID, in gmidentity'""")
				self.statements.append("""

create table enum_clinical_history(
	id SERIAL primary key,
	description text
) inherits (audit_clinical)""")
				self.statements.append("""

COMMENT ON TABLE enum_clinical_history is
'types of history taken during a clinical encounter'""")
				self.statements.append("""


INSERT INTO enum_clinical_history (description)
	values (i18n('past'))""")
				self.statements.append("""
INSERT INTO enum_clinical_history (description)
	values (i18n('presenting complaint'))""")
				self.statements.append("""
INSERT INTO enum_clinical_history (description)
	values (i18n('history of present illness'))""")
				self.statements.append("""
INSERT INTO enum_clinical_history (description)
	values (i18n('social'))""")
				self.statements.append("""
INSERT INTO enum_clinical_history (description)
	values (i18n('family'))""")
				self.statements.append("""
INSERT INTO enum_clinical_history (description)
	values (i18n('immunisation'))""")
				self.statements.append("""
INSERT INTO enum_clinical_history (description)
	values (i18n('requests'))""")
				self.statements.append("""
INSERT INTO enum_clinical_history (description)
	values (i18n('allergy'))""")
				self.statements.append("""
INSERT INTO enum_clinical_history (description)
	values (i18n('drug'))""")
				self.statements.append("""
INSERT INTO enum_clinical_history (description)
	values (i18n('sexual'))""")
				self.statements.append("""
INSERT INTO enum_clinical_history (description)
	values (i18n('psychiatric'))""")
				self.statements.append("""
INSERT INTO enum_clinical_history (description)
	values (i18n('other'))""")
				self.statements.append("""
create table enum_info_sources
(
	id serial primary key,
	description varchar (100)
)""")
				self.statements.append("""

comment on table enum_info_sources is
'sources of clinical information: patient, relative, notes, correspondence'""")
				self.statements.append("""

insert into enum_info_sources (description) values (i18n('patient'))""")
				self.statements.append("""
insert into enum_info_sources (description) values (i18n('clinician'))""")
				self.statements.append("""
insert into enum_info_sources (description) values (i18n('relative'))""")
				self.statements.append("""
insert into enum_info_sources (description) values (i18n('carer'))""")
				self.statements.append("""
insert into enum_info_sources (description) values (i18n('notes'))""")
				self.statements.append("""
insert into enum_info_sources (description) values (i18n('correspondence'))""")
				self.statements.append("""

create table clinical_history(
	id SERIAL primary key,
	id_enum_clinical_history int REFERENCES enum_clinical_history (id),
	id_clinical_transaction int  REFERENCES clinical_transaction (id),
	id_info_sources int REFERENCES enum_info_sources (id),
	text text
)inherits (audit_clinical)""")
				self.statements.append("""

COMMENT ON TABLE clinical_history is
'narrative details of history taken during a clinical encounter'""")
				self.statements.append("""

COMMENT ON COLUMN clinical_history.id_enum_clinical_history is
'the type of history taken'""")
				self.statements.append("""

COMMENT ON COLUMN clinical_history.id_clinical_transaction is
'The transaction during which this history was taken'""")
				self.statements.append("""

COMMENT ON COLUMN clinical_history.text is
'The text typed by the doctor'""")
				self.statements.append("""


create table enum_coding_systems (
	id SERIAL primary key,
	description text
)inherits (audit_clinical)""")
				self.statements.append("""


COMMENT ON TABLE enum_coding_systems is
'The various types of coding systems available'""")
				self.statements.append("""

INSERT INTO enum_coding_systems (description)
	values (i18n('general'))""")
				self.statements.append("""
INSERT INTO enum_coding_systems (description)
	values (i18n('clinical'))""")
				self.statements.append("""
INSERT INTO enum_coding_systems (description)
	values (i18n('diagnosis'))""")
				self.statements.append("""
INSERT INTO enum_coding_systems (description)
	values (i18n('therapy'))""")
				self.statements.append("""
INSERT INTO enum_coding_systems (description)
	values (i18n('pathology'))""")
				self.statements.append("""
INSERT INTO enum_coding_systems (description)
	values (i18n('bureaucratic'))""")
				self.statements.append("""
INSERT INTO enum_coding_systems (description)
	values (i18n('ean'))""")
				self.statements.append("""
INSERT INTO enum_coding_systems (description)
	values (i18n('other'))""")
				self.statements.append("""


create table coding_systems (
	id SERIAL primary key,
	id_enum_coding_systems int REFERENCES enum_coding_systems (id),
	description text,
	version char(6),
	deprecated timestamp
)inherits (audit_clinical)""")
				self.statements.append("""

comment on table coding_systems is
'The coding systems in this database.'""")
				self.statements.append("""

create table diagnosis_code_text( code char(16) not null, id_coding_system int references coding_systems, text text, primary key(code, id_coding_system))""")
				self.statements.append("""

comment on table diagnosis_code_text is 
'use this for a tool to find codes from diagnosis text. Note foreign key 
weak entity reference was removed ( diagnosis_code_text was made a weak entity
dependent on the primary key of coding_systems, which is more difficult to 
create a parser for )'""")
				self.statements.append("""

-- =============================================
create table clinical_diagnosis (
	id SERIAL primary key,
	id_clinical_transaction int  REFERENCES clinical_transaction (id),
	approximate_start text DEFAULT null,
	code char(16) ,
	id_coding_systems int REFERENCES coding_systems (id),
	text text
	--,
	--foreign key (code, id_coding_systems) references diagnosis_code_text
)inherits (audit_clinical)""")
				self.statements.append("""

COMMENT ON TABLE clinical_diagnosis is
'Coded clinical diagnoses assigned to patient, in addition to history'""")
				self.statements.append("""

comment on column clinical_diagnosis.id_clinical_transaction is
'the transaction in which this diagnosis was made.'""")
				self.statements.append("""

comment on column clinical_diagnosis.approximate_start is
'around the time at which this diagnosis was made'""")
				self.statements.append("""

comment on column clinical_diagnosis.code is
'the code'""")
				self.statements.append("""
comment on column clinical_diagnosis.id_coding_systems is
'the coding system used to code the diagnosis'""")
				self.statements.append("""

comment on column clinical_diagnosis.text is
'extra notes on the diagnosis'""")
				self.statements.append("""

create table enum_confidentiality_level (
	id SERIAL primary key,
	description text
)inherits (audit_clinical)""")
				self.statements.append("""

comment on table enum_confidentiality_level is
'Various levels of confidentialoty of a coded diagnosis, such as public, clinical staff, treating doctor, etc.'""")
				self.statements.append("""

INSERT INTO enum_confidentiality_level (description)
	values (i18n('public'))""")
				self.statements.append("""
INSERT INTO enum_confidentiality_level (description)
	values (i18n('relatives'))""")
				self.statements.append("""
INSERT INTO enum_confidentiality_level (description)
	values (i18n('receptionist'))""")
				self.statements.append("""
INSERT INTO enum_confidentiality_level (description)
	values (i18n('clinical staff'))""")
				self.statements.append("""
INSERT INTO enum_confidentiality_level (description)
	values (i18n('doctors'))""")
				self.statements.append("""
INSERT INTO enum_confidentiality_level (description)
	values (i18n('doctors of practice only'))""")
				self.statements.append("""
INSERT INTO enum_confidentiality_level (description)
	values (i18n('treating doctor'))""")
				self.statements.append("""

create table clinical_diagnosis_extra (
	id SERIAL primary key,
	id_clinical_diagnosis int REFERENCES clinical_diagnosis (id),
	id_enum_confidentiality_level int REFERENCES enum_confidentiality_level (id)

)inherits (audit_clinical)""")
				self.statements.append("""

comment on table clinical_diagnosis_extra is
'Extra information about a diagnosis, just the confidentiality level at present.'""")
				self.statements.append("""

-- =============================================
-- episode related tables
create table episode (
	id serial primary key,
	id_patient integer not null,
	name varchar(128) default 'unspecified'
) inherits (audit_clinical)""")
				self.statements.append("""

comment on table episode is
	'clinical episodes such as "recurrent Otitis media", "traffic accident 7/99", "Hepatitis B"'""")
				self.statements.append("""
comment on column episode.id_patient is
	'id of patient this episode relates to'""")
				self.statements.append("""
comment on column episode.name is
	'descriptive name of this episode, may change over time'""")
				self.statements.append("""


-- ============================================
-- Drug related tables


-- These tables are pasted from gmdrugs.sql, how do we otherwise
-- deal with this?

create table drug_units (
	id serial primary key,
	unit varchar(30)
)""")
				self.statements.append("""
comment on table drug_units is
'(SI) units used to quantify/measure drugs'""")
				self.statements.append("""
comment on column drug_units.unit is
'(SI) units used to quantify/measure drugs like "mg", "ml"'""")
				self.statements.append("""
insert into drug_units(unit) values('ml')""")
				self.statements.append("""
insert into drug_units(unit) values('mg')""")
				self.statements.append("""
insert into drug_units(unit) values('mg/ml')""")
				self.statements.append("""
insert into drug_units(unit) values('mg/g')""")
				self.statements.append("""
insert into drug_units(unit) values('U')""")
				self.statements.append("""
insert into drug_units(unit) values('IU')""")
				self.statements.append("""
insert into drug_units(unit) values('each')""")
				self.statements.append("""
insert into drug_units(unit) values('mcg')""")
				self.statements.append("""
insert into drug_units(unit) values('mcg/ml')""")
				self.statements.append("""
insert into drug_units(unit) values('IU/ml')""")
				self.statements.append("""
insert into drug_units(unit) values('day')""")
				self.statements.append("""

create table drug_formulations(
	id serial primary key,
	description varchar(60),
	comment text
)""")
				self.statements.append("""
comment on table drug_formulations is
'presentations or formulations of drugs like "tablet", "capsule" ...'""")
				self.statements.append("""
comment on column drug_formulations.description is
'the formulation of the drug, such as "tablet", "cream", "suspension"'""")
				self.statements.append("""

--I18N!
insert into drug_formulations(description) values ('tablet')""")
				self.statements.append("""
insert into drug_formulations(description) values ('capsule')""")
				self.statements.append("""
insert into drug_formulations(description) values ('syrup')""")
				self.statements.append("""
insert into drug_formulations(description) values ('suspension')""")
				self.statements.append("""
insert into drug_formulations(description) values ('powder')""")
				self.statements.append("""
insert into drug_formulations(description) values ('cream')""")
				self.statements.append("""
insert into drug_formulations(description) values ('ointment')""")
				self.statements.append("""
insert into drug_formulations(description) values ('lotion')""")
				self.statements.append("""
insert into drug_formulations(description) values ('suppository')""")
				self.statements.append("""
insert into drug_formulations(description) values ('solution')""")
				self.statements.append("""
insert into drug_formulations(description) values ('dermal patch')""")
				self.statements.append("""
insert into drug_formulations(description) values ('kit')""")
				self.statements.append("""


create table drug_routes (
	id serial primary key,
	description varchar(60),
	abbreviation varchar(10),
	comment text
)""")
				self.statements.append("""
comment on table drug_routes is
'administration routes of drugs'""")
				self.statements.append("""
comment on column drug_routes.description is
'administration route of a drug like "oral", "sublingual", "intravenous" ...'""")
				self.statements.append("""

--I18N!
insert into drug_routes(description, abbreviation) values('oral', 'o.')""")
				self.statements.append("""
insert into drug_routes(description, abbreviation) values('sublingual', 's.l.')""")
				self.statements.append("""
insert into drug_routes(description, abbreviation) values('nasal', 'nas.')""")
				self.statements.append("""
insert into drug_routes(description, abbreviation) values('topical', 'top.')""")
				self.statements.append("""
insert into drug_routes(description, abbreviation) values('rectal', 'rect.')""")
				self.statements.append("""
insert into drug_routes(description, abbreviation) values('intravenous', 'i.v.')""")
				self.statements.append("""
insert into drug_routes(description, abbreviation) values('intramuscular', 'i.m.')""")
				self.statements.append("""
insert into drug_routes(description, abbreviation) values('subcutaneous', 's.c.')""")
				self.statements.append("""
insert into drug_routes(description, abbreviation) values('intraarterial', 'art.')""")
				self.statements.append("""
insert into drug_routes(description, abbreviation) values('intrathecal', 'i.th.')""")
				self.statements.append("""


create table databases
(
	id serial primary key,
	name varchar (50),
	published date
)""")
				self.statements.append("""

insert into databases (name, published) values ('MIMS', '1/1/02')""")
				self.statements.append("""
insert into databases (name, published) values ('AMIS', '1/1/02')""")
				self.statements.append("""
insert into databases (name, published) values ('AMH', '1/1/02')""")
				self.statements.append("""

comment on table databases is
'different drug databases'""")
				self.statements.append("""



create table script_drug
(
	id serial primary key,
	name varchar (200) default 'GENERIC',
	directions text,
	adjuvant text,
	xref_id varchar (100),
	source integer references databases (id),
	fluid_amount float,
	amount_unit integer references drug_units (id),
	amount integer,
	id_route integer references drug_routes (id),
	id_form integer references drug_formulations (id),
	prn boolean,
	frequency integer
)""")
				self.statements.append("""

comment on table script_drug is
'table for different prexcriptions'""")
				self.statements.append("""
comment on column script_drug.xref_id is 'ID of the source database'""")
				self.statements.append("""
comment on column script_drug.fluid_amount is 'if a fluid, the amount in each bottle/ampoule, etc.'""")
				self.statements.append("""
comment on column script_drug.amount is 'for solid object (tablets, capsules) the number of objects, for fluids, the number of separate containers'""")
				self.statements.append("""
comment on column script_drug.prn is 'true if "pro re nata" (= as required)'""")
				self.statements.append("""
comment on column script_drug.directions is 'free text for directions, such as ''nocte'' etc'""")
				self.statements.append("""
comment on column script_drug.adjuvant is 'free text describing adjuvants, such as ''orange-flavoured'' etc.'""")
				self.statements.append("""
	
create table constituents
(
	id serial primary key,
	name varchar (100),
	dose float,
	dose_unit integer references drug_units (id),
	id_drug integer references script_drug (id)
)""")
				self.statements.append("""

comment on table constituents is
'the constituent substances of the various drugs'""")
				self.statements.append("""
comment on column constituents.name is
'the English IUPHARM standard name, as a base, with no adjuvant, in capitals. So MORPHINE. not Morphine, not MORPHINE SULPHATE, not MORPHINIUM'""")
				self.statements.append("""
comment on column constituents.dose is
'the amount of drug (if salt, the amount of active base substance, in a unit (see amount_unit above)'""")
				self.statements.append("""
 
create table script
(
	id serial primary key,
	id_transaction integer references clinical_transaction (id)
)""")
				self.statements.append("""

comment on table script is
'one row for each physical prescription printed. Can have multiple drugs on a script, 
and multiple scripts in a transaction'""")
				self.statements.append("""

create table link_script_drug
(
	id_drug integer references script_drug (id),
	id_script integer references script (id),
	comment text
)""")
				self.statements.append("""

comment on table link_script_drug is
'many-to-many table for drugs and prescriptions'""")
				self.statements.append("""

-- =============================================

create table enum_immunities
(
	id serial primary key,
	name text
)""")
				self.statements.append("""

comment on table enum_immunities is
'list of diseases to which patients may have immunity. Same table must exist in gmdrugs'""")
				self.statements.append("""

insert into enum_immunities (name) values ('tetanus')""")
				self.statements.append("""

-- do simple schema revision tracking
\i gmSchemaRevision.sql
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: server2.py,v $', '$Revision: 1.1 $')""")
				self.statements.append("""

-- =============================================
-- $Log: server2.py,v $
-- Revision 1.1  2003-02-25 10:32:15  sjtan
-- *** empty log message ***
--
-- Revision 1.1  2003/02/02 22:43:05  sjtan
--
-- playing around with the idea of semi-auto gui generation """)
				self.statements.append(""" idea: get the server to deal out referencing
-- information as well, e.g. get_referencing_entities(table)  get_referenced_entities(table), but this doesn't
-- deal with interpretation of relations . e.g. in gmclinical, many-to-one relationships between
-- clinical_history and clinical_transaction, and clinical_history and enum_clinical_history :
--  clinical_transaction has session ( time) division, and possibly enum_clinical_history has containment
-- ( classifier) division of clinical history. Classifying many to one relationships can be in UI as a containing
-- relationship or a labelling relationship : e.g. tabs in a notebook  or separate panels in a summary panel ,
-- whereas enum_immune_type and immunization_given ( fictional examples) have a many to one relationship but
-- in the UI could be expressed as a labelling choice field in a table editor for immunization_given.
-- Is it possible, if given the relationships and table structures, and additional choices for gui organization
-- of relationships, for a tool to generate a satisfactory ui?
--
-- Revision 1.14  2003/01/20 20:10:12  ncq
-- - adapted to new i18n
--
-- Revision 1.13  2003/01/13 10:07:52  ihaywood
-- add free comment strings to script.
-- Start vaccination Hx tables
--
-- Revision 1.12  2003/01/05 13:05:51  ncq
-- - schema_revision -> gm_schema_revision
--
-- Revision 1.11  2002/12/22 01:26:16  ncq
-- - id_doctor -> id_provider + comment, typo fix
--
-- Revision 1.10  2002/12/14 08:55:17  ihaywood
-- new prescription tables -- fixed typos
--
-- Revision 1.9  2002/12/14 08:12:22  ihaywood
-- New prescription tables in gmclinical.sql
--
-- Revision 1.8  2002/12/06 08:50:51  ihaywood
-- SQL internationalisation, gmclinical.sql now internationalised.
--
-- Revision 1.7  2002/12/05 12:45:43  ncq
-- - added episode table, fixed typo
--
-- Revision 1.6  2002/12/01 13:53:09  ncq
-- - missing """)
				self.statements.append(""" at end of schema tracking line
--
-- Revision 1.5  2002/11/23 13:18:09  ncq
-- - add "proper" metadata handling and schema revision tracking
--
""")

			return self.statements
	

class simple_tables_server( ExportFunc):
	def __init__(self, dns):
		ExportFunc.__init__(self, dns)
	def create_drug_units  (self,  unit ):
		cmd =  """insert into  drug_units (  unit ) values ('%s')  """ % ( unit )
		self._do_update(cmd)
		return ""



	def select_start_drug_units  (self, field_name, field_value, start = 0, limit = 100 ) :
		cmd = """ 
		select * from  drug_units  where strpos( $s, '$s') == 1 '$  ( field_name, field_value) """
		result = self._do_query( cmd, start, limit)
		return self.convert_result(result)

	def select_by_pk_drug_units( self, pk_val):
		cmd =  'select * from drug_units where id = %s'%(pk_val)

		result = self._do_query(cmd, 0, 'ALL')
		return result
	

	def select_all_drug_units( self, start = 0, limit = 200 ):
		total = "select count(*) from  drug_units "
		cmd = "select * from  drug_units "
		result = self._do_query(  cmd, start, limit)
		return self.convert_result(result)
	

	def update_drug_units(self, pk_val, map_fields):

		list = []
		for k,v in map_fields:
			if (v.type == 'n'):
				list.append( "set %s = %s" % ( k, v) )
			else:
				list.append( "set %s = '%s'" % ( k, v) )


		s = ",".join(list)	
		cmd = "update  drug_units  %s where  id  = pk_val" % s 

		self._do_update( cmd)
		return ""
	 	

	def delete_drug_units(self, pk_val):
		cmd = 'delete from drug_units where id = pk_val' 
		self._do_update(cmd)
		return ""

	def describe_fields_drug_units(self):
		d =  self.get_description( 'drug_units')
		print "returning ", d
		return d
	

	def get_tables_referenced_by_drug_units(self):
		return analyse_script.get_references_from_statements( drug_units, self._get_statements())
	

	def get_tables_referencing_to_drug_units(self):
		return analyse_script.get_referencing_from_statements(drug_units, self._get_statements())
	
	def create_enum_clinical_encounters  (self,  description ):
		cmd =  """insert into  enum_clinical_encounters (  description ) values ('%s')  """ % ( description )
		self._do_update(cmd)
		return ""



	def select_start_enum_clinical_encounters  (self, field_name, field_value, start = 0, limit = 100 ) :
		cmd = """ 
		select * from  enum_clinical_encounters  where strpos( $s, '$s') == 1 '$  ( field_name, field_value) """
		result = self._do_query( cmd, start, limit)
		return self.convert_result(result)

	def select_by_pk_enum_clinical_encounters( self, pk_val):
		cmd =  'select * from enum_clinical_encounters where id = %s'%(pk_val)

		result = self._do_query(cmd, 0, 'ALL')
		return result
	

	def select_all_enum_clinical_encounters( self, start = 0, limit = 200 ):
		total = "select count(*) from  enum_clinical_encounters "
		cmd = "select * from  enum_clinical_encounters "
		result = self._do_query(  cmd, start, limit)
		return self.convert_result(result)
	

	def update_enum_clinical_encounters(self, pk_val, map_fields):

		list = []
		for k,v in map_fields:
			if (v.type == 'n'):
				list.append( "set %s = %s" % ( k, v) )
			else:
				list.append( "set %s = '%s'" % ( k, v) )


		s = ",".join(list)	
		cmd = "update  enum_clinical_encounters  %s where  id  = pk_val" % s 

		self._do_update( cmd)
		return ""
	 	

	def delete_enum_clinical_encounters(self, pk_val):
		cmd = 'delete from enum_clinical_encounters where id = pk_val' 
		self._do_update(cmd)
		return ""

	def describe_fields_enum_clinical_encounters(self):
		d =  self.get_description( 'enum_clinical_encounters')
		print "returning ", d
		return d
	

	def get_tables_referenced_by_enum_clinical_encounters(self):
		return analyse_script.get_references_from_statements( enum_clinical_encounters, self._get_statements())
	

	def get_tables_referencing_to_enum_clinical_encounters(self):
		return analyse_script.get_referencing_from_statements(enum_clinical_encounters, self._get_statements())
	
	def create_episode  (self,  id_patient,name ):
		cmd =  """insert into  episode (  id_patient,name ) values ('%s', '%s')  """ % ( id_patient,name )
		self._do_update(cmd)
		return ""



	def select_start_episode  (self, field_name, field_value, start = 0, limit = 100 ) :
		cmd = """ 
		select * from  episode  where strpos( $s, '$s') == 1 '$  ( field_name, field_value) """
		result = self._do_query( cmd, start, limit)
		return self.convert_result(result)

	def select_by_pk_episode( self, pk_val):
		cmd =  'select * from episode where id = %s'%(pk_val)

		result = self._do_query(cmd, 0, 'ALL')
		return result
	

	def select_all_episode( self, start = 0, limit = 200 ):
		total = "select count(*) from  episode "
		cmd = "select * from  episode "
		result = self._do_query(  cmd, start, limit)
		return self.convert_result(result)
	

	def update_episode(self, pk_val, map_fields):

		list = []
		for k,v in map_fields:
			if (v.type == 'n'):
				list.append( "set %s = %s" % ( k, v) )
			else:
				list.append( "set %s = '%s'" % ( k, v) )


		s = ",".join(list)	
		cmd = "update  episode  %s where  id  = pk_val" % s 

		self._do_update( cmd)
		return ""
	 	

	def delete_episode(self, pk_val):
		cmd = 'delete from episode where id = pk_val' 
		self._do_update(cmd)
		return ""

	def describe_fields_episode(self):
		d =  self.get_description( 'episode')
		print "returning ", d
		return d
	

	def get_tables_referenced_by_episode(self):
		return analyse_script.get_references_from_statements( episode, self._get_statements())
	

	def get_tables_referencing_to_episode(self):
		return analyse_script.get_referencing_from_statements(episode, self._get_statements())
	
	def create_clinical_transaction  (self,  stamp,duration,id_location,id_provider,id_patient,id_enum_clinical_encounters ):
		cmd =  """insert into  clinical_transaction (  stamp,duration,id_location,id_provider,id_patient,id_enum_clinical_encounters ) values ('%s', '%s', '%s', '%s', '%s', '%s')  """ % ( stamp,duration,id_location,id_provider,id_patient,id_enum_clinical_encounters )
		self._do_update(cmd)
		return ""



	def select_start_clinical_transaction  (self, field_name, field_value, start = 0, limit = 100 ) :
		cmd = """ 
		select * from  clinical_transaction  where strpos( $s, '$s') == 1 '$  ( field_name, field_value) """
		result = self._do_query( cmd, start, limit)
		return self.convert_result(result)

	def select_by_pk_clinical_transaction( self, pk_val):
		cmd =  'select * from clinical_transaction where id = %s'%(pk_val)

		result = self._do_query(cmd, 0, 'ALL')
		return result
	

	def select_all_clinical_transaction( self, start = 0, limit = 200 ):
		total = "select count(*) from  clinical_transaction "
		cmd = "select * from  clinical_transaction "
		result = self._do_query(  cmd, start, limit)
		return self.convert_result(result)
	

	def update_clinical_transaction(self, pk_val, map_fields):

		list = []
		for k,v in map_fields:
			if (v.type == 'n'):
				list.append( "set %s = %s" % ( k, v) )
			else:
				list.append( "set %s = '%s'" % ( k, v) )


		s = ",".join(list)	
		cmd = "update  clinical_transaction  %s where  id  = pk_val" % s 

		self._do_update( cmd)
		return ""
	 	

	def delete_clinical_transaction(self, pk_val):
		cmd = 'delete from clinical_transaction where id = pk_val' 
		self._do_update(cmd)
		return ""

	def describe_fields_clinical_transaction(self):
		d =  self.get_description( 'clinical_transaction')
		print "returning ", d
		return d
	

	def get_tables_referenced_by_clinical_transaction(self):
		return analyse_script.get_references_from_statements( clinical_transaction, self._get_statements())
	

	def get_tables_referencing_to_clinical_transaction(self):
		return analyse_script.get_referencing_from_statements(clinical_transaction, self._get_statements())
	
	def create_script  (self,  id_transaction ):
		cmd =  """insert into  script (  id_transaction ) values ('%s')  """ % ( id_transaction )
		self._do_update(cmd)
		return ""



	def select_start_script  (self, field_name, field_value, start = 0, limit = 100 ) :
		cmd = """ 
		select * from  script  where strpos( $s, '$s') == 1 '$  ( field_name, field_value) """
		result = self._do_query( cmd, start, limit)
		return self.convert_result(result)

	def select_by_pk_script( self, pk_val):
		cmd =  'select * from script where id = %s'%(pk_val)

		result = self._do_query(cmd, 0, 'ALL')
		return result
	

	def select_all_script( self, start = 0, limit = 200 ):
		total = "select count(*) from  script "
		cmd = "select * from  script "
		result = self._do_query(  cmd, start, limit)
		return self.convert_result(result)
	

	def update_script(self, pk_val, map_fields):

		list = []
		for k,v in map_fields:
			if (v.type == 'n'):
				list.append( "set %s = %s" % ( k, v) )
			else:
				list.append( "set %s = '%s'" % ( k, v) )


		s = ",".join(list)	
		cmd = "update  script  %s where  id  = pk_val" % s 

		self._do_update( cmd)
		return ""
	 	

	def delete_script(self, pk_val):
		cmd = 'delete from script where id = pk_val' 
		self._do_update(cmd)
		return ""

	def describe_fields_script(self):
		d =  self.get_description( 'script')
		print "returning ", d
		return d
	

	def get_tables_referenced_by_script(self):
		return analyse_script.get_references_from_statements( script, self._get_statements())
	

	def get_tables_referencing_to_script(self):
		return analyse_script.get_referencing_from_statements(script, self._get_statements())
	
	def create_enum_coding_systems  (self,  description ):
		cmd =  """insert into  enum_coding_systems (  description ) values ('%s')  """ % ( description )
		self._do_update(cmd)
		return ""



	def select_start_enum_coding_systems  (self, field_name, field_value, start = 0, limit = 100 ) :
		cmd = """ 
		select * from  enum_coding_systems  where strpos( $s, '$s') == 1 '$  ( field_name, field_value) """
		result = self._do_query( cmd, start, limit)
		return self.convert_result(result)

	def select_by_pk_enum_coding_systems( self, pk_val):
		cmd =  'select * from enum_coding_systems where id = %s'%(pk_val)

		result = self._do_query(cmd, 0, 'ALL')
		return result
	

	def select_all_enum_coding_systems( self, start = 0, limit = 200 ):
		total = "select count(*) from  enum_coding_systems "
		cmd = "select * from  enum_coding_systems "
		result = self._do_query(  cmd, start, limit)
		return self.convert_result(result)
	

	def update_enum_coding_systems(self, pk_val, map_fields):

		list = []
		for k,v in map_fields:
			if (v.type == 'n'):
				list.append( "set %s = %s" % ( k, v) )
			else:
				list.append( "set %s = '%s'" % ( k, v) )


		s = ",".join(list)	
		cmd = "update  enum_coding_systems  %s where  id  = pk_val" % s 

		self._do_update( cmd)
		return ""
	 	

	def delete_enum_coding_systems(self, pk_val):
		cmd = 'delete from enum_coding_systems where id = pk_val' 
		self._do_update(cmd)
		return ""

	def describe_fields_enum_coding_systems(self):
		d =  self.get_description( 'enum_coding_systems')
		print "returning ", d
		return d
	

	def get_tables_referenced_by_enum_coding_systems(self):
		return analyse_script.get_references_from_statements( enum_coding_systems, self._get_statements())
	

	def get_tables_referencing_to_enum_coding_systems(self):
		return analyse_script.get_referencing_from_statements(enum_coding_systems, self._get_statements())
	
	def create_constituents  (self,  name,dose,dose_unit,id_drug ):
		cmd =  """insert into  constituents (  name,dose,dose_unit,id_drug ) values ('%s', '%s', '%s', '%s')  """ % ( name,dose,dose_unit,id_drug )
		self._do_update(cmd)
		return ""



	def select_start_constituents  (self, field_name, field_value, start = 0, limit = 100 ) :
		cmd = """ 
		select * from  constituents  where strpos( $s, '$s') == 1 '$  ( field_name, field_value) """
		result = self._do_query( cmd, start, limit)
		return self.convert_result(result)

	def select_by_pk_constituents( self, pk_val):
		cmd =  'select * from constituents where id = %s'%(pk_val)

		result = self._do_query(cmd, 0, 'ALL')
		return result
	

	def select_all_constituents( self, start = 0, limit = 200 ):
		total = "select count(*) from  constituents "
		cmd = "select * from  constituents "
		result = self._do_query(  cmd, start, limit)
		return self.convert_result(result)
	

	def update_constituents(self, pk_val, map_fields):

		list = []
		for k,v in map_fields:
			if (v.type == 'n'):
				list.append( "set %s = %s" % ( k, v) )
			else:
				list.append( "set %s = '%s'" % ( k, v) )


		s = ",".join(list)	
		cmd = "update  constituents  %s where  id  = pk_val" % s 

		self._do_update( cmd)
		return ""
	 	

	def delete_constituents(self, pk_val):
		cmd = 'delete from constituents where id = pk_val' 
		self._do_update(cmd)
		return ""

	def describe_fields_constituents(self):
		d =  self.get_description( 'constituents')
		print "returning ", d
		return d
	

	def get_tables_referenced_by_constituents(self):
		return analyse_script.get_references_from_statements( constituents, self._get_statements())
	

	def get_tables_referencing_to_constituents(self):
		return analyse_script.get_referencing_from_statements(constituents, self._get_statements())
	
	def create_link_script_drug  (self,  id_drug,id_script,comment ):
		cmd =  """insert into  link_script_drug (  id_drug,id_script,comment ) values ('%s', '%s', '%s')  """ % ( id_drug,id_script,comment )
		self._do_update(cmd)
		return ""



	def select_start_link_script_drug  (self, field_name, field_value, start = 0, limit = 100 ) :
		cmd = """ 
		select * from  link_script_drug  where strpos( $s, '$s') == 1 '$  ( field_name, field_value) """
		result = self._do_query( cmd, start, limit)
		return self.convert_result(result)

	def select_by_pk_link_script_drug( self, pk_val):
		cmd =  'select * from link_script_drug where None = %s'%(pk_val)

		result = self._do_query(cmd, 0, 'ALL')
		return result
	

	def select_all_link_script_drug( self, start = 0, limit = 200 ):
		total = "select count(*) from  link_script_drug "
		cmd = "select * from  link_script_drug "
		result = self._do_query(  cmd, start, limit)
		return self.convert_result(result)
	

	def update_link_script_drug(self, pk_val, map_fields):

		list = []
		for k,v in map_fields:
			if (v.type == 'n'):
				list.append( "set %s = %s" % ( k, v) )
			else:
				list.append( "set %s = '%s'" % ( k, v) )


		s = ",".join(list)	
		cmd = "update  link_script_drug  %s where  None  = pk_val" % s 

		self._do_update( cmd)
		return ""
	 	

	def delete_link_script_drug(self, pk_val):
		cmd = 'delete from link_script_drug where None = pk_val' 
		self._do_update(cmd)
		return ""

	def describe_fields_link_script_drug(self):
		d =  self.get_description( 'link_script_drug')
		print "returning ", d
		return d
	

	def get_tables_referenced_by_link_script_drug(self):
		return analyse_script.get_references_from_statements( link_script_drug, self._get_statements())
	

	def get_tables_referencing_to_link_script_drug(self):
		return analyse_script.get_referencing_from_statements(link_script_drug, self._get_statements())
	
	def create_enum_immunities  (self,  name ):
		cmd =  """insert into  enum_immunities (  name ) values ('%s')  """ % ( name )
		self._do_update(cmd)
		return ""



	def select_start_enum_immunities  (self, field_name, field_value, start = 0, limit = 100 ) :
		cmd = """ 
		select * from  enum_immunities  where strpos( $s, '$s') == 1 '$  ( field_name, field_value) """
		result = self._do_query( cmd, start, limit)
		return self.convert_result(result)

	def select_by_pk_enum_immunities( self, pk_val):
		cmd =  'select * from enum_immunities where id = %s'%(pk_val)

		result = self._do_query(cmd, 0, 'ALL')
		return result
	

	def select_all_enum_immunities( self, start = 0, limit = 200 ):
		total = "select count(*) from  enum_immunities "
		cmd = "select * from  enum_immunities "
		result = self._do_query(  cmd, start, limit)
		return self.convert_result(result)
	

	def update_enum_immunities(self, pk_val, map_fields):

		list = []
		for k,v in map_fields:
			if (v.type == 'n'):
				list.append( "set %s = %s" % ( k, v) )
			else:
				list.append( "set %s = '%s'" % ( k, v) )


		s = ",".join(list)	
		cmd = "update  enum_immunities  %s where  id  = pk_val" % s 

		self._do_update( cmd)
		return ""
	 	

	def delete_enum_immunities(self, pk_val):
		cmd = 'delete from enum_immunities where id = pk_val' 
		self._do_update(cmd)
		return ""

	def describe_fields_enum_immunities(self):
		d =  self.get_description( 'enum_immunities')
		print "returning ", d
		return d
	

	def get_tables_referenced_by_enum_immunities(self):
		return analyse_script.get_references_from_statements( enum_immunities, self._get_statements())
	

	def get_tables_referencing_to_enum_immunities(self):
		return analyse_script.get_referencing_from_statements(enum_immunities, self._get_statements())
	
	def create_clinical_history  (self,  id_enum_clinical_history,id_clinical_transaction,id_info_sources,text ):
		cmd =  """insert into  clinical_history (  id_enum_clinical_history,id_clinical_transaction,id_info_sources,text ) values ('%s', '%s', '%s', '%s')  """ % ( id_enum_clinical_history,id_clinical_transaction,id_info_sources,text )
		self._do_update(cmd)
		return ""



	def select_start_clinical_history  (self, field_name, field_value, start = 0, limit = 100 ) :
		cmd = """ 
		select * from  clinical_history  where strpos( $s, '$s') == 1 '$  ( field_name, field_value) """
		result = self._do_query( cmd, start, limit)
		return self.convert_result(result)

	def select_by_pk_clinical_history( self, pk_val):
		cmd =  'select * from clinical_history where id = %s'%(pk_val)

		result = self._do_query(cmd, 0, 'ALL')
		return result
	

	def select_all_clinical_history( self, start = 0, limit = 200 ):
		total = "select count(*) from  clinical_history "
		cmd = "select * from  clinical_history "
		result = self._do_query(  cmd, start, limit)
		return self.convert_result(result)
	

	def update_clinical_history(self, pk_val, map_fields):

		list = []
		for k,v in map_fields:
			if (v.type == 'n'):
				list.append( "set %s = %s" % ( k, v) )
			else:
				list.append( "set %s = '%s'" % ( k, v) )


		s = ",".join(list)	
		cmd = "update  clinical_history  %s where  id  = pk_val" % s 

		self._do_update( cmd)
		return ""
	 	

	def delete_clinical_history(self, pk_val):
		cmd = 'delete from clinical_history where id = pk_val' 
		self._do_update(cmd)
		return ""

	def describe_fields_clinical_history(self):
		d =  self.get_description( 'clinical_history')
		print "returning ", d
		return d
	

	def get_tables_referenced_by_clinical_history(self):
		return analyse_script.get_references_from_statements( clinical_history, self._get_statements())
	

	def get_tables_referencing_to_clinical_history(self):
		return analyse_script.get_referencing_from_statements(clinical_history, self._get_statements())
	
	def create_enum_confidentiality_level  (self,  description ):
		cmd =  """insert into  enum_confidentiality_level (  description ) values ('%s')  """ % ( description )
		self._do_update(cmd)
		return ""



	def select_start_enum_confidentiality_level  (self, field_name, field_value, start = 0, limit = 100 ) :
		cmd = """ 
		select * from  enum_confidentiality_level  where strpos( $s, '$s') == 1 '$  ( field_name, field_value) """
		result = self._do_query( cmd, start, limit)
		return self.convert_result(result)

	def select_by_pk_enum_confidentiality_level( self, pk_val):
		cmd =  'select * from enum_confidentiality_level where id = %s'%(pk_val)

		result = self._do_query(cmd, 0, 'ALL')
		return result
	

	def select_all_enum_confidentiality_level( self, start = 0, limit = 200 ):
		total = "select count(*) from  enum_confidentiality_level "
		cmd = "select * from  enum_confidentiality_level "
		result = self._do_query(  cmd, start, limit)
		return self.convert_result(result)
	

	def update_enum_confidentiality_level(self, pk_val, map_fields):

		list = []
		for k,v in map_fields:
			if (v.type == 'n'):
				list.append( "set %s = %s" % ( k, v) )
			else:
				list.append( "set %s = '%s'" % ( k, v) )


		s = ",".join(list)	
		cmd = "update  enum_confidentiality_level  %s where  id  = pk_val" % s 

		self._do_update( cmd)
		return ""
	 	

	def delete_enum_confidentiality_level(self, pk_val):
		cmd = 'delete from enum_confidentiality_level where id = pk_val' 
		self._do_update(cmd)
		return ""

	def describe_fields_enum_confidentiality_level(self):
		d =  self.get_description( 'enum_confidentiality_level')
		print "returning ", d
		return d
	

	def get_tables_referenced_by_enum_confidentiality_level(self):
		return analyse_script.get_references_from_statements( enum_confidentiality_level, self._get_statements())
	

	def get_tables_referencing_to_enum_confidentiality_level(self):
		return analyse_script.get_referencing_from_statements(enum_confidentiality_level, self._get_statements())
	
	def create_clinical_diagnosis_extra  (self,  id_clinical_diagnosis,id_enum_confidentiality_level ):
		cmd =  """insert into  clinical_diagnosis_extra (  id_clinical_diagnosis,id_enum_confidentiality_level ) values ('%s', '%s')  """ % ( id_clinical_diagnosis,id_enum_confidentiality_level )
		self._do_update(cmd)
		return ""



	def select_start_clinical_diagnosis_extra  (self, field_name, field_value, start = 0, limit = 100 ) :
		cmd = """ 
		select * from  clinical_diagnosis_extra  where strpos( $s, '$s') == 1 '$  ( field_name, field_value) """
		result = self._do_query( cmd, start, limit)
		return self.convert_result(result)

	def select_by_pk_clinical_diagnosis_extra( self, pk_val):
		cmd =  'select * from clinical_diagnosis_extra where id = %s'%(pk_val)

		result = self._do_query(cmd, 0, 'ALL')
		return result
	

	def select_all_clinical_diagnosis_extra( self, start = 0, limit = 200 ):
		total = "select count(*) from  clinical_diagnosis_extra "
		cmd = "select * from  clinical_diagnosis_extra "
		result = self._do_query(  cmd, start, limit)
		return self.convert_result(result)
	

	def update_clinical_diagnosis_extra(self, pk_val, map_fields):

		list = []
		for k,v in map_fields:
			if (v.type == 'n'):
				list.append( "set %s = %s" % ( k, v) )
			else:
				list.append( "set %s = '%s'" % ( k, v) )


		s = ",".join(list)	
		cmd = "update  clinical_diagnosis_extra  %s where  id  = pk_val" % s 

		self._do_update( cmd)
		return ""
	 	

	def delete_clinical_diagnosis_extra(self, pk_val):
		cmd = 'delete from clinical_diagnosis_extra where id = pk_val' 
		self._do_update(cmd)
		return ""

	def describe_fields_clinical_diagnosis_extra(self):
		d =  self.get_description( 'clinical_diagnosis_extra')
		print "returning ", d
		return d
	

	def get_tables_referenced_by_clinical_diagnosis_extra(self):
		return analyse_script.get_references_from_statements( clinical_diagnosis_extra, self._get_statements())
	

	def get_tables_referencing_to_clinical_diagnosis_extra(self):
		return analyse_script.get_referencing_from_statements(clinical_diagnosis_extra, self._get_statements())
	
	def create_script_drug  (self,  name,directions,adjuvant,xref_id,source,fluid_amount,amount_unit,amount,id_route,id_form,frequency ):
		cmd =  """insert into  script_drug (  name,directions,adjuvant,xref_id,source,fluid_amount,amount_unit,amount,id_route,id_form,frequency ) values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')  """ % ( name,directions,adjuvant,xref_id,source,fluid_amount,amount_unit,amount,id_route,id_form,frequency )
		self._do_update(cmd)
		return ""



	def select_start_script_drug  (self, field_name, field_value, start = 0, limit = 100 ) :
		cmd = """ 
		select * from  script_drug  where strpos( $s, '$s') == 1 '$  ( field_name, field_value) """
		result = self._do_query( cmd, start, limit)
		return self.convert_result(result)

	def select_by_pk_script_drug( self, pk_val):
		cmd =  'select * from script_drug where id = %s'%(pk_val)

		result = self._do_query(cmd, 0, 'ALL')
		return result
	

	def select_all_script_drug( self, start = 0, limit = 200 ):
		total = "select count(*) from  script_drug "
		cmd = "select * from  script_drug "
		result = self._do_query(  cmd, start, limit)
		return self.convert_result(result)
	

	def update_script_drug(self, pk_val, map_fields):

		list = []
		for k,v in map_fields:
			if (v.type == 'n'):
				list.append( "set %s = %s" % ( k, v) )
			else:
				list.append( "set %s = '%s'" % ( k, v) )


		s = ",".join(list)	
		cmd = "update  script_drug  %s where  id  = pk_val" % s 

		self._do_update( cmd)
		return ""
	 	

	def delete_script_drug(self, pk_val):
		cmd = 'delete from script_drug where id = pk_val' 
		self._do_update(cmd)
		return ""

	def describe_fields_script_drug(self):
		d =  self.get_description( 'script_drug')
		print "returning ", d
		return d
	

	def get_tables_referenced_by_script_drug(self):
		return analyse_script.get_references_from_statements( script_drug, self._get_statements())
	

	def get_tables_referencing_to_script_drug(self):
		return analyse_script.get_referencing_from_statements(script_drug, self._get_statements())
	
	def create_databases  (self,  name,published ):
		cmd =  """insert into  databases (  name,published ) values ('%s', '%s')  """ % ( name,published )
		self._do_update(cmd)
		return ""



	def select_start_databases  (self, field_name, field_value, start = 0, limit = 100 ) :
		cmd = """ 
		select * from  databases  where strpos( $s, '$s') == 1 '$  ( field_name, field_value) """
		result = self._do_query( cmd, start, limit)
		return self.convert_result(result)

	def select_by_pk_databases( self, pk_val):
		cmd =  'select * from databases where id = %s'%(pk_val)

		result = self._do_query(cmd, 0, 'ALL')
		return result
	

	def select_all_databases( self, start = 0, limit = 200 ):
		total = "select count(*) from  databases "
		cmd = "select * from  databases "
		result = self._do_query(  cmd, start, limit)
		return self.convert_result(result)
	

	def update_databases(self, pk_val, map_fields):

		list = []
		for k,v in map_fields:
			if (v.type == 'n'):
				list.append( "set %s = %s" % ( k, v) )
			else:
				list.append( "set %s = '%s'" % ( k, v) )


		s = ",".join(list)	
		cmd = "update  databases  %s where  id  = pk_val" % s 

		self._do_update( cmd)
		return ""
	 	

	def delete_databases(self, pk_val):
		cmd = 'delete from databases where id = pk_val' 
		self._do_update(cmd)
		return ""

	def describe_fields_databases(self):
		d =  self.get_description( 'databases')
		print "returning ", d
		return d
	

	def get_tables_referenced_by_databases(self):
		return analyse_script.get_references_from_statements( databases, self._get_statements())
	

	def get_tables_referencing_to_databases(self):
		return analyse_script.get_referencing_from_statements(databases, self._get_statements())
	
	def create_drug_routes  (self,  description,abbreviation,comment ):
		cmd =  """insert into  drug_routes (  description,abbreviation,comment ) values ('%s', '%s', '%s')  """ % ( description,abbreviation,comment )
		self._do_update(cmd)
		return ""



	def select_start_drug_routes  (self, field_name, field_value, start = 0, limit = 100 ) :
		cmd = """ 
		select * from  drug_routes  where strpos( $s, '$s') == 1 '$  ( field_name, field_value) """
		result = self._do_query( cmd, start, limit)
		return self.convert_result(result)

	def select_by_pk_drug_routes( self, pk_val):
		cmd =  'select * from drug_routes where id = %s'%(pk_val)

		result = self._do_query(cmd, 0, 'ALL')
		return result
	

	def select_all_drug_routes( self, start = 0, limit = 200 ):
		total = "select count(*) from  drug_routes "
		cmd = "select * from  drug_routes "
		result = self._do_query(  cmd, start, limit)
		return self.convert_result(result)
	

	def update_drug_routes(self, pk_val, map_fields):

		list = []
		for k,v in map_fields:
			if (v.type == 'n'):
				list.append( "set %s = %s" % ( k, v) )
			else:
				list.append( "set %s = '%s'" % ( k, v) )


		s = ",".join(list)	
		cmd = "update  drug_routes  %s where  id  = pk_val" % s 

		self._do_update( cmd)
		return ""
	 	

	def delete_drug_routes(self, pk_val):
		cmd = 'delete from drug_routes where id = pk_val' 
		self._do_update(cmd)
		return ""

	def describe_fields_drug_routes(self):
		d =  self.get_description( 'drug_routes')
		print "returning ", d
		return d
	

	def get_tables_referenced_by_drug_routes(self):
		return analyse_script.get_references_from_statements( drug_routes, self._get_statements())
	

	def get_tables_referencing_to_drug_routes(self):
		return analyse_script.get_referencing_from_statements(drug_routes, self._get_statements())
	
	def create_enum_clinical_history  (self,  description ):
		cmd =  """insert into  enum_clinical_history (  description ) values ('%s')  """ % ( description )
		self._do_update(cmd)
		return ""



	def select_start_enum_clinical_history  (self, field_name, field_value, start = 0, limit = 100 ) :
		cmd = """ 
		select * from  enum_clinical_history  where strpos( $s, '$s') == 1 '$  ( field_name, field_value) """
		result = self._do_query( cmd, start, limit)
		return self.convert_result(result)

	def select_by_pk_enum_clinical_history( self, pk_val):
		cmd =  'select * from enum_clinical_history where id = %s'%(pk_val)

		result = self._do_query(cmd, 0, 'ALL')
		return result
	

	def select_all_enum_clinical_history( self, start = 0, limit = 200 ):
		total = "select count(*) from  enum_clinical_history "
		cmd = "select * from  enum_clinical_history "
		result = self._do_query(  cmd, start, limit)
		return self.convert_result(result)
	

	def update_enum_clinical_history(self, pk_val, map_fields):

		list = []
		for k,v in map_fields:
			if (v.type == 'n'):
				list.append( "set %s = %s" % ( k, v) )
			else:
				list.append( "set %s = '%s'" % ( k, v) )


		s = ",".join(list)	
		cmd = "update  enum_clinical_history  %s where  id  = pk_val" % s 

		self._do_update( cmd)
		return ""
	 	

	def delete_enum_clinical_history(self, pk_val):
		cmd = 'delete from enum_clinical_history where id = pk_val' 
		self._do_update(cmd)
		return ""

	def describe_fields_enum_clinical_history(self):
		d =  self.get_description( 'enum_clinical_history')
		print "returning ", d
		return d
	

	def get_tables_referenced_by_enum_clinical_history(self):
		return analyse_script.get_references_from_statements( enum_clinical_history, self._get_statements())
	

	def get_tables_referencing_to_enum_clinical_history(self):
		return analyse_script.get_referencing_from_statements(enum_clinical_history, self._get_statements())
	
	def create_clinical_diagnosis  (self,  id_clinical_transaction,approximate_start,id_coding_systems,text ):
		cmd =  """insert into  clinical_diagnosis (  id_clinical_transaction,approximate_start,id_coding_systems,text ) values ('%s', '%s', '%s', '%s')  """ % ( id_clinical_transaction,approximate_start,id_coding_systems,text )
		self._do_update(cmd)
		return ""



	def select_start_clinical_diagnosis  (self, field_name, field_value, start = 0, limit = 100 ) :
		cmd = """ 
		select * from  clinical_diagnosis  where strpos( $s, '$s') == 1 '$  ( field_name, field_value) """
		result = self._do_query( cmd, start, limit)
		return self.convert_result(result)

	def select_by_pk_clinical_diagnosis( self, pk_val):
		cmd =  'select * from clinical_diagnosis where id = %s'%(pk_val)

		result = self._do_query(cmd, 0, 'ALL')
		return result
	

	def select_all_clinical_diagnosis( self, start = 0, limit = 200 ):
		total = "select count(*) from  clinical_diagnosis "
		cmd = "select * from  clinical_diagnosis "
		result = self._do_query(  cmd, start, limit)
		return self.convert_result(result)
	

	def update_clinical_diagnosis(self, pk_val, map_fields):

		list = []
		for k,v in map_fields:
			if (v.type == 'n'):
				list.append( "set %s = %s" % ( k, v) )
			else:
				list.append( "set %s = '%s'" % ( k, v) )


		s = ",".join(list)	
		cmd = "update  clinical_diagnosis  %s where  id  = pk_val" % s 

		self._do_update( cmd)
		return ""
	 	

	def delete_clinical_diagnosis(self, pk_val):
		cmd = 'delete from clinical_diagnosis where id = pk_val' 
		self._do_update(cmd)
		return ""

	def describe_fields_clinical_diagnosis(self):
		d =  self.get_description( 'clinical_diagnosis')
		print "returning ", d
		return d
	

	def get_tables_referenced_by_clinical_diagnosis(self):
		return analyse_script.get_references_from_statements( clinical_diagnosis, self._get_statements())
	

	def get_tables_referencing_to_clinical_diagnosis(self):
		return analyse_script.get_referencing_from_statements(clinical_diagnosis, self._get_statements())
	
	def create_drug_formulations  (self,  description,comment ):
		cmd =  """insert into  drug_formulations (  description,comment ) values ('%s', '%s')  """ % ( description,comment )
		self._do_update(cmd)
		return ""



	def select_start_drug_formulations  (self, field_name, field_value, start = 0, limit = 100 ) :
		cmd = """ 
		select * from  drug_formulations  where strpos( $s, '$s') == 1 '$  ( field_name, field_value) """
		result = self._do_query( cmd, start, limit)
		return self.convert_result(result)

	def select_by_pk_drug_formulations( self, pk_val):
		cmd =  'select * from drug_formulations where id = %s'%(pk_val)

		result = self._do_query(cmd, 0, 'ALL')
		return result
	

	def select_all_drug_formulations( self, start = 0, limit = 200 ):
		total = "select count(*) from  drug_formulations "
		cmd = "select * from  drug_formulations "
		result = self._do_query(  cmd, start, limit)
		return self.convert_result(result)
	

	def update_drug_formulations(self, pk_val, map_fields):

		list = []
		for k,v in map_fields:
			if (v.type == 'n'):
				list.append( "set %s = %s" % ( k, v) )
			else:
				list.append( "set %s = '%s'" % ( k, v) )


		s = ",".join(list)	
		cmd = "update  drug_formulations  %s where  id  = pk_val" % s 

		self._do_update( cmd)
		return ""
	 	

	def delete_drug_formulations(self, pk_val):
		cmd = 'delete from drug_formulations where id = pk_val' 
		self._do_update(cmd)
		return ""

	def describe_fields_drug_formulations(self):
		d =  self.get_description( 'drug_formulations')
		print "returning ", d
		return d
	

	def get_tables_referenced_by_drug_formulations(self):
		return analyse_script.get_references_from_statements( drug_formulations, self._get_statements())
	

	def get_tables_referencing_to_drug_formulations(self):
		return analyse_script.get_referencing_from_statements(drug_formulations, self._get_statements())
	
	def create_enum_info_sources  (self,  description ):
		cmd =  """insert into  enum_info_sources (  description ) values ('%s')  """ % ( description )
		self._do_update(cmd)
		return ""



	def select_start_enum_info_sources  (self, field_name, field_value, start = 0, limit = 100 ) :
		cmd = """ 
		select * from  enum_info_sources  where strpos( $s, '$s') == 1 '$  ( field_name, field_value) """
		result = self._do_query( cmd, start, limit)
		return self.convert_result(result)

	def select_by_pk_enum_info_sources( self, pk_val):
		cmd =  'select * from enum_info_sources where id = %s'%(pk_val)

		result = self._do_query(cmd, 0, 'ALL')
		return result
	

	def select_all_enum_info_sources( self, start = 0, limit = 200 ):
		total = "select count(*) from  enum_info_sources "
		cmd = "select * from  enum_info_sources "
		result = self._do_query(  cmd, start, limit)
		return self.convert_result(result)
	

	def update_enum_info_sources(self, pk_val, map_fields):

		list = []
		for k,v in map_fields:
			if (v.type == 'n'):
				list.append( "set %s = %s" % ( k, v) )
			else:
				list.append( "set %s = '%s'" % ( k, v) )


		s = ",".join(list)	
		cmd = "update  enum_info_sources  %s where  id  = pk_val" % s 

		self._do_update( cmd)
		return ""
	 	

	def delete_enum_info_sources(self, pk_val):
		cmd = 'delete from enum_info_sources where id = pk_val' 
		self._do_update(cmd)
		return ""

	def describe_fields_enum_info_sources(self):
		d =  self.get_description( 'enum_info_sources')
		print "returning ", d
		return d
	

	def get_tables_referenced_by_enum_info_sources(self):
		return analyse_script.get_references_from_statements( enum_info_sources, self._get_statements())
	

	def get_tables_referencing_to_enum_info_sources(self):
		return analyse_script.get_referencing_from_statements(enum_info_sources, self._get_statements())
	
	def create_coding_systems  (self,  id_enum_coding_systems,description,deprecated ):
		cmd =  """insert into  coding_systems (  id_enum_coding_systems,description,deprecated ) values ('%s', '%s', '%s')  """ % ( id_enum_coding_systems,description,deprecated )
		self._do_update(cmd)
		return ""



	def select_start_coding_systems  (self, field_name, field_value, start = 0, limit = 100 ) :
		cmd = """ 
		select * from  coding_systems  where strpos( $s, '$s') == 1 '$  ( field_name, field_value) """
		result = self._do_query( cmd, start, limit)
		return self.convert_result(result)

	def select_by_pk_coding_systems( self, pk_val):
		cmd =  'select * from coding_systems where id = %s'%(pk_val)

		result = self._do_query(cmd, 0, 'ALL')
		return result
	

	def select_all_coding_systems( self, start = 0, limit = 200 ):
		total = "select count(*) from  coding_systems "
		cmd = "select * from  coding_systems "
		result = self._do_query(  cmd, start, limit)
		return self.convert_result(result)
	

	def update_coding_systems(self, pk_val, map_fields):

		list = []
		for k,v in map_fields:
			if (v.type == 'n'):
				list.append( "set %s = %s" % ( k, v) )
			else:
				list.append( "set %s = '%s'" % ( k, v) )


		s = ",".join(list)	
		cmd = "update  coding_systems  %s where  id  = pk_val" % s 

		self._do_update( cmd)
		return ""
	 	

	def delete_coding_systems(self, pk_val):
		cmd = 'delete from coding_systems where id = pk_val' 
		self._do_update(cmd)
		return ""

	def describe_fields_coding_systems(self):
		d =  self.get_description( 'coding_systems')
		print "returning ", d
		return d
	

	def get_tables_referenced_by_coding_systems(self):
		return analyse_script.get_references_from_statements( coding_systems, self._get_statements())
	

	def get_tables_referencing_to_coding_systems(self):
		return analyse_script.get_referencing_from_statements(coding_systems, self._get_statements())
	
server = SimpleXMLRPCServer( ('localhost' , 9000))
impl = simple_tables_server( '::gnumed')
server.register_instance(impl)
server.serve_forever()
#


#dependencies = 
# [['clinical_transaction', 'enum_clinical_encounters'], ['clinical_history', 'enum_clinical_history'], ['clinical_history', 'clinical_transaction'], ['clinical_history', 'enum_info_sources'], ['coding_systems', 'enum_coding_systems'], ['diagnosis_code_text', 'coding_systems'], ['clinical_diagnosis', 'clinical_transaction'], ['clinical_diagnosis', 'coding_systems'], ['clinical_diagnosis', 'diagnosis_code_text'], ['clinical_diagnosis_extra', 'clinical_diagnosis'], ['clinical_diagnosis_extra', 'enum_confidentiality_level'], ['script_drug', 'databases'], ['script_drug', 'drug_units'], ['script_drug', 'drug_routes'], ['script_drug', 'drug_formulations'], ['constituents', 'drug_units'], ['constituents', 'script_drug'], ['script', 'clinical_transaction'], ['link_script_drug', 'script_drug'], ['link_script_drug', 'script']]


#These tables have no complex dependencies:
# ['clinical_transaction', 'coding_systems', 'databases', 'drug_units', 'drug_routes', 'drug_formulations']
#  drug_units  has  2 dependants, which are ['script_drug', 'constituents']
#  clinical_transaction  has  3 dependants, which are ['clinical_history', 'clinical_diagnosis', 'script']
#  databases  has  1 dependants, which are ['script_drug']
#  drug_routes  has  1 dependants, which are ['script_drug']
#  coding_systems  has  2 dependants, which are ['diagnosis_code_text', 'clinical_diagnosis']
#  drug_formulations  has  1 dependants, which are ['script_drug']
#sorted =  [('clinical_transaction', ['clinical_history', 'clinical_diagnosis', 'script']), ('drug_units', ['script_drug', 'constituents']), ('script_drug', ['constituents', 'link_script_drug']), ('coding_systems', ['diagnosis_code_text', 'clinical_diagnosis']), ('enum_clinical_encounters', ['clinical_transaction']), ('script', ['link_script_drug']), ('enum_coding_systems', ['coding_systems']), ('databases', ['script_drug']), ('clinical_diagnosis', ['clinical_diagnosis_extra']), ('enum_confidentiality_level', ['clinical_diagnosis_extra']), ('drug_routes', ['script_drug']), ('enum_clinical_history', ['clinical_history']), ('diagnosis_code_text', ['clinical_diagnosis']), ('drug_formulations', ['script_drug']), ('enum_info_sources', ['clinical_history'])]
order =  ['clinical_transaction', 'clinical_diagnosis', 'script', 'drug_units', 'script_drug', 'script_drug', 'coding_systems', 'diagnosis_code_text', 'enum_clinical_encounters', 'script', 'enum_coding_systems', 'databases', 'clinical_diagnosis', 'enum_confidentiality_level', 'drug_routes', 'enum_clinical_history', 'diagnosis_code_text', 'drug_formulations', 'enum_info_sources']


#table  clinical_transaction  is referenced by:
#	0 : clinical_history
#	1 : clinical_diagnosis
#	2 : script


#Enter the list of indexes of tables (separaeted by space) which are being contained in the UI of clinical_transaction :
