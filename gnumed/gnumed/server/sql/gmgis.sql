-- project: GNUMed
-- database: GIS
-- purpose:  geographic information (mostly of type 'address')
-- author: hherb
-- copyright: Dr. Horst Herb, horst@hherb.com
-- license: GPL (details at http://gnu.org)
-- version: 0.4
-- changelog:
-- 17.11.2001:  (hherb) first useable version
-- 04.03.2002:  (hherb) address_type bug in view basic_addess fixed
-- 04.03.2002:  (hherb) table state constraint added

-- =============================================

-- any table that needs auditing MUST inherit audit_gis
-- A python script (gmhistorian.py) generates automatically all triggers
-- and tables neccessary to allow versioning and audit trail keeping of
-- these tables

create table audit_gis (
	audit_id serial primary key
);

COMMENT ON TABLE audit_gis IS
'not for direct use - must be inherited by all auditable tables';

-- country codes as per ISO 3166-1
-- no versioning / check sum neccessary, as this table
-- only uses original ISO data (= reference verifiable any time)

create table country (
	code char(2) unique primary key,
	name varchar(60),
	deprecated date default NULL
);

COMMENT ON TABLE country IS
'a countries name and international code';

COMMENT ON COLUMN country.code IS
'international two character country code as per ISO 3166-1';

COMMENT ON COLUMN country.deprecated IS
'date when this country ceased officially to exist (if applicable)';

-- =============================================

-- state codes. Any need for more than 3 characters?

create table state (
	id serial primary key,
	code char(10),
	country char(2) references country(code),
	name varchar(60),
	deprecated date,
	constraint nodupes UNIQUE (code, country)
) inherits (audit_gis);

COMMENT ON TABLE state IS
'state codes (country specific)';

COMMENT ON COLUMN state.code IS
'3 character long state code';

COMMENT ON COLUMN state.country IS
'2 character ISO 3166-1 country code';

COMMENT ON COLUMN country.deprecated IS
'date when this state ceased officially to exist (if applicable)';

-- =============================================

create table urb (
	id serial primary key,
	statecode int references state(id),
	postcode char(8),
	name varchar(60)
) inherits (audit_gis);

COMMENT ON TABLE urb IS
'cities, towns, dwellings ...';

COMMENT ON COLUMN urb.statecode IS
'reference to information about country and state';

COMMENT ON COLUMN urb.postcode IS
'the postcode';

COMMENT ON COLUMN urb.name IS
'the name of the city/town/dwelling';

-- =============================================

create table street (
	id serial primary key,
	id_urb integer references urb,
	name varchar(60)
) inherits (audit_gis);

COMMENT ON TABLE street IS
'street names, specific for distinct "urbs"';

COMMENT ON COLUMN street.id_urb IS
'reference to information postcode, city, country and state';

COMMENT ON COLUMN street.name IS
'name of this city/town/dwelling';

-- =============================================

create table address_type (
	id serial primary key,
	name char(10) NOT NULL
) inherits (audit_gis);


INSERT INTO address_type(id, name) values(1,'home'); -- do not alter the id of home !
INSERT INTO address_type(id, name) values(2,'work');
INSERT INTO address_type(id, name) values(3,'parents');
INSERT INTO address_type(id, name) values(4,'holidays');
INSERT INTO address_type(id, name) values(5,'temporary');


-- =============================================

create table address (
	id serial primary key,
	addrtype int references address_type(id) default 1,
	street int references street(id),
	number char(10),
	addendum text
) inherits (audit_gis);


create table address_external_ref (
	id int references address primary key,
	refcounter int default 0
);


create view basic_address
-- if you suffer from performance problems when selecting from this view,
-- implement it as a real table and create rules / triggers for insert,
-- update and delete that will update the underlying tables accordingly
as
select
	s.country as country,
	s.code as state,
	u.postcode as postcode,
	u.name as city,
	a.number as number,
	str.name as street,
	a.addendum as street2,
	t.name as address_type

from
	address a,
	state s,
	urb u,
	street str,
	address_type t
where
	a.street = s.id
	and
	a.addrtype = 1	-- home address
	and
	str.id_urb = u.id
	and
	u.statecode = s.id;





-- =============================================

-- the following table still needs a lot of work.
-- especially the GPS and map related information needs to be
-- denormalized

create table address_info (
	address_id int references address(id),
	gps char(30),
	gps_grid char(30),
	mapref char(30),
	map char(30),
	howto_get_there text,
	comments text
) inherits (audit_gis);
-- =============================================



-- =============================================
-- Here come the ISO country codes ...

COPY country FROM stdin;
AF	AFGHANISTAN	\N
AL	ALBANIA	\N
DZ	ALGERIA	\N
AS	AMERICAN SAMOA	\N
AD	ANDORRA	\N
AO	ANGOLA	\N
AI	ANGUILLA	\N
AQ	ANTARCTICA	\N
AG	ANTIGUA AND BARBUDA	\N
AR	ARGENTINA	\N
AM	ARMENIA	\N
AW	ARUBA	\N
AU	AUSTRALIA	\N
AT	AUSTRIA	\N
AZ	AZERBAIJAN	\N
BS	BAHAMAS	\N
BH	BAHRAIN	\N
BD	BANGLADESH	\N
BB	BARBADOS	\N
BY	BELARUS	\N
BE	BELGIUM	\N
BZ	BELIZE	\N
BJ	BENIN	\N
BM	BERMUDA	\N
BT	BHUTAN	\N
BO	BOLIVIA	\N
BA	BOSNIA AND HERZEGOVINA	\N
BW	BOTSWANA	\N
BV	BOUVET ISLAND	\N
BR	BRAZIL	\N
IO	BRITISH INDIAN OCEAN TERRITORY	\N
BN	BRUNEI DARUSSALAM	\N
BG	BULGARIA	\N
BF	BURKINA FASO	\N
BI	BURUNDI	\N
KH	CAMBODIA	\N
CM	CAMEROON	\N
CA	CANADA	\N
CV	CAPE VERDE	\N
KY	CAYMAN ISLANDS	\N
CF	CENTRAL AFRICAN REPUBLIC	\N
TD	CHAD	\N
CL	CHILE	\N
CN	CHINA	\N
CX	CHRISTMAS ISLAND	\N
CC	COCOS (KEELING) ISLANDS	\N
CO	COLOMBIA	\N
KM	COMOROS	\N
CG	CONGO	\N
CD	CONGO, THE DEMOCRATIC REPUBLIC	\N
CK	COOK ISLANDS	\N
CR	COSTA RICA	\N
CI	COTE D'IVOIRE	\N
HR	CROATIA	\N
CU	CUBA	\N
CY	CYPRUS	\N
CZ	CZECH REPUBLIC	\N
DK	DENMARK	\N
DJ	DJIBOUTI	\N
DM	DOMINICA	\N
DO	DOMINICAN REPUBLIC	\N
TP	EAST TIMOR	\N
EC	ECUADOR	\N
EG	EGYPT	\N
SV	EL SALVADOR	\N
GQ	EQUATORIAL GUINEA	\N
ER	ERITREA	\N
EE	ESTONIA	\N
ET	ETHIOPIA	\N
FK	FALKLAND ISLANDS (MALVINAS)	\N
FO	FAROE ISLANDS	\N
FJ	FIJI	\N
FI	FINLAND	\N
FR	FRANCE	\N
GF	FRENCH GUIANA	\N
PF	FRENCH POLYNESIA	\N
TF	FRENCH SOUTHERN TERRITORIES	\N
GA	GABON	\N
GM	GAMBIA	\N
GE	GEORGIA	\N
DE	GERMANY	\N
GH	GHANA	\N
GI	GIBRALTAR	\N
GR	GREECE	\N
GL	GREENLAND	\N
GD	GRENADA	\N
GP	GUADELOUPE	\N
GU	GUAM	\N
GT	GUATEMALA	\N
GN	GUINEA	\N
GW	GUINEA-BISSAU	\N
GY	GUYANA	\N
HT	HAITI	\N
HM	HEARD ISLAND AND MCDONALD ISLA	\N
VA	HOLY SEE (VATICAN CITY STATE)	\N
HN	HONDURAS	\N
HK	HONG KONG	\N
HU	HUNGARY	\N
IS	ICELAND	\N
IN	INDIA	\N
ID	INDONESIA	\N
IR	IRAN, ISLAMIC REPUBLIC OF	\N
IQ	IRAQ	\N
IE	IRELAND	\N
IL	ISRAEL	\N
IT	ITALY	\N
JM	JAMAICA	\N
JP	JAPAN	\N
JO	JORDAN	\N
KZ	KAZAKSTAN	\N
KE	KENYA	\N
KI	KIRIBATI	\N
KP	KOREA, DEMOCRATIC PEOPLE'S REP	\N
KR	KOREA, REPUBLIC OF	\N
KW	KUWAIT	\N
KG	KYRGYZSTAN	\N
LA	LAO PEOPLE'S DEMOCRATIC REPUBL	\N
LV	LATVIA	\N
LB	LEBANON	\N
LS	LESOTHO	\N
LR	LIBERIA	\N
LY	LIBYAN ARAB JAMAHIRIYA	\N
LI	LIECHTENSTEIN	\N
LT	LITHUANIA	\N
LU	LUXEMBOURG	\N
MO	MACAU	\N
MK	MACEDONIA, THE FORMER YUGOSLAV	\N
MG	MADAGASCAR	\N
MW	MALAWI	\N
MY	MALAYSIA	\N
MV	MALDIVES	\N
ML	MALI	\N
MT	MALTA	\N
MH	MARSHALL ISLANDS	\N
MQ	MARTINIQUE	\N
MR	MAURITANIA	\N
MU	MAURITIUS	\N
YT	MAYOTTE	\N
MX	MEXICO	\N
FM	MICRONESIA, FEDERATED STATES O	\N
MD	MOLDOVA, REPUBLIC OF	\N
MC	MONACO	\N
MN	MONGOLIA	\N
MS	MONTSERRAT	\N
MA	MOROCCO	\N
MZ	MOZAMBIQUE	\N
MM	MYANMAR	\N
NA	NAMIBIA	\N
NR	NAURU	\N
NP	NEPAL	\N
NL	NETHERLANDS	\N
AN	NETHERLANDS ANTILLES	\N
NC	NEW CALEDONIA	\N
NZ	NEW ZEALAND	\N
NI	NICARAGUA	\N
NE	NIGER	\N
NG	NIGERIA	\N
NU	NIUE	\N
NF	NORFOLK ISLAND	\N
MP	NORTHERN MARIANA ISLANDS	\N
NO	NORWAY	\N
OM	OMAN	\N
PK	PAKISTAN	\N
PW	PALAU	\N
PS	PALESTINIAN TERRITORY, OCCUPIE	\N
PA	PANAMA	\N
PG	PAPUA NEW GUINEA	\N
PY	PARAGUAY	\N
PE	PERU	\N
PH	PHILIPPINES	\N
PN	PITCAIRN	\N
PL	POLAND	\N
PT	PORTUGAL	\N
PR	PUERTO RICO	\N
QA	QATAR	\N
RE	REUNION	\N
RO	ROMANIA	\N
RU	RUSSIAN FEDERATION	\N
RW	RWANDA	\N
SH	SAINT HELENA	\N
KN	SAINT KITTS AND NEVIS	\N
LC	SAINT LUCIA	\N
PM	SAINT PIERRE AND MIQUELON	\N
VC	SAINT VINCENT AND THE GRENADIN	\N
WS	SAMOA	\N
SM	SAN MARINO	\N
ST	SAO TOME AND PRINCIPE	\N
SA	SAUDI ARABIA	\N
SN	SENEGAL	\N
SC	SEYCHELLES	\N
SL	SIERRA LEONE	\N
SG	SINGAPORE	\N
SK	SLOVAKIA	\N
SI	SLOVENIA	\N
SB	SOLOMON ISLANDS	\N
SO	SOMALIA	\N
ZA	SOUTH AFRICA	\N
GS	SOUTH GEORGIA AND THE SOUTH SA	\N
ES	SPAIN	\N
LK	SRI LANKA	\N
SD	SUDAN	\N
SR	SURINAME	\N
SJ	SVALBARD AND JAN MAYEN	\N
SZ	SWAZILAND	\N
SE	SWEDEN	\N
CH	SWITZERLAND	\N
SY	SYRIAN ARAB REPUBLIC	\N
TW	TAIWAN, PROVINCE OF CHINA	\N
TJ	TAJIKISTAN	\N
TZ	TANZANIA, UNITED REPUBLIC OF	\N
TH	THAILAND	\N
TG	TOGO	\N
TK	TOKELAU	\N
TO	TONGA	\N
TT	TRINIDAD AND TOBAGO	\N
TN	TUNISIA	\N
TR	TURKEY	\N
TM	TURKMENISTAN	\N
TC	TURKS AND CAICOS ISLANDS	\N
TV	TUVALU	\N
UG	UGANDA	\N
UA	UKRAINE	\N
AE	UNITED ARAB EMIRATES	\N
GB	UNITED KINGDOM	\N
US	UNITED STATES	\N
UM	UNITED STATES MINOR OUTLYING I	\N
UY	URUGUAY	\N
UZ	UZBEKISTAN	\N
VU	VANUATU	\N
VE	VENEZUELA	\N
VN	VIET NAM	\N
VG	VIRGIN ISLANDS, BRITISH	\N
VI	VIRGIN ISLANDS, U.S.	\N
WF	WALLIS AND FUTUNA	\N
EH	WESTERN SAHARA	\N
YE	YEMEN	\N
YU	YUGOSLAVIA	\N
ZM	ZAMBIA	\N
ZW	ZIMBABWE	\N

