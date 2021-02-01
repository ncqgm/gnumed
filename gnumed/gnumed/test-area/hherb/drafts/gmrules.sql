-- project: GNUMed
-- database: GNUMed
-- purpose:  event recall system
-- author: ihaywood
-- copyright: (C) Ian Haywood 2003
-- license: GPL v2 or later (details at http://gnu.org)

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/hherb/drafts/gmrules.sql,v $
-- $Id: gmrules.sql,v 1.1 2004-02-02 17:17:31 ncq Exp $
-- $Revision: 1.1 $ $Date: 2004-02-02 17:17:31 $ $Author: ncq $
--
-- =============================================
-- $Log: gmrules.sql,v $
-- Revision 1.1  2004-02-02 17:17:31  ncq
-- - moved here
--
-- Revision 1.1  2003/01/11 08:26:43  ihaywood
-- New file gmrules.sql
--
--
-- =============================================
-- DEPENDENCIES:
-- 1/ plpython
-- 2/ dblink () if you want distributed db
-- WARNING: totally untested. I *guarantee* you this will throw an error 
-- if you try to use it.

-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

create table rules
(
	id serial,
	title varchar (100),
	rule text
);

comment on table rules is
'database of python rules';

comment on column rules.rule is
'the Python code snippet implementing the rule.';

create table idx_rule_drug
(
	drug varchar (100),
	id_rule integer references rules (id)
);

create table idx_rule_disease
(
	disease varchar (100),
	id_rule integer references rules (id)
);

create table idx_rule_keyword
(
	keyword varchar (100),
	id_rule integer references rules (id)
);

create table idx_rule_recall
(
	id_rule integer references rules (id)
);

comment on table idx_rule_recall is '
a list of rules calling recall (): i.e a list of rules
suitable from running from a nightly cron task';

create function exec (text, integer) returns opaque as 
'
__rule = args[0]
patient_id = args[1]

# convience functions for the snippet
# (theoretically, the snippets can plpy.execute () directly, but
# this is a Bad Idea)

def query (service, str):
 """
 perform a query, using dblink ()mas appropriate
 """
 res = plpy.execute ("select conn from remote_dbs where service=''%s''" % service)
 if len (res) > 0:
  conn = res[0][0]
  res = plpy.execute ("select dblink_tok (dblink (''%s'', ''%s''), 0)" % (conn, str))
 else:
  res = plpy.execute (str)[0][0]
if len (res) == 0:
 return None
else:
 # unpack arrays for the 90% condition where we fetch one value only
 if len (res) == 1:
  res = res[0]
 if len (res) == 1:
  res = res[0]
 return res


def age ():
 """
 Return patient age, in integer years.
 FIXME: return as a float
 """
 return int (query ("demographica", "select extract (year from age (dob)) from identity where id = %s" % patient_id))

def gender ():
 """
 Return patient gender.
 From the identity.sql comments:(m)ale, (f)emale, (h)ermaphrodite, (tm)transsexual phaenotype male, (tf)transsexual phaenotype female, (?)unknown
 """ 
 return query ("demographica", "select gender from identity where id = %s" % patient_id)

def prescribed (drug):
 """
 Returns true if drug X prescribed
 """
 return 0 # no tables in gmclinical to express this

def tested (text):
 """
 Returns the length of time since the last time the patient had X tested
 """
 return 0 # again, blocked on gmclinical.sql

def diagnosed (disease):
 """
 Returns true if the disease word is found in the patient's list
 of diagnoses
 """
 return 0

def keyword (text):
 """
 Returns true if a particular word occurs in the clinical narrative of
 this consultation
 """
 return 0

def notify (text, urgency=1, path=""):
 """
 Send a message to the client for display.
 Urgency is a number 0..9 which controls how
 the client displays the message. Transmitted
 as the first character of the NOTIFY string.
 The message ends with a pipe (|), optionally then
 a URL follows. If the user clicks of the message
 they pass to the guidelines/drug reference browser 
 pointing to that path Thus rules may suggest a guideline
 or drug reference to explain themselves.
 FIXME: can pyPgSQL receive SQL NOTIFY messages??
 """
 plpy.notice (str (urgency) + text + "|" + url)

def recall (what, time = "0 second"):
 """
 insert an entry into the recall database. Time must be a string 
 that parses as a SQL INTERVAL type. This is quite easy. "2 weeks"
 "5 months", etc. are all acceptable.
 """
 # FIXME: more fields need to be set here, Horst, please comment.
 query ("recalls", "insert into recall (due, id_patient, reason) values (now () + interval ''%s'', %d, ''%s'')" % (time, patient_id, what))

# execute the rule
exec (__rule)

return None
' language 'plpython';

create function exec_all () returns opaque as
-- a trigger function.
-- this function must be attached to tables with a 
-- column "patient_id", on insert or update.
-- It will execute all the rules
-- for this patient
-- FIXME: optimise by rule-selection depending on the 
-- table. For example prescribing table: only execute
-- rules referring to those drugs
'
BEGIN
 SELECT exec (rule, NEW.patient_id) FROM rules;
END;' language 'plpgsql';

create function trig_rule () returns opaque as
'
from string import *

# trigger function for new rules.
# Rules API is re-implemented, but this time, 
# functions insert the rule into the appropriate index

def keyword (text):
 plpy.execute ("insert into idx_rule_keyword (keyword, id_rule) values (''%s'',%s)" % (text, TD["new"]["id"]))
 return 1

def prescribed (drug):
 plpy.execute ("insert into idx_rule_drug (drug, id_rule) values (''%s'', %s)" % (drug, TD["new"]["id"]))
 return 1

def diagnosed (disease):
 plpy.execute ("insert into idx_rule_disease (disease, id_rule) values (''%s'', %s)" % (disease, TD["new"]["id"]))
 return 1

def recall (what, time):
 pass

def notify (text, urgency = 0, path = ""):
 pass

def age ():
 return 1

def gender ():
 return "f"

def tested (test):
 return 1

if TD["event"] == "UPDATE" or TD["event"] == "DELETE":
 plpy.execute ("delete from idx_rule_drug where id_rule = %s" % TD["old"]["id"])
 plpy.execute ("delete from idx_rule_disease where id_rule = %s" % TD["old"]["id"])
 plpy.execute ("delete from idx_rule_recall where id_rule = %s" % TD["old"]["id"])
 plpy.execute ("delete from idx_rule_keyword where id_rule = %s" % TD["old"]["id"])

if (TD["event"] == "UPDATE" or TD["event"] == "INSERT":
 exec (TD["new"]["rule"]) # insert for functions defined above
 # as we can't guarantee recall () will be called, just search for the name
 if find (TD["new"]["rule"], "recall") > -1: 
  plpy.execute ("insert into idx_rule_recall (id_rule) values (%s)" % TD["new"]["id"])

return None
' language 'plpython';

insert into rules (title, rule) values ('pap smear check', '
if gender () == "f" and age () > 16 and age () < 70 and (tested ("pap smear") > 750 or not tested ("pap smear")):
 recall ("Pap smear due")
');

create trigger t_trig_rule on rules before update, insert, delete for each row
call procedure trig_rule ();
   
 
-- do simple schema revision tracking
\i gmSchemaRevision.sql
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmrules.sql,v $', '$Revision: 1.1 $');


