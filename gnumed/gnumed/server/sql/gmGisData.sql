-- project: GNUMed
-- database: GIS
-- purpose:  geographic information (mostly of type 'address')

-- license: GPL (details at http://gnu.org)
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/Attic/gmGisData.sql,v $
-- $Id $
-- ===================================================================
-- do fixed string i18n()ing
\i gmI18N.sql

-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================================
-- do NOT alter the id of home !
INSERT INTO address_type(id, name) values(1, i18n('home'));
INSERT INTO address_type(id, name) values(2, i18n('work'));
INSERT INTO address_type(id, name) values(3, i18n('parents'));
INSERT INTO address_type(id, name) values(4, i18n('holidays'));
INSERT INTO address_type(id, name) values(5, i18n('temporary'));

-- ===================================================================
-- here come the ISO country codes ...

BEGIN WORK;
insert into country(code, name) values('AF', i18n('AFGHANISTAN'));
insert into country(code, name) values('AL', i18n('ALBANIA'));
insert into country(code, name) values('DZ', i18n('ALGERIA'));
insert into country(code, name) values('AS', i18n('AMERICAN SAMOA'));
insert into country(code, name) values('AD', i18n('ANDORRA'));
insert into country(code, name) values('AO', i18n('ANGOLA'));
insert into country(code, name) values('AI', i18n('ANGUILLA'));
insert into country(code, name) values('AQ', i18n('ANTARCTICA'));
insert into country(code, name) values('AG', i18n('ANTIGUA AND BARBUDA'));
insert into country(code, name) values('AR', i18n('ARGENTINA'));
insert into country(code, name) values('AM', i18n('ARMENIA'));
insert into country(code, name) values('AW', i18n('ARUBA'));
insert into country(code, name) values('AU', i18n('AUSTRALIA'));
insert into country(code, name) values('AT', i18n('AUSTRIA'));
insert into country(code, name) values('AZ', i18n('AZERBAIJAN'));
insert into country(code, name) values('BS', i18n('BAHAMAS'));
insert into country(code, name) values('BH', i18n('BAHRAIN'));
insert into country(code, name) values('BD', i18n('BANGLADESH'));
insert into country(code, name) values('BB', i18n('BARBADOS'));
insert into country(code, name) values('BY', i18n('BELARUS'));
insert into country(code, name) values('BE', i18n('BELGIUM'));
insert into country(code, name) values('BZ', i18n('BELIZE'));
insert into country(code, name) values('BJ', i18n('BENIN'));
insert into country(code, name) values('BM', i18n('BERMUDA'));
insert into country(code, name) values('BT', i18n('BHUTAN'));
insert into country(code, name) values('BO', i18n('BOLIVIA'));
insert into country(code, name) values('BA', i18n('BOSNIA AND HERZEGOVINA'));
insert into country(code, name) values('BW', i18n('BOTSWANA'));
insert into country(code, name) values('BV', i18n('BOUVET ISLAND'));
insert into country(code, name) values('BR', i18n('BRAZIL'));
insert into country(code, name) values('IO', i18n('BRITISH INDIAN OCEAN TERRITORY'));
insert into country(code, name) values('BN', i18n('BRUNEI DARUSSALAM'));
insert into country(code, name) values('BG', i18n('BULGARIA'));
insert into country(code, name) values('BF', i18n('BURKINA FASO'));
insert into country(code, name) values('BI', i18n('BURUNDI'));
insert into country(code, name) values('KH', i18n('CAMBODIA'));
insert into country(code, name) values('CM', i18n('CAMEROON'));
insert into country(code, name) values('CA', i18n('CANADA'));
insert into country(code, name) values('CV', i18n('CAPE VERDE'));
insert into country(code, name) values('KY', i18n('CAYMAN ISLANDS'));
insert into country(code, name) values('CF', i18n('CENTRAL AFRICAN REPUBLIC'));
insert into country(code, name) values('TD', i18n('CHAD'));
insert into country(code, name) values('CL', i18n('CHILE'));
insert into country(code, name) values('CN', i18n('CHINA'));
insert into country(code, name) values('CX', i18n('CHRISTMAS ISLAND'));
insert into country(code, name) values('CC', i18n('COCOS (KEELING) ISLANDS'));
insert into country(code, name) values('CO', i18n('COLOMBIA'));
insert into country(code, name) values('KM', i18n('COMOROS'));
insert into country(code, name) values('CG', i18n('CONGO'));
insert into country(code, name) values('CD', i18n('CONGO, THE DEMOCRATIC REPUBLIC'));
insert into country(code, name) values('CK', i18n('COOK ISLANDS'));
insert into country(code, name) values('CR', i18n('COSTA RICA'));
insert into country(code, name) values('CI', i18n('COTE D''IVOIRE'));
insert into country(code, name) values('HR', i18n('CROATIA'));
insert into country(code, name) values('CU', i18n('CUBA'));
insert into country(code, name) values('CY', i18n('CYPRUS'));
insert into country(code, name) values('CZ', i18n('CZECH REPUBLIC'));
insert into country(code, name) values('DK', i18n('DENMARK'));
insert into country(code, name) values('DJ', i18n('DJIBOUTI'));
insert into country(code, name) values('DM', i18n('DOMINICA'));
insert into country(code, name) values('DO', i18n('DOMINICAN REPUBLIC'));
insert into country(code, name) values('TP', i18n('EAST TIMOR'));
insert into country(code, name) values('EC', i18n('ECUADOR'));
insert into country(code, name) values('EG', i18n('EGYPT'));
insert into country(code, name) values('SV', i18n('EL SALVADOR'));
insert into country(code, name) values('GQ', i18n('EQUATORIAL GUINEA'));
insert into country(code, name) values('ER', i18n('ERITREA'));
insert into country(code, name) values('EE', i18n('ESTONIA'));
insert into country(code, name) values('ET', i18n('ETHIOPIA'));
insert into country(code, name) values('FK', i18n('FALKLAND ISLANDS (MALVINAS)'));
insert into country(code, name) values('FO', i18n('FAROE ISLANDS'));
insert into country(code, name) values('FJ', i18n('FIJI'));
insert into country(code, name) values('FI', i18n('FINLAND'));
insert into country(code, name) values('FR', i18n('FRANCE'));
insert into country(code, name) values('GF', i18n('FRENCH GUIANA'));
insert into country(code, name) values('PF', i18n('FRENCH POLYNESIA'));
insert into country(code, name) values('TF', i18n('FRENCH SOUTHERN TERRITORIES'));
insert into country(code, name) values('GA', i18n('GABON'));
insert into country(code, name) values('GM', i18n('GAMBIA'));
insert into country(code, name) values('GE', i18n('GEORGIA'));
insert into country(code, name) values('DE', i18n('GERMANY'));
insert into country(code, name) values('GH', i18n('GHANA'));
insert into country(code, name) values('GI', i18n('GIBRALTAR'));
insert into country(code, name) values('GR', i18n('GREECE'));
insert into country(code, name) values('GL', i18n('GREENLAND'));
insert into country(code, name) values('GD', i18n('GRENADA'));
insert into country(code, name) values('GP', i18n('GUADELOUPE'));
insert into country(code, name) values('GU', i18n('GUAM'));
insert into country(code, name) values('GT', i18n('GUATEMALA'));
insert into country(code, name) values('GN', i18n('GUINEA'));
insert into country(code, name) values('GW', i18n('GUINEA-BISSAU'));
insert into country(code, name) values('GY', i18n('GUYANA'));
insert into country(code, name) values('HT', i18n('HAITI'));
insert into country(code, name) values('HM', i18n('HEARD ISLAND AND MCDONALD ISLA'));
insert into country(code, name) values('VA', i18n('HOLY SEE (VATICAN CITY STATE)'));
insert into country(code, name) values('HN', i18n('HONDURAS'));
insert into country(code, name) values('HK', i18n('HONG KONG'));
insert into country(code, name) values('HU', i18n('HUNGARY'));
insert into country(code, name) values('IS', i18n('ICELAND'));
insert into country(code, name) values('IN', i18n('INDIA'));
insert into country(code, name) values('ID', i18n('INDONESIA'));
insert into country(code, name) values('IR', i18n('IRAN, ISLAMIC REPUBLIC OF'));
insert into country(code, name) values('IQ', i18n('IRAQ'));
insert into country(code, name) values('IE', i18n('IRELAND'));
insert into country(code, name) values('IL', i18n('ISRAEL'));
insert into country(code, name) values('IT', i18n('ITALY'));
insert into country(code, name) values('JM', i18n('JAMAICA'));
insert into country(code, name) values('JP', i18n('JAPAN'));
insert into country(code, name) values('JO', i18n('JORDAN'));
insert into country(code, name) values('KZ', i18n('KAZAKSTAN'));
insert into country(code, name) values('KE', i18n('KENYA'));
insert into country(code, name) values('KI', i18n('KIRIBATI'));
insert into country(code, name) values('KP', i18n('KOREA, DEMOCRATIC PEOPLE''S REP'));
insert into country(code, name) values('KR', i18n('KOREA, REPUBLIC OF'));
insert into country(code, name) values('KW', i18n('KUWAIT'));
insert into country(code, name) values('KG', i18n('KYRGYZSTAN'));
insert into country(code, name) values('LA', i18n('LAO PEOPLE''S DEMOCRATIC REPUBL'));
insert into country(code, name) values('LV', i18n('LATVIA'));
insert into country(code, name) values('LB', i18n('LEBANON'));
insert into country(code, name) values('LS', i18n('LESOTHO'));
insert into country(code, name) values('LR', i18n('LIBERIA'));
insert into country(code, name) values('LY', i18n('LIBYAN ARAB JAMAHIRIYA'));
insert into country(code, name) values('LI', i18n('LIECHTENSTEIN'));
insert into country(code, name) values('LT', i18n('LITHUANIA'));
insert into country(code, name) values('LU', i18n('LUXEMBOURG'));
insert into country(code, name) values('MO', i18n('MACAU'));
insert into country(code, name) values('MK', i18n('MACEDONIA, THE FORMER YUGOSLAV'));
insert into country(code, name) values('MG', i18n('MADAGASCAR'));
insert into country(code, name) values('MW', i18n('MALAWI'));
insert into country(code, name) values('MY', i18n('MALAYSIA'));
insert into country(code, name) values('MV', i18n('MALDIVES'));
insert into country(code, name) values('ML', i18n('MALI'));
insert into country(code, name) values('MT', i18n('MALTA'));
insert into country(code, name) values('MH', i18n('MARSHALL ISLANDS'));
insert into country(code, name) values('MQ', i18n('MARTINIQUE'));
insert into country(code, name) values('MR', i18n('MAURITANIA'));
insert into country(code, name) values('MU', i18n('MAURITIUS'));
insert into country(code, name) values('YT', i18n('MAYOTTE'));
insert into country(code, name) values('MX', i18n('MEXICO'));
insert into country(code, name) values('FM', i18n('MICRONESIA, FEDERATED STATES O'));
insert into country(code, name) values('MD', i18n('MOLDOVA, REPUBLIC OF'));
insert into country(code, name) values('MC', i18n('MONACO'));
insert into country(code, name) values('MN', i18n('MONGOLIA'));
insert into country(code, name) values('MS', i18n('MONTSERRAT'));
insert into country(code, name) values('MA', i18n('MOROCCO'));
insert into country(code, name) values('MZ', i18n('MOZAMBIQUE'));
insert into country(code, name) values('MM', i18n('MYANMAR'));
insert into country(code, name) values('NA', i18n('NAMIBIA'));
insert into country(code, name) values('NR', i18n('NAURU'));
insert into country(code, name) values('NP', i18n('NEPAL'));
insert into country(code, name) values('NL', i18n('NETHERLANDS'));
insert into country(code, name) values('AN', i18n('NETHERLANDS ANTILLES'));
insert into country(code, name) values('NC', i18n('NEW CALEDONIA'));
insert into country(code, name) values('NZ', i18n('NEW ZEALAND'));
insert into country(code, name) values('NI', i18n('NICARAGUA'));
insert into country(code, name) values('NE', i18n('NIGER'));
insert into country(code, name) values('NG', i18n('NIGERIA'));
insert into country(code, name) values('NU', i18n('NIUE'));
insert into country(code, name) values('NF', i18n('NORFOLK ISLAND'));
insert into country(code, name) values('MP', i18n('NORTHERN MARIANA ISLANDS'));
insert into country(code, name) values('NO', i18n('NORWAY'));
insert into country(code, name) values('OM', i18n('OMAN'));
insert into country(code, name) values('PK', i18n('PAKISTAN'));
insert into country(code, name) values('PW', i18n('PALAU'));
insert into country(code, name) values('PS', i18n('PALESTINIAN TERRITORY, OCCUPIE'));
insert into country(code, name) values('PA', i18n('PANAMA'));
insert into country(code, name) values('PG', i18n('PAPUA NEW GUINEA'));
insert into country(code, name) values('PY', i18n('PARAGUAY'));
insert into country(code, name) values('PE', i18n('PERU'));
insert into country(code, name) values('PH', i18n('PHILIPPINES'));
insert into country(code, name) values('PN', i18n('PITCAIRN'));
insert into country(code, name) values('PL', i18n('POLAND'));
insert into country(code, name) values('PT', i18n('PORTUGAL'));
insert into country(code, name) values('PR', i18n('PUERTO RICO'));
insert into country(code, name) values('QA', i18n('QATAR'));
insert into country(code, name) values('RE', i18n('REUNION'));
insert into country(code, name) values('RO', i18n('ROMANIA'));
insert into country(code, name) values('RU', i18n('RUSSIAN FEDERATION'));
insert into country(code, name) values('RW', i18n('RWANDA'));
insert into country(code, name) values('SH', i18n('SAINT HELENA'));
insert into country(code, name) values('KN', i18n('SAINT KITTS AND NEVIS'));
insert into country(code, name) values('LC', i18n('SAINT LUCIA'));
insert into country(code, name) values('PM', i18n('SAINT PIERRE AND MIQUELON'));
insert into country(code, name) values('VC', i18n('SAINT VINCENT AND THE GRENADIN'));
insert into country(code, name) values('WS', i18n('SAMOA'));
insert into country(code, name) values('SM', i18n('SAN MARINO'));
insert into country(code, name) values('ST', i18n('SAO TOME AND PRINCIPE'));
insert into country(code, name) values('SA', i18n('SAUDI ARABIA'));
insert into country(code, name) values('SN', i18n('SENEGAL'));
insert into country(code, name) values('SC', i18n('SEYCHELLES'));
insert into country(code, name) values('SL', i18n('SIERRA LEONE'));
insert into country(code, name) values('SG', i18n('SINGAPORE'));
insert into country(code, name) values('SK', i18n('SLOVAKIA'));
insert into country(code, name) values('SI', i18n('SLOVENIA'));
insert into country(code, name) values('SB', i18n('SOLOMON ISLANDS'));
insert into country(code, name) values('SO', i18n('SOMALIA'));
insert into country(code, name) values('ZA', i18n('SOUTH AFRICA'));
insert into country(code, name) values('GS', i18n('SOUTH GEORGIA AND THE SOUTH SA'));
insert into country(code, name) values('ES', i18n('SPAIN'));
insert into country(code, name) values('LK', i18n('SRI LANKA'));
insert into country(code, name) values('SD', i18n('SUDAN'));
insert into country(code, name) values('SR', i18n('SURINAME'));
insert into country(code, name) values('SJ', i18n('SVALBARD AND JAN MAYEN'));
insert into country(code, name) values('SZ', i18n('SWAZILAND'));
insert into country(code, name) values('SE', i18n('SWEDEN'));
insert into country(code, name) values('CH', i18n('SWITZERLAND'));
insert into country(code, name) values('SY', i18n('SYRIAN ARAB REPUBLIC'));
insert into country(code, name) values('TW', i18n('TAIWAN, PROVINCE OF CHINA'));
insert into country(code, name) values('TJ', i18n('TAJIKISTAN'));
insert into country(code, name) values('TZ', i18n('TANZANIA, UNITED REPUBLIC OF'));
insert into country(code, name) values('TH', i18n('THAILAND'));
insert into country(code, name) values('TG', i18n('TOGO'));
insert into country(code, name) values('TK', i18n('TOKELAU'));
insert into country(code, name) values('TO', i18n('TONGA'));
insert into country(code, name) values('TT', i18n('TRINIDAD AND TOBAGO'));
insert into country(code, name) values('TN', i18n('TUNISIA'));
insert into country(code, name) values('TR', i18n('TURKEY'));
insert into country(code, name) values('TM', i18n('TURKMENISTAN'));
insert into country(code, name) values('TC', i18n('TURKS AND CAICOS ISLANDS'));
insert into country(code, name) values('TV', i18n('TUVALU'));
insert into country(code, name) values('UG', i18n('UGANDA'));
insert into country(code, name) values('UA', i18n('UKRAINE'));
insert into country(code, name) values('AE', i18n('UNITED ARAB EMIRATES'));
insert into country(code, name) values('GB', i18n('UNITED KINGDOM'));
insert into country(code, name) values('US', i18n('UNITED STATES'));
COMMIT WORK;

-- ===================================================================
-- do simple schema revision tracking
\i gmSchemaRevision.sql
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmGisData.sql,v $', '$Revision: 1.3 $');

-- ===================================================================
-- $Log: gmGisData.sql,v $
-- Revision 1.3  2003-03-24 10:45:12  ncq
-- - country codes moved to GisData
-- - added constraint on table urb
--
-- Revision 1.2  2003/03/24 10:41:16  ncq
-- - added ISO country codes
--
-- Revision 1.1  2003/02/14 10:46:17  ncq
-- - breaking out enumeration data
--
