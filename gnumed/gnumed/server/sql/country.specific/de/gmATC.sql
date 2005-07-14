-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/de/gmATC.sql,v $
-- $Revision: 1.2 $

-- part of GnuMed
-- GPL
-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>

-- German ATC data
-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

set client_encoding to 'LATIN1';
-- =============================================
delete from atc_substance;
delete from atc_group;
delete from ref_source where name_short='ATC/DDD-GM-2004';

-- reference entry
insert into ref_source (
	name_short,
	name_long,
	version,
	description,
	source
) values (
	'ATC/DDD-GM-2004',
	'ATC/DDD-GM; Systematik; Version 2004; Amtliche Fassung für die Bundesrepublik Deutschland',
	'2004',

'ATC/DDD-GM
Systematik
Version 2004

Amtliche Fassung für die Bundesrepublik Deutschland

Lizenz:
========================================================================================================
Mit dem Download der Dateien kommt ein Erwerbervertrag zwischen Ihnen und DIMDI zustande. Sie
verpflichten sich dadurch, unsere Abgabebedingungen einzuhalten. Sie umfassen:

§1 Urheberrecht/Nutzungsumfang

 1. Bei den vom DIMDI herausgegebenen amtlichen deutschsprachigen Ausgaben der ATC mit DDD und den
    "Richtlinien für die ATC-Klassifikation und die DDD-Festlegung" handelt es sich um ein "anderes
    amtliches Werk" i. S. des § 5 Abs. 2 Urheberrechtsgesetz (UrhG).
    Bei Beachtung des Änderungsverbotes (§ 62 UrhG) und des Gebotes der Quellenangabe (§ 63 UrhG)
    verfügen Sie zeitlich befristet über die Nutzungsrechte an diesem Werk.
 2. Wollen Sie die Daten auszugsweise oder vollständig an Dritte weitergeben (vervielfältigen), so
    gelten die nachstehenden Vereinbarungen, und Sie verpflichten sich, diese Vereinbarungen ebenfalls
    an Dritte weiterzugeben:
    Bei der auszugsweisen oder vollständigen Weitergabe der Daten an Dritte sind Änderungen der
    inhaltlichen Struktur und Normierung der der ATC mit DDD und den "Richtlinien für die
    ATC-Klassifikation und die DDD-Festlegung" nicht gestattet. Insbesondere darf das amtliche Werk
    keine kommerzielle Werbung enthalten. Erlaubt sind lediglich werbende Hinweise auf verlagseigene
    Produkte, jedoch dürfen auch diese Hinweise nicht im amtlichen Text stehen. Vor der Erstellung einer
    Druckausgabe und deren Weitergabe müssen Sie Kontakt mit DIMDI aufnehmen, weil eine Reihe von
    Vorschriften zu beachten ist. In jedes maschinenlesbare Weitergabeexemplar ist die folgende
    Formulierung aufzunehmen: Die Erstellung erfolgte unter Verwendung der Datenträger der amtlichen
    Fassung der ATC mit DDD und den "Richtlinien für die ATC-Klassifikation und die DDD-Festlegung" des
    Deutschen Instituts für medizinische Dokumentation und Information (DIMDI).
      + Für die ATC mit DDDs: In der Originalausgabe veröffentlicht durch das WHO-Zentrum für die
        Erarbeitung der Methodik der Arzneimittelstatistik, Oslo, unter dem Titel ATC-Index mit DDDs
      + Für die Richtlinien für die ATC-Klassifikation und die DDD-Festlegung: In der Originalausgabe
        veröffentlicht durch das WHO-Zentrum für die Erarbeitung der Methodik der Arzneimittelstatistik,
        Oslo, unter dem Titel Richtlinien für die ATC-Klassifikation und die DDD-Festlegung
 3. Die Nutzung dieser Fassung ist nur in der Bundesrepublik Deutschland gestattet.

§2 Gewährleistung und Haftung

 1. Für Schäden, die durch Fehler bei der Herstellung bzw. Bearbeitung der ATC mit DDD und der
    "Richtlinien für die ATC-Klassifikation und die DDD-Festlegung" entstehen, haftet das DIMDI nur,
    soweit ihm Vorsatz oder grobe Fahrlässigkeit zur Last fällt. Es wird nur der Ersatz des
    unmittelbaren Schadens geschuldet.
 2. Sie stellen das DIMDI frei von Ansprüchen, die dadurch entstehen, daß Sie die Rechte Dritter bei der
    Vervielfältigung und Weitergabe von Daten nach § 1 Abs. 2 dieses Vertrages verletzen.

[*] Ja, ich habe die Download-Bestimmungen gelesen und bin mit ihnen einverstanden.
========================================================================================================
',

'Herausgegeben vom Deutschen Institut für Medizinische Dokumentation und Information, DIMDI

downloaded Samstag 26 Jun 2004 22:18:42 CEST
http://www.dimdi.de/dynamic/de/klassi/download/atc1/index.html

DIMDI
Waisenhausgasse 36 - 38 a
50676 Köln
Tel.: +49 (0) 221 47 24 1
Fax:  +49 (0) 221 47 24 444
Mail: posteingang@dimdi.de'
);

-- =============================================
-- do simple revision tracking
delete from gm_schema_revision where filename = '$RCSfile: gmATC.sql,v $';
INSERT INTO gm_schema_revision (filename, version, is_core) VALUES('$RCSfile: gmATC.sql,v $', '$Revision: 1.2 $', False);

-- =============================================
-- $Log: gmATC.sql,v $
-- Revision 1.2  2005-07-14 21:31:43  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.1  2004/06/26 21:14:27  ncq
-- German ATC data
--
