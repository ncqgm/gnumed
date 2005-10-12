-- ===================================================================
-- project: GNUmed

-- The following state codes have been prepared by
-- Jim Busser working with data provided by Thilo Schuler
-- as an external database taken from 'tealow_zencart'.

-- license: GPL (details at http://gnu.org)

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmCountryZones.sql,v $
-- $Id: gmCountryZones.sql,v 1.2 2005-10-12 22:29:11 ncq Exp $
-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================================
set client_encoding to latin1;

-- country AD
INSERT INTO state(code, country, name) VALUES ('AN','AD',i18n('Andorra'));
INSERT INTO state(code, country, name) VALUES ('CA','AD',i18n('Canillo'));
INSERT INTO state(code, country, name) VALUES ('EN','AD',i18n('Encamp'));
INSERT INTO state(code, country, name) VALUES ('LM','AD',i18n('La Massana'));
INSERT INTO state(code, country, name) VALUES ('LE','AD',i18n('Les Escaldes'));
INSERT INTO state(code, country, name) VALUES ('OR','AD',i18n('Ordino'));
INSERT INTO state(code, country, name) VALUES ('SJ','AD',i18n('Sant Julia de Lori'));
-- country AE
INSERT INTO state(code, country, name) VALUES ('AE-1','AE',i18n('Arab Emirates territory'));
-- country AF
INSERT INTO state(code, country, name) VALUES ('BA','AF',i18n('Badakhshan'));
INSERT INTO state(code, country, name) VALUES ('BD','AF',i18n('Badghis'));
INSERT INTO state(code, country, name) VALUES ('BG','AF',i18n('Baghlan'));
INSERT INTO state(code, country, name) VALUES ('BL','AF',i18n('Balkh'));
INSERT INTO state(code, country, name) VALUES ('BM','AF',i18n('Bamian'));
INSERT INTO state(code, country, name) VALUES ('FA','AF',i18n('Farah'));
INSERT INTO state(code, country, name) VALUES ('FR','AF',i18n('Faryab'));
INSERT INTO state(code, country, name) VALUES ('GH','AF',i18n('Ghazni'));
INSERT INTO state(code, country, name) VALUES ('GO','AF',i18n('Ghowr'));
INSERT INTO state(code, country, name) VALUES ('HE','AF',i18n('Helmand'));
INSERT INTO state(code, country, name) VALUES ('HR','AF',i18n('Herat'));
INSERT INTO state(code, country, name) VALUES ('JO','AF',i18n('Jowzjan'));
INSERT INTO state(code, country, name) VALUES ('KA','AF',i18n('Kabol'));
INSERT INTO state(code, country, name) VALUES ('KN','AF',i18n('Kandahar'));
INSERT INTO state(code, country, name) VALUES ('KP','AF',i18n('Kapisa'));
INSERT INTO state(code, country, name) VALUES ('KO','AF',i18n('Konar'));
INSERT INTO state(code, country, name) VALUES ('KD','AF',i18n('Kondoz'));
INSERT INTO state(code, country, name) VALUES ('LA','AF',i18n('Laghman'));
INSERT INTO state(code, country, name) VALUES ('LO','AF',i18n('Lowgar'));
INSERT INTO state(code, country, name) VALUES ('NA','AF',i18n('Nangarhar'));
INSERT INTO state(code, country, name) VALUES ('NI','AF',i18n('Nimruz'));
INSERT INTO state(code, country, name) VALUES ('OR','AF',i18n('Oruzgan'));
INSERT INTO state(code, country, name) VALUES ('PA','AF',i18n('Paktia'));
INSERT INTO state(code, country, name) VALUES ('PK','AF',i18n('Paktika'));
INSERT INTO state(code, country, name) VALUES ('PR','AF',i18n('Parvan'));
INSERT INTO state(code, country, name) VALUES ('SA','AF',i18n('Samangan'));
INSERT INTO state(code, country, name) VALUES ('SP','AF',i18n('Sar-e Pol'));
INSERT INTO state(code, country, name) VALUES ('TA','AF',i18n('Takhar'));
INSERT INTO state(code, country, name) VALUES ('VA','AF',i18n('Vardak'));
INSERT INTO state(code, country, name) VALUES ('ZA','AF',i18n('Zabol'));
-- country AG
INSERT INTO state(code, country, name) VALUES ('BA','AG',i18n('Barbuda'));
INSERT INTO state(code, country, name) VALUES ('RE','AG',i18n('Redonda'));
INSERT INTO state(code, country, name) VALUES ('SG','AG',i18n('Saint George'));
INSERT INTO state(code, country, name) VALUES ('SJ','AG',i18n('Saint John'));
INSERT INTO state(code, country, name) VALUES ('SM','AG',i18n('Saint Mary'));
INSERT INTO state(code, country, name) VALUES ('SP','AG',i18n('Saint Paul'));
INSERT INTO state(code, country, name) VALUES ('SE','AG',i18n('Saint Peter'));
INSERT INTO state(code, country, name) VALUES ('SH','AG',i18n('Saint Philip'));
-- country AI
INSERT INTO state(code, country, name) VALUES ('AI-1','AI',i18n('Anguilla territory'));
-- country AL
INSERT INTO state(code, country, name) VALUES ('BE','AL',i18n('Berat'));
INSERT INTO state(code, country, name) VALUES ('BU','AL',i18n('Bulqize'));
INSERT INTO state(code, country, name) VALUES ('DE','AL',i18n('Delvine'));
INSERT INTO state(code, country, name) VALUES ('DV','AL',i18n('Devoll (Bilisht)'));
INSERT INTO state(code, country, name) VALUES ('DI','AL',i18n('Diber (Peshkopi)'));
INSERT INTO state(code, country, name) VALUES ('DU','AL',i18n('Durres'));
INSERT INTO state(code, country, name) VALUES ('EL','AL',i18n('Elbasan'));
INSERT INTO state(code, country, name) VALUES ('FI','AL',i18n('Fier'));
INSERT INTO state(code, country, name) VALUES ('GJ','AL',i18n('Gjirokaster'));
INSERT INTO state(code, country, name) VALUES ('GR','AL',i18n('Gramsh'));
INSERT INTO state(code, country, name) VALUES ('HA','AL',i18n('Has (Krume)'));
INSERT INTO state(code, country, name) VALUES ('KA','AL',i18n('Kavaje'));
INSERT INTO state(code, country, name) VALUES ('KO','AL',i18n('Kolonje (Erseke)'));
INSERT INTO state(code, country, name) VALUES ('KR','AL',i18n('Korce'));
INSERT INTO state(code, country, name) VALUES ('KU','AL',i18n('Kruje'));
INSERT INTO state(code, country, name) VALUES ('KC','AL',i18n('Kucove'));
INSERT INTO state(code, country, name) VALUES ('KK','AL',i18n('Kukes'));
INSERT INTO state(code, country, name) VALUES ('LA','AL',i18n('Lac'));
INSERT INTO state(code, country, name) VALUES ('LE','AL',i18n('Lezhe'));
INSERT INTO state(code, country, name) VALUES ('LI','AL',i18n('Librazhd'));
INSERT INTO state(code, country, name) VALUES ('LU','AL',i18n('Lushnje'));
INSERT INTO state(code, country, name) VALUES ('MM','AL',i18n('Malesi e Madhe (Koplik)'));
INSERT INTO state(code, country, name) VALUES ('MA','AL',i18n('Mallakaster (Ballsh)'));
INSERT INTO state(code, country, name) VALUES ('MT','AL',i18n('Mat (Burrel)'));
INSERT INTO state(code, country, name) VALUES ('MI','AL',i18n('Mirdite (Rreshen)'));
INSERT INTO state(code, country, name) VALUES ('PE','AL',i18n('Peqin'));
INSERT INTO state(code, country, name) VALUES ('PR','AL',i18n('Permet'));
INSERT INTO state(code, country, name) VALUES ('PO','AL',i18n('Pogradec'));
INSERT INTO state(code, country, name) VALUES ('PU','AL',i18n('Puke'));
INSERT INTO state(code, country, name) VALUES ('SA','AL',i18n('Sarande'));
INSERT INTO state(code, country, name) VALUES ('SH','AL',i18n('Shkoder'));
INSERT INTO state(code, country, name) VALUES ('SK','AL',i18n('Skrapar (Corovode)'));
INSERT INTO state(code, country, name) VALUES ('TE','AL',i18n('Tepelene'));
INSERT INTO state(code, country, name) VALUES ('TI','AL',i18n('Tirane (Tirana)'));
INSERT INTO state(code, country, name) VALUES ('TR','AL',i18n('Tropoje (Bajram Curri)'));
INSERT INTO state(code, country, name) VALUES ('VL','AL',i18n('Vlore'));
-- country AM
INSERT INTO state(code, country, name) VALUES ('AR','AM',i18n('Aragatsotn'));
INSERT INTO state(code, country, name) VALUES ('AA','AM',i18n('Ararat'));
INSERT INTO state(code, country, name) VALUES ('AM','AM',i18n('Armavir'));
INSERT INTO state(code, country, name) VALUES ('GE','AM',i18n('Geghark''unik|'));
INSERT INTO state(code, country, name) VALUES ('KO','AM',i18n('Kotayk'''));
INSERT INTO state(code, country, name) VALUES ('LO','AM',i18n('Lorri'));
INSERT INTO state(code, country, name) VALUES ('SH','AM',i18n('Shirak'));
INSERT INTO state(code, country, name) VALUES ('SY','AM',i18n('Syunik'''));
INSERT INTO state(code, country, name) VALUES ('TA','AM',i18n('Tavush'));
INSERT INTO state(code, country, name) VALUES ('VA','AM',i18n('Vayots'' Dzor'));
INSERT INTO state(code, country, name) VALUES ('YE','AM',i18n('Yerevan'));
-- country AN
INSERT INTO state(code, country, name) VALUES ('AN-1','AN',i18n('Netherlands Antilles territory'));
-- country AO
INSERT INTO state(code, country, name) VALUES ('BE','AO',i18n('Bengo'));
INSERT INTO state(code, country, name) VALUES ('BN','AO',i18n('Benguela'));
INSERT INTO state(code, country, name) VALUES ('BI','AO',i18n('Bie'));
INSERT INTO state(code, country, name) VALUES ('CA','AO',i18n('Cabinda'));
INSERT INTO state(code, country, name) VALUES ('CC','AO',i18n('Cuando Cubango'));
INSERT INTO state(code, country, name) VALUES ('CN','AO',i18n('Cuanza Norte'));
INSERT INTO state(code, country, name) VALUES ('CS','AO',i18n('Cuanza Sul'));
INSERT INTO state(code, country, name) VALUES ('CU','AO',i18n('Cunene'));
INSERT INTO state(code, country, name) VALUES ('HU','AO',i18n('Huambo'));
INSERT INTO state(code, country, name) VALUES ('HI','AO',i18n('Huila'));
INSERT INTO state(code, country, name) VALUES ('LU','AO',i18n('Luanda'));
INSERT INTO state(code, country, name) VALUES ('LN','AO',i18n('Lunda Norte'));
INSERT INTO state(code, country, name) VALUES ('LS','AO',i18n('Lunda Sul'));
INSERT INTO state(code, country, name) VALUES ('MA','AO',i18n('Malanje'));
INSERT INTO state(code, country, name) VALUES ('MO','AO',i18n('Moxico'));
INSERT INTO state(code, country, name) VALUES ('NA','AO',i18n('Namibe'));
INSERT INTO state(code, country, name) VALUES ('UI','AO',i18n('Uige'));
INSERT INTO state(code, country, name) VALUES ('ZA','AO',i18n('Zaire'));
-- country AQ
INSERT INTO state(code, country, name) VALUES ('AQ-1','AQ',i18n('Antarctica territory'));
-- country AR
INSERT INTO state(code, country, name) VALUES ('AN','AR',i18n('Antartida e Islas del Atlantico'));
INSERT INTO state(code, country, name) VALUES ('BA','AR',i18n('Buenos Aires'));
INSERT INTO state(code, country, name) VALUES ('CA','AR',i18n('Catamarca'));
INSERT INTO state(code, country, name) VALUES ('CH','AR',i18n('Chaco'));
INSERT INTO state(code, country, name) VALUES ('CU','AR',i18n('Chubut'));
INSERT INTO state(code, country, name) VALUES ('CO','AR',i18n('Cordoba'));
INSERT INTO state(code, country, name) VALUES ('CR','AR',i18n('Corrientes'));
INSERT INTO state(code, country, name) VALUES ('DF','AR',i18n('Distrito Federal'));
INSERT INTO state(code, country, name) VALUES ('ER','AR',i18n('Entre Rios'));
INSERT INTO state(code, country, name) VALUES ('FO','AR',i18n('Formosa'));
INSERT INTO state(code, country, name) VALUES ('JU','AR',i18n('Jujuy'));
INSERT INTO state(code, country, name) VALUES ('LP','AR',i18n('La Pampa'));
INSERT INTO state(code, country, name) VALUES ('LR','AR',i18n('La Rioja'));
INSERT INTO state(code, country, name) VALUES ('ME','AR',i18n('Mendoza'));
INSERT INTO state(code, country, name) VALUES ('MI','AR',i18n('Misiones'));
INSERT INTO state(code, country, name) VALUES ('NE','AR',i18n('Neuquen'));
INSERT INTO state(code, country, name) VALUES ('RN','AR',i18n('Rio Negro'));
INSERT INTO state(code, country, name) VALUES ('SA','AR',i18n('Salta'));
INSERT INTO state(code, country, name) VALUES ('SJ','AR',i18n('San Juan'));
INSERT INTO state(code, country, name) VALUES ('SL','AR',i18n('San Luis'));
INSERT INTO state(code, country, name) VALUES ('SC','AR',i18n('Santa Cruz'));
INSERT INTO state(code, country, name) VALUES ('SF','AR',i18n('Santa Fe'));
INSERT INTO state(code, country, name) VALUES ('SD','AR',i18n('Santiago del Estero'));
INSERT INTO state(code, country, name) VALUES ('TF','AR',i18n('Tierra del Fuego'));
INSERT INTO state(code, country, name) VALUES ('TU','AR',i18n('Tucuman'));
-- country AS
INSERT INTO state(code, country, name) VALUES ('EA','AS',i18n('Eastern'));
INSERT INTO state(code, country, name) VALUES ('MA','AS',i18n('Manu''a'));
INSERT INTO state(code, country, name) VALUES ('RI','AS',i18n('Rose Island'));
INSERT INTO state(code, country, name) VALUES ('SI','AS',i18n('Swains Island'));
INSERT INTO state(code, country, name) VALUES ('WE','AS',i18n('Western'));
-- country AW
INSERT INTO state(code, country, name) VALUES ('AW-1','AW',i18n('Aruba territory'));
-- country AZ
INSERT INTO state(code, country, name) VALUES ('AB','AZ',i18n('Abseron Rayonu'));
INSERT INTO state(code, country, name) VALUES ('AG','AZ',i18n('Agcabadi Rayonu'));
INSERT INTO state(code, country, name) VALUES ('AD','AZ',i18n('Agdam Rayonu'));
INSERT INTO state(code, country, name) VALUES ('AA','AZ',i18n('Agdas Rayonu'));
INSERT INTO state(code, country, name) VALUES ('AS','AZ',i18n('Agstafa Rayonu'));
INSERT INTO state(code, country, name) VALUES ('AU','AZ',i18n('Agsu Rayonu'));
INSERT INTO state(code, country, name) VALUES ('AL','AZ',i18n('Ali Bayramli Sahari'));
INSERT INTO state(code, country, name) VALUES ('AT','AZ',i18n('Astara Rayonu'));
INSERT INTO state(code, country, name) VALUES ('BS','AZ',i18n('Baki Sahari'));
INSERT INTO state(code, country, name) VALUES ('BR','AZ',i18n('Balakan Rayonu'));
INSERT INTO state(code, country, name) VALUES ('BA','AZ',i18n('Barda Rayonu'));
INSERT INTO state(code, country, name) VALUES ('BE','AZ',i18n('Beylaqan Rayonu'));
INSERT INTO state(code, country, name) VALUES ('BI','AZ',i18n('Bilasuvar Rayonu'));
INSERT INTO state(code, country, name) VALUES ('CA','AZ',i18n('Cabrayil Rayonu'));
INSERT INTO state(code, country, name) VALUES ('CL','AZ',i18n('Calilabad Rayonu'));
INSERT INTO state(code, country, name) VALUES ('DA','AZ',i18n('Daskasan Rayonu'));
INSERT INTO state(code, country, name) VALUES ('DV','AZ',i18n('Davaci Rayonu'));
INSERT INTO state(code, country, name) VALUES ('FU','AZ',i18n('Fuzuli Rayonu'));
INSERT INTO state(code, country, name) VALUES ('GA','AZ',i18n('Gadabay Rayonu'));
INSERT INTO state(code, country, name) VALUES ('GN','AZ',i18n('Ganca Sahari'));
INSERT INTO state(code, country, name) VALUES ('GO','AZ',i18n('Goranboy Rayonu'));
INSERT INTO state(code, country, name) VALUES ('GY','AZ',i18n('Goycay Rayonu'));
INSERT INTO state(code, country, name) VALUES ('HA','AZ',i18n('Haciqabul Rayonu'));
INSERT INTO state(code, country, name) VALUES ('IM','AZ',i18n('Imisli Rayonu'));
INSERT INTO state(code, country, name) VALUES ('IS','AZ',i18n('Ismayilli Rayonu'));
INSERT INTO state(code, country, name) VALUES ('KA','AZ',i18n('Kalbacar Rayonu'));
INSERT INTO state(code, country, name) VALUES ('KU','AZ',i18n('Kurdamir Rayonu'));
INSERT INTO state(code, country, name) VALUES ('LA','AZ',i18n('Lacin Rayonu'));
INSERT INTO state(code, country, name) VALUES ('LN','AZ',i18n('Lankaran Rayonu'));
INSERT INTO state(code, country, name) VALUES ('LK','AZ',i18n('Lankaran Sahari'));
INSERT INTO state(code, country, name) VALUES ('LE','AZ',i18n('Lerik Rayonu'));
INSERT INTO state(code, country, name) VALUES ('MA','AZ',i18n('Masalli Rayonu'));
INSERT INTO state(code, country, name) VALUES ('MI','AZ',i18n('Mingacevir Sahari'));
INSERT INTO state(code, country, name) VALUES ('NA','AZ',i18n('Naftalan Sahari'));
INSERT INTO state(code, country, name) VALUES ('NX','AZ',i18n('Naxcivan Muxtar Respublikasi'));
INSERT INTO state(code, country, name) VALUES ('NE','AZ',i18n('Neftcala Rayonu'));
INSERT INTO state(code, country, name) VALUES ('OG','AZ',i18n('Oguz Rayonu'));
INSERT INTO state(code, country, name) VALUES ('QA','AZ',i18n('Qabala Rayonu'));
INSERT INTO state(code, country, name) VALUES ('QX','AZ',i18n('Qax Rayonu'));
INSERT INTO state(code, country, name) VALUES ('QZ','AZ',i18n('Qazax Rayonu'));
INSERT INTO state(code, country, name) VALUES ('QO','AZ',i18n('Qobustan Rayonu'));
INSERT INTO state(code, country, name) VALUES ('QU','AZ',i18n('Quba Rayonu'));
INSERT INTO state(code, country, name) VALUES ('QB','AZ',i18n('Qubadli Rayonu'));
INSERT INTO state(code, country, name) VALUES ('QS','AZ',i18n('Qusar Rayonu'));
INSERT INTO state(code, country, name) VALUES ('SA','AZ',i18n('Saatli Rayonu'));
INSERT INTO state(code, country, name) VALUES ('SB','AZ',i18n('Sabirabad Rayonu'));
INSERT INTO state(code, country, name) VALUES ('SK','AZ',i18n('Saki Rayonu'));
INSERT INTO state(code, country, name) VALUES ('SI','AZ',i18n('Saki Sahari'));
INSERT INTO state(code, country, name) VALUES ('SL','AZ',i18n('Salyan Rayonu'));
INSERT INTO state(code, country, name) VALUES ('SM','AZ',i18n('Samaxi Rayonu'));
INSERT INTO state(code, country, name) VALUES ('SR','AZ',i18n('Samkir Rayonu'));
INSERT INTO state(code, country, name) VALUES ('SX','AZ',i18n('Samux Rayonu'));
INSERT INTO state(code, country, name) VALUES ('SY','AZ',i18n('Siyazan Rayonu'));
INSERT INTO state(code, country, name) VALUES ('SU','AZ',i18n('Sumqayit Sahari'));
INSERT INTO state(code, country, name) VALUES ('SS','AZ',i18n('Susa Rayonu'));
INSERT INTO state(code, country, name) VALUES ('ST','AZ',i18n('Susa Sahari'));
INSERT INTO state(code, country, name) VALUES ('TA','AZ',i18n('Tartar Rayonu'));
INSERT INTO state(code, country, name) VALUES ('TO','AZ',i18n('Tovuz Rayonu'));
INSERT INTO state(code, country, name) VALUES ('UC','AZ',i18n('Ucar Rayonu'));
INSERT INTO state(code, country, name) VALUES ('XA','AZ',i18n('Xacmaz Rayonu'));
INSERT INTO state(code, country, name) VALUES ('XN','AZ',i18n('Xankandi Sahari'));
INSERT INTO state(code, country, name) VALUES ('XL','AZ',i18n('Xanlar Rayonu'));
INSERT INTO state(code, country, name) VALUES ('XI','AZ',i18n('Xizi Rayonu'));
INSERT INTO state(code, country, name) VALUES ('XO','AZ',i18n('Xocali Rayonu'));
INSERT INTO state(code, country, name) VALUES ('XC','AZ',i18n('Xocavand Rayonu'));
INSERT INTO state(code, country, name) VALUES ('YA','AZ',i18n('Yardimli Rayonu'));
INSERT INTO state(code, country, name) VALUES ('YE','AZ',i18n('Yevlax Rayonu'));
INSERT INTO state(code, country, name) VALUES ('YV','AZ',i18n('Yevlax Sahari'));
INSERT INTO state(code, country, name) VALUES ('ZA','AZ',i18n('Zangilan Rayonu'));
INSERT INTO state(code, country, name) VALUES ('ZQ','AZ',i18n('Zaqatala Rayonu'));
INSERT INTO state(code, country, name) VALUES ('ZR','AZ',i18n('Zardab Rayonu'));
-- country BA
INSERT INTO state(code, country, name) VALUES ('BA-1','BA',i18n('Bosnia and Herzegovina territory'));
-- country BB
INSERT INTO state(code, country, name) VALUES ('CC','BB',i18n('Christ Church'));
INSERT INTO state(code, country, name) VALUES ('SA','BB',i18n('Saint Andrew'));
INSERT INTO state(code, country, name) VALUES ('SG','BB',i18n('Saint George'));
INSERT INTO state(code, country, name) VALUES ('SJ','BB',i18n('Saint James'));
INSERT INTO state(code, country, name) VALUES ('SO','BB',i18n('Saint John'));
INSERT INTO state(code, country, name) VALUES ('SS','BB',i18n('Saint Joseph'));
INSERT INTO state(code, country, name) VALUES ('SL','BB',i18n('Saint Lucy'));
INSERT INTO state(code, country, name) VALUES ('SM','BB',i18n('Saint Michael'));
INSERT INTO state(code, country, name) VALUES ('SP','BB',i18n('Saint Peter'));
INSERT INTO state(code, country, name) VALUES ('SH','BB',i18n('Saint Philip'));
INSERT INTO state(code, country, name) VALUES ('ST','BB',i18n('Saint Thomas'));
-- country BD
INSERT INTO state(code, country, name) VALUES ('BA','BD',i18n('Barisal'));
INSERT INTO state(code, country, name) VALUES ('CH','BD',i18n('Chittagong'));
INSERT INTO state(code, country, name) VALUES ('DH','BD',i18n('Dhaka'));
INSERT INTO state(code, country, name) VALUES ('KH','BD',i18n('Khulna'));
INSERT INTO state(code, country, name) VALUES ('RA','BD',i18n('Rajshahi'));
-- country BE
INSERT INTO state(code, country, name) VALUES ('AN','BE',i18n('Antwerpen'));
INSERT INTO state(code, country, name) VALUES ('BW','BE',i18n('Brabant Wallon'));
INSERT INTO state(code, country, name) VALUES ('HA','BE',i18n('Hainaut'));
INSERT INTO state(code, country, name) VALUES ('LG','BE',i18n('Liege'));
INSERT INTO state(code, country, name) VALUES ('LM','BE',i18n('Limburg'));
INSERT INTO state(code, country, name) VALUES ('LX','BE',i18n('Luxembourg'));
INSERT INTO state(code, country, name) VALUES ('NM','BE',i18n('Namur'));
INSERT INTO state(code, country, name) VALUES ('OV','BE',i18n('Oost-Vlaanderen'));
INSERT INTO state(code, country, name) VALUES ('VB','BE',i18n('Vlaams Brabant'));
INSERT INTO state(code, country, name) VALUES ('WV','BE',i18n('West-Vlaanderen'));
-- country BF
INSERT INTO state(code, country, name) VALUES ('BA','BF',i18n('Bale'));
INSERT INTO state(code, country, name) VALUES ('BM','BF',i18n('Bam'));
INSERT INTO state(code, country, name) VALUES ('BN','BF',i18n('Banwa'));
INSERT INTO state(code, country, name) VALUES ('BZ','BF',i18n('Bazega'));
INSERT INTO state(code, country, name) VALUES ('BO','BF',i18n('Bougouriba'));
INSERT INTO state(code, country, name) VALUES ('BU','BF',i18n('Boulgou'));
INSERT INTO state(code, country, name) VALUES ('BL','BF',i18n('Boulkiemde'));
INSERT INTO state(code, country, name) VALUES ('CO','BF',i18n('Comoe'));
INSERT INTO state(code, country, name) VALUES ('GA','BF',i18n('Ganzourgou'));
INSERT INTO state(code, country, name) VALUES ('GN','BF',i18n('Gnagna'));
INSERT INTO state(code, country, name) VALUES ('GO','BF',i18n('Gourma'));
INSERT INTO state(code, country, name) VALUES ('HO','BF',i18n('Houet'));
INSERT INTO state(code, country, name) VALUES ('IO','BF',i18n('Ioba'));
INSERT INTO state(code, country, name) VALUES ('KA','BF',i18n('Kadiogo'));
INSERT INTO state(code, country, name) VALUES ('KE','BF',i18n('Kenedougou'));
INSERT INTO state(code, country, name) VALUES ('KO','BF',i18n('Komandjari'));
INSERT INTO state(code, country, name) VALUES ('KM','BF',i18n('Kompienga'));
INSERT INTO state(code, country, name) VALUES ('KS','BF',i18n('Kossi'));
INSERT INTO state(code, country, name) VALUES ('KU','BF',i18n('Koupelogo'));
INSERT INTO state(code, country, name) VALUES ('KR','BF',i18n('Kouritenga'));
INSERT INTO state(code, country, name) VALUES ('KW','BF',i18n('Kourweogo'));
INSERT INTO state(code, country, name) VALUES ('LE','BF',i18n('Leraba'));
INSERT INTO state(code, country, name) VALUES ('LO','BF',i18n('Loroum'));
INSERT INTO state(code, country, name) VALUES ('MO','BF',i18n('Mouhoun'));
INSERT INTO state(code, country, name) VALUES ('NA','BF',i18n('Nahouri'));
INSERT INTO state(code, country, name) VALUES ('NM','BF',i18n('Namentenga'));
INSERT INTO state(code, country, name) VALUES ('NU','BF',i18n('Naumbiel'));
INSERT INTO state(code, country, name) VALUES ('NY','BF',i18n('Nayala'));
INSERT INTO state(code, country, name) VALUES ('OU','BF',i18n('Oubritenga'));
INSERT INTO state(code, country, name) VALUES ('OD','BF',i18n('Oudalan'));
INSERT INTO state(code, country, name) VALUES ('PA','BF',i18n('Passore'));
INSERT INTO state(code, country, name) VALUES ('PO','BF',i18n('Poni'));
INSERT INTO state(code, country, name) VALUES ('SA','BF',i18n('Samentenga'));
INSERT INTO state(code, country, name) VALUES ('SN','BF',i18n('Sanguie'));
INSERT INTO state(code, country, name) VALUES ('SE','BF',i18n('Seno'));
INSERT INTO state(code, country, name) VALUES ('SI','BF',i18n('Sissili'));
INSERT INTO state(code, country, name) VALUES ('SO','BF',i18n('Soum'));
INSERT INTO state(code, country, name) VALUES ('SU','BF',i18n('Sourou'));
INSERT INTO state(code, country, name) VALUES ('TA','BF',i18n('Tapoa'));
INSERT INTO state(code, country, name) VALUES ('TU','BF',i18n('Tuy'));
INSERT INTO state(code, country, name) VALUES ('YA','BF',i18n('Yagha'));
INSERT INTO state(code, country, name) VALUES ('YT','BF',i18n('Yatenga'));
INSERT INTO state(code, country, name) VALUES ('ZI','BF',i18n('Ziro'));
INSERT INTO state(code, country, name) VALUES ('ZO','BF',i18n('Zondomo'));
INSERT INTO state(code, country, name) VALUES ('ZU','BF',i18n('Zoundweogo'));
-- country BG
INSERT INTO state(code, country, name) VALUES ('BU','BG',i18n('Burgas'));
INSERT INTO state(code, country, name) VALUES ('GS','BG',i18n('Grad Sofiya'));
INSERT INTO state(code, country, name) VALUES ('KH','BG',i18n('Khaskovo'));
INSERT INTO state(code, country, name) VALUES ('LO','BG',i18n('Lovech'));
INSERT INTO state(code, country, name) VALUES ('MO','BG',i18n('Montana'));
INSERT INTO state(code, country, name) VALUES ('PL','BG',i18n('Plovdiv'));
INSERT INTO state(code, country, name) VALUES ('RU','BG',i18n('Ruse'));
INSERT INTO state(code, country, name) VALUES ('SO','BG',i18n('Sofiya'));
INSERT INTO state(code, country, name) VALUES ('VA','BG',i18n('Varna'));
-- country BH
INSERT INTO state(code, country, name) VALUES ('AH','BH',i18n('Al Hadd'));
INSERT INTO state(code, country, name) VALUES ('AM','BH',i18n('Al Manamah'));
INSERT INTO state(code, country, name) VALUES ('AG','BH',i18n('Al Mintaqah al Gharbiyah'));
INSERT INTO state(code, country, name) VALUES ('AW','BH',i18n('Al Mintaqah al Wusta'));
INSERT INTO state(code, country, name) VALUES ('AS','BH',i18n('Al Mintaqah ash Shamaliyah'));
INSERT INTO state(code, country, name) VALUES ('AU','BH',i18n('Al Muharraq'));
INSERT INTO state(code, country, name) VALUES ('AR','BH',i18n('Ar Rifa'' wa al Mintaqah al Janub'));
INSERT INTO state(code, country, name) VALUES ('JH','BH',i18n('Jidd Hafs'));
INSERT INTO state(code, country, name) VALUES ('JU','BH',i18n('Juzur Hawar'));
INSERT INTO state(code, country, name) VALUES ('MI','BH',i18n('Madinat ''Isa'));
INSERT INTO state(code, country, name) VALUES ('MH','BH',i18n('Madinat Hamad'));
INSERT INTO state(code, country, name) VALUES ('SI','BH',i18n('Sitrah'));
-- country BI
INSERT INTO state(code, country, name) VALUES ('BU','BI',i18n('Bubanza'));
INSERT INTO state(code, country, name) VALUES ('BJ','BI',i18n('Bujumbura'));
INSERT INTO state(code, country, name) VALUES ('BR','BI',i18n('Bururi'));
INSERT INTO state(code, country, name) VALUES ('CA','BI',i18n('Cankuzo'));
INSERT INTO state(code, country, name) VALUES ('CI','BI',i18n('Cibitoke'));
INSERT INTO state(code, country, name) VALUES ('GI','BI',i18n('Gitega'));
INSERT INTO state(code, country, name) VALUES ('KA','BI',i18n('Karuzi'));
INSERT INTO state(code, country, name) VALUES ('KY','BI',i18n('Kayanza'));
INSERT INTO state(code, country, name) VALUES ('KI','BI',i18n('Kirundo'));
INSERT INTO state(code, country, name) VALUES ('MA','BI',i18n('Makamba'));
INSERT INTO state(code, country, name) VALUES ('MU','BI',i18n('Muramvya'));
INSERT INTO state(code, country, name) VALUES ('MY','BI',i18n('Muyinga'));
INSERT INTO state(code, country, name) VALUES ('MW','BI',i18n('Mwaro'));
INSERT INTO state(code, country, name) VALUES ('NG','BI',i18n('Ngozi'));
INSERT INTO state(code, country, name) VALUES ('RU','BI',i18n('Rutana'));
INSERT INTO state(code, country, name) VALUES ('RY','BI',i18n('Ruyigi'));
-- country BJ
INSERT INTO state(code, country, name) VALUES ('AI','BJ',i18n('Alibori'));
INSERT INTO state(code, country, name) VALUES ('AT','BJ',i18n('Atakora'));
INSERT INTO state(code, country, name) VALUES ('AL','BJ',i18n('Atlantique'));
INSERT INTO state(code, country, name) VALUES ('BO','BJ',i18n('Borgou'));
INSERT INTO state(code, country, name) VALUES ('CO','BJ',i18n('Collines'));
INSERT INTO state(code, country, name) VALUES ('CF','BJ',i18n('Couffo'));
INSERT INTO state(code, country, name) VALUES ('DO','BJ',i18n('Donga'));
INSERT INTO state(code, country, name) VALUES ('LI','BJ',i18n('Littoral'));
INSERT INTO state(code, country, name) VALUES ('MO','BJ',i18n('Mono'));
INSERT INTO state(code, country, name) VALUES ('OU','BJ',i18n('Oueme'));
INSERT INTO state(code, country, name) VALUES ('PL','BJ',i18n('Plateau'));
INSERT INTO state(code, country, name) VALUES ('ZO','BJ',i18n('Zou'));
-- country BM
INSERT INTO state(code, country, name) VALUES ('DE','BM',i18n('Devonshire'));
INSERT INTO state(code, country, name) VALUES ('HA','BM',i18n('Hamilton'));
INSERT INTO state(code, country, name) VALUES ('PA','BM',i18n('Paget'));
INSERT INTO state(code, country, name) VALUES ('PE','BM',i18n('Pembroke'));
INSERT INTO state(code, country, name) VALUES ('SG','BM',i18n('Saint Georges'));
INSERT INTO state(code, country, name) VALUES ('SA','BM',i18n('Sandys'));
INSERT INTO state(code, country, name) VALUES ('SM','BM',i18n('Smiths'));
INSERT INTO state(code, country, name) VALUES ('SO','BM',i18n('Southampton'));
INSERT INTO state(code, country, name) VALUES ('WA','BM',i18n('Warwick'));
-- country BN
INSERT INTO state(code, country, name) VALUES ('BE','BN',i18n('Belait'));
INSERT INTO state(code, country, name) VALUES ('BM','BN',i18n('Brunei and Muara'));
INSERT INTO state(code, country, name) VALUES ('TE','BN',i18n('Temburong'));
INSERT INTO state(code, country, name) VALUES ('TU','BN',i18n('Tutong'));
-- country BO
INSERT INTO state(code, country, name) VALUES ('BE','BO',i18n('Beni'));
INSERT INTO state(code, country, name) VALUES ('CH','BO',i18n('Chuquisaca'));
INSERT INTO state(code, country, name) VALUES ('CO','BO',i18n('Cochabamba'));
INSERT INTO state(code, country, name) VALUES ('LP','BO',i18n('La Paz'));
INSERT INTO state(code, country, name) VALUES ('OR','BO',i18n('Oruro'));
INSERT INTO state(code, country, name) VALUES ('PA','BO',i18n('Pando'));
INSERT INTO state(code, country, name) VALUES ('PO','BO',i18n('Potosi'));
INSERT INTO state(code, country, name) VALUES ('SC','BO',i18n('Santa Cruz'));
INSERT INTO state(code, country, name) VALUES ('TA','BO',i18n('Tarija'));
-- country BR
INSERT INTO state(code, country, name) VALUES ('AC','BR',i18n('Acre'));
INSERT INTO state(code, country, name) VALUES ('AL','BR',i18n('Alagoas'));
INSERT INTO state(code, country, name) VALUES ('AM','BR',i18n('Amapa'));
INSERT INTO state(code, country, name) VALUES ('AZ','BR',i18n('Amazonas'));
INSERT INTO state(code, country, name) VALUES ('BA','BR',i18n('Bahia'));
INSERT INTO state(code, country, name) VALUES ('CE','BR',i18n('Ceara'));
INSERT INTO state(code, country, name) VALUES ('DF','BR',i18n('Distrito Federal'));
INSERT INTO state(code, country, name) VALUES ('ES','BR',i18n('Espirito Santo'));
INSERT INTO state(code, country, name) VALUES ('GO','BR',i18n('Goias'));
INSERT INTO state(code, country, name) VALUES ('MA','BR',i18n('Maranhao'));
INSERT INTO state(code, country, name) VALUES ('MG','BR',i18n('Mato Grosso'));
INSERT INTO state(code, country, name) VALUES ('MS','BR',i18n('Mato Grosso do Sul'));
INSERT INTO state(code, country, name) VALUES ('MR','BR',i18n('Minas Gerais'));
INSERT INTO state(code, country, name) VALUES ('PA','BR',i18n('Para'));
INSERT INTO state(code, country, name) VALUES ('PR','BR',i18n('Paraiba'));
INSERT INTO state(code, country, name) VALUES ('PN','BR',i18n('Parana'));
INSERT INTO state(code, country, name) VALUES ('PE','BR',i18n('Pernambuco'));
INSERT INTO state(code, country, name) VALUES ('PI','BR',i18n('Piaui'));
INSERT INTO state(code, country, name) VALUES ('RJ','BR',i18n('Rio de Janeiro'));
INSERT INTO state(code, country, name) VALUES ('RN','BR',i18n('Rio Grande do Norte'));
INSERT INTO state(code, country, name) VALUES ('RS','BR',i18n('Rio Grande do Sul'));
INSERT INTO state(code, country, name) VALUES ('RO','BR',i18n('Rondonia'));
INSERT INTO state(code, country, name) VALUES ('RR','BR',i18n('Roraima'));
INSERT INTO state(code, country, name) VALUES ('SC','BR',i18n('Santa Catarina'));
INSERT INTO state(code, country, name) VALUES ('SP','BR',i18n('Sao Paulo'));
INSERT INTO state(code, country, name) VALUES ('SE','BR',i18n('Sergipe'));
INSERT INTO state(code, country, name) VALUES ('TO','BR',i18n('Tocantins'));
-- country BS
INSERT INTO state(code, country, name) VALUES ('AC','BS',i18n('Acklins and Crooked Islands'));
INSERT INTO state(code, country, name) VALUES ('BI','BS',i18n('Bimini'));
INSERT INTO state(code, country, name) VALUES ('CI','BS',i18n('Cat Island'));
INSERT INTO state(code, country, name) VALUES ('EX','BS',i18n('Exuma'));
INSERT INTO state(code, country, name) VALUES ('FR','BS',i18n('Freeport'));
INSERT INTO state(code, country, name) VALUES ('FC','BS',i18n('Fresh Creek'));
INSERT INTO state(code, country, name) VALUES ('GH','BS',i18n('Governor''s Harbour'));
INSERT INTO state(code, country, name) VALUES ('GT','BS',i18n('Green Turtle Cay'));
INSERT INTO state(code, country, name) VALUES ('HI','BS',i18n('Harbour Island'));
INSERT INTO state(code, country, name) VALUES ('HR','BS',i18n('High Rock'));
INSERT INTO state(code, country, name) VALUES ('IN','BS',i18n('Inagua'));
INSERT INTO state(code, country, name) VALUES ('KB','BS',i18n('Kemps Bay'));
INSERT INTO state(code, country, name) VALUES ('LI','BS',i18n('Long Island'));
INSERT INTO state(code, country, name) VALUES ('MH','BS',i18n('Marsh Harbour'));
INSERT INTO state(code, country, name) VALUES ('MA','BS',i18n('Mayaguana'));
INSERT INTO state(code, country, name) VALUES ('NP','BS',i18n('New Providence'));
INSERT INTO state(code, country, name) VALUES ('NT','BS',i18n('Nicholls Town and Berry Islands'));
INSERT INTO state(code, country, name) VALUES ('RI','BS',i18n('Ragged Island'));
INSERT INTO state(code, country, name) VALUES ('RS','BS',i18n('Rock Sound'));
INSERT INTO state(code, country, name) VALUES ('SS','BS',i18n('San Salvador and Rum Cay'));
INSERT INTO state(code, country, name) VALUES ('SP','BS',i18n('Sandy Point'));
-- country BT
INSERT INTO state(code, country, name) VALUES ('BU','BT',i18n('Bumthang'));
INSERT INTO state(code, country, name) VALUES ('CH','BT',i18n('Chhukha'));
INSERT INTO state(code, country, name) VALUES ('CI','BT',i18n('Chirang'));
INSERT INTO state(code, country, name) VALUES ('DA','BT',i18n('Daga'));
INSERT INTO state(code, country, name) VALUES ('GE','BT',i18n('Geylegphug'));
INSERT INTO state(code, country, name) VALUES ('HA','BT',i18n('Ha'));
INSERT INTO state(code, country, name) VALUES ('LH','BT',i18n('Lhuntshi'));
INSERT INTO state(code, country, name) VALUES ('MO','BT',i18n('Mongar'));
INSERT INTO state(code, country, name) VALUES ('PA','BT',i18n('Paro'));
INSERT INTO state(code, country, name) VALUES ('PE','BT',i18n('Pemagatsel'));
INSERT INTO state(code, country, name) VALUES ('PU','BT',i18n('Punakha'));
INSERT INTO state(code, country, name) VALUES ('SA','BT',i18n('Samchi'));
INSERT INTO state(code, country, name) VALUES ('SJ','BT',i18n('Samdrup Jongkhar'));
INSERT INTO state(code, country, name) VALUES ('SH','BT',i18n('Shemgang'));
INSERT INTO state(code, country, name) VALUES ('TA','BT',i18n('Tashigang'));
INSERT INTO state(code, country, name) VALUES ('TH','BT',i18n('Thimphu'));
INSERT INTO state(code, country, name) VALUES ('TO','BT',i18n('Tongsa'));
INSERT INTO state(code, country, name) VALUES ('WP','BT',i18n('Wangdi Phodrang'));
-- country BV
INSERT INTO state(code, country, name) VALUES ('BV-1','BV',i18n('Bouvet Island territory'));
-- country BW
INSERT INTO state(code, country, name) VALUES ('CD','BW',i18n('Central District'));
INSERT INTO state(code, country, name) VALUES ('CH','BW',i18n('Chobe'));
INSERT INTO state(code, country, name) VALUES ('GH','BW',i18n('Ghanzi'));
INSERT INTO state(code, country, name) VALUES ('KG','BW',i18n('Kgalagadi'));
INSERT INTO state(code, country, name) VALUES ('KL','BW',i18n('Kgatleng'));
INSERT INTO state(code, country, name) VALUES ('KW','BW',i18n('Kweneng'));
INSERT INTO state(code, country, name) VALUES ('NG','BW',i18n('Ngamiland'));
INSERT INTO state(code, country, name) VALUES ('NE','BW',i18n('North East District'));
INSERT INTO state(code, country, name) VALUES ('SE','BW',i18n('South East District'));
INSERT INTO state(code, country, name) VALUES ('SD','BW',i18n('Southern District'));
-- country BY
INSERT INTO state(code, country, name) VALUES ('BR','BY',i18n('Brestskaya (Brest)'));
INSERT INTO state(code, country, name) VALUES ('HO','BY',i18n('Homyel''skaya (Homyel|)'));
INSERT INTO state(code, country, name) VALUES ('HM','BY',i18n('Horad Minsk'));
INSERT INTO state(code, country, name) VALUES ('HR','BY',i18n('Hrodzyenskaya (Hrodna)'));
INSERT INTO state(code, country, name) VALUES ('MA','BY',i18n('Mahilyowskaya (Mahilyow)'));
INSERT INTO state(code, country, name) VALUES ('MI','BY',i18n('Minskaya'));
INSERT INTO state(code, country, name) VALUES ('VI','BY',i18n('Vitsyebskaya (Vitsyebsk)'));
-- country BZ
INSERT INTO state(code, country, name) VALUES ('BE','BZ',i18n('Belize'));
INSERT INTO state(code, country, name) VALUES ('CA','BZ',i18n('Cayo'));
INSERT INTO state(code, country, name) VALUES ('CO','BZ',i18n('Corozal'));
INSERT INTO state(code, country, name) VALUES ('OW','BZ',i18n('Orange Walk'));
INSERT INTO state(code, country, name) VALUES ('SC','BZ',i18n('Stann Creek'));
INSERT INTO state(code, country, name) VALUES ('TO','BZ',i18n('Toledo'));
-- country CC
INSERT INTO state(code, country, name) VALUES ('CC-1','CC',i18n('Cocos (Keeling) Islands territory'));
-- country CF
INSERT INTO state(code, country, name) VALUES ('CF-1','CF',i18n('Central African Republic territory'));
-- country CG
INSERT INTO state(code, country, name) VALUES ('CG-1','CG',i18n('Congo territory'));

-- country CH
INSERT INTO state(code, country, name) VALUES ('AG','CH',i18n('Aargau'));
INSERT INTO state(code, country, name) VALUES ('AR','CH',i18n('Appenzell Ausserrhoden'));
INSERT INTO state(code, country, name) VALUES ('AI','CH',i18n('Appenzelli Innerrhoden'));
INSERT INTO state(code, country, name) VALUES ('BS','CH',i18n('Basel'));
INSERT INTO state(code, country, name) VALUES ('BE','CH',i18n('Bern'));
INSERT INTO state(code, country, name) VALUES ('FR','CH',i18n('Freiburg'));
INSERT INTO state(code, country, name) VALUES ('GE','CH',i18n('Geneve'));
INSERT INTO state(code, country, name) VALUES ('GL','CH',i18n('Glarus'));
INSERT INTO state(code, country, name) VALUES ('GR','CH',i18n('Graubünden'));
INSERT INTO state(code, country, name) VALUES ('JU','CH',i18n('Jura'));
INSERT INTO state(code, country, name) VALUES ('LU','CH',i18n('Luzern'));
INSERT INTO state(code, country, name) VALUES ('NE','CH',i18n('Neuchâtel'));
INSERT INTO state(code, country, name) VALUES ('NW','CH',i18n('Nidwalden'));
INSERT INTO state(code, country, name) VALUES ('OW','CH',i18n('Obwalden'));
INSERT INTO state(code, country, name) VALUES ('SG','CH',i18n('Sankt Gallen'));
INSERT INTO state(code, country, name) VALUES ('SH','CH',i18n('Schaffhausen'));
INSERT INTO state(code, country, name) VALUES ('SZ','CH',i18n('Schwyz'));
INSERT INTO state(code, country, name) VALUES ('SO','CH',i18n('Solothurn'));
INSERT INTO state(code, country, name) VALUES ('TG','CH',i18n('Thurgau'));
INSERT INTO state(code, country, name) VALUES ('TI','CH',i18n('Ticino'));
INSERT INTO state(code, country, name) VALUES ('UW','CH',i18n('Unterwalden'));
INSERT INTO state(code, country, name) VALUES ('UR','CH',i18n('Uri'));
INSERT INTO state(code, country, name) VALUES ('VS','CH',i18n('Valais'));
INSERT INTO state(code, country, name) VALUES ('VD','CH',i18n('Vaud'));
INSERT INTO state(code, country, name) VALUES ('ZG','CH',i18n('Zug'));
-- country CI
INSERT INTO state(code, country, name) VALUES ('CI-1','CI',i18n('Cote D''Ivoire territory'));
-- country CK
INSERT INTO state(code, country, name) VALUES ('CK-1','CK',i18n('Cook Islands territory'));
-- country CL
INSERT INTO state(code, country, name) VALUES ('AI','CL',i18n('Aisen del General Carlos Ibanez'));
INSERT INTO state(code, country, name) VALUES ('AN','CL',i18n('Antofagasta'));
INSERT INTO state(code, country, name) VALUES ('AR','CL',i18n('Araucania'));
INSERT INTO state(code, country, name) VALUES ('AT','CL',i18n('Atacama'));
INSERT INTO state(code, country, name) VALUES ('BB','CL',i18n('Bio-Bio'));
INSERT INTO state(code, country, name) VALUES ('CO','CL',i18n('Coquimbo'));
INSERT INTO state(code, country, name) VALUES ('LI','CL',i18n('Libertador General Bernardo O''Hi'));
INSERT INTO state(code, country, name) VALUES ('LL','CL',i18n('Los Lagos'));
INSERT INTO state(code, country, name) VALUES ('MA','CL',i18n('Magallanes y de la Antartica Chi'));
INSERT INTO state(code, country, name) VALUES ('MU','CL',i18n('Maule'));
INSERT INTO state(code, country, name) VALUES ('RM','CL',i18n('Region Metropolitana'));
INSERT INTO state(code, country, name) VALUES ('TA','CL',i18n('Tarapaca'));
INSERT INTO state(code, country, name) VALUES ('VA','CL',i18n('Valparaiso'));
-- country CM
INSERT INTO state(code, country, name) VALUES ('CM-1','CM',i18n('Cameroon territory'));
-- country CN
INSERT INTO state(code, country, name) VALUES ('AN','CN',i18n('Anhui'));
INSERT INTO state(code, country, name) VALUES ('BE','CN',i18n('Beijing'));
INSERT INTO state(code, country, name) VALUES ('CH','CN',i18n('Chongqing'));
INSERT INTO state(code, country, name) VALUES ('FU','CN',i18n('Fujian'));
INSERT INTO state(code, country, name) VALUES ('GA','CN',i18n('Gansu'));
INSERT INTO state(code, country, name) VALUES ('GU','CN',i18n('Guangdong'));
INSERT INTO state(code, country, name) VALUES ('GX','CN',i18n('Guangxi'));
INSERT INTO state(code, country, name) VALUES ('GZ','CN',i18n('Guizhou'));
INSERT INTO state(code, country, name) VALUES ('HA','CN',i18n('Hainan'));
INSERT INTO state(code, country, name) VALUES ('HB','CN',i18n('Hebei'));
INSERT INTO state(code, country, name) VALUES ('HL','CN',i18n('Heilongjiang'));
INSERT INTO state(code, country, name) VALUES ('HE','CN',i18n('Henan'));
INSERT INTO state(code, country, name) VALUES ('HK','CN',i18n('Hong Kong'));
INSERT INTO state(code, country, name) VALUES ('HU','CN',i18n('Hubei'));
INSERT INTO state(code, country, name) VALUES ('HN','CN',i18n('Hunan'));
INSERT INTO state(code, country, name) VALUES ('IM','CN',i18n('Inner Mongolia'));
INSERT INTO state(code, country, name) VALUES ('JI','CN',i18n('Jiangsu'));
INSERT INTO state(code, country, name) VALUES ('JX','CN',i18n('Jiangxi'));
INSERT INTO state(code, country, name) VALUES ('JL','CN',i18n('Jilin'));
INSERT INTO state(code, country, name) VALUES ('LI','CN',i18n('Liaoning'));
INSERT INTO state(code, country, name) VALUES ('MA','CN',i18n('Macau'));
INSERT INTO state(code, country, name) VALUES ('NI','CN',i18n('Ningxia'));
INSERT INTO state(code, country, name) VALUES ('SH','CN',i18n('Shaanxi'));
INSERT INTO state(code, country, name) VALUES ('SA','CN',i18n('Shandong'));
INSERT INTO state(code, country, name) VALUES ('SG','CN',i18n('Shanghai'));
INSERT INTO state(code, country, name) VALUES ('SX','CN',i18n('Shanxi'));
INSERT INTO state(code, country, name) VALUES ('SI','CN',i18n('Sichuan'));
INSERT INTO state(code, country, name) VALUES ('TI','CN',i18n('Tianjin'));
INSERT INTO state(code, country, name) VALUES ('XI','CN',i18n('Xinjiang'));
INSERT INTO state(code, country, name) VALUES ('YU','CN',i18n('Yunnan'));
INSERT INTO state(code, country, name) VALUES ('ZH','CN',i18n('Zhejiang'));
-- country CO
INSERT INTO state(code, country, name) VALUES ('AM','CO',i18n('Amazonas'));
INSERT INTO state(code, country, name) VALUES ('AN','CO',i18n('Antioquia'));
INSERT INTO state(code, country, name) VALUES ('AR','CO',i18n('Arauca'));
INSERT INTO state(code, country, name) VALUES ('AT','CO',i18n('Atlantico'));
INSERT INTO state(code, country, name) VALUES ('BO','CO',i18n('Bolivar'));
INSERT INTO state(code, country, name) VALUES ('BY','CO',i18n('Boyaca'));
INSERT INTO state(code, country, name) VALUES ('CA','CO',i18n('Caldas'));
INSERT INTO state(code, country, name) VALUES ('CQ','CO',i18n('Caqueta'));
INSERT INTO state(code, country, name) VALUES ('CS','CO',i18n('Casanare'));
INSERT INTO state(code, country, name) VALUES ('CU','CO',i18n('Cauca'));
INSERT INTO state(code, country, name) VALUES ('CE','CO',i18n('Cesar'));
INSERT INTO state(code, country, name) VALUES ('CH','CO',i18n('Choco'));
INSERT INTO state(code, country, name) VALUES ('CO','CO',i18n('Cordoba'));
INSERT INTO state(code, country, name) VALUES ('DC','CO',i18n('Distrito Capital de Santa Fe de'));
INSERT INTO state(code, country, name) VALUES ('GU','CO',i18n('Guainia'));
INSERT INTO state(code, country, name) VALUES ('GA','CO',i18n('Guaviare'));
INSERT INTO state(code, country, name) VALUES ('HU','CO',i18n('Huila'));
INSERT INTO state(code, country, name) VALUES ('LG','CO',i18n('La Guajira'));
INSERT INTO state(code, country, name) VALUES ('MA','CO',i18n('Magdalena'));
INSERT INTO state(code, country, name) VALUES ('ME','CO',i18n('Meta'));
INSERT INTO state(code, country, name) VALUES ('NA','CO',i18n('Narino'));
INSERT INTO state(code, country, name) VALUES ('NS','CO',i18n('Norte de Santander'));
INSERT INTO state(code, country, name) VALUES ('PU','CO',i18n('Putumayo'));
INSERT INTO state(code, country, name) VALUES ('QU','CO',i18n('Quindio'));
INSERT INTO state(code, country, name) VALUES ('RI','CO',i18n('Risaralda'));
INSERT INTO state(code, country, name) VALUES ('SA','CO',i18n('San Andres y Providencia'));
INSERT INTO state(code, country, name) VALUES ('SN','CO',i18n('Santander'));
INSERT INTO state(code, country, name) VALUES ('SU','CO',i18n('Sucre'));
INSERT INTO state(code, country, name) VALUES ('TO','CO',i18n('Tolima'));
INSERT INTO state(code, country, name) VALUES ('VC','CO',i18n('Valle del Cauca'));
INSERT INTO state(code, country, name) VALUES ('VA','CO',i18n('Vaupes'));
INSERT INTO state(code, country, name) VALUES ('VI','CO',i18n('Vichada'));
-- country CR
INSERT INTO state(code, country, name) VALUES ('AL','CR',i18n('Alajuela'));
INSERT INTO state(code, country, name) VALUES ('CA','CR',i18n('Cartago'));
INSERT INTO state(code, country, name) VALUES ('GU','CR',i18n('Guanacaste'));
INSERT INTO state(code, country, name) VALUES ('HE','CR',i18n('Heredia'));
INSERT INTO state(code, country, name) VALUES ('LI','CR',i18n('Limon'));
INSERT INTO state(code, country, name) VALUES ('PU','CR',i18n('Puntarenas'));
INSERT INTO state(code, country, name) VALUES ('SJ','CR',i18n('San Jose'));
-- country CU
INSERT INTO state(code, country, name) VALUES ('CA','CU',i18n('Camaguey'));
INSERT INTO state(code, country, name) VALUES ('CD','CU',i18n('Ciego de Avila'));
INSERT INTO state(code, country, name) VALUES ('CI','CU',i18n('Cienfuegos'));
INSERT INTO state(code, country, name) VALUES ('CH','CU',i18n('Ciudad de La Habana'));
INSERT INTO state(code, country, name) VALUES ('GR','CU',i18n('Granma'));
INSERT INTO state(code, country, name) VALUES ('GU','CU',i18n('Guantanamo'));
INSERT INTO state(code, country, name) VALUES ('HO','CU',i18n('Holguin'));
INSERT INTO state(code, country, name) VALUES ('IJ','CU',i18n('Isla de la Juventud'));
INSERT INTO state(code, country, name) VALUES ('LH','CU',i18n('La Habana'));
INSERT INTO state(code, country, name) VALUES ('LT','CU',i18n('Las Tunas'));
INSERT INTO state(code, country, name) VALUES ('MA','CU',i18n('Matanzas'));
INSERT INTO state(code, country, name) VALUES ('PR','CU',i18n('Pinar del Rio'));
INSERT INTO state(code, country, name) VALUES ('SS','CU',i18n('Sancti Spiritus'));
INSERT INTO state(code, country, name) VALUES ('SC','CU',i18n('Santiago de Cuba'));
INSERT INTO state(code, country, name) VALUES ('VC','CU',i18n('Villa Clara'));
-- country CV
INSERT INTO state(code, country, name) VALUES ('CV-1','CV',i18n('Cape Verde territory'));
-- country CX
INSERT INTO state(code, country, name) VALUES ('CX-1','CX',i18n('Christmas Island territory'));
-- country CY
INSERT INTO state(code, country, name) VALUES ('CY-1','CY',i18n('Cyprus territory'));
-- country CZ
INSERT INTO state(code, country, name) VALUES ('U ','CZ',i18n('Ustecky'));
INSERT INTO state(code, country, name) VALUES ('C ','CZ',i18n('Jihocesky'));
INSERT INTO state(code, country, name) VALUES ('B ','CZ',i18n('Jihomoravsky'));
INSERT INTO state(code, country, name) VALUES ('K ','CZ',i18n('Karlovarsky'));
INSERT INTO state(code, country, name) VALUES ('H ','CZ',i18n('Kralovehradecky'));
INSERT INTO state(code, country, name) VALUES ('L ','CZ',i18n('Liberecky'));
INSERT INTO state(code, country, name) VALUES ('T ','CZ',i18n('Moravskoslezsky'));
INSERT INTO state(code, country, name) VALUES ('M ','CZ',i18n('Olomoucky'));
INSERT INTO state(code, country, name) VALUES ('E ','CZ',i18n('Pardubicky'));
INSERT INTO state(code, country, name) VALUES ('P ','CZ',i18n('Plzensky'));
INSERT INTO state(code, country, name) VALUES ('A ','CZ',i18n('Praha'));
INSERT INTO state(code, country, name) VALUES ('S ','CZ',i18n('Stredocesky'));
INSERT INTO state(code, country, name) VALUES ('J ','CZ',i18n('Vysocina'));
INSERT INTO state(code, country, name) VALUES ('Z ','CZ',i18n('Zlinsky'));
-- country DJ
INSERT INTO state(code, country, name) VALUES ('DJ-1','DJ',i18n('Djibouti territory'));
-- country DK
INSERT INTO state(code, country, name) VALUES ('AR','DK',i18n('Arhus'));
INSERT INTO state(code, country, name) VALUES ('BO','DK',i18n('Bornholm'));
INSERT INTO state(code, country, name) VALUES ('FR','DK',i18n('Frederiksborg'));
INSERT INTO state(code, country, name) VALUES ('FY','DK',i18n('Fyn'));
INSERT INTO state(code, country, name) VALUES ('KO','DK',i18n('Kobenhavn'));
INSERT INTO state(code, country, name) VALUES ('NO','DK',i18n('Nordjylland'));
INSERT INTO state(code, country, name) VALUES ('RI','DK',i18n('Ribe'));
INSERT INTO state(code, country, name) VALUES ('RK','DK',i18n('Ringkobing'));
INSERT INTO state(code, country, name) VALUES ('RO','DK',i18n('Roskilde'));
INSERT INTO state(code, country, name) VALUES ('SO','DK',i18n('Sonderjylland'));
INSERT INTO state(code, country, name) VALUES ('ST','DK',i18n('Storstrom'));
INSERT INTO state(code, country, name) VALUES ('VE','DK',i18n('Vejle'));
INSERT INTO state(code, country, name) VALUES ('VJ','DK',i18n('Vestjælland'));
INSERT INTO state(code, country, name) VALUES ('VI','DK',i18n('Viborg'));
-- country DM
INSERT INTO state(code, country, name) VALUES ('DM-1','DM',i18n('Dominica territory'));
-- country DO
INSERT INTO state(code, country, name) VALUES ('DO-1','DO',i18n('Dominican Republic territory'));
-- country DZ
INSERT INTO state(code, country, name) VALUES ('AD','DZ',i18n('Adrar'));
INSERT INTO state(code, country, name) VALUES ('AI','DZ',i18n('Ain Defla'));
INSERT INTO state(code, country, name) VALUES ('AT','DZ',i18n('Ain Temouchent'));
INSERT INTO state(code, country, name) VALUES ('AL','DZ',i18n('Alger'));
INSERT INTO state(code, country, name) VALUES ('AN','DZ',i18n('Annaba'));
INSERT INTO state(code, country, name) VALUES ('BA','DZ',i18n('Batna'));
INSERT INTO state(code, country, name) VALUES ('BE','DZ',i18n('Bechar'));
INSERT INTO state(code, country, name) VALUES ('BJ','DZ',i18n('Bejaia'));
INSERT INTO state(code, country, name) VALUES ('BI','DZ',i18n('Biskra'));
INSERT INTO state(code, country, name) VALUES ('BL','DZ',i18n('Blida'));
INSERT INTO state(code, country, name) VALUES ('BB','DZ',i18n('Bordj Bou Arreridj'));
INSERT INTO state(code, country, name) VALUES ('BO','DZ',i18n('Bouira'));
INSERT INTO state(code, country, name) VALUES ('BU','DZ',i18n('Boumerdes'));
INSERT INTO state(code, country, name) VALUES ('CH','DZ',i18n('Chlef'));
INSERT INTO state(code, country, name) VALUES ('CO','DZ',i18n('Constantine'));
INSERT INTO state(code, country, name) VALUES ('DJ','DZ',i18n('Djelfa'));
INSERT INTO state(code, country, name) VALUES ('EB','DZ',i18n('El Bayadh'));
INSERT INTO state(code, country, name) VALUES ('EO','DZ',i18n('El Oued'));
INSERT INTO state(code, country, name) VALUES ('ET','DZ',i18n('El Tarf'));
INSERT INTO state(code, country, name) VALUES ('GH','DZ',i18n('Ghardaia'));
INSERT INTO state(code, country, name) VALUES ('GU','DZ',i18n('Guelma'));
INSERT INTO state(code, country, name) VALUES ('IL','DZ',i18n('Illizi'));
INSERT INTO state(code, country, name) VALUES ('JI','DZ',i18n('Jijel'));
INSERT INTO state(code, country, name) VALUES ('KH','DZ',i18n('Khenchela'));
INSERT INTO state(code, country, name) VALUES ('LA','DZ',i18n('Laghouat'));
INSERT INTO state(code, country, name) VALUES ('MS','DZ',i18n('M''Sila'));
INSERT INTO state(code, country, name) VALUES ('MA','DZ',i18n('Mascara'));
INSERT INTO state(code, country, name) VALUES ('ME','DZ',i18n('Medea'));
INSERT INTO state(code, country, name) VALUES ('MI','DZ',i18n('Mila'));
INSERT INTO state(code, country, name) VALUES ('MO','DZ',i18n('Mostaganem'));
INSERT INTO state(code, country, name) VALUES ('NA','DZ',i18n('Naama'));
INSERT INTO state(code, country, name) VALUES ('OR','DZ',i18n('Oran'));
INSERT INTO state(code, country, name) VALUES ('OU','DZ',i18n('Ouargla'));
INSERT INTO state(code, country, name) VALUES ('OB','DZ',i18n('Oum el Bouaghi'));
INSERT INTO state(code, country, name) VALUES ('RE','DZ',i18n('Relizane'));
INSERT INTO state(code, country, name) VALUES ('SA','DZ',i18n('Saida'));
INSERT INTO state(code, country, name) VALUES ('SE','DZ',i18n('Setif'));
INSERT INTO state(code, country, name) VALUES ('SB','DZ',i18n('Sidi Bel Abbes'));
INSERT INTO state(code, country, name) VALUES ('SK','DZ',i18n('Skikda'));
INSERT INTO state(code, country, name) VALUES ('TA','DZ',i18n('Tamanghasset'));
INSERT INTO state(code, country, name) VALUES ('TE','DZ',i18n('Tebessa'));
INSERT INTO state(code, country, name) VALUES ('TI','DZ',i18n('Tiaret'));
INSERT INTO state(code, country, name) VALUES ('TN','DZ',i18n('Tindouf'));
INSERT INTO state(code, country, name) VALUES ('TP','DZ',i18n('Tipaza'));
INSERT INTO state(code, country, name) VALUES ('TS','DZ',i18n('Tissemsilt'));
INSERT INTO state(code, country, name) VALUES ('TO','DZ',i18n('Tizi Ouzou'));
INSERT INTO state(code, country, name) VALUES ('TL','DZ',i18n('Tlemcen'));
-- country EC
INSERT INTO state(code, country, name) VALUES ('EC-1','EC',i18n('Ecuador territory'));
-- country EE
INSERT INTO state(code, country, name) VALUES ('HA','EE',i18n('Harjumaa (Tallinn)'));
INSERT INTO state(code, country, name) VALUES ('HI','EE',i18n('Hiiumaa (Kardla)'));
INSERT INTO state(code, country, name) VALUES ('IV','EE',i18n('Ida-Virumaa (Johvi)'));
INSERT INTO state(code, country, name) VALUES ('JA','EE',i18n('Jarvamaa (Paide)'));
INSERT INTO state(code, country, name) VALUES ('JO','EE',i18n('Jogevamaa (Jogeva)'));
INSERT INTO state(code, country, name) VALUES ('LV','EE',i18n('Laane-Virumaa (Rakvere)'));
INSERT INTO state(code, country, name) VALUES ('LA','EE',i18n('Laanemaa (Haapsalu)'));
INSERT INTO state(code, country, name) VALUES ('PA','EE',i18n('Parnumaa (Parnu)'));
INSERT INTO state(code, country, name) VALUES ('PO','EE',i18n('Polvamaa (Polva)'));
INSERT INTO state(code, country, name) VALUES ('RA','EE',i18n('Raplamaa (Rapla)'));
INSERT INTO state(code, country, name) VALUES ('SA','EE',i18n('Saaremaa (Kuessaare)'));
INSERT INTO state(code, country, name) VALUES ('TA','EE',i18n('Tartumaa (Tartu)'));
INSERT INTO state(code, country, name) VALUES ('VA','EE',i18n('Valgamaa (Valga)'));
INSERT INTO state(code, country, name) VALUES ('VI','EE',i18n('Viljandimaa (Viljandi)'));
INSERT INTO state(code, country, name) VALUES ('VO','EE',i18n('Vorumaa (Voru)'));
-- country EG
INSERT INTO state(code, country, name) VALUES ('EG-1','EG',i18n('Egypt territory'));
-- country EH
--INSERT INTO state(code, country, name) VALUES ('EH-1','EH',i18n('which country !!!'));
-- country ER
INSERT INTO state(code, country, name) VALUES ('ER-1','ER',i18n('Eritrea territory'));
-- country ET
INSERT INTO state(code, country, name) VALUES ('ET-1','ET',i18n('Ethiopia territory'));
-- country FI
INSERT INTO state(code, country, name) VALUES ('AL','FI',i18n('Aland'));
INSERT INTO state(code, country, name) VALUES ('ES','FI',i18n('Etela-Suomen Laani'));
INSERT INTO state(code, country, name) VALUES ('IS','FI',i18n('Ita-Suomen Laani'));
INSERT INTO state(code, country, name) VALUES ('LS','FI',i18n('Lansi-Suomen Laani'));
INSERT INTO state(code, country, name) VALUES ('LA','FI',i18n('Lappi'));
INSERT INTO state(code, country, name) VALUES ('OU','FI',i18n('Oulun Laani'));
-- country FJ
INSERT INTO state(code, country, name) VALUES ('FJ-1','FJ',i18n('Fiji territory'));
-- country FK
INSERT INTO state(code, country, name) VALUES ('FK-1','FK',i18n('Falkland Islands (Malvinas) territory'));
-- country FM
INSERT INTO state(code, country, name) VALUES ('FM-1','FM',i18n('Micronesia, Federated States Of, territory'));
-- country FO
INSERT INTO state(code, country, name) VALUES ('FO-1','FO',i18n('Faroe Islands territory'));
-- country FR
INSERT INTO state(code, country, name) VALUES ('AL','FR',i18n('Alsace'));
INSERT INTO state(code, country, name) VALUES ('AQ','FR',i18n('Aquitaine'));
INSERT INTO state(code, country, name) VALUES ('AU','FR',i18n('Auvergne'));
INSERT INTO state(code, country, name) VALUES ('BR','FR',i18n('Brittany'));
INSERT INTO state(code, country, name) VALUES ('BU','FR',i18n('Burgundy'));
INSERT INTO state(code, country, name) VALUES ('CE','FR',i18n('Center Loire Valley'));
INSERT INTO state(code, country, name) VALUES ('CH','FR',i18n('Champagne'));
INSERT INTO state(code, country, name) VALUES ('CO','FR',i18n('Corse'));
INSERT INTO state(code, country, name) VALUES ('FR','FR',i18n('France Comte'));
INSERT INTO state(code, country, name) VALUES ('LA','FR',i18n('Languedoc Roussillon'));
INSERT INTO state(code, country, name) VALUES ('LI','FR',i18n('Limousin'));
INSERT INTO state(code, country, name) VALUES ('LO','FR',i18n('Lorraine'));
INSERT INTO state(code, country, name) VALUES ('MI','FR',i18n('Midi Pyrenees'));
INSERT INTO state(code, country, name) VALUES ('NO','FR',i18n('Nord Pas de Calais'));
INSERT INTO state(code, country, name) VALUES ('NR','FR',i18n('Normandy'));
INSERT INTO state(code, country, name) VALUES ('PA','FR',i18n('Paris / Ill de France'));
INSERT INTO state(code, country, name) VALUES ('PI','FR',i18n('Picardie'));
INSERT INTO state(code, country, name) VALUES ('PO','FR',i18n('Poitou Charente'));
INSERT INTO state(code, country, name) VALUES ('PR','FR',i18n('Provence'));
INSERT INTO state(code, country, name) VALUES ('RH','FR',i18n('Rhone Alps'));
INSERT INTO state(code, country, name) VALUES ('RI','FR',i18n('Riviera'));
INSERT INTO state(code, country, name) VALUES ('WE','FR',i18n('Western Loire Valley'));
-- country FX
-- INSERT INTO state(code, country, name) VALUES ('FX-1','FX',i18n('StateNameStub'));
-- country GA
INSERT INTO state(code, country, name) VALUES ('GA-1','GA',i18n('Gabon territory'));
-- country GB
INSERT INTO state(code, country, name) VALUES ('AB','GB',i18n('Aberdeen'));
--INSERT INTO state(code, country, name) VALUES ('AB','GB',i18n('Aberdeenshire'));
INSERT INTO state(code, country, name) VALUES ('AN','GB',i18n('Anglesey'));
INSERT INTO state(code, country, name) VALUES ('AG','GB',i18n('Angus'));
INSERT INTO state(code, country, name) VALUES ('AR','GB',i18n('Argyll and Bute'));
INSERT INTO state(code, country, name) VALUES ('BE','GB',i18n('Bedfordshire'));
--INSERT INTO state(code, country, name) VALUES ('BE','GB',i18n('Berkshire'));
INSERT INTO state(code, country, name) VALUES ('BL','GB',i18n('Blaenau Gwent'));
INSERT INTO state(code, country, name) VALUES ('BR','GB',i18n('Bridgend'));
INSERT INTO state(code, country, name) VALUES ('BS','GB',i18n('Bristol'));
INSERT INTO state(code, country, name) VALUES ('BU','GB',i18n('Buckinghamshire'));
INSERT INTO state(code, country, name) VALUES ('CA','GB',i18n('Caerphilly'));
--INSERT INTO state(code, country, name) VALUES ('CA','GB',i18n('Cambridgeshire'));
--INSERT INTO state(code, country, name) VALUES ('CA','GB',i18n('Carmarthenshire'));
INSERT INTO state(code, country, name) VALUES ('CD','GB',i18n('Cardiff'));
--INSERT INTO state(code, country, name) VALUES ('CD','GB',i18n('Ceredigion'));
INSERT INTO state(code, country, name) VALUES ('CH','GB',i18n('Cheshire'));
INSERT INTO state(code, country, name) VALUES ('CL','GB',i18n('Clackmannanshire'));
INSERT INTO state(code, country, name) VALUES ('CO','GB',i18n('Conwy'));
--INSERT INTO state(code, country, name) VALUES ('CO','GB',i18n('Cornwall'));
INSERT INTO state(code, country, name) VALUES ('DN','GB',i18n('Denbighshire'));
INSERT INTO state(code, country, name) VALUES ('DE','GB',i18n('Derbyshire'));
INSERT INTO state(code, country, name) VALUES ('DV','GB',i18n('Devon'));
INSERT INTO state(code, country, name) VALUES ('DO','GB',i18n('Dorset'));
INSERT INTO state(code, country, name) VALUES ('DG','GB',i18n('Dumfries and Galloway'));
INSERT INTO state(code, country, name) VALUES ('DU','GB',i18n('Dundee'));
INSERT INTO state(code, country, name) VALUES ('DH','GB',i18n('Durham'));
--INSERT INTO state(code, country, name) VALUES ('AR','GB',i18n('East Ayrshire'));
--INSERT INTO state(code, country, name) VALUES ('DU','GB',i18n('East Dunbartonshire'));
INSERT INTO state(code, country, name) VALUES ('LO','GB',i18n('East Lothian'));
INSERT INTO state(code, country, name) VALUES ('RE','GB',i18n('East Renfrewshire'));
INSERT INTO state(code, country, name) VALUES ('ER','GB',i18n('East Riding of Yorkshire'));
INSERT INTO state(code, country, name) VALUES ('SX','GB',i18n('East Sussex'));
INSERT INTO state(code, country, name) VALUES ('ED','GB',i18n('Edinburgh'));
INSERT INTO state(code, country, name) VALUES ('ES','GB',i18n('Essex'));
INSERT INTO state(code, country, name) VALUES ('FA','GB',i18n('Falkirk'));
INSERT INTO state(code, country, name) VALUES ('FF','GB',i18n('Fife'));
INSERT INTO state(code, country, name) VALUES ('FL','GB',i18n('Flintshire'));
INSERT INTO state(code, country, name) VALUES ('GL','GB',i18n('Glasgow'));
--INSERT INTO state(code, country, name) VALUES ('GL','GB',i18n('Gloucestershire'));
INSERT INTO state(code, country, name) VALUES ('LD','GB',i18n('Greater London'));
INSERT INTO state(code, country, name) VALUES ('MC','GB',i18n('Greater Manchester'));
INSERT INTO state(code, country, name) VALUES ('GD','GB',i18n('Gwynedd'));
INSERT INTO state(code, country, name) VALUES ('HA','GB',i18n('Hampshire'));
INSERT INTO state(code, country, name) VALUES ('HW','GB',i18n('Herefordshire'));
INSERT INTO state(code, country, name) VALUES ('HE','GB',i18n('Hertfordshire'));
INSERT INTO state(code, country, name) VALUES ('HL','GB',i18n('Highlands'));
INSERT INTO state(code, country, name) VALUES ('IV','GB',i18n('Inverclyde'));
INSERT INTO state(code, country, name) VALUES ('IO','GB',i18n('Isle of Wight'));
INSERT INTO state(code, country, name) VALUES ('KN','GB',i18n('Kent'));
INSERT INTO state(code, country, name) VALUES ('LA','GB',i18n('Lancashire'));
INSERT INTO state(code, country, name) VALUES ('LE','GB',i18n('Leicestershire'));
INSERT INTO state(code, country, name) VALUES ('LI','GB',i18n('Lincolnshire'));
INSERT INTO state(code, country, name) VALUES ('MS','GB',i18n('Merseyside'));
INSERT INTO state(code, country, name) VALUES ('ME','GB',i18n('Merthyr Tydfil'));
INSERT INTO state(code, country, name) VALUES ('ML','GB',i18n('Midlothian'));
INSERT INTO state(code, country, name) VALUES ('MM','GB',i18n('Monmouthshire'));
INSERT INTO state(code, country, name) VALUES ('MO','GB',i18n('Moray'));
INSERT INTO state(code, country, name) VALUES ('NP','GB',i18n('Neath Port Talbot'));
INSERT INTO state(code, country, name) VALUES ('NE','GB',i18n('Newport'));
INSERT INTO state(code, country, name) VALUES ('NO','GB',i18n('Norfolk'));
--INSERT INTO state(code, country, name) VALUES ('AR','GB',i18n('North Ayrshire'));
--INSERT INTO state(code, country, name) VALUES ('LA','GB',i18n('North Lanarkshire'));
INSERT INTO state(code, country, name) VALUES ('YS','GB',i18n('North Yorkshire'));
INSERT INTO state(code, country, name) VALUES ('NH','GB',i18n('Northamptonshire'));
INSERT INTO state(code, country, name) VALUES ('NL','GB',i18n('Northumberland'));
--INSERT INTO state(code, country, name) VALUES ('NO','GB',i18n('Nottinghamshire'));
INSERT INTO state(code, country, name) VALUES ('OR','GB',i18n('Orkney Islands'));
INSERT INTO state(code, country, name) VALUES ('OF','GB',i18n('Oxfordshire'));
INSERT INTO state(code, country, name) VALUES ('PE','GB',i18n('Pembrokeshire'));
--INSERT INTO state(code, country, name) VALUES ('PE','GB',i18n('Perth and Kinross'));
INSERT INTO state(code, country, name) VALUES ('PW','GB',i18n('Powys'));
--INSERT INTO state(code, country, name) VALUES ('RE','GB',i18n('Renfrewshire'));
INSERT INTO state(code, country, name) VALUES ('RH','GB',i18n('Rhondda Cynon Taff'));
INSERT INTO state(code, country, name) VALUES ('RU','GB',i18n('Rutland'));
INSERT INTO state(code, country, name) VALUES ('BO','GB',i18n('Scottish Borders'));
INSERT INTO state(code, country, name) VALUES ('SH','GB',i18n('Shetland Islands'));
INSERT INTO state(code, country, name) VALUES ('SP','GB',i18n('Shropshire'));
INSERT INTO state(code, country, name) VALUES ('SO','GB',i18n('Somerset'));
--INSERT INTO state(code, country, name) VALUES ('AR','GB',i18n('South Ayrshire'));
--INSERT INTO state(code, country, name) VALUES ('LA','GB',i18n('South Lanarkshire'));
--INSERT INTO state(code, country, name) VALUES ('YS','GB',i18n('South Yorkshire'));
INSERT INTO state(code, country, name) VALUES ('SF','GB',i18n('Staffordshire'));
INSERT INTO state(code, country, name) VALUES ('ST','GB',i18n('Stirling'));
--INSERT INTO state(code, country, name) VALUES ('SF','GB',i18n('Suffolk'));
INSERT INTO state(code, country, name) VALUES ('SR','GB',i18n('Surrey'));
INSERT INTO state(code, country, name) VALUES ('SW','GB',i18n('Swansea'));
INSERT INTO state(code, country, name) VALUES ('TO','GB',i18n('Torfaen'));
INSERT INTO state(code, country, name) VALUES ('TW','GB',i18n('Tyne and Wear'));
INSERT INTO state(code, country, name) VALUES ('VG','GB',i18n('Vale of Glamorgan'));
INSERT INTO state(code, country, name) VALUES ('WA','GB',i18n('Warwickshire'));
INSERT INTO state(code, country, name) VALUES ('WD','GB',i18n('West Dunbartonshire'));
INSERT INTO state(code, country, name) VALUES ('WL','GB',i18n('West Lothian'));
INSERT INTO state(code, country, name) VALUES ('WM','GB',i18n('West Midlands'));
--INSERT INTO state(code, country, name) VALUES ('SX','GB',i18n('West Sussex'));
--INSERT INTO state(code, country, name) VALUES ('YS','GB',i18n('West Yorkshire'));
INSERT INTO state(code, country, name) VALUES ('WI','GB',i18n('Western Isles'));
--INSERT INTO state(code, country, name) VALUES ('WL','GB',i18n('Wiltshire'));
INSERT INTO state(code, country, name) VALUES ('WO','GB',i18n('Worcestershire'));
INSERT INTO state(code, country, name) VALUES ('WR','GB',i18n('Wrexham'));
-- country GD
INSERT INTO state(code, country, name) VALUES ('GD-1','GD',i18n('StateNameStub'));
-- country GE
INSERT INTO state(code, country, name) VALUES ('GE-1','GE',i18n('StateNameStub'));
-- country GF
INSERT INTO state(code, country, name) VALUES ('GF-1','GF',i18n('StateNameStub'));
-- country GH
INSERT INTO state(code, country, name) VALUES ('GH-1','GH',i18n('StateNameStub'));
-- country GI
INSERT INTO state(code, country, name) VALUES ('GI-1','GI',i18n('StateNameStub'));
-- country GL
INSERT INTO state(code, country, name) VALUES ('GL-1','GL',i18n('StateNameStub'));
-- country GM
INSERT INTO state(code, country, name) VALUES ('GM-1','GM',i18n('StateNameStub'));
-- country GN
INSERT INTO state(code, country, name) VALUES ('GN-1','GN',i18n('StateNameStub'));
-- country GP
INSERT INTO state(code, country, name) VALUES ('GP-1','GP',i18n('StateNameStub'));
-- country GQ
INSERT INTO state(code, country, name) VALUES ('GQ-1','GQ',i18n('StateNameStub'));
-- country GR
INSERT INTO state(code, country, name) VALUES ('AI','GR',i18n('Aitolia kai Akarnania'));
INSERT INTO state(code, country, name) VALUES ('AK','GR',i18n('Akhaia'));
INSERT INTO state(code, country, name) VALUES ('AG','GR',i18n('Argolis'));
INSERT INTO state(code, country, name) VALUES ('AD','GR',i18n('Arkadhia'));
INSERT INTO state(code, country, name) VALUES ('AR','GR',i18n('Arta'));
INSERT INTO state(code, country, name) VALUES ('AT','GR',i18n('Attiki'));
INSERT INTO state(code, country, name) VALUES ('AY','GR',i18n('Ayion Oros (Mt. Athos)'));
INSERT INTO state(code, country, name) VALUES ('DH','GR',i18n('Dhodhekanisos'));
INSERT INTO state(code, country, name) VALUES ('DR','GR',i18n('Drama'));
INSERT INTO state(code, country, name) VALUES ('ET','GR',i18n('Evritania'));
INSERT INTO state(code, country, name) VALUES ('ES','GR',i18n('Evros'));
INSERT INTO state(code, country, name) VALUES ('EV','GR',i18n('Evvoia'));
INSERT INTO state(code, country, name) VALUES ('FL','GR',i18n('Florina'));
INSERT INTO state(code, country, name) VALUES ('FO','GR',i18n('Fokis'));
INSERT INTO state(code, country, name) VALUES ('FT','GR',i18n('Fthiotis'));
INSERT INTO state(code, country, name) VALUES ('GR','GR',i18n('Grevena'));
INSERT INTO state(code, country, name) VALUES ('IL','GR',i18n('Ilia'));
INSERT INTO state(code, country, name) VALUES ('IM','GR',i18n('Imathia'));
INSERT INTO state(code, country, name) VALUES ('IO','GR',i18n('Ioannina'));
INSERT INTO state(code, country, name) VALUES ('IR','GR',i18n('Irakleion'));
INSERT INTO state(code, country, name) VALUES ('KA','GR',i18n('Kardhitsa'));
INSERT INTO state(code, country, name) VALUES ('KS','GR',i18n('Kastoria'));
INSERT INTO state(code, country, name) VALUES ('KV','GR',i18n('Kavala'));
INSERT INTO state(code, country, name) VALUES ('KE','GR',i18n('Kefallinia'));
INSERT INTO state(code, country, name) VALUES ('KR','GR',i18n('Kerkyra'));
INSERT INTO state(code, country, name) VALUES ('KH','GR',i18n('Khalkidhiki'));
INSERT INTO state(code, country, name) VALUES ('KN','GR',i18n('Khania'));
INSERT INTO state(code, country, name) VALUES ('KI','GR',i18n('Khios'));
INSERT INTO state(code, country, name) VALUES ('KK','GR',i18n('Kikladhes'));
INSERT INTO state(code, country, name) VALUES ('KL','GR',i18n('Kilkis'));
INSERT INTO state(code, country, name) VALUES ('KO','GR',i18n('Korinthia'));
INSERT INTO state(code, country, name) VALUES ('KZ','GR',i18n('Kozani'));
INSERT INTO state(code, country, name) VALUES ('LA','GR',i18n('Lakonia'));
INSERT INTO state(code, country, name) VALUES ('LR','GR',i18n('Larisa'));
INSERT INTO state(code, country, name) VALUES ('LS','GR',i18n('Lasithi'));
INSERT INTO state(code, country, name) VALUES ('LE','GR',i18n('Lesvos'));
INSERT INTO state(code, country, name) VALUES ('LV','GR',i18n('Levkas'));
INSERT INTO state(code, country, name) VALUES ('MA','GR',i18n('Magnisia'));
INSERT INTO state(code, country, name) VALUES ('ME','GR',i18n('Messinia'));
INSERT INTO state(code, country, name) VALUES ('PE','GR',i18n('Pella'));
INSERT INTO state(code, country, name) VALUES ('PI','GR',i18n('Pieria'));
INSERT INTO state(code, country, name) VALUES ('PR','GR',i18n('Preveza'));
INSERT INTO state(code, country, name) VALUES ('RE','GR',i18n('Rethimni'));
INSERT INTO state(code, country, name) VALUES ('RO','GR',i18n('Rodhopi'));
INSERT INTO state(code, country, name) VALUES ('SA','GR',i18n('Samos'));
INSERT INTO state(code, country, name) VALUES ('SE','GR',i18n('Serrai'));
INSERT INTO state(code, country, name) VALUES ('TH','GR',i18n('Thesprotia'));
INSERT INTO state(code, country, name) VALUES ('TS','GR',i18n('Thessaloniki'));
INSERT INTO state(code, country, name) VALUES ('TR','GR',i18n('Trikala'));
INSERT INTO state(code, country, name) VALUES ('VO','GR',i18n('Voiotia'));
INSERT INTO state(code, country, name) VALUES ('XA','GR',i18n('Xanthi'));
INSERT INTO state(code, country, name) VALUES ('ZA','GR',i18n('Zakinthos'));
-- country GS
INSERT INTO state(code, country, name) VALUES ('GS-1','GS',i18n('StateNameStub'));
-- country GT
INSERT INTO state(code, country, name) VALUES ('AV','GT',i18n('Alta Verapaz'));
INSERT INTO state(code, country, name) VALUES ('BV','GT',i18n('Baja Verapaz'));
INSERT INTO state(code, country, name) VALUES ('CH','GT',i18n('Chimaltenango'));
INSERT INTO state(code, country, name) VALUES ('CI','GT',i18n('Chiquimula'));
INSERT INTO state(code, country, name) VALUES ('EP','GT',i18n('El Progreso'));
INSERT INTO state(code, country, name) VALUES ('ES','GT',i18n('Escuintla'));
INSERT INTO state(code, country, name) VALUES ('GU','GT',i18n('Guatemala'));
INSERT INTO state(code, country, name) VALUES ('HU','GT',i18n('Huehuetenango'));
INSERT INTO state(code, country, name) VALUES ('IZ','GT',i18n('Izabal'));
INSERT INTO state(code, country, name) VALUES ('JA','GT',i18n('Jalapa'));
INSERT INTO state(code, country, name) VALUES ('JU','GT',i18n('Jutiapa'));
INSERT INTO state(code, country, name) VALUES ('PE','GT',i18n('Peten'));
INSERT INTO state(code, country, name) VALUES ('QU','GT',i18n('Quetzaltenango'));
INSERT INTO state(code, country, name) VALUES ('QI','GT',i18n('Quiche'));
INSERT INTO state(code, country, name) VALUES ('RE','GT',i18n('Retalhuleu'));
INSERT INTO state(code, country, name) VALUES ('SA','GT',i18n('Sacatepequez'));
INSERT INTO state(code, country, name) VALUES ('SM','GT',i18n('San Marcos'));
INSERT INTO state(code, country, name) VALUES ('SR','GT',i18n('Santa Rosa'));
INSERT INTO state(code, country, name) VALUES ('SO','GT',i18n('Solola'));
INSERT INTO state(code, country, name) VALUES ('SU','GT',i18n('Suchitepequez'));
INSERT INTO state(code, country, name) VALUES ('TO','GT',i18n('Totonicapan'));
INSERT INTO state(code, country, name) VALUES ('ZA','GT',i18n('Zacapa'));
-- country GU
INSERT INTO state(code, country, name) VALUES ('GU-1','GU',i18n('StateNameStub'));
-- country GW
INSERT INTO state(code, country, name) VALUES ('GW-1','GW',i18n('StateNameStub'));
-- country GY
INSERT INTO state(code, country, name) VALUES ('GY-1','GY',i18n('StateNameStub'));
-- country HK
INSERT INTO state(code, country, name) VALUES ('HK-1','HK',i18n('StateNameStub'));
-- country HM
INSERT INTO state(code, country, name) VALUES ('HM-1','HM',i18n('StateNameStub'));
-- country HN
INSERT INTO state(code, country, name) VALUES ('HN-1','HN',i18n('StateNameStub'));
-- country HR
INSERT INTO state(code, country, name) VALUES ('BB','HR',i18n('Bjelovar-Bilogora'));
INSERT INTO state(code, country, name) VALUES ('CZ','HR',i18n('City of Zagreb'));
INSERT INTO state(code, country, name) VALUES ('DN','HR',i18n('Dubrovnik-Neretva'));
INSERT INTO state(code, country, name) VALUES ('IS','HR',i18n('Istra'));
INSERT INTO state(code, country, name) VALUES ('KA','HR',i18n('Karlovac'));
INSERT INTO state(code, country, name) VALUES ('KK','HR',i18n('Koprivnica-Krizevci'));
INSERT INTO state(code, country, name) VALUES ('KZ','HR',i18n('Krapina-Zagorje'));
INSERT INTO state(code, country, name) VALUES ('LS','HR',i18n('Lika-Senj'));
INSERT INTO state(code, country, name) VALUES ('ME','HR',i18n('Medimurje'));
INSERT INTO state(code, country, name) VALUES ('OB','HR',i18n('Osijek-Baranja'));
INSERT INTO state(code, country, name) VALUES ('PS','HR',i18n('Pozega-Slavonia'));
INSERT INTO state(code, country, name) VALUES ('PG','HR',i18n('Primorje-Gorski Kotar'));
INSERT INTO state(code, country, name) VALUES ('SI','HR',i18n('Sibenik'));
INSERT INTO state(code, country, name) VALUES ('SM','HR',i18n('Sisak-Moslavina'));
INSERT INTO state(code, country, name) VALUES ('SB','HR',i18n('Slavonski Brod-Posavina'));
INSERT INTO state(code, country, name) VALUES ('SD','HR',i18n('Split-Dalmatia'));
INSERT INTO state(code, country, name) VALUES ('VA','HR',i18n('Varazdin'));
INSERT INTO state(code, country, name) VALUES ('VP','HR',i18n('Virovitica-Podravina'));
INSERT INTO state(code, country, name) VALUES ('VS','HR',i18n('Vukovar-Srijem'));
INSERT INTO state(code, country, name) VALUES ('ZK','HR',i18n('Zadar-Knin'));
INSERT INTO state(code, country, name) VALUES ('ZA','HR',i18n('Zagreb'));
-- country HT
INSERT INTO state(code, country, name) VALUES ('HT-1','HT',i18n('StateNameStub'));
-- country HU
INSERT INTO state(code, country, name) VALUES ('BK','HU',i18n('Bacs-Kiskun'));
INSERT INTO state(code, country, name) VALUES ('BA','HU',i18n('Baranya'));
INSERT INTO state(code, country, name) VALUES ('BE','HU',i18n('Bekes'));
INSERT INTO state(code, country, name) VALUES ('BS','HU',i18n('Bekescsaba'));
INSERT INTO state(code, country, name) VALUES ('BZ','HU',i18n('Borsod-Abauj-Zemplen'));
INSERT INTO state(code, country, name) VALUES ('BU','HU',i18n('Budapest'));
INSERT INTO state(code, country, name) VALUES ('CS','HU',i18n('Csongrad'));
INSERT INTO state(code, country, name) VALUES ('DE','HU',i18n('Debrecen'));
INSERT INTO state(code, country, name) VALUES ('DU','HU',i18n('Dunaujvaros'));
INSERT INTO state(code, country, name) VALUES ('EG','HU',i18n('Eger'));
INSERT INTO state(code, country, name) VALUES ('FE','HU',i18n('Fejer'));
INSERT INTO state(code, country, name) VALUES ('GY','HU',i18n('Gyor'));
INSERT INTO state(code, country, name) VALUES ('GM','HU',i18n('Gyor-Moson-Sopron'));
INSERT INTO state(code, country, name) VALUES ('HB','HU',i18n('Hajdu-Bihar'));
INSERT INTO state(code, country, name) VALUES ('HE','HU',i18n('Heves'));
INSERT INTO state(code, country, name) VALUES ('HO','HU',i18n('Hodmezovasarhely'));
INSERT INTO state(code, country, name) VALUES ('JN','HU',i18n('Jasz-Nagykun-Szolnok'));
INSERT INTO state(code, country, name) VALUES ('KA','HU',i18n('Kaposvar'));
INSERT INTO state(code, country, name) VALUES ('KE','HU',i18n('Kecskemet'));
INSERT INTO state(code, country, name) VALUES ('KO','HU',i18n('Komarom-Esztergom'));
INSERT INTO state(code, country, name) VALUES ('MI','HU',i18n('Miskolc'));
INSERT INTO state(code, country, name) VALUES ('NA','HU',i18n('Nagykanizsa'));
INSERT INTO state(code, country, name) VALUES ('NO','HU',i18n('Nograd'));
INSERT INTO state(code, country, name) VALUES ('NY','HU',i18n('Nyiregyhaza'));
INSERT INTO state(code, country, name) VALUES ('PE','HU',i18n('Pecs'));
INSERT INTO state(code, country, name) VALUES ('PS','HU',i18n('Pest'));
INSERT INTO state(code, country, name) VALUES ('SO','HU',i18n('Somogy'));
INSERT INTO state(code, country, name) VALUES ('SP','HU',i18n('Sopron'));
INSERT INTO state(code, country, name) VALUES ('SS','HU',i18n('Szabolcs-Szatmar-Bereg'));
INSERT INTO state(code, country, name) VALUES ('SZ','HU',i18n('Szeged'));
INSERT INTO state(code, country, name) VALUES ('SE','HU',i18n('Szekesfehervar'));
INSERT INTO state(code, country, name) VALUES ('SL','HU',i18n('Szolnok'));
INSERT INTO state(code, country, name) VALUES ('SM','HU',i18n('Szombathely'));
INSERT INTO state(code, country, name) VALUES ('TA','HU',i18n('Tatabanya'));
INSERT INTO state(code, country, name) VALUES ('TO','HU',i18n('Tolna'));
INSERT INTO state(code, country, name) VALUES ('VA','HU',i18n('Vas'));
INSERT INTO state(code, country, name) VALUES ('VE','HU',i18n('Veszprem'));
INSERT INTO state(code, country, name) VALUES ('ZA','HU',i18n('Zala'));
INSERT INTO state(code, country, name) VALUES ('ZZ','HU',i18n('Zalaegerszeg'));
-- country ID
INSERT INTO state(code, country, name) VALUES ('AC','ID',i18n('Aceh'));
INSERT INTO state(code, country, name) VALUES ('BA','ID',i18n('Bali'));
INSERT INTO state(code, country, name) VALUES ('BT','ID',i18n('Banten'));
INSERT INTO state(code, country, name) VALUES ('BE','ID',i18n('Bengkulu'));
INSERT INTO state(code, country, name) VALUES ('BD','ID',i18n('BoDeTaBek'));
INSERT INTO state(code, country, name) VALUES ('GO','ID',i18n('Gorontalo'));
INSERT INTO state(code, country, name) VALUES ('JK','ID',i18n('Jakarta Raya'));
INSERT INTO state(code, country, name) VALUES ('JA','ID',i18n('Jambi'));
INSERT INTO state(code, country, name) VALUES ('JB','ID',i18n('Jawa Barat'));
INSERT INTO state(code, country, name) VALUES ('JT','ID',i18n('Jawa Tengah'));
INSERT INTO state(code, country, name) VALUES ('JI','ID',i18n('Jawa Timur'));
INSERT INTO state(code, country, name) VALUES ('KB','ID',i18n('Kalimantan Barat'));
INSERT INTO state(code, country, name) VALUES ('KS','ID',i18n('Kalimantan Selatan'));
INSERT INTO state(code, country, name) VALUES ('KT','ID',i18n('Kalimantan Tengah'));
INSERT INTO state(code, country, name) VALUES ('KI','ID',i18n('Kalimantan Timur'));
INSERT INTO state(code, country, name) VALUES ('BB','ID',i18n('Kepulauan Bangka Belitung'));
INSERT INTO state(code, country, name) VALUES ('LA','ID',i18n('Lampung'));
INSERT INTO state(code, country, name) VALUES ('MA','ID',i18n('Maluku'));
INSERT INTO state(code, country, name) VALUES ('MU','ID',i18n('Maluku Utara'));
INSERT INTO state(code, country, name) VALUES ('NB','ID',i18n('Nusa Tenggara Barat'));
INSERT INTO state(code, country, name) VALUES ('NT','ID',i18n('Nusa Tenggara Timur'));
INSERT INTO state(code, country, name) VALUES ('PA','ID',i18n('Papua'));
INSERT INTO state(code, country, name) VALUES ('RI','ID',i18n('Riau'));
INSERT INTO state(code, country, name) VALUES ('SN','ID',i18n('Sulawesi Selatan'));
INSERT INTO state(code, country, name) VALUES ('ST','ID',i18n('Sulawesi Tengah'));
INSERT INTO state(code, country, name) VALUES ('SG','ID',i18n('Sulawesi Tenggara'));
INSERT INTO state(code, country, name) VALUES ('SA','ID',i18n('Sulawesi Utara'));
INSERT INTO state(code, country, name) VALUES ('SB','ID',i18n('Sumatera Barat'));
INSERT INTO state(code, country, name) VALUES ('SS','ID',i18n('Sumatera Selatan'));
INSERT INTO state(code, country, name) VALUES ('SU','ID',i18n('Sumatera Utara'));
INSERT INTO state(code, country, name) VALUES ('YO','ID',i18n('Yogyakarta'));
-- country IE
INSERT INTO state(code, country, name) VALUES ('CA','IE',i18n('Carlow'));
INSERT INTO state(code, country, name) VALUES ('CV','IE',i18n('Cavan'));
INSERT INTO state(code, country, name) VALUES ('CL','IE',i18n('Clare'));
INSERT INTO state(code, country, name) VALUES ('CO','IE',i18n('Cork'));
INSERT INTO state(code, country, name) VALUES ('DO','IE',i18n('Donegal'));
INSERT INTO state(code, country, name) VALUES ('DU','IE',i18n('Dublin'));
INSERT INTO state(code, country, name) VALUES ('GA','IE',i18n('Galway'));
INSERT INTO state(code, country, name) VALUES ('KE','IE',i18n('Kerry'));
INSERT INTO state(code, country, name) VALUES ('KI','IE',i18n('Kildare'));
INSERT INTO state(code, country, name) VALUES ('KL','IE',i18n('Kilkenny'));
INSERT INTO state(code, country, name) VALUES ('LA','IE',i18n('Laois'));
INSERT INTO state(code, country, name) VALUES ('LE','IE',i18n('Leitrim'));
INSERT INTO state(code, country, name) VALUES ('LI','IE',i18n('Limerick'));
INSERT INTO state(code, country, name) VALUES ('LO','IE',i18n('Longford'));
INSERT INTO state(code, country, name) VALUES ('LU','IE',i18n('Louth'));
INSERT INTO state(code, country, name) VALUES ('MA','IE',i18n('Mayo'));
INSERT INTO state(code, country, name) VALUES ('ME','IE',i18n('Meath'));
INSERT INTO state(code, country, name) VALUES ('MO','IE',i18n('Monaghan'));
INSERT INTO state(code, country, name) VALUES ('OF','IE',i18n('Offaly'));
INSERT INTO state(code, country, name) VALUES ('RO','IE',i18n('Roscommon'));
INSERT INTO state(code, country, name) VALUES ('SL','IE',i18n('Sligo'));
INSERT INTO state(code, country, name) VALUES ('TI','IE',i18n('Tipperary'));
INSERT INTO state(code, country, name) VALUES ('WA','IE',i18n('Waterford'));
INSERT INTO state(code, country, name) VALUES ('WE','IE',i18n('Westmeath'));
INSERT INTO state(code, country, name) VALUES ('WX','IE',i18n('Wexford'));
INSERT INTO state(code, country, name) VALUES ('WI','IE',i18n('Wicklow'));
-- country IL
INSERT INTO state(code, country, name) VALUES ('BS','IL',i18n('Be''er Sheva'));
INSERT INTO state(code, country, name) VALUES ('BH','IL',i18n('Bika''at Hayarden'));
INSERT INTO state(code, country, name) VALUES ('EA','IL',i18n('Eilat and Arava'));
INSERT INTO state(code, country, name) VALUES ('GA','IL',i18n('Galil'));
INSERT INTO state(code, country, name) VALUES ('HA','IL',i18n('Haifa'));
INSERT INTO state(code, country, name) VALUES ('JM','IL',i18n('Jehuda Mountains'));
INSERT INTO state(code, country, name) VALUES ('JE','IL',i18n('Jerusalem'));
INSERT INTO state(code, country, name) VALUES ('NE','IL',i18n('Negev'));
INSERT INTO state(code, country, name) VALUES ('SE','IL',i18n('Semaria'));
INSERT INTO state(code, country, name) VALUES ('SH','IL',i18n('Sharon'));
INSERT INTO state(code, country, name) VALUES ('TA','IL',i18n('Tel Aviv (Gosh Dan)'));
-- country IN
INSERT INTO state(code, country, name) VALUES ('AN','IN',i18n('Andaman and Nicobar Islands'));
INSERT INTO state(code, country, name) VALUES ('AP','IN',i18n('Andhra Pradesh'));
INSERT INTO state(code, country, name) VALUES ('AR','IN',i18n('Arunachal Pradesh'));
INSERT INTO state(code, country, name) VALUES ('AS','IN',i18n('Assam'));
INSERT INTO state(code, country, name) VALUES ('BI','IN',i18n('Bihar'));
INSERT INTO state(code, country, name) VALUES ('CH','IN',i18n('Chandigarh'));
INSERT INTO state(code, country, name) VALUES ('DA','IN',i18n('Dadra and Nagar Haveli'));
INSERT INTO state(code, country, name) VALUES ('DM','IN',i18n('Daman and Diu'));
INSERT INTO state(code, country, name) VALUES ('DE','IN',i18n('Delhi'));
INSERT INTO state(code, country, name) VALUES ('GO','IN',i18n('Goa'));
INSERT INTO state(code, country, name) VALUES ('GU','IN',i18n('Gujarat'));
INSERT INTO state(code, country, name) VALUES ('HA','IN',i18n('Haryana'));
INSERT INTO state(code, country, name) VALUES ('HP','IN',i18n('Himachal Pradesh'));
INSERT INTO state(code, country, name) VALUES ('JA','IN',i18n('Jammu and Kashmir'));
INSERT INTO state(code, country, name) VALUES ('KA','IN',i18n('Karnataka'));
INSERT INTO state(code, country, name) VALUES ('KE','IN',i18n('Kerala'));
INSERT INTO state(code, country, name) VALUES ('LI','IN',i18n('Lakshadweep Islands'));
INSERT INTO state(code, country, name) VALUES ('MP','IN',i18n('Madhya Pradesh'));
INSERT INTO state(code, country, name) VALUES ('MA','IN',i18n('Maharashtra'));
INSERT INTO state(code, country, name) VALUES ('MN','IN',i18n('Manipur'));
INSERT INTO state(code, country, name) VALUES ('ME','IN',i18n('Meghalaya'));
INSERT INTO state(code, country, name) VALUES ('MI','IN',i18n('Mizoram'));
INSERT INTO state(code, country, name) VALUES ('NA','IN',i18n('Nagaland'));
INSERT INTO state(code, country, name) VALUES ('OR','IN',i18n('Orissa'));
INSERT INTO state(code, country, name) VALUES ('PO','IN',i18n('Pondicherry'));
INSERT INTO state(code, country, name) VALUES ('PU','IN',i18n('Punjab'));
INSERT INTO state(code, country, name) VALUES ('RA','IN',i18n('Rajasthan'));
INSERT INTO state(code, country, name) VALUES ('SI','IN',i18n('Sikkim'));
INSERT INTO state(code, country, name) VALUES ('TN','IN',i18n('Tamil Nadu'));
INSERT INTO state(code, country, name) VALUES ('TR','IN',i18n('Tripura'));
INSERT INTO state(code, country, name) VALUES ('UP','IN',i18n('Uttar Pradesh'));
INSERT INTO state(code, country, name) VALUES ('WB','IN',i18n('West Bengal'));
-- country IO
INSERT INTO state(code, country, name) VALUES ('IO-1','IO',i18n('StateNameStub'));
-- country IQ
INSERT INTO state(code, country, name) VALUES ('IQ-1','IQ',i18n('StateNameStub'));
-- country IR
INSERT INTO state(code, country, name) VALUES ('IR-1','IR',i18n('StateNameStub'));
-- country IS
INSERT INTO state(code, country, name) VALUES ('IS-1','IS',i18n('StateNameStub'));
-- country IT
INSERT INTO state(code, country, name) VALUES ('AB','IT',i18n('Abruzzo'));
INSERT INTO state(code, country, name) VALUES ('BA','IT',i18n('Basilicata'));
INSERT INTO state(code, country, name) VALUES ('CA','IT',i18n('Calabria'));
INSERT INTO state(code, country, name) VALUES ('CP','IT',i18n('Campania'));
INSERT INTO state(code, country, name) VALUES ('ER','IT',i18n('Emilia Romagna'));
INSERT INTO state(code, country, name) VALUES ('FV','IT',i18n('Friuli-Venezia Giulia'));
INSERT INTO state(code, country, name) VALUES ('LA','IT',i18n('Lazio (Latium & Rome)'));
INSERT INTO state(code, country, name) VALUES ('TM','IT',i18n('Le Marche (The Marches)'));
INSERT INTO state(code, country, name) VALUES ('LI','IT',i18n('Liguria'));
INSERT INTO state(code, country, name) VALUES ('LO','IT',i18n('Lombardia (Lombardy)'));
INSERT INTO state(code, country, name) VALUES ('MO','IT',i18n('Molise'));
INSERT INTO state(code, country, name) VALUES ('PI','IT',i18n('Piemonte (Piedmont)'));
INSERT INTO state(code, country, name) VALUES ('AP','IT',i18n('Puglia (Apulia)'));
INSERT INTO state(code, country, name) VALUES ('SA','IT',i18n('Sardegna (Sardinia)'));
INSERT INTO state(code, country, name) VALUES ('SI','IT',i18n('Sicilia (Sicily)'));
INSERT INTO state(code, country, name) VALUES ('TU','IT',i18n('Toscana (Tuscany)'));
INSERT INTO state(code, country, name) VALUES ('TR','IT',i18n('Trentino Alto Adige'));
INSERT INTO state(code, country, name) VALUES ('UM','IT',i18n('Umbria'));
INSERT INTO state(code, country, name) VALUES ('VA','IT',i18n('Val d''Aosta'));
INSERT INTO state(code, country, name) VALUES ('VE','IT',i18n('Veneto'));
-- country JM
INSERT INTO state(code, country, name) VALUES ('JM-1','JM',i18n('StateNameStub'));
-- country JO
INSERT INTO state(code, country, name) VALUES ('AM','JO',i18n('Amman'));
INSERT INTO state(code, country, name) VALUES ('AJ','JO',i18n('Ajlun'));
INSERT INTO state(code, country, name) VALUES ('AA','JO',i18n('Al ''Aqabah'));
INSERT INTO state(code, country, name) VALUES ('AB','JO',i18n('Al Balqa'''));
INSERT INTO state(code, country, name) VALUES ('AK','JO',i18n('Al Karak'));
INSERT INTO state(code, country, name) VALUES ('AL','JO',i18n('Al Mafraq'));
INSERT INTO state(code, country, name) VALUES ('AT','JO',i18n('At Tafilah'));
INSERT INTO state(code, country, name) VALUES ('AZ','JO',i18n('Az Zarqa'''));
INSERT INTO state(code, country, name) VALUES ('IR','JO',i18n('Irbid'));
INSERT INTO state(code, country, name) VALUES ('JA','JO',i18n('Jarash'));
INSERT INTO state(code, country, name) VALUES ('MA','JO',i18n('Ma''an'));
INSERT INTO state(code, country, name) VALUES ('MD','JO',i18n('Madaba'));
-- country JP
INSERT INTO state(code, country, name) VALUES ('AI','JP',i18n('Aichi'));
INSERT INTO state(code, country, name) VALUES ('AK','JP',i18n('Akita'));
INSERT INTO state(code, country, name) VALUES ('AO','JP',i18n('Aomori'));
INSERT INTO state(code, country, name) VALUES ('CH','JP',i18n('Chiba'));
INSERT INTO state(code, country, name) VALUES ('EH','JP',i18n('Ehime'));
INSERT INTO state(code, country, name) VALUES ('FK','JP',i18n('Fukui'));
INSERT INTO state(code, country, name) VALUES ('FU','JP',i18n('Fukuoka'));
INSERT INTO state(code, country, name) VALUES ('FS','JP',i18n('Fukushima'));
INSERT INTO state(code, country, name) VALUES ('GI','JP',i18n('Gifu'));
INSERT INTO state(code, country, name) VALUES ('GU','JP',i18n('Gumma'));
INSERT INTO state(code, country, name) VALUES ('HI','JP',i18n('Hiroshima'));
INSERT INTO state(code, country, name) VALUES ('HO','JP',i18n('Hokkaido'));
INSERT INTO state(code, country, name) VALUES ('HY','JP',i18n('Hyogo'));
INSERT INTO state(code, country, name) VALUES ('IB','JP',i18n('Ibaraki'));
INSERT INTO state(code, country, name) VALUES ('IS','JP',i18n('Ishikawa'));
INSERT INTO state(code, country, name) VALUES ('IW','JP',i18n('Iwate'));
INSERT INTO state(code, country, name) VALUES ('KA','JP',i18n('Kagawa'));
INSERT INTO state(code, country, name) VALUES ('KG','JP',i18n('Kagoshima'));
INSERT INTO state(code, country, name) VALUES ('KN','JP',i18n('Kanagawa'));
INSERT INTO state(code, country, name) VALUES ('KO','JP',i18n('Kochi'));
INSERT INTO state(code, country, name) VALUES ('KU','JP',i18n('Kumamoto'));
INSERT INTO state(code, country, name) VALUES ('KY','JP',i18n('Kyoto'));
INSERT INTO state(code, country, name) VALUES ('MI','JP',i18n('Mie'));
INSERT INTO state(code, country, name) VALUES ('MY','JP',i18n('Miyagi'));
INSERT INTO state(code, country, name) VALUES ('MZ','JP',i18n('Miyazaki'));
INSERT INTO state(code, country, name) VALUES ('NA','JP',i18n('Nagano'));
INSERT INTO state(code, country, name) VALUES ('NG','JP',i18n('Nagasaki'));
INSERT INTO state(code, country, name) VALUES ('NR','JP',i18n('Nara'));
INSERT INTO state(code, country, name) VALUES ('NI','JP',i18n('Niigata'));
INSERT INTO state(code, country, name) VALUES ('OI','JP',i18n('Oita'));
INSERT INTO state(code, country, name) VALUES ('OK','JP',i18n('Okayama'));
INSERT INTO state(code, country, name) VALUES ('ON','JP',i18n('Okinawa'));
INSERT INTO state(code, country, name) VALUES ('OS','JP',i18n('Osaka'));
INSERT INTO state(code, country, name) VALUES ('SA','JP',i18n('Saga'));
INSERT INTO state(code, country, name) VALUES ('SI','JP',i18n('Saitama'));
INSERT INTO state(code, country, name) VALUES ('SH','JP',i18n('Shiga'));
INSERT INTO state(code, country, name) VALUES ('SM','JP',i18n('Shimane'));
INSERT INTO state(code, country, name) VALUES ('SZ','JP',i18n('Shizuoka'));
INSERT INTO state(code, country, name) VALUES ('TO','JP',i18n('Tochigi'));
INSERT INTO state(code, country, name) VALUES ('TS','JP',i18n('Tokushima'));
INSERT INTO state(code, country, name) VALUES ('TK','JP',i18n('Tokyo'));
INSERT INTO state(code, country, name) VALUES ('TT','JP',i18n('Tottori'));
INSERT INTO state(code, country, name) VALUES ('TY','JP',i18n('Toyama'));
INSERT INTO state(code, country, name) VALUES ('WA','JP',i18n('Wakayama'));
INSERT INTO state(code, country, name) VALUES ('YA','JP',i18n('Yamagata'));
INSERT INTO state(code, country, name) VALUES ('YM','JP',i18n('Yamaguchi'));
INSERT INTO state(code, country, name) VALUES ('YN','JP',i18n('Yamanashi'));
-- country KE
INSERT INTO state(code, country, name) VALUES ('CE','KE',i18n('Central'));
INSERT INTO state(code, country, name) VALUES ('CO','KE',i18n('Coast'));
INSERT INTO state(code, country, name) VALUES ('EA','KE',i18n('Eastern'));
INSERT INTO state(code, country, name) VALUES ('NA','KE',i18n('Nairobi Area'));
INSERT INTO state(code, country, name) VALUES ('NE','KE',i18n('North Eastern'));
INSERT INTO state(code, country, name) VALUES ('NY','KE',i18n('Nyanza'));
INSERT INTO state(code, country, name) VALUES ('RV','KE',i18n('Rift Valley'));
INSERT INTO state(code, country, name) VALUES ('WE','KE',i18n('Western'));
-- country KG
INSERT INTO state(code, country, name) VALUES ('KG-1','KG',i18n('StateNameStub'));
-- country KH
INSERT INTO state(code, country, name) VALUES ('KH-1','KH',i18n('StateNameStub'));
-- country KI
INSERT INTO state(code, country, name) VALUES ('KI-1','KI',i18n('StateNameStub'));
-- country KM
INSERT INTO state(code, country, name) VALUES ('KM-1','KM',i18n('StateNameStub'));
-- country KN
INSERT INTO state(code, country, name) VALUES ('KN-1','KN',i18n('StateNameStub'));
-- country KP
INSERT INTO state(code, country, name) VALUES ('KP-1','KP',i18n('StateNameStub'));
-- country KR
INSERT INTO state(code, country, name) VALUES ('CO','KR',i18n('Ch''ungch|ong-bukto'));
INSERT INTO state(code, country, name) VALUES ('CH','KR',i18n('Ch''ungch|ong-namdo'));
INSERT INTO state(code, country, name) VALUES ('CD','KR',i18n('Cheju-do'));
INSERT INTO state(code, country, name) VALUES ('CB','KR',i18n('Cholla-bukto'));
INSERT INTO state(code, country, name) VALUES ('CN','KR',i18n('Cholla-namdo'));
INSERT INTO state(code, country, name) VALUES ('IG','KR',i18n('Inch''on-gwangyoksi'));
INSERT INTO state(code, country, name) VALUES ('KA','KR',i18n('Kangwon-do'));
INSERT INTO state(code, country, name) VALUES ('KG','KR',i18n('Kwangju-gwangyoksi'));
INSERT INTO state(code, country, name) VALUES ('KD','KR',i18n('Kyonggi-do'));
INSERT INTO state(code, country, name) VALUES ('KB','KR',i18n('Kyongsang-bukto'));
INSERT INTO state(code, country, name) VALUES ('KN','KR',i18n('Kyongsang-namdo'));
INSERT INTO state(code, country, name) VALUES ('PG','KR',i18n('Pusan-gwangyoksi'));
INSERT INTO state(code, country, name) VALUES ('SO','KR',i18n('Soul-t''ukpyolsi'));
INSERT INTO state(code, country, name) VALUES ('TA','KR',i18n('Taegu-gwangyoksi'));
INSERT INTO state(code, country, name) VALUES ('TG','KR',i18n('Taejon-gwangyoksi'));
-- country KW
INSERT INTO state(code, country, name) VALUES ('AL','KW',i18n('Al ''Asimah'));
INSERT INTO state(code, country, name) VALUES ('AA','KW',i18n('Al Ahmadi'));
INSERT INTO state(code, country, name) VALUES ('AF','KW',i18n('Al Farwaniyah'));
INSERT INTO state(code, country, name) VALUES ('AJ','KW',i18n('Al Jahra'''));
INSERT INTO state(code, country, name) VALUES ('HA','KW',i18n('Hawalli'));
-- country KY
INSERT INTO state(code, country, name) VALUES ('KY-1','KY',i18n('StateNameStub'));
-- country KZ
INSERT INTO state(code, country, name) VALUES ('AL','KZ',i18n('Almaty'));
INSERT INTO state(code, country, name) VALUES ('AC','KZ',i18n('Almaty City'));
INSERT INTO state(code, country, name) VALUES ('AM','KZ',i18n('Aqmola'));
INSERT INTO state(code, country, name) VALUES ('AQ','KZ',i18n('Aqtobe'));
INSERT INTO state(code, country, name) VALUES ('AS','KZ',i18n('Astana City'));
INSERT INTO state(code, country, name) VALUES ('AT','KZ',i18n('Atyrau'));
INSERT INTO state(code, country, name) VALUES ('BA','KZ',i18n('Batys Qazaqstan'));
INSERT INTO state(code, country, name) VALUES ('BY','KZ',i18n('Bayqongyr City'));
INSERT INTO state(code, country, name) VALUES ('MA','KZ',i18n('Mangghystau'));
INSERT INTO state(code, country, name) VALUES ('ON','KZ',i18n('Ongtustik Qazaqstan'));
INSERT INTO state(code, country, name) VALUES ('PA','KZ',i18n('Pavlodar'));
INSERT INTO state(code, country, name) VALUES ('QA','KZ',i18n('Qaraghandy'));
INSERT INTO state(code, country, name) VALUES ('QO','KZ',i18n('Qostanay'));
INSERT INTO state(code, country, name) VALUES ('QY','KZ',i18n('Qyzylorda'));
INSERT INTO state(code, country, name) VALUES ('SH','KZ',i18n('Shyghys Qazaqstan'));
INSERT INTO state(code, country, name) VALUES ('SO','KZ',i18n('Soltustik Qazaqstan'));
INSERT INTO state(code, country, name) VALUES ('ZH','KZ',i18n('Zhambyl'));
-- country LA
INSERT INTO state(code, country, name) VALUES ('LA-1','LA',i18n('StateNameStub'));
-- country LB
INSERT INTO state(code, country, name) VALUES ('LB-1','LB',i18n('StateNameStub'));
-- country LC
INSERT INTO state(code, country, name) VALUES ('LC-1','LC',i18n('StateNameStub'));
-- country LI
INSERT INTO state(code, country, name) VALUES ('LI-1','LI',i18n('StateNameStub'));
-- country LK
INSERT INTO state(code, country, name) VALUES ('CE','LK',i18n('Central'));
INSERT INTO state(code, country, name) VALUES ('NC','LK',i18n('North Central'));
INSERT INTO state(code, country, name) VALUES ('NE','LK',i18n('North Eastern'));
INSERT INTO state(code, country, name) VALUES ('NW','LK',i18n('North Western'));
INSERT INTO state(code, country, name) VALUES ('SA','LK',i18n('Sabaragamuwa'));
INSERT INTO state(code, country, name) VALUES ('SO','LK',i18n('Southern'));
INSERT INTO state(code, country, name) VALUES ('UV','LK',i18n('Uva'));
INSERT INTO state(code, country, name) VALUES ('WE','LK',i18n('Western'));
-- country LR
INSERT INTO state(code, country, name) VALUES ('LR-1','LR',i18n('StateNameStub'));
-- country LS
INSERT INTO state(code, country, name) VALUES ('LS-1','LS',i18n('StateNameStub'));
-- country LT
INSERT INTO state(code, country, name) VALUES ('LT-1','LT',i18n('StateNameStub'));
-- country LU
INSERT INTO state(code, country, name) VALUES ('DI','LU',i18n('Diekirch'));
INSERT INTO state(code, country, name) VALUES ('GR','LU',i18n('Grevenmacher'));
INSERT INTO state(code, country, name) VALUES ('LU','LU',i18n('Luxembourg'));
-- country LV
INSERT INTO state(code, country, name) VALUES ('LV-1','LV',i18n('StateNameStub'));
-- country LY
INSERT INTO state(code, country, name) VALUES ('LY-1','LY',i18n('StateNameStub'));
-- country MA
INSERT INTO state(code, country, name) VALUES ('MA-1','MA',i18n('StateNameStub'));
-- country MC
INSERT INTO state(code, country, name) VALUES ('MC-1','MC',i18n('StateNameStub'));
-- country MD
INSERT INTO state(code, country, name) VALUES ('MD-1','MD',i18n('StateNameStub'));
-- country MG
INSERT INTO state(code, country, name) VALUES ('MG-1','MG',i18n('StateNameStub'));
-- country MH
INSERT INTO state(code, country, name) VALUES ('MH-1','MH',i18n('StateNameStub'));
-- country MK
INSERT INTO state(code, country, name) VALUES ('MK-1','MK',i18n('StateNameStub'));
-- country ML
INSERT INTO state(code, country, name) VALUES ('ML-1','ML',i18n('StateNameStub'));
-- country MM
INSERT INTO state(code, country, name) VALUES ('MM-1','MM',i18n('StateNameStub'));
-- country MN
INSERT INTO state(code, country, name) VALUES ('MN-1','MN',i18n('StateNameStub'));
-- country MO
INSERT INTO state(code, country, name) VALUES ('MO-1','MO',i18n('StateNameStub'));
-- country MP
INSERT INTO state(code, country, name) VALUES ('MP-1','MP',i18n('StateNameStub'));
-- country MQ
INSERT INTO state(code, country, name) VALUES ('MQ-1','MQ',i18n('StateNameStub'));
-- country MR
INSERT INTO state(code, country, name) VALUES ('MR-1','MR',i18n('StateNameStub'));
-- country MS
INSERT INTO state(code, country, name) VALUES ('MS-1','MS',i18n('StateNameStub'));
-- country MT
INSERT INTO state(code, country, name) VALUES ('MT-1','MT',i18n('StateNameStub'));
-- country MU
INSERT INTO state(code, country, name) VALUES ('MU-1','MU',i18n('StateNameStub'));
-- country MV
INSERT INTO state(code, country, name) VALUES ('MV-1','MV',i18n('StateNameStub'));
-- country MW
INSERT INTO state(code, country, name) VALUES ('MW-1','MW',i18n('StateNameStub'));
-- country MX
INSERT INTO state(code, country, name) VALUES ('BC','MX',i18n('Baja California'));
INSERT INTO state(code, country, name) VALUES ('BS','MX',i18n('Baja California Sur'));
INSERT INTO state(code, country, name) VALUES ('CA','MX',i18n('Campeche'));
INSERT INTO state(code, country, name) VALUES ('CI','MX',i18n('Chiapas'));
INSERT INTO state(code, country, name) VALUES ('CH','MX',i18n('Chihuahua'));
INSERT INTO state(code, country, name) VALUES ('CZ','MX',i18n('Coahuila de Zaragoza'));
INSERT INTO state(code, country, name) VALUES ('CL','MX',i18n('Colima'));
INSERT INTO state(code, country, name) VALUES ('DF','MX',i18n('Distrito Federal'));
INSERT INTO state(code, country, name) VALUES ('DU','MX',i18n('Durango'));
INSERT INTO state(code, country, name) VALUES ('GA','MX',i18n('Guanajuato'));
INSERT INTO state(code, country, name) VALUES ('GE','MX',i18n('Guerrero'));
INSERT INTO state(code, country, name) VALUES ('HI','MX',i18n('Hidalgo'));
INSERT INTO state(code, country, name) VALUES ('JA','MX',i18n('Jalisco'));
INSERT INTO state(code, country, name) VALUES ('ME','MX',i18n('Mexico'));
INSERT INTO state(code, country, name) VALUES ('MI','MX',i18n('Michoacan de Ocampo'));
INSERT INTO state(code, country, name) VALUES ('MO','MX',i18n('Morelos'));
INSERT INTO state(code, country, name) VALUES ('NA','MX',i18n('Nayarit'));
INSERT INTO state(code, country, name) VALUES ('NL','MX',i18n('Nuevo Leon'));
INSERT INTO state(code, country, name) VALUES ('OA','MX',i18n('Oaxaca'));
INSERT INTO state(code, country, name) VALUES ('PU','MX',i18n('Puebla'));
INSERT INTO state(code, country, name) VALUES ('QA','MX',i18n('Queretaro de Arteaga'));
INSERT INTO state(code, country, name) VALUES ('QR','MX',i18n('Quintana Roo'));
INSERT INTO state(code, country, name) VALUES ('SA','MX',i18n('San Luis Potosi'));
INSERT INTO state(code, country, name) VALUES ('SI','MX',i18n('Sinaloa'));
INSERT INTO state(code, country, name) VALUES ('SO','MX',i18n('Sonora'));
INSERT INTO state(code, country, name) VALUES ('TB','MX',i18n('Tabasco'));
INSERT INTO state(code, country, name) VALUES ('TM','MX',i18n('Tamaulipas'));
INSERT INTO state(code, country, name) VALUES ('TL','MX',i18n('Tlaxcala'));
INSERT INTO state(code, country, name) VALUES ('VE','MX',i18n('Veracruz-Llave'));
INSERT INTO state(code, country, name) VALUES ('YU','MX',i18n('Yucatan'));
INSERT INTO state(code, country, name) VALUES ('ZA','MX',i18n('Zacatecas'));
-- country MY
INSERT INTO state(code, country, name) VALUES ('JO','MY',i18n('Johor'));
INSERT INTO state(code, country, name) VALUES ('KE','MY',i18n('Kedah'));
INSERT INTO state(code, country, name) VALUES ('KL','MY',i18n('Kelantan'));
INSERT INTO state(code, country, name) VALUES ('LA','MY',i18n('Labuan'));
INSERT INTO state(code, country, name) VALUES ('ME','MY',i18n('Melaka'));
INSERT INTO state(code, country, name) VALUES ('NS','MY',i18n('Negeri Sembilan'));
INSERT INTO state(code, country, name) VALUES ('PA','MY',i18n('Pahang'));
INSERT INTO state(code, country, name) VALUES ('PE','MY',i18n('Perak'));
INSERT INTO state(code, country, name) VALUES ('PR','MY',i18n('Perlis'));
INSERT INTO state(code, country, name) VALUES ('PP','MY',i18n('Pulau Pinang'));
INSERT INTO state(code, country, name) VALUES ('SA','MY',i18n('Sabah'));
INSERT INTO state(code, country, name) VALUES ('SR','MY',i18n('Sarawak'));
INSERT INTO state(code, country, name) VALUES ('SE','MY',i18n('Selangor'));
INSERT INTO state(code, country, name) VALUES ('TE','MY',i18n('Terengganu'));
INSERT INTO state(code, country, name) VALUES ('WP','MY',i18n('Wilayah Persekutuan'));
-- country MZ
INSERT INTO state(code, country, name) VALUES ('MZ-1','MZ',i18n('StateNameStub'));
-- country NA
INSERT INTO state(code, country, name) VALUES ('NA-1','NA',i18n('StateNameStub'));
-- country NC
INSERT INTO state(code, country, name) VALUES ('NC-1','NC',i18n('StateNameStub'));
-- country NE
INSERT INTO state(code, country, name) VALUES ('AG','NE',i18n('Agadez'));
INSERT INTO state(code, country, name) VALUES ('DI','NE',i18n('Diffa'));
INSERT INTO state(code, country, name) VALUES ('DO','NE',i18n('Dosso'));
INSERT INTO state(code, country, name) VALUES ('MA','NE',i18n('Maradi'));
INSERT INTO state(code, country, name) VALUES ('NI','NE',i18n('Niamey'));
INSERT INTO state(code, country, name) VALUES ('TA','NE',i18n('Tahoua'));
INSERT INTO state(code, country, name) VALUES ('TI','NE',i18n('Tillaberi'));
INSERT INTO state(code, country, name) VALUES ('ZI','NE',i18n('Zinder'));
-- country NF
INSERT INTO state(code, country, name) VALUES ('NF-1','NF',i18n('StateNameStub'));
-- country NG
INSERT INTO state(code, country, name) VALUES ('AB','NG',i18n('Abia'));
INSERT INTO state(code, country, name) VALUES ('FC','NG',i18n('Abuja Federal Capital Territory'));
INSERT INTO state(code, country, name) VALUES ('AD','NG',i18n('Adamawa'));
INSERT INTO state(code, country, name) VALUES ('AI','NG',i18n('Akwa Ibom'));
INSERT INTO state(code, country, name) VALUES ('AN','NG',i18n('Anambra'));
INSERT INTO state(code, country, name) VALUES ('BA','NG',i18n('Bauchi'));
INSERT INTO state(code, country, name) VALUES ('BY','NG',i18n('Bayelsa'));
INSERT INTO state(code, country, name) VALUES ('BE','NG',i18n('Benue'));
INSERT INTO state(code, country, name) VALUES ('BO','NG',i18n('Borno'));
INSERT INTO state(code, country, name) VALUES ('CR','NG',i18n('Cross River'));
INSERT INTO state(code, country, name) VALUES ('DE','NG',i18n('Delta'));
INSERT INTO state(code, country, name) VALUES ('EB','NG',i18n('Ebonyi'));
INSERT INTO state(code, country, name) VALUES ('ED','NG',i18n('Edo'));
INSERT INTO state(code, country, name) VALUES ('EK','NG',i18n('Ekiti'));
INSERT INTO state(code, country, name) VALUES ('EN','NG',i18n('Enugu'));
INSERT INTO state(code, country, name) VALUES ('GO','NG',i18n('Gombe'));
INSERT INTO state(code, country, name) VALUES ('IM','NG',i18n('Imo'));
INSERT INTO state(code, country, name) VALUES ('JI','NG',i18n('Jigawa'));
INSERT INTO state(code, country, name) VALUES ('KA','NG',i18n('Kaduna'));
INSERT INTO state(code, country, name) VALUES ('KN','NG',i18n('Kano'));
INSERT INTO state(code, country, name) VALUES ('KT','NG',i18n('Katsina'));
INSERT INTO state(code, country, name) VALUES ('KE','NG',i18n('Kebbi'));
INSERT INTO state(code, country, name) VALUES ('KO','NG',i18n('Kogi'));
INSERT INTO state(code, country, name) VALUES ('KW','NG',i18n('Kwara'));
INSERT INTO state(code, country, name) VALUES ('LA','NG',i18n('Lagos'));
INSERT INTO state(code, country, name) VALUES ('NA','NG',i18n('Nassarawa'));
INSERT INTO state(code, country, name) VALUES ('NI','NG',i18n('Niger'));
INSERT INTO state(code, country, name) VALUES ('OG','NG',i18n('Ogun'));
INSERT INTO state(code, country, name) VALUES ('ON','NG',i18n('Ondo'));
INSERT INTO state(code, country, name) VALUES ('OS','NG',i18n('Osun'));
INSERT INTO state(code, country, name) VALUES ('OY','NG',i18n('Oyo'));
INSERT INTO state(code, country, name) VALUES ('PL','NG',i18n('Plateau'));
INSERT INTO state(code, country, name) VALUES ('RI','NG',i18n('Rivers'));
INSERT INTO state(code, country, name) VALUES ('SO','NG',i18n('Sokoto'));
INSERT INTO state(code, country, name) VALUES ('TA','NG',i18n('Taraba'));
INSERT INTO state(code, country, name) VALUES ('YO','NG',i18n('Yobe'));
INSERT INTO state(code, country, name) VALUES ('ZA','NG',i18n('Zamfara'));
-- country NI
INSERT INTO state(code, country, name) VALUES ('AN','NI',i18n('Atlantico Norte'));
INSERT INTO state(code, country, name) VALUES ('AS','NI',i18n('Atlantico Sur'));
INSERT INTO state(code, country, name) VALUES ('BO','NI',i18n('Boaco'));
INSERT INTO state(code, country, name) VALUES ('CA','NI',i18n('Carazo'));
INSERT INTO state(code, country, name) VALUES ('CI','NI',i18n('Chinandega'));
INSERT INTO state(code, country, name) VALUES ('CO','NI',i18n('Chontales'));
INSERT INTO state(code, country, name) VALUES ('ES','NI',i18n('Esteli'));
INSERT INTO state(code, country, name) VALUES ('GR','NI',i18n('Granada'));
INSERT INTO state(code, country, name) VALUES ('JI','NI',i18n('Jinotega'));
INSERT INTO state(code, country, name) VALUES ('LE','NI',i18n('Leon'));
INSERT INTO state(code, country, name) VALUES ('MD','NI',i18n('Madriz'));
INSERT INTO state(code, country, name) VALUES ('MN','NI',i18n('Managua'));
INSERT INTO state(code, country, name) VALUES ('MS','NI',i18n('Masaya'));
INSERT INTO state(code, country, name) VALUES ('MT','NI',i18n('Matagalpa'));
INSERT INTO state(code, country, name) VALUES ('NS','NI',i18n('Nuevo Segovia'));
INSERT INTO state(code, country, name) VALUES ('RS','NI',i18n('Rio San Juan'));
INSERT INTO state(code, country, name) VALUES ('RI','NI',i18n('Rivas'));
-- country NL
INSERT INTO state(code, country, name) VALUES ('DR','NL',i18n('Drente'));
INSERT INTO state(code, country, name) VALUES ('FL','NL',i18n('Flevoland'));
INSERT INTO state(code, country, name) VALUES ('FR','NL',i18n('Friesland'));
INSERT INTO state(code, country, name) VALUES ('GE','NL',i18n('Gelderland'));
INSERT INTO state(code, country, name) VALUES ('GR','NL',i18n('Groningen'));
INSERT INTO state(code, country, name) VALUES ('LB','NL',i18n('Limburg'));
INSERT INTO state(code, country, name) VALUES ('NB','NL',i18n('Noord-Brabant'));
INSERT INTO state(code, country, name) VALUES ('NH','NL',i18n('Noord-Holland'));
INSERT INTO state(code, country, name) VALUES ('OV','NL',i18n('Overijssel'));
INSERT INTO state(code, country, name) VALUES ('UT','NL',i18n('Utrecht'));
INSERT INTO state(code, country, name) VALUES ('ZE','NL',i18n('Zeeland'));
INSERT INTO state(code, country, name) VALUES ('ZH','NL',i18n('Zuid-Holland'));
-- country NO
INSERT INTO state(code, country, name) VALUES ('AK','NO',i18n('Akershus'));
INSERT INTO state(code, country, name) VALUES ('AA','NO',i18n('Aust-Agder'));
INSERT INTO state(code, country, name) VALUES ('BU','NO',i18n('Buskerud'));
INSERT INTO state(code, country, name) VALUES ('FI','NO',i18n('Finnmark'));
INSERT INTO state(code, country, name) VALUES ('HE','NO',i18n('Hedmark'));
INSERT INTO state(code, country, name) VALUES ('HO','NO',i18n('Hordaland'));
INSERT INTO state(code, country, name) VALUES ('MR','NO',i18n('More og Romsdal'));
INSERT INTO state(code, country, name) VALUES ('NT','NO',i18n('Nord-Trondelag'));
INSERT INTO state(code, country, name) VALUES ('NL','NO',i18n('Nordland'));
INSERT INTO state(code, country, name) VALUES ('OF','NO',i18n('Ostfold'));
INSERT INTO state(code, country, name) VALUES ('OP','NO',i18n('Oppland'));
INSERT INTO state(code, country, name) VALUES ('OS','NO',i18n('Oslo'));
INSERT INTO state(code, country, name) VALUES ('RO','NO',i18n('Rogaland'));
INSERT INTO state(code, country, name) VALUES ('ST','NO',i18n('Sor-Trondelag'));
INSERT INTO state(code, country, name) VALUES ('SF','NO',i18n('Sogn og Fjordane'));
INSERT INTO state(code, country, name) VALUES ('SV','NO',i18n('Svalbard'));
INSERT INTO state(code, country, name) VALUES ('TE','NO',i18n('Telemark'));
INSERT INTO state(code, country, name) VALUES ('TR','NO',i18n('Troms'));
INSERT INTO state(code, country, name) VALUES ('VA','NO',i18n('Vest-Agder'));
INSERT INTO state(code, country, name) VALUES ('VF','NO',i18n('Vestfold'));
-- country NP
INSERT INTO state(code, country, name) VALUES ('NP-1','NP',i18n('StateNameStub'));
-- country NR
INSERT INTO state(code, country, name) VALUES ('NR-1','NR',i18n('StateNameStub'));
-- country NU
INSERT INTO state(code, country, name) VALUES ('NU-1','NU',i18n('StateNameStub'));
-- country NZ
INSERT INTO state(code, country, name) VALUES ('AU','NZ',i18n('Auckland'));
INSERT INTO state(code, country, name) VALUES ('BP','NZ',i18n('Bay of Plenty'));
INSERT INTO state(code, country, name) VALUES ('CA','NZ',i18n('Canterbury'));
INSERT INTO state(code, country, name) VALUES ('GI','NZ',i18n('Gisborne'));
INSERT INTO state(code, country, name) VALUES ('HB','NZ',i18n('Hawke''s Bay'));
INSERT INTO state(code, country, name) VALUES ('MA','NZ',i18n('Marlborough'));
INSERT INTO state(code, country, name) VALUES ('NE','NZ',i18n('Nelson'));
INSERT INTO state(code, country, name) VALUES ('NO','NZ',i18n('Northland'));
INSERT INTO state(code, country, name) VALUES ('OT','NZ',i18n('Otago'));
INSERT INTO state(code, country, name) VALUES ('SO','NZ',i18n('Southland'));
INSERT INTO state(code, country, name) VALUES ('TA','NZ',i18n('Taranaki'));
INSERT INTO state(code, country, name) VALUES ('TS','NZ',i18n('Tasman'));
INSERT INTO state(code, country, name) VALUES ('WA','NZ',i18n('Waikato'));
INSERT INTO state(code, country, name) VALUES ('WM','NZ',i18n('Wanganui-Manawatu'));
INSERT INTO state(code, country, name) VALUES ('WE','NZ',i18n('Wellington'));
INSERT INTO state(code, country, name) VALUES ('WC','NZ',i18n('West Coast'));
-- country OM
INSERT INTO state(code, country, name) VALUES ('OM-1','OM',i18n('StateNameStub'));
-- country PA
INSERT INTO state(code, country, name) VALUES ('PA-1','PA',i18n('StateNameStub'));
-- country PE
INSERT INTO state(code, country, name) VALUES ('PE-1','PE',i18n('StateNameStub'));
-- country PF
INSERT INTO state(code, country, name) VALUES ('PF-1','PF',i18n('StateNameStub'));
-- country PG
INSERT INTO state(code, country, name) VALUES ('PG-1','PG',i18n('StateNameStub'));
-- country PH
INSERT INTO state(code, country, name) VALUES ('AB','PH',i18n('Abra'));
INSERT INTO state(code, country, name) VALUES ('AG','PH',i18n('Agusan del Norte'));
INSERT INTO state(code, country, name) VALUES ('AU','PH',i18n('Agusan del Sur'));
INSERT INTO state(code, country, name) VALUES ('AK','PH',i18n('Aklan'));
INSERT INTO state(code, country, name) VALUES ('AL','PH',i18n('Albay'));
INSERT INTO state(code, country, name) VALUES ('AN','PH',i18n('Angeles'));
INSERT INTO state(code, country, name) VALUES ('AT','PH',i18n('Antique'));
INSERT INTO state(code, country, name) VALUES ('BA','PH',i18n('Bacolod'));
INSERT INTO state(code, country, name) VALUES ('BG','PH',i18n('Bago'));
INSERT INTO state(code, country, name) VALUES ('BU','PH',i18n('Baguio'));
INSERT INTO state(code, country, name) VALUES ('BI','PH',i18n('Bais'));
INSERT INTO state(code, country, name) VALUES ('BS','PH',i18n('Basilan'));
INSERT INTO state(code, country, name) VALUES ('BC','PH',i18n('Basilan City'));
INSERT INTO state(code, country, name) VALUES ('BT','PH',i18n('Bataan'));
INSERT INTO state(code, country, name) VALUES ('BN','PH',i18n('Batanes'));
INSERT INTO state(code, country, name) VALUES ('BB','PH',i18n('Batangas'));
INSERT INTO state(code, country, name) VALUES ('BD','PH',i18n('Batangas City'));
INSERT INTO state(code, country, name) VALUES ('BE','PH',i18n('Benguet'));
INSERT INTO state(code, country, name) VALUES ('BO','PH',i18n('Bohol'));
INSERT INTO state(code, country, name) VALUES ('BK','PH',i18n('Bukidnon'));
INSERT INTO state(code, country, name) VALUES ('BL','PH',i18n('Bulacan'));
INSERT INTO state(code, country, name) VALUES ('BV','PH',i18n('Butuan'));
INSERT INTO state(code, country, name) VALUES ('CA','PH',i18n('Cabanatuan'));
INSERT INTO state(code, country, name) VALUES ('CD','PH',i18n('Cadiz'));
INSERT INTO state(code, country, name) VALUES ('CG','PH',i18n('Cagayan'));
INSERT INTO state(code, country, name) VALUES ('CO','PH',i18n('Cagayan de Oro'));
INSERT INTO state(code, country, name) VALUES ('CL','PH',i18n('Calbayog'));
INSERT INTO state(code, country, name) VALUES ('CC','PH',i18n('Caloocan'));
INSERT INTO state(code, country, name) VALUES ('CN','PH',i18n('Camarines Norte'));
INSERT INTO state(code, country, name) VALUES ('CS','PH',i18n('Camarines Sur'));
INSERT INTO state(code, country, name) VALUES ('CM','PH',i18n('Camiguin'));
INSERT INTO state(code, country, name) VALUES ('CB','PH',i18n('Canlaon'));
INSERT INTO state(code, country, name) VALUES ('CP','PH',i18n('Capiz'));
INSERT INTO state(code, country, name) VALUES ('CT','PH',i18n('Catanduanes'));
INSERT INTO state(code, country, name) VALUES ('CV','PH',i18n('Cavite'));
INSERT INTO state(code, country, name) VALUES ('CH','PH',i18n('Cavite City'));
INSERT INTO state(code, country, name) VALUES ('CE','PH',i18n('Cebu'));
INSERT INTO state(code, country, name) VALUES ('CY','PH',i18n('Cebu City'));
INSERT INTO state(code, country, name) VALUES ('CF','PH',i18n('Cotabato'));
INSERT INTO state(code, country, name) VALUES ('DA','PH',i18n('Dagupan'));
INSERT INTO state(code, country, name) VALUES ('DN','PH',i18n('Danao'));
INSERT INTO state(code, country, name) VALUES ('DP','PH',i18n('Dapitan'));
INSERT INTO state(code, country, name) VALUES ('DD','PH',i18n('Davao City Davao'));
INSERT INTO state(code, country, name) VALUES ('DS','PH',i18n('Davao del Sur'));
INSERT INTO state(code, country, name) VALUES ('DO','PH',i18n('Davao Oriental'));
INSERT INTO state(code, country, name) VALUES ('DI','PH',i18n('Dipolog'));
INSERT INTO state(code, country, name) VALUES ('DU','PH',i18n('Dumaguete'));
INSERT INTO state(code, country, name) VALUES ('ES','PH',i18n('Eastern Samar'));
INSERT INTO state(code, country, name) VALUES ('GS','PH',i18n('General Santos'));
INSERT INTO state(code, country, name) VALUES ('GI','PH',i18n('Gingoog'));
INSERT INTO state(code, country, name) VALUES ('IF','PH',i18n('Ifugao'));
INSERT INTO state(code, country, name) VALUES ('IL','PH',i18n('Iligan'));
INSERT INTO state(code, country, name) VALUES ('IN','PH',i18n('Ilocos Norte'));
INSERT INTO state(code, country, name) VALUES ('IS','PH',i18n('Ilocos Sur'));
INSERT INTO state(code, country, name) VALUES ('IO','PH',i18n('Iloilo'));
INSERT INTO state(code, country, name) VALUES ('IC','PH',i18n('Iloilo City'));
INSERT INTO state(code, country, name) VALUES ('IR','PH',i18n('Iriga'));
INSERT INTO state(code, country, name) VALUES ('IB','PH',i18n('Isabela'));
INSERT INTO state(code, country, name) VALUES ('KA','PH',i18n('Kalinga-Apayao'));
INSERT INTO state(code, country, name) VALUES ('LC','PH',i18n('La Carlota'));
INSERT INTO state(code, country, name) VALUES ('LU','PH',i18n('La Union'));
INSERT INTO state(code, country, name) VALUES ('LA','PH',i18n('Laguna'));
INSERT INTO state(code, country, name) VALUES ('LN','PH',i18n('Lanao del Norte'));
INSERT INTO state(code, country, name) VALUES ('LS','PH',i18n('Lanao del Sur'));
INSERT INTO state(code, country, name) VALUES ('LG','PH',i18n('Laoag'));
INSERT INTO state(code, country, name) VALUES ('LL','PH',i18n('Lapu-Lapu'));
INSERT INTO state(code, country, name) VALUES ('LE','PH',i18n('Legaspi'));
INSERT INTO state(code, country, name) VALUES ('LY','PH',i18n('Leyte'));
INSERT INTO state(code, country, name) VALUES ('LI','PH',i18n('Lipa'));
INSERT INTO state(code, country, name) VALUES ('LV','PH',i18n('Lucena'));
INSERT INTO state(code, country, name) VALUES ('MA','PH',i18n('Maguindanao'));
INSERT INTO state(code, country, name) VALUES ('MN','PH',i18n('Mandaue'));
INSERT INTO state(code, country, name) VALUES ('MI','PH',i18n('Manila'));
INSERT INTO state(code, country, name) VALUES ('MR','PH',i18n('Marawi'));
INSERT INTO state(code, country, name) VALUES ('MD','PH',i18n('Marinduque'));
INSERT INTO state(code, country, name) VALUES ('MS','PH',i18n('Masbate'));
INSERT INTO state(code, country, name) VALUES ('MO','PH',i18n('Mindoro Occidental'));
INSERT INTO state(code, country, name) VALUES ('MT','PH',i18n('Mindoro Oriental'));
INSERT INTO state(code, country, name) VALUES ('ML','PH',i18n('Misamis Occidental'));
INSERT INTO state(code, country, name) VALUES ('ME','PH',i18n('Misamis Oriental'));
INSERT INTO state(code, country, name) VALUES ('MU','PH',i18n('Mountain'));
INSERT INTO state(code, country, name) VALUES ('NA','PH',i18n('Naga'));
INSERT INTO state(code, country, name) VALUES ('NO','PH',i18n('Negros Occidental'));
INSERT INTO state(code, country, name) VALUES ('NE','PH',i18n('Negros Oriental'));
INSERT INTO state(code, country, name) VALUES ('NC','PH',i18n('North Cotabato'));
INSERT INTO state(code, country, name) VALUES ('NS','PH',i18n('Northern Samar'));
INSERT INTO state(code, country, name) VALUES ('NI','PH',i18n('Nueva Ecija'));
INSERT INTO state(code, country, name) VALUES ('NV','PH',i18n('Nueva Vizcaya'));
INSERT INTO state(code, country, name) VALUES ('OL','PH',i18n('Olongapo'));
INSERT INTO state(code, country, name) VALUES ('OR','PH',i18n('Ormoc'));
INSERT INTO state(code, country, name) VALUES ('OQ','PH',i18n('Oroquieta'));
INSERT INTO state(code, country, name) VALUES ('OZ','PH',i18n('Ozamis'));
INSERT INTO state(code, country, name) VALUES ('PA','PH',i18n('Pagadian'));
INSERT INTO state(code, country, name) VALUES ('PL','PH',i18n('Palawan'));
INSERT INTO state(code, country, name) VALUES ('PY','PH',i18n('Palayan'));
INSERT INTO state(code, country, name) VALUES ('PM','PH',i18n('Pampanga'));
INSERT INTO state(code, country, name) VALUES ('PN','PH',i18n('Pangasinan'));
INSERT INTO state(code, country, name) VALUES ('PS','PH',i18n('Pasay'));
INSERT INTO state(code, country, name) VALUES ('PU','PH',i18n('Puerto Princesa'));
INSERT INTO state(code, country, name) VALUES ('QU','PH',i18n('Quezon'));
INSERT INTO state(code, country, name) VALUES ('QZ','PH',i18n('Quezon City'));
INSERT INTO state(code, country, name) VALUES ('QR','PH',i18n('Quirino'));
INSERT INTO state(code, country, name) VALUES ('RI','PH',i18n('Rizal'));
INSERT INTO state(code, country, name) VALUES ('RO','PH',i18n('Romblon'));
INSERT INTO state(code, country, name) VALUES ('RX','PH',i18n('Roxas'));
INSERT INTO state(code, country, name) VALUES ('SA','PH',i18n('Samar'));
INSERT INTO state(code, country, name) VALUES ('SC','PH',i18n('San Carlos (in Negros Occidental'));
INSERT INTO state(code, country, name) VALUES ('SN','PH',i18n('San Carlos (in Pangasinan)'));
INSERT INTO state(code, country, name) VALUES ('SJ','PH',i18n('San Jose'));
INSERT INTO state(code, country, name) VALUES ('SP','PH',i18n('San Pablo'));
INSERT INTO state(code, country, name) VALUES ('SI','PH',i18n('Silay'));
INSERT INTO state(code, country, name) VALUES ('SQ','PH',i18n('Siquijor'));
INSERT INTO state(code, country, name) VALUES ('SO','PH',i18n('Sorsogon'));
INSERT INTO state(code, country, name) VALUES ('ST','PH',i18n('South Cotabato'));
INSERT INTO state(code, country, name) VALUES ('SL','PH',i18n('Southern Leyte'));
INSERT INTO state(code, country, name) VALUES ('SK','PH',i18n('Sultan Kudarat'));
INSERT INTO state(code, country, name) VALUES ('SU','PH',i18n('Sulu'));
INSERT INTO state(code, country, name) VALUES ('SG','PH',i18n('Surigao'));
INSERT INTO state(code, country, name) VALUES ('SD','PH',i18n('Surigao del Norte'));
INSERT INTO state(code, country, name) VALUES ('SS','PH',i18n('Surigao del Sur'));
INSERT INTO state(code, country, name) VALUES ('TA','PH',i18n('Tacloban'));
INSERT INTO state(code, country, name) VALUES ('TG','PH',i18n('Tagaytay'));
INSERT INTO state(code, country, name) VALUES ('TB','PH',i18n('Tagbilaran'));
INSERT INTO state(code, country, name) VALUES ('TN','PH',i18n('Tangub'));
INSERT INTO state(code, country, name) VALUES ('TR','PH',i18n('Tarlac'));
INSERT INTO state(code, country, name) VALUES ('TW','PH',i18n('Tawitawi'));
INSERT INTO state(code, country, name) VALUES ('TO','PH',i18n('Toledo'));
INSERT INTO state(code, country, name) VALUES ('TM','PH',i18n('Trece Martires'));
INSERT INTO state(code, country, name) VALUES ('ZA','PH',i18n('Zambales'));
INSERT INTO state(code, country, name) VALUES ('ZM','PH',i18n('Zamboanga'));
INSERT INTO state(code, country, name) VALUES ('ZN','PH',i18n('Zamboanga del Norte'));
INSERT INTO state(code, country, name) VALUES ('ZS','PH',i18n('Zamboanga del Sur'));
-- country PK
INSERT INTO state(code, country, name) VALUES ('BA','PK',i18n('Balochistan'));
INSERT INTO state(code, country, name) VALUES ('TA','PK',i18n('Federally Administered Tribal Ar'));
INSERT INTO state(code, country, name) VALUES ('IS','PK',i18n('Islamabad Capital Territory'));
INSERT INTO state(code, country, name) VALUES ('NF','PK',i18n('North-West Frontier'));
INSERT INTO state(code, country, name) VALUES ('PU','PK',i18n('Punjab'));
INSERT INTO state(code, country, name) VALUES ('SI','PK',i18n('Sindh'));
-- country PL
INSERT INTO state(code, country, name) VALUES ('DO','PL',i18n('Dolnoslaskie'));
INSERT INTO state(code, country, name) VALUES ('KM','PL',i18n('Kujawsko-Pomorskie'));
INSERT INTO state(code, country, name) VALUES ('LO','PL',i18n('Lodzkie'));
INSERT INTO state(code, country, name) VALUES ('LE','PL',i18n('Lubelskie'));
INSERT INTO state(code, country, name) VALUES ('LU','PL',i18n('Lubuskie'));
INSERT INTO state(code, country, name) VALUES ('ML','PL',i18n('Malopolskie'));
INSERT INTO state(code, country, name) VALUES ('MZ','PL',i18n('Mazowieckie'));
INSERT INTO state(code, country, name) VALUES ('OP','PL',i18n('Opolskie'));
INSERT INTO state(code, country, name) VALUES ('PK','PL',i18n('Podkarpackie'));
INSERT INTO state(code, country, name) VALUES ('PL','PL',i18n('Podlaskie'));
INSERT INTO state(code, country, name) VALUES ('PM','PL',i18n('Pomorskie'));
INSERT INTO state(code, country, name) VALUES ('SL','PL',i18n('Slaskie'));
INSERT INTO state(code, country, name) VALUES ('SW','PL',i18n('Swietokrzyskie'));
INSERT INTO state(code, country, name) VALUES ('WM','PL',i18n('Warminsko-Mazurskie'));
INSERT INTO state(code, country, name) VALUES ('WI','PL',i18n('Wielkopolskie'));
INSERT INTO state(code, country, name) VALUES ('ZA','PL',i18n('Zachodniopomorskie'));
-- country PM
INSERT INTO state(code, country, name) VALUES ('PM-1','PM',i18n('StateNameStub'));
-- country PN
INSERT INTO state(code, country, name) VALUES ('PN-1','PN',i18n('StateNameStub'));
-- country PR
INSERT INTO state(code, country, name) VALUES ('PR-1','PR',i18n('StateNameStub'));
-- country PT
INSERT INTO state(code, country, name) VALUES ('AC','PT',i18n('Acores (Azores)'));
INSERT INTO state(code, country, name) VALUES ('AV','PT',i18n('Aveiro'));
INSERT INTO state(code, country, name) VALUES ('BE','PT',i18n('Beja'));
INSERT INTO state(code, country, name) VALUES ('BR','PT',i18n('Braga'));
INSERT INTO state(code, country, name) VALUES ('BA','PT',i18n('Braganca'));
INSERT INTO state(code, country, name) VALUES ('CB','PT',i18n('Castelo Branco'));
INSERT INTO state(code, country, name) VALUES ('CO','PT',i18n('Coimbra'));
INSERT INTO state(code, country, name) VALUES ('EV','PT',i18n('Evora'));
INSERT INTO state(code, country, name) VALUES ('FA','PT',i18n('Faro'));
INSERT INTO state(code, country, name) VALUES ('GU','PT',i18n('Guarda'));
INSERT INTO state(code, country, name) VALUES ('LE','PT',i18n('Leiria'));
INSERT INTO state(code, country, name) VALUES ('LI','PT',i18n('Lisboa'));
INSERT INTO state(code, country, name) VALUES ('ME','PT',i18n('Madeira'));
INSERT INTO state(code, country, name) VALUES ('PO','PT',i18n('Portalegre'));
INSERT INTO state(code, country, name) VALUES ('PR','PT',i18n('Porto'));
INSERT INTO state(code, country, name) VALUES ('SA','PT',i18n('Santarem'));
INSERT INTO state(code, country, name) VALUES ('SE','PT',i18n('Setubal'));
INSERT INTO state(code, country, name) VALUES ('VC','PT',i18n('Viana do Castelo'));
INSERT INTO state(code, country, name) VALUES ('VR','PT',i18n('Vila Real'));
INSERT INTO state(code, country, name) VALUES ('VI','PT',i18n('Viseu'));
-- country PW
INSERT INTO state(code, country, name) VALUES ('PW-1','PW',i18n('StateNameStub'));
-- country PY
INSERT INTO state(code, country, name) VALUES ('PY-1','PY',i18n('StateNameStub'));
-- country QA
INSERT INTO state(code, country, name) VALUES ('QA-1','QA',i18n('StateNameStub'));
-- country RE
INSERT INTO state(code, country, name) VALUES ('RE-1','RE',i18n('StateNameStub'));
-- country RO
INSERT INTO state(code, country, name) VALUES ('AL','RO',i18n('Alba'));
INSERT INTO state(code, country, name) VALUES ('AR','RO',i18n('Arad'));
INSERT INTO state(code, country, name) VALUES ('AG','RO',i18n('Arges'));
INSERT INTO state(code, country, name) VALUES ('BA','RO',i18n('Bacau'));
INSERT INTO state(code, country, name) VALUES ('BI','RO',i18n('Bihor'));
INSERT INTO state(code, country, name) VALUES ('BN','RO',i18n('Bistrita-Nasaud'));
INSERT INTO state(code, country, name) VALUES ('BO','RO',i18n('Botosani'));
INSERT INTO state(code, country, name) VALUES ('BL','RO',i18n('Braila'));
INSERT INTO state(code, country, name) VALUES ('BR','RO',i18n('Brasov'));
INSERT INTO state(code, country, name) VALUES ('BU','RO',i18n('Bucuresti'));
INSERT INTO state(code, country, name) VALUES ('BZ','RO',i18n('Buzau'));
INSERT INTO state(code, country, name) VALUES ('CA','RO',i18n('Calarasi'));
INSERT INTO state(code, country, name) VALUES ('CS','RO',i18n('Caras-Severin'));
INSERT INTO state(code, country, name) VALUES ('CL','RO',i18n('Cluj'));
INSERT INTO state(code, country, name) VALUES ('CO','RO',i18n('Constanta'));
INSERT INTO state(code, country, name) VALUES ('CV','RO',i18n('Covasna'));
INSERT INTO state(code, country, name) VALUES ('DI','RO',i18n('Dimbovita'));
INSERT INTO state(code, country, name) VALUES ('DO','RO',i18n('Dolj'));
INSERT INTO state(code, country, name) VALUES ('GA','RO',i18n('Galati'));
INSERT INTO state(code, country, name) VALUES ('GI','RO',i18n('Giurgiu'));
INSERT INTO state(code, country, name) VALUES ('GO','RO',i18n('Gorj'));
INSERT INTO state(code, country, name) VALUES ('HA','RO',i18n('Harghita'));
INSERT INTO state(code, country, name) VALUES ('HU','RO',i18n('Hunedoara'));
INSERT INTO state(code, country, name) VALUES ('IA','RO',i18n('Ialomita'));
INSERT INTO state(code, country, name) VALUES ('IS','RO',i18n('Iasi'));
INSERT INTO state(code, country, name) VALUES ('IL','RO',i18n('Ilfov'));
INSERT INTO state(code, country, name) VALUES ('MA','RO',i18n('Maramures'));
INSERT INTO state(code, country, name) VALUES ('ME','RO',i18n('Mehedinti'));
INSERT INTO state(code, country, name) VALUES ('MU','RO',i18n('Mures'));
INSERT INTO state(code, country, name) VALUES ('NE','RO',i18n('Neamt'));
INSERT INTO state(code, country, name) VALUES ('OL','RO',i18n('Olt'));
INSERT INTO state(code, country, name) VALUES ('PR','RO',i18n('Prahova'));
INSERT INTO state(code, country, name) VALUES ('SA','RO',i18n('Salaj'));
INSERT INTO state(code, country, name) VALUES ('SM','RO',i18n('Satu-Mare'));
INSERT INTO state(code, country, name) VALUES ('SI','RO',i18n('Sibiu'));
INSERT INTO state(code, country, name) VALUES ('SU','RO',i18n('Suceava'));
INSERT INTO state(code, country, name) VALUES ('TE','RO',i18n('Teleorman'));
INSERT INTO state(code, country, name) VALUES ('TI','RO',i18n('Timis'));
INSERT INTO state(code, country, name) VALUES ('TU','RO',i18n('Tulcea'));
INSERT INTO state(code, country, name) VALUES ('VA','RO',i18n('Vaslui'));
INSERT INTO state(code, country, name) VALUES ('VI','RO',i18n('Vilcea'));
INSERT INTO state(code, country, name) VALUES ('VR','RO',i18n('Vrancea'));
-- country RU
INSERT INTO state(code, country, name) VALUES ('AB','RU',i18n('Abakan'));
INSERT INTO state(code, country, name) VALUES ('AG','RU',i18n('Aginskoye'));
INSERT INTO state(code, country, name) VALUES ('AN','RU',i18n('Anadyr'));
INSERT INTO state(code, country, name) VALUES ('AR','RU',i18n('Arkahangelsk'));
INSERT INTO state(code, country, name) VALUES ('AS','RU',i18n('Astrakhan'));
INSERT INTO state(code, country, name) VALUES ('BA','RU',i18n('Barnaul'));
INSERT INTO state(code, country, name) VALUES ('BE','RU',i18n('Belgorod'));
INSERT INTO state(code, country, name) VALUES ('BI','RU',i18n('Birobidzhan'));
INSERT INTO state(code, country, name) VALUES ('BL','RU',i18n('Blagoveshchensk'));
INSERT INTO state(code, country, name) VALUES ('BR','RU',i18n('Bryansk'));
INSERT INTO state(code, country, name) VALUES ('CH','RU',i18n('Cheboksary'));
INSERT INTO state(code, country, name) VALUES ('CL','RU',i18n('Chelyabinsk'));
INSERT INTO state(code, country, name) VALUES ('CR','RU',i18n('Cherkessk'));
INSERT INTO state(code, country, name) VALUES ('CI','RU',i18n('Chita'));
INSERT INTO state(code, country, name) VALUES ('DU','RU',i18n('Dudinka'));
INSERT INTO state(code, country, name) VALUES ('EL','RU',i18n('Elista'));
INSERT INTO state(code, country, name) VALUES ('GO','RU',i18n('Gomo-Altaysk'));
INSERT INTO state(code, country, name) VALUES ('GA','RU',i18n('Gorno-Altaysk'));
INSERT INTO state(code, country, name) VALUES ('GR','RU',i18n('Groznyy'));
INSERT INTO state(code, country, name) VALUES ('IR','RU',i18n('Irkutsk'));
INSERT INTO state(code, country, name) VALUES ('IV','RU',i18n('Ivanovo'));
INSERT INTO state(code, country, name) VALUES ('IZ','RU',i18n('Izhevsk'));
INSERT INTO state(code, country, name) VALUES ('KA','RU',i18n('Kalinigrad'));
INSERT INTO state(code, country, name) VALUES ('KL','RU',i18n('Kaluga'));
INSERT INTO state(code, country, name) VALUES ('KS','RU',i18n('Kasnodar'));
INSERT INTO state(code, country, name) VALUES ('KZ','RU',i18n('Kazan'));
INSERT INTO state(code, country, name) VALUES ('KE','RU',i18n('Kemerovo'));
INSERT INTO state(code, country, name) VALUES ('KH','RU',i18n('Khabarovsk'));
INSERT INTO state(code, country, name) VALUES ('KM','RU',i18n('Khanty-Mansiysk'));
INSERT INTO state(code, country, name) VALUES ('KO','RU',i18n('Kostroma'));
INSERT INTO state(code, country, name) VALUES ('KR','RU',i18n('Krasnodar'));
INSERT INTO state(code, country, name) VALUES ('KN','RU',i18n('Krasnoyarsk'));
INSERT INTO state(code, country, name) VALUES ('KU','RU',i18n('Kudymkar'));
INSERT INTO state(code, country, name) VALUES ('KG','RU',i18n('Kurgan'));
INSERT INTO state(code, country, name) VALUES ('KK','RU',i18n('Kursk'));
INSERT INTO state(code, country, name) VALUES ('KY','RU',i18n('Kyzyl'));
INSERT INTO state(code, country, name) VALUES ('LI','RU',i18n('Lipetsk'));
INSERT INTO state(code, country, name) VALUES ('MA','RU',i18n('Magadan'));
INSERT INTO state(code, country, name) VALUES ('MK','RU',i18n('Makhachkala'));
INSERT INTO state(code, country, name) VALUES ('MY','RU',i18n('Maykop'));
INSERT INTO state(code, country, name) VALUES ('MO','RU',i18n('Moscow'));
INSERT INTO state(code, country, name) VALUES ('MU','RU',i18n('Murmansk'));
INSERT INTO state(code, country, name) VALUES ('NA','RU',i18n('Nalchik'));
INSERT INTO state(code, country, name) VALUES ('NR','RU',i18n('Naryan Mar'));
INSERT INTO state(code, country, name) VALUES ('NZ','RU',i18n('Nazran'));
INSERT INTO state(code, country, name) VALUES ('NI','RU',i18n('Nizhniy Novgorod'));
INSERT INTO state(code, country, name) VALUES ('NO','RU',i18n('Novgorod'));
INSERT INTO state(code, country, name) VALUES ('NV','RU',i18n('Novosibirsk'));
INSERT INTO state(code, country, name) VALUES ('OM','RU',i18n('Omsk'));
INSERT INTO state(code, country, name) VALUES ('OR','RU',i18n('Orel'));
INSERT INTO state(code, country, name) VALUES ('OE','RU',i18n('Orenburg'));
INSERT INTO state(code, country, name) VALUES ('PA','RU',i18n('Palana'));
INSERT INTO state(code, country, name) VALUES ('PE','RU',i18n('Penza'));
INSERT INTO state(code, country, name) VALUES ('PR','RU',i18n('Perm'));
INSERT INTO state(code, country, name) VALUES ('PK','RU',i18n('Petropavlovsk-Kamchatskiy'));
INSERT INTO state(code, country, name) VALUES ('PT','RU',i18n('Petrozavodsk'));
INSERT INTO state(code, country, name) VALUES ('PS','RU',i18n('Pskov'));
INSERT INTO state(code, country, name) VALUES ('RO','RU',i18n('Rostov-na-Donu'));
INSERT INTO state(code, country, name) VALUES ('RY','RU',i18n('Ryazan'));
INSERT INTO state(code, country, name) VALUES ('SL','RU',i18n('Salekhard'));
INSERT INTO state(code, country, name) VALUES ('SA','RU',i18n('Samara'));
INSERT INTO state(code, country, name) VALUES ('SR','RU',i18n('Saransk'));
INSERT INTO state(code, country, name) VALUES ('SV','RU',i18n('Saratov'));
INSERT INTO state(code, country, name) VALUES ('SM','RU',i18n('Smolensk'));
INSERT INTO state(code, country, name) VALUES ('SP','RU',i18n('St. Petersburg'));
INSERT INTO state(code, country, name) VALUES ('ST','RU',i18n('Stavropol'));
INSERT INTO state(code, country, name) VALUES ('SY','RU',i18n('Syktyvkar'));
INSERT INTO state(code, country, name) VALUES ('TA','RU',i18n('Tambov'));
INSERT INTO state(code, country, name) VALUES ('TO','RU',i18n('Tomsk'));
INSERT INTO state(code, country, name) VALUES ('TU','RU',i18n('Tula'));
INSERT INTO state(code, country, name) VALUES ('TR','RU',i18n('Tura'));
INSERT INTO state(code, country, name) VALUES ('TV','RU',i18n('Tver'));
INSERT INTO state(code, country, name) VALUES ('TY','RU',i18n('Tyumen'));
INSERT INTO state(code, country, name) VALUES ('UF','RU',i18n('Ufa'));
INSERT INTO state(code, country, name) VALUES ('UL','RU',i18n('Ul''yanovsk'));
INSERT INTO state(code, country, name) VALUES ('UU','RU',i18n('Ulan-Ude'));
INSERT INTO state(code, country, name) VALUES ('US','RU',i18n('Ust''-Ordynskiy'));
INSERT INTO state(code, country, name) VALUES ('VL','RU',i18n('Vladikavkaz'));
INSERT INTO state(code, country, name) VALUES ('VA','RU',i18n('Vladimir'));
INSERT INTO state(code, country, name) VALUES ('VV','RU',i18n('Vladivostok'));
INSERT INTO state(code, country, name) VALUES ('VG','RU',i18n('Volgograd'));
INSERT INTO state(code, country, name) VALUES ('VD','RU',i18n('Vologda'));
INSERT INTO state(code, country, name) VALUES ('VO','RU',i18n('Voronezh'));
INSERT INTO state(code, country, name) VALUES ('VY','RU',i18n('Vyatka'));
INSERT INTO state(code, country, name) VALUES ('YA','RU',i18n('Yakutsk'));
INSERT INTO state(code, country, name) VALUES ('YR','RU',i18n('Yaroslavl'));
INSERT INTO state(code, country, name) VALUES ('YE','RU',i18n('Yekaterinburg'));
INSERT INTO state(code, country, name) VALUES ('YO','RU',i18n('Yoshkar-Ola'));
-- country RW
INSERT INTO state(code, country, name) VALUES ('RW-1','RW',i18n('StateNameStub'));
-- country SA
INSERT INTO state(code, country, name) VALUES ('SA-1','SA',i18n('StateNameStub'));
-- country SB
INSERT INTO state(code, country, name) VALUES ('SB-1','SB',i18n('StateNameStub'));
-- country SC
INSERT INTO state(code, country, name) VALUES ('SC-1','SC',i18n('StateNameStub'));
-- country SD
INSERT INTO state(code, country, name) VALUES ('SD-1','SD',i18n('StateNameStub'));
-- country SE
INSERT INTO state(code, country, name) VALUES ('BL','SE',i18n('Blekinge'));
INSERT INTO state(code, country, name) VALUES ('DA','SE',i18n('Dalarnas'));
INSERT INTO state(code, country, name) VALUES ('GA','SE',i18n('Gavleborgs'));
INSERT INTO state(code, country, name) VALUES ('GO','SE',i18n('Gotlands'));
INSERT INTO state(code, country, name) VALUES ('HA','SE',i18n('Hallands'));
INSERT INTO state(code, country, name) VALUES ('JA','SE',i18n('Jamtlands'));
INSERT INTO state(code, country, name) VALUES ('JO','SE',i18n('Jonkopings'));
INSERT INTO state(code, country, name) VALUES ('KA','SE',i18n('Kalmar'));
INSERT INTO state(code, country, name) VALUES ('KR','SE',i18n('Kronobergs'));
INSERT INTO state(code, country, name) VALUES ('NO','SE',i18n('Norrbottens'));
INSERT INTO state(code, country, name) VALUES ('OR','SE',i18n('Orebro'));
INSERT INTO state(code, country, name) VALUES ('OS','SE',i18n('Ostergotlands'));
INSERT INTO state(code, country, name) VALUES ('SK','SE',i18n('Skane'));
INSERT INTO state(code, country, name) VALUES ('SO','SE',i18n('Sodermanlands'));
INSERT INTO state(code, country, name) VALUES ('ST','SE',i18n('Stockholms'));
INSERT INTO state(code, country, name) VALUES ('UP','SE',i18n('Uppsala'));
INSERT INTO state(code, country, name) VALUES ('VA','SE',i18n('Varmlands'));
INSERT INTO state(code, country, name) VALUES ('VS','SE',i18n('Vasterbottens'));
INSERT INTO state(code, country, name) VALUES ('VT','SE',i18n('Vasternorrlands'));
INSERT INTO state(code, country, name) VALUES ('VM','SE',i18n('Vastmanlands'));
INSERT INTO state(code, country, name) VALUES ('VG','SE',i18n('Vastra Gotalands'));
-- country SG
INSERT INTO state(code, country, name) VALUES ('SG-1','SG',i18n('StateNameStub'));
-- country SH
INSERT INTO state(code, country, name) VALUES ('AS','SH',i18n('Ascension'));
INSERT INTO state(code, country, name) VALUES ('SH','SH',i18n('Saint Helena'));
INSERT INTO state(code, country, name) VALUES ('TC','SH',i18n('Tristan da Cunha'));
-- country SI
INSERT INTO state(code, country, name) VALUES ('SI-1','SI',i18n('StateNameStub'));
-- country SJ
INSERT INTO state(code, country, name) VALUES ('SJ-1','SJ',i18n('StateNameStub'));
-- country SK
INSERT INTO state(code, country, name) VALUES ('BA','SK',i18n('Banskobystricky'));
INSERT INTO state(code, country, name) VALUES ('BR','SK',i18n('Bratislavsky'));
INSERT INTO state(code, country, name) VALUES ('KO','SK',i18n('Kosicky'));
INSERT INTO state(code, country, name) VALUES ('NI','SK',i18n('Nitriansky'));
INSERT INTO state(code, country, name) VALUES ('PR','SK',i18n('Presovsky'));
INSERT INTO state(code, country, name) VALUES ('TR','SK',i18n('Trenciansky'));
INSERT INTO state(code, country, name) VALUES ('TN','SK',i18n('Trnavsky'));
INSERT INTO state(code, country, name) VALUES ('ZI','SK',i18n('Zilinsky'));
-- country SL
INSERT INTO state(code, country, name) VALUES ('SL-1','SL',i18n('StateNameStub'));
-- country SM
INSERT INTO state(code, country, name) VALUES ('SM-1','SM',i18n('StateNameStub'));
-- country SN
INSERT INTO state(code, country, name) VALUES ('SN-1','SN',i18n('StateNameStub'));
-- country SO
INSERT INTO state(code, country, name) VALUES ('SO-1','SO',i18n('StateNameStub'));
-- country SR
INSERT INTO state(code, country, name) VALUES ('SR-1','SR',i18n('StateNameStub'));
-- country ST
INSERT INTO state(code, country, name) VALUES ('ST-1','ST',i18n('StateNameStub'));
-- country SV
INSERT INTO state(code, country, name) VALUES ('AH','SV',i18n('Ahuachapan'));
INSERT INTO state(code, country, name) VALUES ('CA','SV',i18n('Cabanas'));
INSERT INTO state(code, country, name) VALUES ('CH','SV',i18n('Chalatenango'));
INSERT INTO state(code, country, name) VALUES ('CU','SV',i18n('Cuscatlan'));
INSERT INTO state(code, country, name) VALUES ('LL','SV',i18n('La Libertad'));
INSERT INTO state(code, country, name) VALUES ('LP','SV',i18n('La Paz'));
INSERT INTO state(code, country, name) VALUES ('LU','SV',i18n('La Union'));
INSERT INTO state(code, country, name) VALUES ('MO','SV',i18n('Morazan'));
INSERT INTO state(code, country, name) VALUES ('SM','SV',i18n('San Miguel'));
INSERT INTO state(code, country, name) VALUES ('SS','SV',i18n('San Salvador'));
INSERT INTO state(code, country, name) VALUES ('SV','SV',i18n('San Vicente'));
INSERT INTO state(code, country, name) VALUES ('SA','SV',i18n('Santa Ana'));
INSERT INTO state(code, country, name) VALUES ('SO','SV',i18n('Sonsonate'));
INSERT INTO state(code, country, name) VALUES ('US','SV',i18n('Usulutan'));
-- country SY
INSERT INTO state(code, country, name) VALUES ('SY-1','SY',i18n('StateNameStub'));
-- country SZ
INSERT INTO state(code, country, name) VALUES ('SZ-1','SZ',i18n('StateNameStub'));
-- country TC
INSERT INTO state(code, country, name) VALUES ('TC-1','TC',i18n('StateNameStub'));
-- country TD
INSERT INTO state(code, country, name) VALUES ('TD-1','TD',i18n('StateNameStub'));
-- country TF
INSERT INTO state(code, country, name) VALUES ('TF-1','TF',i18n('StateNameStub'));
-- country TG
INSERT INTO state(code, country, name) VALUES ('TG-1','TG',i18n('StateNameStub'));
-- country TH
INSERT INTO state(code, country, name) VALUES ('AC','TH',i18n('Amnat Charoen'));
INSERT INTO state(code, country, name) VALUES ('AT','TH',i18n('Ang Thong'));
INSERT INTO state(code, country, name) VALUES ('BU','TH',i18n('Buriram'));
INSERT INTO state(code, country, name) VALUES ('CH','TH',i18n('Chachoengsao'));
INSERT INTO state(code, country, name) VALUES ('CN','TH',i18n('Chai Nat'));
INSERT INTO state(code, country, name) VALUES ('CA','TH',i18n('Chaiyaphum'));
INSERT INTO state(code, country, name) VALUES ('CT','TH',i18n('Chanthaburi'));
INSERT INTO state(code, country, name) VALUES ('CM','TH',i18n('Chiang Mai'));
INSERT INTO state(code, country, name) VALUES ('CR','TH',i18n('Chiang Rai'));
INSERT INTO state(code, country, name) VALUES ('CB','TH',i18n('Chon Buri'));
INSERT INTO state(code, country, name) VALUES ('CU','TH',i18n('Chumphon'));
INSERT INTO state(code, country, name) VALUES ('KA','TH',i18n('Kalasin'));
INSERT INTO state(code, country, name) VALUES ('KP','TH',i18n('Kamphaeng Phet'));
INSERT INTO state(code, country, name) VALUES ('KN','TH',i18n('Kanchanaburi'));
INSERT INTO state(code, country, name) VALUES ('KK','TH',i18n('Khon Kaen'));
INSERT INTO state(code, country, name) VALUES ('KR','TH',i18n('Krabi'));
INSERT INTO state(code, country, name) VALUES ('KT','TH',i18n('Krung Thep Mahanakhon (Bangkok)'));
INSERT INTO state(code, country, name) VALUES ('LA','TH',i18n('Lampang'));
INSERT INTO state(code, country, name) VALUES ('LM','TH',i18n('Lamphun'));
INSERT INTO state(code, country, name) VALUES ('LO','TH',i18n('Loei'));
INSERT INTO state(code, country, name) VALUES ('LB','TH',i18n('Lop Buri'));
INSERT INTO state(code, country, name) VALUES ('MH','TH',i18n('Mae Hong Son'));
INSERT INTO state(code, country, name) VALUES ('MS','TH',i18n('Maha Sarakham'));
INSERT INTO state(code, country, name) VALUES ('MU','TH',i18n('Mukdahan'));
INSERT INTO state(code, country, name) VALUES ('NN','TH',i18n('Nakhon Nayok'));
INSERT INTO state(code, country, name) VALUES ('NP','TH',i18n('Nakhon Pathom'));
INSERT INTO state(code, country, name) VALUES ('NM','TH',i18n('Nakhon Phanom'));
INSERT INTO state(code, country, name) VALUES ('NR','TH',i18n('Nakhon Ratchasima'));
INSERT INTO state(code, country, name) VALUES ('NS','TH',i18n('Nakhon Sawan'));
INSERT INTO state(code, country, name) VALUES ('NT','TH',i18n('Nakhon Si Thammarat'));
INSERT INTO state(code, country, name) VALUES ('NA','TH',i18n('Nan'));
INSERT INTO state(code, country, name) VALUES ('NW','TH',i18n('Narathiwat'));
INSERT INTO state(code, country, name) VALUES ('NB','TH',i18n('Nong Bua Lamphu'));
INSERT INTO state(code, country, name) VALUES ('NK','TH',i18n('Nong Khai'));
INSERT INTO state(code, country, name) VALUES ('NO','TH',i18n('Nonthaburi'));
INSERT INTO state(code, country, name) VALUES ('PT','TH',i18n('Pathum Thani'));
INSERT INTO state(code, country, name) VALUES ('PA','TH',i18n('Pattani'));
INSERT INTO state(code, country, name) VALUES ('PH','TH',i18n('Phangnga'));
INSERT INTO state(code, country, name) VALUES ('PL','TH',i18n('Phatthalung'));
INSERT INTO state(code, country, name) VALUES ('PY','TH',i18n('Phayao'));
INSERT INTO state(code, country, name) VALUES ('PE','TH',i18n('Phetchabun'));
INSERT INTO state(code, country, name) VALUES ('PC','TH',i18n('Phetchaburi'));
INSERT INTO state(code, country, name) VALUES ('PI','TH',i18n('Phichit'));
INSERT INTO state(code, country, name) VALUES ('PX','TH',i18n('Phitsanulok'));
INSERT INTO state(code, country, name) VALUES ('PN','TH',i18n('Phra Nakhon Si Ayutthaya'));
INSERT INTO state(code, country, name) VALUES ('PR','TH',i18n('Phrae'));
INSERT INTO state(code, country, name) VALUES ('PU','TH',i18n('Phuket'));
INSERT INTO state(code, country, name) VALUES ('PB','TH',i18n('Prachin Buri'));
INSERT INTO state(code, country, name) VALUES ('PK','TH',i18n('Prachuap Khiri Khan'));
INSERT INTO state(code, country, name) VALUES ('RA','TH',i18n('Ranong'));
INSERT INTO state(code, country, name) VALUES ('RT','TH',i18n('Ratchaburi'));
INSERT INTO state(code, country, name) VALUES ('RY','TH',i18n('Rayong'));
INSERT INTO state(code, country, name) VALUES ('RE','TH',i18n('Roi Et'));
INSERT INTO state(code, country, name) VALUES ('SK','TH',i18n('Sa Kaeo'));
INSERT INTO state(code, country, name) VALUES ('SN','TH',i18n('Sakon Nakhon'));
INSERT INTO state(code, country, name) VALUES ('SP','TH',i18n('Samut Prakan'));
INSERT INTO state(code, country, name) VALUES ('SS','TH',i18n('Samut Sakhon'));
INSERT INTO state(code, country, name) VALUES ('SM','TH',i18n('Samut Songkhram'));
INSERT INTO state(code, country, name) VALUES ('SB','TH',i18n('Sara Buri'));
INSERT INTO state(code, country, name) VALUES ('SA','TH',i18n('Satun'));
INSERT INTO state(code, country, name) VALUES ('SI','TH',i18n('Sing Buri'));
INSERT INTO state(code, country, name) VALUES ('SC','TH',i18n('Sisaket'));
INSERT INTO state(code, country, name) VALUES ('SO','TH',i18n('Songkhla'));
INSERT INTO state(code, country, name) VALUES ('SH','TH',i18n('Sukhothai'));
INSERT INTO state(code, country, name) VALUES ('SR','TH',i18n('Suphan Buri'));
INSERT INTO state(code, country, name) VALUES ('ST','TH',i18n('Surat Thani'));
INSERT INTO state(code, country, name) VALUES ('SU','TH',i18n('Surin'));
INSERT INTO state(code, country, name) VALUES ('TA','TH',i18n('Tak'));
INSERT INTO state(code, country, name) VALUES ('TR','TH',i18n('Trang'));
INSERT INTO state(code, country, name) VALUES ('TT','TH',i18n('Trat'));
INSERT INTO state(code, country, name) VALUES ('UR','TH',i18n('Ubon Ratchathani'));
INSERT INTO state(code, country, name) VALUES ('UT','TH',i18n('Udon Thani'));
INSERT INTO state(code, country, name) VALUES ('UH','TH',i18n('Uthai Thani'));
INSERT INTO state(code, country, name) VALUES ('UA','TH',i18n('Uttaradit'));
INSERT INTO state(code, country, name) VALUES ('YA','TH',i18n('Yala'));
INSERT INTO state(code, country, name) VALUES ('YS','TH',i18n('Yasothon'));
-- country TJ
INSERT INTO state(code, country, name) VALUES ('TJ-1','TJ',i18n('StateNameStub'));
-- country TK
INSERT INTO state(code, country, name) VALUES ('TK-1','TK',i18n('StateNameStub'));
-- country TM
INSERT INTO state(code, country, name) VALUES ('TM-1','TM',i18n('StateNameStub'));
-- country TN
INSERT INTO state(code, country, name) VALUES ('AK','TN',i18n('Al Kaf'));
INSERT INTO state(code, country, name) VALUES ('AM','TN',i18n('Al Mahdiyah'));
INSERT INTO state(code, country, name) VALUES ('AU','TN',i18n('Al Munastir'));
INSERT INTO state(code, country, name) VALUES ('AQ','TN',i18n('Al Qasrayn'));
INSERT INTO state(code, country, name) VALUES ('AA','TN',i18n('Al Qayrawan'));
INSERT INTO state(code, country, name) VALUES ('AR','TN',i18n('Aryanah'));
INSERT INTO state(code, country, name) VALUES ('BJ','TN',i18n('Bajah'));
INSERT INTO state(code, country, name) VALUES ('BN','TN',i18n('Banzart'));
INSERT INTO state(code, country, name) VALUES ('BA','TN',i18n('Bin ''Arus'));
INSERT INTO state(code, country, name) VALUES ('JU','TN',i18n('Jundubah'));
INSERT INTO state(code, country, name) VALUES ('MA','TN',i18n('Madanin'));
INSERT INTO state(code, country, name) VALUES ('NA','TN',i18n('Nabul'));
INSERT INTO state(code, country, name) VALUES ('QB','TN',i18n('Qabis'));
INSERT INTO state(code, country, name) VALUES ('QF','TN',i18n('Qafsah'));
INSERT INTO state(code, country, name) VALUES ('QI','TN',i18n('Qibili'));
INSERT INTO state(code, country, name) VALUES ('SA','TN',i18n('Safaqis'));
INSERT INTO state(code, country, name) VALUES ('SZ','TN',i18n('Sidi Bu Zayd'));
INSERT INTO state(code, country, name) VALUES ('SI','TN',i18n('Silyanah'));
INSERT INTO state(code, country, name) VALUES ('SU','TN',i18n('Susah'));
INSERT INTO state(code, country, name) VALUES ('TA','TN',i18n('Tatawin'));
INSERT INTO state(code, country, name) VALUES ('TW','TN',i18n('Tawzar'));
INSERT INTO state(code, country, name) VALUES ('TU','TN',i18n('Tunis'));
INSERT INTO state(code, country, name) VALUES ('ZA','TN',i18n('Zaghwan'));
-- country TO
INSERT INTO state(code, country, name) VALUES ('TO-1','TO',i18n('StateNameStub'));
-- country TP
INSERT INTO state(code, country, name) VALUES ('TP-1','TP',i18n('StateNameStub'));
-- country TR
INSERT INTO state(code, country, name) VALUES ('AD','TR',i18n('Adana'));
INSERT INTO state(code, country, name) VALUES ('AI','TR',i18n('Adiyaman'));
INSERT INTO state(code, country, name) VALUES ('AF','TR',i18n('Afyon'));
INSERT INTO state(code, country, name) VALUES ('AG','TR',i18n('Agri'));
INSERT INTO state(code, country, name) VALUES ('AK','TR',i18n('Aksaray'));
INSERT INTO state(code, country, name) VALUES ('AM','TR',i18n('Amasya'));
INSERT INTO state(code, country, name) VALUES ('AN','TR',i18n('Ankara'));
INSERT INTO state(code, country, name) VALUES ('AT','TR',i18n('Antalya'));
INSERT INTO state(code, country, name) VALUES ('AR','TR',i18n('Ardahan'));
INSERT INTO state(code, country, name) VALUES ('AV','TR',i18n('Artvin'));
INSERT INTO state(code, country, name) VALUES ('AY','TR',i18n('Aydin'));
INSERT INTO state(code, country, name) VALUES ('BA','TR',i18n('Balikesir'));
INSERT INTO state(code, country, name) VALUES ('BR','TR',i18n('Bartin'));
INSERT INTO state(code, country, name) VALUES ('BT','TR',i18n('Batman'));
INSERT INTO state(code, country, name) VALUES ('BY','TR',i18n('Bayburt'));
INSERT INTO state(code, country, name) VALUES ('BI','TR',i18n('Bilecik'));
INSERT INTO state(code, country, name) VALUES ('BN','TR',i18n('Bingol'));
INSERT INTO state(code, country, name) VALUES ('BL','TR',i18n('Bitlis'));
INSERT INTO state(code, country, name) VALUES ('BO','TR',i18n('Bolu'));
INSERT INTO state(code, country, name) VALUES ('BU','TR',i18n('Burdur'));
INSERT INTO state(code, country, name) VALUES ('BS','TR',i18n('Bursa'));
INSERT INTO state(code, country, name) VALUES ('CA','TR',i18n('Canakkale'));
INSERT INTO state(code, country, name) VALUES ('CN','TR',i18n('Cankiri'));
INSERT INTO state(code, country, name) VALUES ('CO','TR',i18n('Corum'));
INSERT INTO state(code, country, name) VALUES ('DE','TR',i18n('Denizli'));
INSERT INTO state(code, country, name) VALUES ('DI','TR',i18n('Diyarbakir'));
INSERT INTO state(code, country, name) VALUES ('ED','TR',i18n('Edirne'));
INSERT INTO state(code, country, name) VALUES ('EL','TR',i18n('Elazig'));
INSERT INTO state(code, country, name) VALUES ('ER','TR',i18n('Erzincan'));
INSERT INTO state(code, country, name) VALUES ('EZ','TR',i18n('Erzurum'));
INSERT INTO state(code, country, name) VALUES ('ES','TR',i18n('Eskisehir'));
INSERT INTO state(code, country, name) VALUES ('GA','TR',i18n('Gazi Antep'));
INSERT INTO state(code, country, name) VALUES ('GI','TR',i18n('Giresun'));
INSERT INTO state(code, country, name) VALUES ('GU','TR',i18n('Gumushane'));
INSERT INTO state(code, country, name) VALUES ('HA','TR',i18n('Hakkari'));
INSERT INTO state(code, country, name) VALUES ('HT','TR',i18n('Hatay'));
INSERT INTO state(code, country, name) VALUES ('IC','TR',i18n('Icel'));
INSERT INTO state(code, country, name) VALUES ('IG','TR',i18n('Igdir'));
INSERT INTO state(code, country, name) VALUES ('IS','TR',i18n('Isparta'));
INSERT INTO state(code, country, name) VALUES ('IT','TR',i18n('Istanbul'));
INSERT INTO state(code, country, name) VALUES ('IZ','TR',i18n('Izmir'));
INSERT INTO state(code, country, name) VALUES ('KM','TR',i18n('Kahraman Maras'));
INSERT INTO state(code, country, name) VALUES ('KB','TR',i18n('Karabuk'));
INSERT INTO state(code, country, name) VALUES ('KN','TR',i18n('Karaman'));
INSERT INTO state(code, country, name) VALUES ('KA','TR',i18n('Kars'));
INSERT INTO state(code, country, name) VALUES ('KT','TR',i18n('Kastamonu'));
INSERT INTO state(code, country, name) VALUES ('KY','TR',i18n('Kayseri'));
INSERT INTO state(code, country, name) VALUES ('KL','TR',i18n('Kilis'));
INSERT INTO state(code, country, name) VALUES ('KR','TR',i18n('Kirikkale'));
INSERT INTO state(code, country, name) VALUES ('KK','TR',i18n('Kirklareli'));
INSERT INTO state(code, country, name) VALUES ('KS','TR',i18n('Kirsehir'));
INSERT INTO state(code, country, name) VALUES ('KC','TR',i18n('Kocaeli'));
INSERT INTO state(code, country, name) VALUES ('KO','TR',i18n('Konya'));
INSERT INTO state(code, country, name) VALUES ('KU','TR',i18n('Kutahya'));
INSERT INTO state(code, country, name) VALUES ('ML','TR',i18n('Malatya'));
INSERT INTO state(code, country, name) VALUES ('MN','TR',i18n('Manisa'));
INSERT INTO state(code, country, name) VALUES ('MR','TR',i18n('Mardin'));
INSERT INTO state(code, country, name) VALUES ('MG','TR',i18n('Mugla'));
INSERT INTO state(code, country, name) VALUES ('MS','TR',i18n('Mus'));
INSERT INTO state(code, country, name) VALUES ('NE','TR',i18n('Nevsehir'));
INSERT INTO state(code, country, name) VALUES ('NI','TR',i18n('Nigde'));
INSERT INTO state(code, country, name) VALUES ('OR','TR',i18n('Ordu'));
INSERT INTO state(code, country, name) VALUES ('OS','TR',i18n('Osmaniye'));
INSERT INTO state(code, country, name) VALUES ('RI','TR',i18n('Rize'));
INSERT INTO state(code, country, name) VALUES ('SA','TR',i18n('Sakarya'));
INSERT INTO state(code, country, name) VALUES ('SM','TR',i18n('Samsun'));
INSERT INTO state(code, country, name) VALUES ('SU','TR',i18n('Sanli Urfa'));
INSERT INTO state(code, country, name) VALUES ('SI','TR',i18n('Siirt'));
INSERT INTO state(code, country, name) VALUES ('SN','TR',i18n('Sinop'));
INSERT INTO state(code, country, name) VALUES ('SR','TR',i18n('Sirnak'));
INSERT INTO state(code, country, name) VALUES ('SV','TR',i18n('Sivas'));
INSERT INTO state(code, country, name) VALUES ('TE','TR',i18n('Tekirdag'));
INSERT INTO state(code, country, name) VALUES ('TO','TR',i18n('Tokat'));
INSERT INTO state(code, country, name) VALUES ('TR','TR',i18n('Trabzon'));
INSERT INTO state(code, country, name) VALUES ('TU','TR',i18n('Tunceli'));
INSERT INTO state(code, country, name) VALUES ('US','TR',i18n('Usak'));
INSERT INTO state(code, country, name) VALUES ('VA','TR',i18n('Van'));
INSERT INTO state(code, country, name) VALUES ('YA','TR',i18n('Yalova'));
INSERT INTO state(code, country, name) VALUES ('YO','TR',i18n('Yozgat'));
INSERT INTO state(code, country, name) VALUES ('ZO','TR',i18n('Zonguldak'));
-- country TT
INSERT INTO state(code, country, name) VALUES ('TT-1','TT',i18n('StateNameStub'));
-- country TV
INSERT INTO state(code, country, name) VALUES ('TV-1','TV',i18n('StateNameStub'));
-- country TW
INSERT INTO state(code, country, name) VALUES ('TW-1','TW',i18n('StateNameStub'));
-- country TZ
INSERT INTO state(code, country, name) VALUES ('TZ-1','TZ',i18n('StateNameStub'));
-- country UA
INSERT INTO state(code, country, name) VALUES ('KR','UA',i18n('Avtonomna Respublika Krym'));
INSERT INTO state(code, country, name) VALUES ('CH','UA',i18n('Cherkas''ka'));
INSERT INTO state(code, country, name) VALUES ('CE','UA',i18n('Chernihivs''ka'));
INSERT INTO state(code, country, name) VALUES ('CR','UA',i18n('Chernivets''ka'));
INSERT INTO state(code, country, name) VALUES ('DN','UA',i18n('Dnipropetrovs''ka'));
INSERT INTO state(code, country, name) VALUES ('DO','UA',i18n('Donets''ka'));
INSERT INTO state(code, country, name) VALUES ('IV','UA',i18n('Ivano-Frankivs''ka'));
INSERT INTO state(code, country, name) VALUES ('KA','UA',i18n('Kharkivs''ka'));
INSERT INTO state(code, country, name) VALUES ('KE','UA',i18n('Khersons''ka'));
INSERT INTO state(code, country, name) VALUES ('KL','UA',i18n('Khmel''nyts|ka'));
INSERT INTO state(code, country, name) VALUES ('KI','UA',i18n('Kirovohrads''ka'));
INSERT INTO state(code, country, name) VALUES ('KY','UA',i18n('Kyyiv'));
INSERT INTO state(code, country, name) VALUES ('KV','UA',i18n('Kyyivs''ka'));
INSERT INTO state(code, country, name) VALUES ('LV','UA',i18n('L''vivs|ka'));
INSERT INTO state(code, country, name) VALUES ('LU','UA',i18n('Luhans''ka'));
INSERT INTO state(code, country, name) VALUES ('MY','UA',i18n('Mykolayivs''ka'));
INSERT INTO state(code, country, name) VALUES ('OD','UA',i18n('Odes''ka'));
INSERT INTO state(code, country, name) VALUES ('PO','UA',i18n('Poltavs''ka'));
INSERT INTO state(code, country, name) VALUES ('RI','UA',i18n('Rivnens''ka'));
INSERT INTO state(code, country, name) VALUES ('SE','UA',i18n('Sevastopol'''));
INSERT INTO state(code, country, name) VALUES ('SU','UA',i18n('Sums''ka'));
INSERT INTO state(code, country, name) VALUES ('TE','UA',i18n('Ternopil''s|ka'));
INSERT INTO state(code, country, name) VALUES ('VI','UA',i18n('Vinnyts''ka'));
INSERT INTO state(code, country, name) VALUES ('VO','UA',i18n('Volyns''ka'));
INSERT INTO state(code, country, name) VALUES ('ZK','UA',i18n('Zakarpats''ka'));
INSERT INTO state(code, country, name) VALUES ('ZP','UA',i18n('Zaporiz''ka'));
INSERT INTO state(code, country, name) VALUES ('ZH','UA',i18n('Zhytomyrs''ka'));
-- country UG
INSERT INTO state(code, country, name) VALUES ('UG-1','UG',i18n('StateNameStub'));
-- country UM
--INSERT INTO state(code, country, name) VALUES ('UM-1','UM',i18n('StateNameStub'));
-- country US
INSERT INTO state(code, country, name) VALUES ('AL','US',i18n('Alabama'));
INSERT INTO state(code, country, name) VALUES ('AK','US',i18n('Alaska'));
INSERT INTO state(code, country, name) VALUES ('AS','US',i18n('American Samoa'));
INSERT INTO state(code, country, name) VALUES ('AZ','US',i18n('Arizona'));
INSERT INTO state(code, country, name) VALUES ('AR','US',i18n('Arkansas'));
INSERT INTO state(code, country, name) VALUES ('AF','US',i18n('Armed Forces Africa'));
INSERT INTO state(code, country, name) VALUES ('AA','US',i18n('Armed Forces Americas'));
INSERT INTO state(code, country, name) VALUES ('AC','US',i18n('Armed Forces Canada'));
INSERT INTO state(code, country, name) VALUES ('AE','US',i18n('Armed Forces Europe'));
INSERT INTO state(code, country, name) VALUES ('AM','US',i18n('Armed Forces Middle East'));
INSERT INTO state(code, country, name) VALUES ('AP','US',i18n('Armed Forces Pacific'));
INSERT INTO state(code, country, name) VALUES ('CA','US',i18n('California'));
INSERT INTO state(code, country, name) VALUES ('CO','US',i18n('Colorado'));
INSERT INTO state(code, country, name) VALUES ('CT','US',i18n('Connecticut'));
INSERT INTO state(code, country, name) VALUES ('DE','US',i18n('Delaware'));
INSERT INTO state(code, country, name) VALUES ('DC','US',i18n('District of Columbia'));
INSERT INTO state(code, country, name) VALUES ('FM','US',i18n('Federated States Of Micronesia'));
INSERT INTO state(code, country, name) VALUES ('FL','US',i18n('Florida'));
INSERT INTO state(code, country, name) VALUES ('GA','US',i18n('Georgia'));
INSERT INTO state(code, country, name) VALUES ('GU','US',i18n('Guam'));
INSERT INTO state(code, country, name) VALUES ('HI','US',i18n('Hawaii'));
INSERT INTO state(code, country, name) VALUES ('ID','US',i18n('Idaho'));
INSERT INTO state(code, country, name) VALUES ('IL','US',i18n('Illinois'));
INSERT INTO state(code, country, name) VALUES ('IN','US',i18n('Indiana'));
INSERT INTO state(code, country, name) VALUES ('IA','US',i18n('Iowa'));
INSERT INTO state(code, country, name) VALUES ('KS','US',i18n('Kansas'));
INSERT INTO state(code, country, name) VALUES ('KY','US',i18n('Kentucky'));
INSERT INTO state(code, country, name) VALUES ('LA','US',i18n('Louisiana'));
INSERT INTO state(code, country, name) VALUES ('ME','US',i18n('Maine'));
INSERT INTO state(code, country, name) VALUES ('MH','US',i18n('Marshall Islands'));
INSERT INTO state(code, country, name) VALUES ('MD','US',i18n('Maryland'));
INSERT INTO state(code, country, name) VALUES ('MA','US',i18n('Massachusetts'));
INSERT INTO state(code, country, name) VALUES ('MI','US',i18n('Michigan'));
INSERT INTO state(code, country, name) VALUES ('MN','US',i18n('Minnesota'));
INSERT INTO state(code, country, name) VALUES ('MS','US',i18n('Mississippi'));
INSERT INTO state(code, country, name) VALUES ('MO','US',i18n('Missouri'));
INSERT INTO state(code, country, name) VALUES ('MT','US',i18n('Montana'));
INSERT INTO state(code, country, name) VALUES ('NE','US',i18n('Nebraska'));
INSERT INTO state(code, country, name) VALUES ('NV','US',i18n('Nevada'));
INSERT INTO state(code, country, name) VALUES ('NH','US',i18n('New Hampshire'));
INSERT INTO state(code, country, name) VALUES ('NJ','US',i18n('New Jersey'));
INSERT INTO state(code, country, name) VALUES ('NM','US',i18n('New Mexico'));
INSERT INTO state(code, country, name) VALUES ('NY','US',i18n('New York'));
INSERT INTO state(code, country, name) VALUES ('NC','US',i18n('North Carolina'));
INSERT INTO state(code, country, name) VALUES ('ND','US',i18n('North Dakota'));
INSERT INTO state(code, country, name) VALUES ('MP','US',i18n('Northern Mariana Islands'));
INSERT INTO state(code, country, name) VALUES ('OH','US',i18n('Ohio'));
INSERT INTO state(code, country, name) VALUES ('OK','US',i18n('Oklahoma'));
INSERT INTO state(code, country, name) VALUES ('OR','US',i18n('Oregon'));
INSERT INTO state(code, country, name) VALUES ('PW','US',i18n('Palau'));
INSERT INTO state(code, country, name) VALUES ('PA','US',i18n('Pennsylvania'));
INSERT INTO state(code, country, name) VALUES ('PR','US',i18n('Puerto Rico'));
INSERT INTO state(code, country, name) VALUES ('RI','US',i18n('Rhode Island'));
INSERT INTO state(code, country, name) VALUES ('SC','US',i18n('South Carolina'));
INSERT INTO state(code, country, name) VALUES ('SD','US',i18n('South Dakota'));
INSERT INTO state(code, country, name) VALUES ('TN','US',i18n('Tennessee'));
INSERT INTO state(code, country, name) VALUES ('TX','US',i18n('Texas'));
INSERT INTO state(code, country, name) VALUES ('UT','US',i18n('Utah'));
INSERT INTO state(code, country, name) VALUES ('VT','US',i18n('Vermont'));
INSERT INTO state(code, country, name) VALUES ('VI','US',i18n('Virgin Islands'));
INSERT INTO state(code, country, name) VALUES ('VA','US',i18n('Virginia'));
INSERT INTO state(code, country, name) VALUES ('WA','US',i18n('Washington'));
INSERT INTO state(code, country, name) VALUES ('WV','US',i18n('West Virginia'));
INSERT INTO state(code, country, name) VALUES ('WI','US',i18n('Wisconsin'));
INSERT INTO state(code, country, name) VALUES ('WY','US',i18n('Wyoming'));

-- country UY
insert into country(code, name) values('UY', i18n('Uruguay'));

INSERT INTO state(code, country, name) VALUES ('AR','UY',i18n('Artigas'));
INSERT INTO state(code, country, name) VALUES ('CA','UY',i18n('Canelones'));
INSERT INTO state(code, country, name) VALUES ('CL','UY',i18n('Cerro Largo'));
INSERT INTO state(code, country, name) VALUES ('CO','UY',i18n('Colonia'));
INSERT INTO state(code, country, name) VALUES ('DU','UY',i18n('Durazno'));
INSERT INTO state(code, country, name) VALUES ('FL','UY',i18n('Flores'));
INSERT INTO state(code, country, name) VALUES ('FO','UY',i18n('Florida'));
INSERT INTO state(code, country, name) VALUES ('LA','UY',i18n('Lavalleja'));
INSERT INTO state(code, country, name) VALUES ('MA','UY',i18n('Maldonado'));
INSERT INTO state(code, country, name) VALUES ('MO','UY',i18n('Montevideo'));
INSERT INTO state(code, country, name) VALUES ('PA','UY',i18n('Paysandu'));
INSERT INTO state(code, country, name) VALUES ('RN','UY',i18n('Rio Negro'));
INSERT INTO state(code, country, name) VALUES ('RI','UY',i18n('Rivera'));
INSERT INTO state(code, country, name) VALUES ('RO','UY',i18n('Rocha'));
INSERT INTO state(code, country, name) VALUES ('SA','UY',i18n('Salto'));
INSERT INTO state(code, country, name) VALUES ('SJ','UY',i18n('San Jose'));
INSERT INTO state(code, country, name) VALUES ('SO','UY',i18n('Soriano'));
INSERT INTO state(code, country, name) VALUES ('TA','UY',i18n('Tacuarembo'));
INSERT INTO state(code, country, name) VALUES ('TT','UY',i18n('Treinta y Tres'));
-- country UZ
--INSERT INTO state(code, country, name) VALUES ('UZ-1','UZ',i18n('StateNameStub'));
-- country VA
INSERT INTO state(code, country, name) VALUES ('VA-1','VA',i18n('StateNameStub'));
-- country VC
INSERT INTO state(code, country, name) VALUES ('VC-1','VC',i18n('StateNameStub'));

-- country VE
insert into country(code, name) values('VE', i18n('Venezuelas'));

INSERT INTO state(code, country, name) VALUES ('AM','VE',i18n('Amazonas'));
INSERT INTO state(code, country, name) VALUES ('AN','VE',i18n('Anzoategui'));
INSERT INTO state(code, country, name) VALUES ('AP','VE',i18n('Apure'));
INSERT INTO state(code, country, name) VALUES ('AR','VE',i18n('Aragua'));
INSERT INTO state(code, country, name) VALUES ('BA','VE',i18n('Barinas'));
INSERT INTO state(code, country, name) VALUES ('BO','VE',i18n('Bolivar'));
INSERT INTO state(code, country, name) VALUES ('CA','VE',i18n('Carabobo'));
INSERT INTO state(code, country, name) VALUES ('CO','VE',i18n('Cojedes'));
INSERT INTO state(code, country, name) VALUES ('DA','VE',i18n('Delta Amacuro'));
INSERT INTO state(code, country, name) VALUES ('DF','VE',i18n('Dependencias Federales'));
INSERT INTO state(code, country, name) VALUES ('DI','VE',i18n('Distrito Federal'));
INSERT INTO state(code, country, name) VALUES ('FA','VE',i18n('Falcon'));
INSERT INTO state(code, country, name) VALUES ('GU','VE',i18n('Guarico'));
INSERT INTO state(code, country, name) VALUES ('LA','VE',i18n('Lara'));
INSERT INTO state(code, country, name) VALUES ('ME','VE',i18n('Merida'));
INSERT INTO state(code, country, name) VALUES ('MI','VE',i18n('Miranda'));
INSERT INTO state(code, country, name) VALUES ('MO','VE',i18n('Monagas'));
INSERT INTO state(code, country, name) VALUES ('NE','VE',i18n('Nueva Esparta'));
INSERT INTO state(code, country, name) VALUES ('PO','VE',i18n('Portuguesa'));
INSERT INTO state(code, country, name) VALUES ('SU','VE',i18n('Sucre'));
INSERT INTO state(code, country, name) VALUES ('TA','VE',i18n('Tachira'));
INSERT INTO state(code, country, name) VALUES ('TR','VE',i18n('Trujillo'));
INSERT INTO state(code, country, name) VALUES ('YA','VE',i18n('Yaracuy'));
INSERT INTO state(code, country, name) VALUES ('ZU','VE',i18n('Zulia'));
-- country VG
--INSERT INTO state(code, country, name) VALUES ('VG-1','VG',i18n('StateNameStub'));
-- country VI
--INSERT INTO state(code, country, name) VALUES ('VI-1','VI',i18n('StateNameStub'));
-- country VN
--INSERT INTO state(code, country, name) VALUES ('VN-1','VN',i18n('StateNameStub'));
-- country VU
--INSERT INTO state(code, country, name) VALUES ('VU-1','VU',i18n('StateNameStub'));
-- country WF
--INSERT INTO state(code, country, name) VALUES ('WF-1','WF',i18n('StateNameStub'));
-- country WS
--INSERT INTO state(code, country, name) VALUES ('WS-1','WS',i18n('StateNameStub'));

-- country YE
insert into country(code, name) values('YE', i18n('Yemen'));

INSERT INTO state(code, country, name) VALUES ('AD','YE',i18n('Adan'));
INSERT INTO state(code, country, name) VALUES ('AT','YE',i18n('Ataq'));
INSERT INTO state(code, country, name) VALUES ('AB','YE',i18n('Abyan'));
INSERT INTO state(code, country, name) VALUES ('AL','YE',i18n('Al Bayda'''));
INSERT INTO state(code, country, name) VALUES ('AH','YE',i18n('Al Hudaydah'));
INSERT INTO state(code, country, name) VALUES ('AJ','YE',i18n('Al Jawf'));
INSERT INTO state(code, country, name) VALUES ('AM','YE',i18n('Al Mahrah'));
INSERT INTO state(code, country, name) VALUES ('AW','YE',i18n('Al Mahwit'));
INSERT INTO state(code, country, name) VALUES ('DH','YE',i18n('Dhamar'));
INSERT INTO state(code, country, name) VALUES ('HA','YE',i18n('Hadhramawt'));
INSERT INTO state(code, country, name) VALUES ('HJ','YE',i18n('Hajjah'));
INSERT INTO state(code, country, name) VALUES ('IB','YE',i18n('Ibb'));
INSERT INTO state(code, country, name) VALUES ('LA','YE',i18n('Lahij'));
INSERT INTO state(code, country, name) VALUES ('MA','YE',i18n('Ma''rib'));
INSERT INTO state(code, country, name) VALUES ('SA','YE',i18n('Sa''dah'));
INSERT INTO state(code, country, name) VALUES ('SN','YE',i18n('San''a|'));
INSERT INTO state(code, country, name) VALUES ('TA','YE',i18n('Ta''izz'));
-- country YT
--INSERT INTO state(code, country, name) VALUES ('YT-1','YT',i18n('StateNameStub'));
-- country YU
--INSERT INTO state(code, country, name) VALUES ('KO','YU',i18n('Kosovo'));
--INSERT INTO state(code, country, name) VALUES ('MO','YU',i18n('Montenegro'));
--INSERT INTO state(code, country, name) VALUES ('SE','YU',i18n('Serbia'));
--INSERT INTO state(code, country, name) VALUES ('VO','YU',i18n('Vojvodina'));
-- country ZA
INSERT INTO state(code, country, name) VALUES ('EC','ZA',i18n('Eastern Cape'));
INSERT INTO state(code, country, name) VALUES ('FS','ZA',i18n('Free State'));
INSERT INTO state(code, country, name) VALUES ('GA','ZA',i18n('Gauteng'));
INSERT INTO state(code, country, name) VALUES ('KN','ZA',i18n('KwaZulu-Natal'));
INSERT INTO state(code, country, name) VALUES ('MP','ZA',i18n('Mpumalanga'));
INSERT INTO state(code, country, name) VALUES ('NW','ZA',i18n('North-West'));
INSERT INTO state(code, country, name) VALUES ('NC','ZA',i18n('Northern Cape'));
INSERT INTO state(code, country, name) VALUES ('NP','ZA',i18n('Northern Province'));
INSERT INTO state(code, country, name) VALUES ('WC','ZA',i18n('Western Cape'));

-- country ZM
insert into country(code, name) values('ZM', i18n('Zambia'));

INSERT INTO state(code, country, name) VALUES ('CE','ZM',i18n('Central'));
INSERT INTO state(code, country, name) VALUES ('CO','ZM',i18n('Copperbelt'));
INSERT INTO state(code, country, name) VALUES ('EA','ZM',i18n('Eastern'));
INSERT INTO state(code, country, name) VALUES ('LU','ZM',i18n('Luapula'));
INSERT INTO state(code, country, name) VALUES ('LS','ZM',i18n('Lusaka'));
INSERT INTO state(code, country, name) VALUES ('NW','ZM',i18n('North-Western'));
INSERT INTO state(code, country, name) VALUES ('NO','ZM',i18n('Northern'));
INSERT INTO state(code, country, name) VALUES ('SO','ZM',i18n('Southern'));
INSERT INTO state(code, country, name) VALUES ('WE','ZM',i18n('Western'));

-- country ZR
--INSERT INTO state(code, country, name) VALUES ('ZR-1','ZR',i18n('StateNameStub'));

-- country ZW
insert into country(code, name) values('ZW', i18n('Zimbabwe'));

INSERT INTO state(code, country, name) VALUES ('BU','ZW',i18n('Bulawayo'));
INSERT INTO state(code, country, name) VALUES ('HA','ZW',i18n('Harare'));
INSERT INTO state(code, country, name) VALUES ('MA','ZW',i18n('Manicaland'));
INSERT INTO state(code, country, name) VALUES ('MC','ZW',i18n('Mashonaland Central'));
INSERT INTO state(code, country, name) VALUES ('ME','ZW',i18n('Mashonaland East'));
INSERT INTO state(code, country, name) VALUES ('MW','ZW',i18n('Mashonaland West'));
INSERT INTO state(code, country, name) VALUES ('MV','ZW',i18n('Masvingo'));
INSERT INTO state(code, country, name) VALUES ('MN','ZW',i18n('Matabeleland North'));
INSERT INTO state(code, country, name) VALUES ('MS','ZW',i18n('Matabeleland South'));
INSERT INTO state(code, country, name) VALUES ('MI','ZW',i18n('Midlands'));

-- =============================================
-- do simple schema revision tracking
select log_script_insertion('$RCSfile: gmCountryZones.sql,v $', '$Revision: 1.2 $');

-- =============================================
-- $Log: gmCountryZones.sql,v $
-- Revision 1.2  2005-10-12 22:29:11  ncq
-- - comment out states/add in countries which (would) error out
--
-- Revision 1.1  2005/09/25 17:45:16  ncq
-- - we now got states for pretty much every country
--
--
