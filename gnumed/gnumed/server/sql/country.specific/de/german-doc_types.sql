-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/de/Attic/german-doc_types.sql,v $
-- $Revision: 1.4 $

-- part of GnuMed
-- GPL

-- doc types useful in Germany
-- run this _after_ gmBlobs.sql !
-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
INSERT INTO doc_type(id, name) values(100, 'Entlassung Chirurgie');
INSERT INTO doc_type(id, name) values(101, 'Entlassung Interne');
INSERT INTO doc_type(id, name) values(102, 'Entlassung Psychatrie');
INSERT INTO doc_type(id, name) values(103, 'Entlassung Reha');
INSERT INTO doc_type(id, name) values(104, 'Entlassung Orthopädie');

INSERT INTO doc_type(id, name) values(105, 'Arztbrief Chirurgie');
INSERT INTO doc_type(id, name) values(106, 'Arztbrief Orthopädie');
INSERT INTO doc_type(id, name) values(107, 'Arztbrief Innere');
INSERT INTO doc_type(id, name) values(108, 'Arztbrief Neurologie');
INSERT INTO doc_type(id, name) values(109, 'Arztbrief Psychotherapie');
INSERT INTO doc_type(id, name) values(110, 'Arztbrief Radiologie');
INSERT INTO doc_type(id, name) values(111, 'Arztbrief Umweltmedizin');
INSERT INTO doc_type(id, name) values(112, 'Arztbrief Mikrobiologie');
INSERT INTO doc_type(id, name) values(113, 'Labor');
INSERT INTO doc_type(id, name) values(114, 'Befund Röntgen');
INSERT INTO doc_type(id, name) values(115, 'Arztbrief Kardiologie');

-- do simple revision tracking
\i gmSchemaRevision.sql
INSERT INTO schema_revision (filename, version) VALUES('$RCSfile: german-doc_types.sql,v $', '$Revision: 1.4 $');

-- =============================================
-- $Log: german-doc_types.sql,v $
-- Revision 1.4  2002-12-26 15:52:28  ncq
-- - add two types
--
-- Revision 1.3  2002/12/01 13:53:09  ncq
-- - missing ; at end of schema tracking line
--
-- Revision 1.2  2002/11/16 00:21:44  ncq
-- - add simplistic revision tracking
--
