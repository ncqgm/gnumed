-- GnuMed
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/de/gmDemographics.de.sql,v $
-- $Revision: 1.4 $

-- part of GnuMed
-- license: GPL

-- demographics tables specific for Germany

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- set client_encoding to 'LATIN1';
-- ===================================================================
-- tables related to the German Krankenversichtenkarte KVK
create table de_kvk (
	id serial primary key,
	id_patient integer not null references identity(pk),

	-- eigentliche KVK-Felder
	-- Datenbereich (020h-0FFh)				--  Feldtag	Länge	Feldname				Optional
	KK_Name varchar(28) not null,			--  0x80	2-28	Krankenkassenname		nein
	KK_Nummer character(7) not null,		--  0x81	7		Krankenkassennummer		nein
	KVK_Nummer character(5),				--  0x8F	5		Versichertenkarten-Nr.	ja
	Mitgliedsnummer varchar(12) not null,	--  0x82	6-12	Versichertennummer		nein
	Mitgliedsstatus varchar(4) not null,	--  0x83	1/4		Versichertenstatus		nein
	Zusatzstatus varchar(3),				--  0x90	1-3		Statusergänzung			ja
	Titel varchar(15),						--  0x84	3-15	Titel					ja
	Vorname varchar(28),					--  0x85	2-28	Vorname					ja
	Namenszuatz varchar(15),				--  0x86	1-15	Namenszusatz			ja
	Familienname varchar(28) not null,		--  0x87	2-28	Familienname			nein
	Geburtsdatum character(8) not null,		--  0x88	8		Geburtsdatum			nein
	Straße varchar(28),						--  0x89	1-28	Straßenname				ja
	Landescode  varchar(3),					--  0x8A	1-3		Wohnsitzländercode		ja
	PLZ varchar(7) not null,				--  0x8B	4-7		Postleitzahl			nein
	Ort varchar(23) not null,				--  0x8C	2-23	Ortsname				nein
	Gueltigkeit character(4),				--  0x8D	4		Gültigkeitsdatum		ja
	CRC character(1) not null,				--  0x8E	1		Prüfsumme				nein

	is_valid_address boolean default true,

	valid_since timestamp with time zone not null,
	presented timestamp with time zone [] not null,
	invalidated timestamp with time zone default null
);

-- Der Datenbereich ist wie folgt gegliedert:
--  1. Feldtag (1 Byte)
--  2. Feldlaenge (1 Byte)
--  3. ASCII-codierter Text (der angegebenen Feldlaenge, 1 Zeichen=1 Byte )

comment on table de_kvk is
	'Speichert die Daten einer bestimmten KVK. Wir trennen die KVK-Daten von
	 den Daten ueber Person, Wohnort, Kassenzugehoerigkeit, Mitgliedsstatus und
	 Abrechnungsfaellen. Diese Daten werden jedoch a) als Vorgaben fuer die
	 eigentlichen Personendaten und b) als gueltig fuer abrechnungstechnische
	 Belange angesehen.';

comment on column de_kvk.invalidated is
	'Kann durchaus vor Ende von "Gueltigkeit" liegen. Zeitpunkt des
	 Austritts aus der Krankenkasse. Beim Setzen dieses Feldes muss
	 auch die Zuzahlungsbefreiung auf NULL gesetzt werden.';

-- ---------------------------------------------
--create table de_kvk_presented (
--	id serial primary key,
--	id_kvk integer not null references de_kvk(id),
--	presented timestamp with time zone not null,
--	unique (id_kvk, presented)
--);

-- ---------------------------------------------
create table de_zuzahlungsbefreiung (
	id serial primary key,
	id_patient integer references identity(pk),

	Medikamente date default null,
	Heilmittel date default null,
	Hilfsmittel date default null,

	presented timestamp with time zone not null default CURRENT_TIMESTAMP
);

-- =============================================
-- Praxisgebuehr
-- ---------------------------------------------
create table beh_fall_typ (
	pk serial primary key,
	code text unique not null,
	kurzform text unique not null,
	name text unique not null
) inherits (audit_fields);

select add_table_for_audit('beh_fall_typ');

comment on table beh_fall_typ is
	'Art des Behandlungsfalls (MuVo/Impfung/...)';

-- ---------------------------------------------
create table behandlungsfall (
	pk serial primary key,
	fk_patient integer
		not null
		references identity(pk)
		on delete restrict
		on update cascade,
	fk_falltyp integer
		not null
		references beh_fall_typ(pk)
		on delete restrict
		on update cascade,
	started date
		not null
		default CURRENT_DATE,
	must_pay_prax_geb boolean
		not null
		default true
);

select add_table_for_audit('behandlungsfall');

-- ---------------------------------------------
-- this general table belongs elsewhere
create table payment_method (
	pk serial primary key,
	description text unique not null
);

-- ---------------------------------------------
create table prax_geb_paid (
	pk serial primary key,
	fk_fall integer
		not null
		references behandlungsfall(pk)
		on delete restrict
		on update cascade,
	paid_amount numeric
		not null
		default 0,
	paid_when date
		not null
		default CURRENT_DATE,
	paid_with integer
		not null
		references payment_method(pk)
		on delete restrict
		on update cascade
) inherits (audit_fields);

select add_table_for_audit('prax_geb_paid');

comment on table prax_geb_paid is
	'';

-- =============================================
-- do simple revision tracking
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmDemographics.de.sql,v $', '$Revision: 1.4 $');

-- =============================================
-- $Log: gmDemographics.de.sql,v $
-- Revision 1.4  2005-04-14 16:48:33  ncq
-- - name_gender_map moved to generic demographics script
--
-- Revision 1.3  2005/02/12 13:49:14  ncq
-- - identity.id -> identity.pk
-- - allow NULL for identity.fk_marital_status
-- - subsequent schema changes
--
-- Revision 1.2  2003/12/29 16:02:28  uid66147
-- - client_encoding breakage
--
-- Revision 1.1  2003/08/05 08:16:00  ncq
-- - cleanup/renaming
--
