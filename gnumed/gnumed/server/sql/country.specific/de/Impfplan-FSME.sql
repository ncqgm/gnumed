-- Projekt GnuMed
-- Impfkalender der Hersteller von Influenza-Impfstoff

-- Quellen: Beipackzettel

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/de/Impfplan-FSME.sql,v $
-- $Revision: 1.3 $
-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- Impfplan erstellen
insert into vacc_regime
	(fk_recommended_by, fk_indication, name)
values (
	-1,
	(select id from vacc_indication where description='tick-borne meningoencephalitis'),
	'Normal-Immunisierung (Hersteller)'
);

-- Impfzeitpunkte definieren
insert into vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due)
values (
	currval('vacc_regime_id_seq'),
	1,
	'12 months'::interval,
	'12 years'::interval
);

insert into vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due, min_interval, comment)
values (
	currval('vacc_regime_id_seq'),
	2,
	'13 months'::interval,
	'12 years'::interval,
	'1 month'::interval,
	'frühestmögliche Serokonversion in 14 Tagen, 1-3 Monate nach 1.Impfung'
);

insert into vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due, min_interval, comment)
values (
	currval('vacc_regime_id_seq'),
	3,
	'22 months'::interval,
	'12 years'::interval,
	'9 months'::interval,
	'9-12 Monate nach 2.Impfung'
);

-- fast path
insert into vacc_regime
	(fk_recommended_by, fk_indication, name)
values (
	-1,
	(select id from vacc_indication where description='tick-borne meningoencephalitis'),
	'Schnell-Immunisierung (Hersteller)'
);

-- Impfzeitpunkte definieren
insert into vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due)
values (
	currval('vacc_regime_id_seq'),
	1,
	'12 months'::interval,
	'12 years'::interval
);

insert into vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due, min_interval, comment)
values (
	currval('vacc_regime_id_seq'),
	2,
	'12 months 7 days'::interval,
	'12 years'::interval,
	'7 days'::interval,
	'am Tag 7 nach 1.Impfung, frühestmögliche Serokonversion in 14 Tagen'
);

insert into vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due, min_interval, comment)
values (
	currval('vacc_regime_id_seq'),
	3,
	'12 months 21 days'::interval,
	'12 years'::interval,
	'14 days'::interval,
	'am Tag 21, 14 Tage nach 2.Impfung'
);

-- =============================================
-- do simple revision tracking
delete from gm_schema_revision where filename = '$RCSfile: Impfplan-FSME.sql,v $';
INSERT INTO gm_schema_revision (filename, version, is_core) VALUES('$RCSfile: Impfplan-FSME.sql,v $', '$Revision: 1.3 $', False);

-- =============================================
-- $Log: Impfplan-FSME.sql,v $
-- Revision 1.3  2005-07-14 21:31:43  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.2  2004/04/14 13:33:04  ncq
-- - need to adjust min_interval for seq_no=1 after tightening interval checks
--
-- Revision 1.1  2004/03/27 18:38:55  ncq
-- - FSME schedule
--
