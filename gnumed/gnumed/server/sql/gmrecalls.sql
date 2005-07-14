-- project: GNUMed
-- database: GNUMed
-- purpose:  event recall system
-- author: hherb
-- copyright: Dr. Horst Herb, horst@hherb.com
-- license: GPL (details at http://gnu.org)

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmrecalls.sql,v $
-- $Id: gmrecalls.sql,v 1.4 2005-07-14 21:31:42 ncq Exp $
-- $Revision: 1.4 $ $Date: 2005-07-14 21:31:42 $ $Author: ncq $
--
-- =============================================
-- $Log: gmrecalls.sql,v $
-- Revision 1.4  2005-07-14 21:31:42  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.3  2005/03/01 20:38:19  ncq
-- - varchar -> text
--
-- Revision 1.2  2004/03/18 09:44:31  ncq
-- - removed spurious \i
--
-- Revision 1.1  2003/01/09 14:53:33  hherb
-- first draft
--
-- =============================================

-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

create table recall_identity (
	id serial primary key,
	identity_external integer,
	URL text
);

comment on table recall_identity is
'lookup table tranlating an external identity into an internal one, allowing recalls to reside within its own database';
comment on column recall_identity.identity_external is
'mapped identity id, sort of a foreign key, but no referential integrity checking yet';
comment on column recall_identity.URL is
'DSN like string in the form of "host:port:database:user:password:table:column" where either parameter between colons may reamin empty';


create table audit_recall (
	id serial primary key
);

comment on table audit_recall is
'allows automatic creation of an audit trail for all children of this table';


create table signed_recall (
	signed_by integer references recall_identity(id) default Null,
	signature text default Null,
	signed_columns integer[] default Null
);

comment on table signed_recall is
'tables deriving from this one feature optional digital signatures for row contents';
comment on column signed_recall.signed_by is
'person or entity signing (part of) this record';
comment on column signed_recall.signature is
'ASCII armoured OpenPGP compliant digital signature';
comment on column signed_recall.signed_columns is
'columns that have been signed, listed in correct order';


create table recall_flags (
	id serial primary key,
	description text,
	icon bytea
);

comment on table recall_flags is
'arbitray categories of recalls';
comment on column recall_flags.icon is
'icon for this flag in XPM fomat if applicable';


create table recall (
	id serial primary key,
	done boolean default 'f',
	id_patient integer references recall_identity(id) default NULL,
	id_responsible integer references recall_identity(id),
	importance integer,
	flag integer references recall_flags(id),
	created timestamp default now(),
	duestring text,
	due timestamp,
	reason text,
	comment text,
	recorded_by text default CURRENT_USER
) inherits (audit_recall, signed_recall);

comment on table recall is
'individual recall event';
comment on column recall.done is
'true if this recall has been dealt with finality';
comment on column recall.id_patient is
'if this recall refers to a person/identity, this should be not Null. May be Null for non-person-related event reminders';
comment on column recall.id_responsible is
'the person who is responsible for this recall';
comment on column recall.importance is
'importance of this recall on an arbitray scale 1-255, 1 having the highest priority ("vital")';
comment on column recall.flag is
'arbitrary category this recall belongs to';
comment on column recall.created is
'when this recall was created';
comment on column recall.duestring is
'text that was entered at creation of this recall (subsequently parsed and interpreted into a concrete date and time)';
comment on column recall.due is
'date and time when this recall falls due';
comment on column recall.reason is
'reason for this recall';
comment on column recall.recorded_by is
'logged-in user who recorded this recall';




create table action_types (
	id serial primary key,
	description text,
	command text
);

comment on table action_types is
'all the things we can or should do when we need to be reminded of a recall event';
comment on column action_types.command is
'optional command string that is passed to the shell / command line interpreter after parameter substitution. Parameters are prepended with an "@"';


-- non-intrusive on-screen reminder
insert into action_types (description) values ('display');
-- on-screen equivalent of getting your wrists slapped
insert into action_types (description) values ('popup');
-- ring them
insert into action_types (description) values ('phone');
-- use last centuries technology
insert into action_types (description) values ('fax');
-- personal contact: talk to them
insert into action_types (description) values ('talk');
-- send an email. How would one do this on crippled platform like Windows?
insert into action_types (description, command) values ('mail (Unix)', 'mail -s @subject @recipient < @filename');
-- print the reminder and send by snail mail
insert into action_types (description, command) values ('print (PDF Unix)', 'cat @filename | acroread -toPostscript | lp');


create table action_on_recall_due (
	id serial primary key,
	id_recall integer references recall(id),
	due timestamp NOT NULL,
	action_type integer references action_types(id),
	action_param text
) inherits (audit_recall);

comment on table action_on_recall_due is
'what to do and how to do it when a specific recall is due';
comment on column action_on_recall_due.due is
'when this action should be triggered';
comment on column action_on_recall_due.action_type is
'what to do when a recall is due';
comment on column action_on_recall_due.action_param is
'parameter list for the action taken in XML format: <param_name> parameters </param_name> ...';


create table recall_managed (
	id_recall integer references recall,
	finalized boolean default 'f',
	done_when timestamp,
	done_by integer references recall_identity(id) default NULL,
	done_what integer references action_on_recall_due(id),
	recorded_when timestamp default now(),
	recorded_by text default current_user,
	comment text
) inherits (audit_recall, signed_recall);


comment on table recall_managed is
'when anything has been done in relationship to a recall, it is recorded here';
comment on column recall_managed.finalized is
'only true if this recall requires no further action';
comment on column recall_managed.done_when is
'when this action has been taken (and not when it has been recorded)';
comment on column recall_managed.done_by is
'who undertook this action. If not recorded as identity, see comment as to who done it';
comment on column recall_managed.done_what is
'what has actually been done (letter sent, phoned, ...)';
comment on column recall_managed.recorded_when is
'when this action has been recorded';
comment on column recall_managed.recorded_by is
'who recorded this action';

-- TO DO: trigger that updates recall.done if recall_managed.finalized is true


-- do simple schema revision tracking
INSERT INTO gm_schema_revision (filename, version, is_core) VALUES('$RCSfile: gmrecalls.sql,v $', '$Revision: 1.4 $', True);
