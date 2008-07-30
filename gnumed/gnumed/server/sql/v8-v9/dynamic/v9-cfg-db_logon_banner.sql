-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- $Id: v9-cfg-db_logon_banner.sql,v 1.1 2008-07-30 22:03:10 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
set default_transaction_read_only to off;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
delete from cfg.db_logon_banner;
insert into cfg.db_logon_banner (message) values (
i18n.i18n('Welcome to the USS Enterprise Medical Department GNUmed database.

This database is the default installation intended for demonstration of the GNUmed client. It may be running on a publicly accessible server on the internet. Therefore any data you enter here is likely to be lost when the database is upgraded. It is also put at risk of unlawful disclosure.

DO NOT USE THIS DATABASE TO STORE REAL LIVE PATIENT DATA.


Starfleet Central Medical Facilities

Uncle Pavel Wants You!    Sign up for Starfleet Now!
http://wiki.gnumed.de/bin/view/Gnumed/GettingStarted'
));

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v9-cfg-db_logon_banner.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v9-cfg-db_logon_banner.sql,v $
-- Revision 1.1  2008-07-30 22:03:10  ncq
-- - new default logon banner
--
--
