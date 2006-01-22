-- ============================================
-- GNUmed - initial data for the provider inbox
-- ============================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmProviderInbox-data.sql,v $
-- $Id: gmProviderInbox-data.sql,v 1.1 2006-01-22 18:11:42 ncq Exp $
-- license: GPL
-- author: Karsten.Hilbert@gmx.net

-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- dem.inbox_item_category --
insert into dem.inbox_item_category (description, is_user) values (
	i18n.i18n('clinical'), False);
insert into dem.inbox_item_category (description, is_user) values (
	i18n.i18n('personal'), False);
insert into dem.inbox_item_category (description, is_user) values (
	i18n.i18n('administrative'), False);

-- dem.inbox_item_type --
insert into dem.inbox_item_type
	(fk_inbox_item_category, description, is_user)
values (
	(select pk from dem.inbox_item_category where description = 'clinical'),
	i18n.i18n('review lab'),
	False
);

insert into dem.inbox_item_type
	(fk_inbox_item_category, description, is_user)
values (
	(select pk from dem.inbox_item_category where description = 'clinical'),
	i18n.i18n('review docs'),
	False
);

-- =============================================
-- do simple schema revision tracking
select log_script_insertion('$RCSfile: gmProviderInbox-data.sql,v $2', '$Revision: 1.1 $');

-- =============================================
-- $Log: gmProviderInbox-data.sql,v $
-- Revision 1.1  2006-01-22 18:11:42  ncq
-- - add some essential data such as types/categories
--
--
