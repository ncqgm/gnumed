-- Project: GnuMed - public database table for phrase wheel SQL test
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmPhraseWheelTest.sql,v $
-- $Revision: 1.8 $
-- license: GPL
-- author: Karsten Hilbert

-- this provides a table that is hardcoded as a test table
-- in the phrase wheel module test code,
-- it is useful for importing into a publically accessible
-- database such that people can remotely test the phrase
-- wheel connected to a database table
-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

set client_encoding to 'latin1';
-- ===================================================================
\unset ON_ERROR_STOP
drop table gmpw_sql_test;
drop sequence gmpw_sql_test_id_seq;
\set ON_ERROR_STOP 1

create table gmpw_sql_test (
	id serial primary key,
	phrase text not null
);

select add_table_for_scoring('gmpw_sql_test');

GRANT all on
	gmpw_sql_test
to group "gm-doctors";

-- ===================================================================
insert into gmpw_sql_test(phrase) values ('Sepsis acutissima hyperergica fulminans');
insert into gmpw_sql_test(phrase) values ('Carate, hyperchrome Schädigung');
insert into gmpw_sql_test(phrase) values ('Phäohyphomykose');
insert into gmpw_sql_test(phrase) values ('Atypische Melanozytenhyperplasie');
insert into gmpw_sql_test(phrase) values ('Schilddrüsenhyperplasie');
insert into gmpw_sql_test(phrase) values ('Sporadische hyperplastische Struma');
insert into gmpw_sql_test(phrase) values ('Struma hyperplastica');
insert into gmpw_sql_test(phrase) values ('Thyreoideahyperplasie');
insert into gmpw_sql_test(phrase) values ('Latent hyperthyreote Struma');
insert into gmpw_sql_test(phrase) values ('Coma hyperglycaemicum diabeticum');
insert into gmpw_sql_test(phrase) values ('Coma hypoglycaemicum');
insert into gmpw_sql_test(phrase) values ('Nichtdiabetisches hypoglykämisches Koma');
insert into gmpw_sql_test(phrase) values ('B-Zellhyperplasie');
insert into gmpw_sql_test(phrase) values ('Beta-Zellhyperplasie');
insert into gmpw_sql_test(phrase) values ('Inselzellhyperplasie');
insert into gmpw_sql_test(phrase) values ('Pseudohypoparathyreoidismus');
insert into gmpw_sql_test(phrase) values ('Panhypopituitarismus');
insert into gmpw_sql_test(phrase) values ('Extrahypophysäres ACTH [Adrenocorticotropes Hormon]-Syndrom');
insert into gmpw_sql_test(phrase) values ('Adrenale Androgenhypersekretion');
insert into gmpw_sql_test(phrase) values ('Androgenhyperkrinie, Nebenniere');
insert into gmpw_sql_test(phrase) values ('Androgenhypersekretion, Nebenniere');
insert into gmpw_sql_test(phrase) values ('Ovarielle Androgenhypersekretion');
insert into gmpw_sql_test(phrase) values ('Testikuläre Androgenhypersekretion');
insert into gmpw_sql_test(phrase) values ('Persistierende Thymushyperplasie');
insert into gmpw_sql_test(phrase) values ('Pseudohypokaliämiesyndrom');
insert into gmpw_sql_test(phrase) values ('Verdünnungshyponatriämie');
insert into gmpw_sql_test(phrase) values ('Bipolare affektive Störung, hypomanische Episode');
insert into gmpw_sql_test(phrase) values ('Manisch-depressive Reaktion, hypomanische Form');
insert into gmpw_sql_test(phrase) values ('Herzhypochondrie');
insert into gmpw_sql_test(phrase) values ('Akinetisches hypotones Syndrom');
insert into gmpw_sql_test(phrase) values ('Affektion, Nervus hypoglossus');
insert into gmpw_sql_test(phrase) values ('Krankheit, Nervus hypoglossus');
insert into gmpw_sql_test(phrase) values ('Parese, Nervus hypoglossus');
insert into gmpw_sql_test(phrase) values ('Neuritis hypertrophicans');
insert into gmpw_sql_test(phrase) values ('Pseudohypertrophische Muskeldystrophie');
insert into gmpw_sql_test(phrase) values ('Myotonia hypertrophica congenita');
insert into gmpw_sql_test(phrase) values ('Cataracta senilis hypermatura');
insert into gmpw_sql_test(phrase) values ('Fundus hypertonicus');
insert into gmpw_sql_test(phrase) values ('Achsenhypermetropie');
insert into gmpw_sql_test(phrase) values ('Achsenhyperopie');
insert into gmpw_sql_test(phrase) values ('Brechungshypermetropie');
insert into gmpw_sql_test(phrase) values ('Brechungshyperopie');
insert into gmpw_sql_test(phrase) values ('Belastungshypertonie');
insert into gmpw_sql_test(phrase) values ('Benigne hypertensive Herzkrankheit');
insert into gmpw_sql_test(phrase) values ('Hypertensive Herzhypertrophie');
insert into gmpw_sql_test(phrase) values ('Nierenhypertonie, maligne');
insert into gmpw_sql_test(phrase) values ('Ischämische Herzkrankheit, chronisch, hypertonisch');
insert into gmpw_sql_test(phrase) values ('Idiopathische hypertrophische Subaortenstenose');
insert into gmpw_sql_test(phrase) values ('IHSS [Idiopathische hypertrophische Subaortenstenose]');
insert into gmpw_sql_test(phrase) values ('Chronische Herzhypertrophie');
insert into gmpw_sql_test(phrase) values ('Herzhypertrophie');
insert into gmpw_sql_test(phrase) values ('Herzmuskelhypertrophie');
insert into gmpw_sql_test(phrase) values ('Konzentrische Linksherzhypertrophie');
insert into gmpw_sql_test(phrase) values ('Linksherzhypertrophie');
insert into gmpw_sql_test(phrase) values ('Myokardhypertrophie');
insert into gmpw_sql_test(phrase) values ('Rechtsherzhypertrophie');
insert into gmpw_sql_test(phrase) values ('Nierenarterienhyperplasie');
insert into gmpw_sql_test(phrase) values ('Dermatitis hypostatica');
insert into gmpw_sql_test(phrase) values ('Regulationsstörung, hypoton');
insert into gmpw_sql_test(phrase) values ('Chronische hyperplastische Rhinitis');
insert into gmpw_sql_test(phrase) values ('Nasenmuschelhyperplasie');
insert into gmpw_sql_test(phrase) values ('Nasennebenhöhlenhypoplasie');
insert into gmpw_sql_test(phrase) values ('Angina hypertrophica');
insert into gmpw_sql_test(phrase) values ('Gaumenmandelhyperplasie');
insert into gmpw_sql_test(phrase) values ('Gaumenmandelhypertrophie');
insert into gmpw_sql_test(phrase) values ('Mandelhypertrophie');
insert into gmpw_sql_test(phrase) values ('Tonsillenhyperplasie');
insert into gmpw_sql_test(phrase) values ('Tonsillenhypertrophie');
insert into gmpw_sql_test(phrase) values ('Rachenmandelhyperplasie');
insert into gmpw_sql_test(phrase) values ('Rachenmandelhypertrophie');
insert into gmpw_sql_test(phrase) values ('Adenotonsillarhyperplasie');
insert into gmpw_sql_test(phrase) values ('Gaumen- und Rachenmandelhypertrophie');
insert into gmpw_sql_test(phrase) values ('Chronisch-hyperplastische Laryngitis');
insert into gmpw_sql_test(phrase) values ('Hypertrophische hyperplastische Laryngitis');
insert into gmpw_sql_test(phrase) values ('Allergisches hyperreaktives Bronchialsystem');
insert into gmpw_sql_test(phrase) values ('Lungenhypostase');
insert into gmpw_sql_test(phrase) values ('Zahnschmelzhypoplasie');
insert into gmpw_sql_test(phrase) values ('Odontogenesis hypoplastica');
insert into gmpw_sql_test(phrase) values ('Pulpahyperplasie');
insert into gmpw_sql_test(phrase) values ('Gingivahyperplasie');
insert into gmpw_sql_test(phrase) values ('Kieferhyperplasie');
insert into gmpw_sql_test(phrase) values ('Kieferhypoplasie');
insert into gmpw_sql_test(phrase) values ('Mandibulahypoplasie');
insert into gmpw_sql_test(phrase) values ('Speicheldrüsenhypertrophie');
insert into gmpw_sql_test(phrase) values ('Zungengrundhyperplasie');
insert into gmpw_sql_test(phrase) values ('Zungenhypertrophie');
insert into gmpw_sql_test(phrase) values ('Ösophagushypertrophie');
insert into gmpw_sql_test(phrase) values ('Gastropathia hypertrophica gigantea');
insert into gmpw_sql_test(phrase) values ('Pylorushypertrophie');
insert into gmpw_sql_test(phrase) values ('Magenhypermobilität');
insert into gmpw_sql_test(phrase) values ('Magenhypomotilität');
insert into gmpw_sql_test(phrase) values ('Appendixhyperplasie');
insert into gmpw_sql_test(phrase) values ('Darmhypomotilität');
insert into gmpw_sql_test(phrase) values ('Perihepatitis chronica hyperplastica');
insert into gmpw_sql_test(phrase) values ('Gallenblasenhypertrophie');
insert into gmpw_sql_test(phrase) values ('Gallengangshypertrophie');
insert into gmpw_sql_test(phrase) values ('Lichen ruber hypertrophicus');
insert into gmpw_sql_test(phrase) values ('Nagelhypertrophie');
insert into gmpw_sql_test(phrase) values ('Talgdrüsenhyperplasie');
insert into gmpw_sql_test(phrase) values ('Narbenhypertrophie');
insert into gmpw_sql_test(phrase) values ('Subsepsis hyperergica sive allergica');
insert into gmpw_sql_test(phrase) values ('Meniskushypermobilität');
insert into gmpw_sql_test(phrase) values ('Arteriitis hyperergica');
insert into gmpw_sql_test(phrase) values ('Diffuse idiopathische Skeletthyperostose');
insert into gmpw_sql_test(phrase) values ('Spondylitis hyperostotica');
insert into gmpw_sql_test(phrase) values ('Spondylitis hyperostotica [Forestier-Ott-Syndrom]');
insert into gmpw_sql_test(phrase) values ('Muskelhypertrophie');
insert into gmpw_sql_test(phrase) values ('Hoffahypertrophie im Knie [Krankheit des Corpus adiposum infrapatellare]');
insert into gmpw_sql_test(phrase) values ('Harnleiterhypertrophie');
insert into gmpw_sql_test(phrase) values ('Nierenhypertrophie');
insert into gmpw_sql_test(phrase) values ('Ureterhypertrophie');
insert into gmpw_sql_test(phrase) values ('Detrusorhyperreflexie, Harnblase');
insert into gmpw_sql_test(phrase) values ('Detrusorhypoaktivität, Harnblase');
insert into gmpw_sql_test(phrase) values ('Harnblasenhypotonie');
insert into gmpw_sql_test(phrase) values ('Detrusorhyperaktivität');
insert into gmpw_sql_test(phrase) values ('Blasenhalshypertrophie');
insert into gmpw_sql_test(phrase) values ('Blasenhypertrophie');
insert into gmpw_sql_test(phrase) values ('Harnblasenhalshypertrophie');
insert into gmpw_sql_test(phrase) values ('Harnblasenhyperämie');
insert into gmpw_sql_test(phrase) values ('Harnblasenhypertrophie');
insert into gmpw_sql_test(phrase) values ('Benigne Prostatahyperplasie');
insert into gmpw_sql_test(phrase) values ('Benigne Prostatahypertrophie');
insert into gmpw_sql_test(phrase) values ('BPH [Benigne Prostatahyperplasie]');
insert into gmpw_sql_test(phrase) values ('Prostatahyperplasie');
insert into gmpw_sql_test(phrase) values ('Prostatahypertrophie');
insert into gmpw_sql_test(phrase) values ('Präputiumhypertrophie');
insert into gmpw_sql_test(phrase) values ('Vorhauthypertrophie');
insert into gmpw_sql_test(phrase) values ('Penishypertrophie');
insert into gmpw_sql_test(phrase) values ('Hodenhypotrophie');
insert into gmpw_sql_test(phrase) values ('Hodenhyperplasie');
insert into gmpw_sql_test(phrase) values ('Hodenhypertrophie');
insert into gmpw_sql_test(phrase) values ('Skrotumhypertrophie');
insert into gmpw_sql_test(phrase) values ('Glanduläre Mammahyperplasie');
insert into gmpw_sql_test(phrase) values ('Mammahyperplasie');
insert into gmpw_sql_test(phrase) values ('Mammahypertrophie');
insert into gmpw_sql_test(phrase) values ('Pubertätsmammahypertrophie');
insert into gmpw_sql_test(phrase) values ('Endometriumhyperplasie');
insert into gmpw_sql_test(phrase) values ('Polypoide Endometriumhyperplasie');
insert into gmpw_sql_test(phrase) values ('Adenomatöse Uterushyperplasie');
insert into gmpw_sql_test(phrase) values ('Myohyperplasie, Uterus');
insert into gmpw_sql_test(phrase) values ('Uterushyperplasie');
insert into gmpw_sql_test(phrase) values ('Uterushypertrophie');
insert into gmpw_sql_test(phrase) values ('Laktationshyperinvolution, Uterus');
insert into gmpw_sql_test(phrase) values ('Zervixhypertrophie');
insert into gmpw_sql_test(phrase) values ('Labienhypertrophie');
insert into gmpw_sql_test(phrase) values ('Vulvahypertrophie');
insert into gmpw_sql_test(phrase) values ('Klitorishypertrophie');
insert into gmpw_sql_test(phrase) values ('Gestationshypertonie');
insert into gmpw_sql_test(phrase) values ('Schwangerschaftshypertonie');
insert into gmpw_sql_test(phrase) values ('Gestationshypertonie, mit Proteinurie');
insert into gmpw_sql_test(phrase) values ('Primäre hypotone uterine Dysfunktion');
insert into gmpw_sql_test(phrase) values ('Sekundäre hypotone uterine Dysfunktion');
insert into gmpw_sql_test(phrase) values ('Puerperale Uterushypertrophie');
insert into gmpw_sql_test(phrase) values ('Transitorische Tachypnoe, beim Neugeborenen');
insert into gmpw_sql_test(phrase) values ('Angeborene Muskelhypertonie');
insert into gmpw_sql_test(phrase) values ('Angeborene Muskelhypotonie');
insert into gmpw_sql_test(phrase) values ('Gehirnhypoplasie');
insert into gmpw_sql_test(phrase) values ('Rückenmarkhypoplasie');
insert into gmpw_sql_test(phrase) values ('Persistierender hyperplastischer primärer Glaskörper');
insert into gmpw_sql_test(phrase) values ('Papillenhypoplasie, Mikropapille');
insert into gmpw_sql_test(phrase) values ('Ohrmuschelhyperplasie');
insert into gmpw_sql_test(phrase) values ('Ohrmuschelhypoplasie');
insert into gmpw_sql_test(phrase) values ('Aortenklappenhypoplasie');
insert into gmpw_sql_test(phrase) values ('Linksherzhypoplasie-Syndrom');
insert into gmpw_sql_test(phrase) values ('Ventrikelhypoplasie, links');
insert into gmpw_sql_test(phrase) values ('Nasenhypoplasie');
insert into gmpw_sql_test(phrase) values ('Kehlkopfhypoplasie');
insert into gmpw_sql_test(phrase) values ('Lungenhypoplasie');
insert into gmpw_sql_test(phrase) values ('Lingua hypertrophica');
insert into gmpw_sql_test(phrase) values ('Zungenhypoplasie');
insert into gmpw_sql_test(phrase) values ('Angeborene hypertrophische Pylorusstenose');
insert into gmpw_sql_test(phrase) values ('Kongenitale hypertrophische Pylorusstenose');
insert into gmpw_sql_test(phrase) values ('Gallengangshypoplasie');
insert into gmpw_sql_test(phrase) values ('Konnatale Leberhypertrophie');
insert into gmpw_sql_test(phrase) values ('Uterushypoplasie');
insert into gmpw_sql_test(phrase) values ('Zervixhypoplasie, angeboren');
insert into gmpw_sql_test(phrase) values ('Hodenhypoplasie');
insert into gmpw_sql_test(phrase) values ('Testishypoplasie');
insert into gmpw_sql_test(phrase) values ('Penishypoplasie');
insert into gmpw_sql_test(phrase) values ('Einseitige Nierenhypoplasie');
insert into gmpw_sql_test(phrase) values ('Beidseitige Nierenhypoplasie');
insert into gmpw_sql_test(phrase) values ('Nierenhypoplasie');
insert into gmpw_sql_test(phrase) values ('Nierenhyperplasie');
insert into gmpw_sql_test(phrase) values ('Harnblasenhypoplasie');
insert into gmpw_sql_test(phrase) values ('Radiushypoplasie');
insert into gmpw_sql_test(phrase) values ('Mittelgesichtshypoplasie');
insert into gmpw_sql_test(phrase) values ('Mammahypoplasie');
insert into gmpw_sql_test(phrase) values ('Mammahypotrophie');
insert into gmpw_sql_test(phrase) values ('Niedriger Blutdruck, ohne hypotone Regulationsstörung, einmaliger Meßwert');
insert into gmpw_sql_test(phrase) values ('Tachypnoe');
insert into gmpw_sql_test(phrase) values ('Transitorische Tachypnoe');
insert into gmpw_sql_test(phrase) values ('Leberhypertrophie');
insert into gmpw_sql_test(phrase) values ('Hemihypalgesie');
insert into gmpw_sql_test(phrase) values ('Muskelhypotonie');
insert into gmpw_sql_test(phrase) values ('Unklare Muskelhypotonie');
insert into gmpw_sql_test(phrase) values ('Nervenhyperregeneration [Narbenneurom]');

-- =============================================
-- do simple schema revision tracking
delete from gm_schema_revision where filename = '$RCSfile: gmPhraseWheelTest.sql,v $';
insert into gm_schema_revision (filename, version, is_core) VALUES('$RCSfile: gmPhraseWheelTest.sql,v $', '$Revision: 1.8 $', False);

-- ===================================================================
-- $Log: gmPhraseWheelTest.sql,v $
-- Revision 1.8  2005-07-14 21:31:42  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.7  2004/07/17 20:57:53  ncq
-- - don't use user/_user workaround anymore as we dropped supporting
--   it (but we did NOT drop supporting readonly connections on > 7.3)
--
-- Revision 1.6  2004/01/10 01:29:25  ncq
-- - add test data for test-nurse, test-doctor
--
-- Revision 1.5  2003/12/29 15:41:15  uid66147
-- - cleanup
--
-- Revision 1.4  2003/10/19 13:05:25  ncq
-- - use scoring implementation
--
-- Revision 1.3  2003/10/09 15:22:14  ncq
-- - added cookie field based on Hilmar's context tree suggestion
--
-- Revision 1.2  2003/10/07 22:27:27  ncq
-- - grants
-- - separate scoring table
--
-- Revision 1.1  2003/09/16 21:55:32  ncq
-- - test data for phrase wheel test
--
