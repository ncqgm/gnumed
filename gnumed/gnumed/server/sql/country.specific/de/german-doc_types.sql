-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/de/Attic/german-doc_types.sql,v $
-- $Revision: 1.1 $

-- part of GnuMed
-- GPL

-- doc types useful in Germany
-- run this _after_ gmBlobs.sql !

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
