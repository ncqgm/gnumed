-- =============================================
-- GNUmed - static tables for the provider inbox
-- =============================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmProviderInbox-static.sql,v $
-- $Id: gmProviderInbox-static.sql,v 1.2 2006-01-09 13:44:02 ncq Exp $
-- license: GPL
-- author: Karsten.Hilbert@gmx.net

-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ---------------------------------------------
create table dem.inbox_item_category (
	pk serial primary key,
	description text
		unique
		not null
		check (trim(coalesce(description, 'xxxDEFAULTxxx')) != ''),
	is_user boolean
		not null
		default true
) inherits (audit.audit_fields);

select audit.add_table_for_audit('dem', 'inbox_item_category');

-- ---------------------------------------------
create table dem.inbox_item_type (
	pk serial primary key,
	fk_inbox_item_category integer
		not null
		references dem.inbox_item_category(pk),
	description text
		unique
		not null
		check (trim(coalesce(description, 'xxxDEFAULTxxx')) != ''),
	is_user boolean
		not null
		default true
) inherits (audit.audit_fields);

select audit.add_table_for_audit('dem', 'inbox_item_type');

-- ---------------------------------------------
create table dem.provider_inbox (
	pk serial primary key,
	fk_staff integer
		not null
		references dem.staff(pk),
	fk_inbox_item_type integer
		not null
		references dem.inbox_item_type(pk),
	comment text
		default null
		check (trim(coalesce(comment, 'xxxDEFAULTxxx')) != ''),
	ufk_context integer,
	importance smallint
		check (importance=-1 or importance=0 or importance=1),
	unique(fk_staff, fk_inbox_item_type, ufk_context)
) inherits (audit.audit_fields);

select audit.add_table_for_audit('dem', 'provider_inbox');

-- =============================================
-- do simple schema revision tracking
select log_script_insertion('$RCSfile: gmProviderInbox-static.sql,v $2', '$Revision: 1.2 $');

-- =============================================
-- $Log: gmProviderInbox-static.sql,v $
-- Revision 1.2  2006-01-09 13:44:02  ncq
-- - add inbox item type category and adjust view
--
-- Revision 1.1  2006/01/07 15:22:23  ncq
-- - initial attempt at provider inbox tables
--
