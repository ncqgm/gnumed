-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- What it does:
-- - upgrade cfg.cfg_item
--
-- License: GPL v2 or later
-- Author: 
-- 
-- ==============================================================
-- $Id: cfg-cfg_item.sql,v 1.4 2006-12-29 11:33:19 ncq Exp $
-- $Revision: 1.4 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table cfg.cfg_item
	alter column workplace
		drop not null;

alter table cfg.cfg_item
	alter column workplace
		set default null;


alter table cfg.cfg_item
	alter column cookie
		drop not null;

alter table cfg.cfg_item
	alter column cookie
		set default null;

alter table cfg.cfg_item
	drop constraint if exists "$1";
alter table cfg.cfg_item
	drop constraint if exists "cfg_item_fk_template_fkey";

alter table cfg.cfg_item
	add foreign key (fk_template)
		references cfg.cfg_template(pk)
		on update cascade
		on delete cascade;

-- --------------------------------------------------------------
-- a 'workplace' called "Release 0.2.3"
insert into cfg.cfg_item
	(fk_template, owner, workplace)
values (
	(select pk from cfg.cfg_template where name='horstspace.notebook.plugin_load_order' and type='str_array'),
	'xxxDEFAULTxxx',
	'Release 0.2.3'
);

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: cfg-cfg_item.sql,v $', '$Revision: 1.4 $');
