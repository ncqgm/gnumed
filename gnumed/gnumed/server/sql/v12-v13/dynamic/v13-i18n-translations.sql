-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v13-i18n-translations.sql,v 1.1 2010-02-02 13:40:08 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
-- Dutch geography
select i18n.upd_tx('nl_NL', 'Netherlands', 'Nederland');

select i18n.upd_tx('nl_NL', 'state/territory/province/region not available', 'staat/provincie/regio/gemeente niet beschikbaar');
select i18n.upd_tx('nl_NL', 'Friesland', 'Fryslân');

-- Antillen
select i18n.upd_tx('nl_NL', 'Netherlands Antilles', 'Nederlandse Antillen');
select i18n.upd_tx('pap_AN', 'Netherlands Antilles', 'Antias Hulandes');

delete from dem.state where country = 'AN';

insert into dem.state (code, country, name) values ('Bo', 'AN', i18n.i18n('Bonaire'));
insert into dem.state (code, country, name) values ('kBo', 'AN', i18n.i18n('Klein Bonaire'));
insert into dem.state (code, country, name) values ('SE', 'AN', i18n.i18n('Sint-Eustatius'));
insert into dem.state (code, country, name) values ('Sa', 'AN', i18n.i18n('Saba'));
insert into dem.state (code, country, name) values ('Cç', 'AN', i18n.i18n('Curaçao'));
insert into dem.state (code, country, name) values ('kCç', 'AN', i18n.i18n('Klein Curaçao'));
insert into dem.state (code, country, name) values ('SM', 'AN', i18n.i18n('Sint Maarten'));
insert into dem.state (code, country, name) values ('GI', 'AN', i18n.i18n('Green Island'));
insert into dem.state (code, country, name) values ('GK', 'AN', i18n.i18n('Guana Key'));
insert into dem.state (code, country, name) values ('HC', 'AN', i18n.i18n('Hen & Chickens'));
insert into dem.state (code, country, name) values ('CC', 'AN', i18n.i18n('Cow & Calff'));
insert into dem.state (code, country, name) values ('MB', 'AN', i18n.i18n('Molly Beday'));
insert into dem.state (code, country, name) values ('PK', 'AN', i18n.i18n('Pelikan Key'));

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v13-i18n-translations.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v13-i18n-translations.sql,v $
-- Revision 1.1  2010-02-02 13:40:08  ncq
-- - add Dutch thanks to John Jaarsve
--
--