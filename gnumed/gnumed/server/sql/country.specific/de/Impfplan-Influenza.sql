-- Projekt GnuMed
-- Impfkalender der Hersteller von Influenza-Impfstoff

-- Quellen: Beipackzettel

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/de/Impfplan-Influenza.sql,v $
-- $Revision: 1.8 $
-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- Impfplan erstellen
insert into clin.vacc_regime
	(fk_recommended_by, fk_indication, name)
values (
	-1,
	(select id from clin.vacc_indication where description='influenza'),
	'Influenza (>6 Monate, Hersteller)'
);

-- Impfzeitpunkte definieren
insert into clin.vacc_def
	(fk_regime, seq_no, min_age_due, comment)
values (
	currval('clin.vacc_regime_id_seq'),
	1,
	'6 months'::interval,
	'nie zuvor geimpfte Kinder 4 Wo danach boostern'
);

-- =============================================
-- do simple revision tracking
delete from gm_schema_revision where filename = '$RCSfile: Impfplan-Influenza.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: Impfplan-Influenza.sql,v $', '$Revision: 1.8 $');

-- =============================================
-- $Log: Impfplan-Influenza.sql,v $
-- Revision 1.8  2005-11-25 15:07:28  ncq
-- - create schema "clin" and move all things clinical into it
--
-- Revision 1.7  2005/09/19 16:38:51  ncq
-- - adjust to removed is_core from gm_schema_revision
--
-- Revision 1.6  2005/07/14 21:31:43  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.5  2004/04/14 13:33:04  ncq
-- - need to adjust min_interval for seq_no=1 after tightening interval checks
--
-- Revision 1.4  2004/03/18 09:58:50  ncq
-- - removed is_booster reference where is false
--
-- Revision 1.3  2003/12/29 15:57:58  uid66147
-- - name cleanup
--
-- Revision 1.2  2003/12/01 22:13:57  ncq
-- - wording change
--
-- Revision 1.1  2003/11/30 12:37:39  ncq
-- - InfectoVac Flu 2003/4
--
-- Revision 1.4  2003/11/28 08:15:57  ncq
-- - PG 7.1/pyPgSQL/mxDateTime returns 0 for interval=1 month,
--   it works with interval=4 weeks, though, so use that
--
-- Revision 1.3  2003/11/26 23:54:51  ncq
-- - lnk_vaccdef2reg does not exist anymore
--
-- Revision 1.2  2003/11/26 00:12:19  ncq
-- - fix fk_recommended_by value
--
-- Revision 1.1  2003/11/26 00:10:45  ncq
-- - Prevenar
--
