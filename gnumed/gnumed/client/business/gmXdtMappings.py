"""GnuMed German XDT mapping data.

This maps XDT fields in various ways.
"""
#==============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmXdtMappings.py,v $
# $Id: gmXdtMappings.py,v 1.10 2003-02-19 15:57:57 ncq Exp $
__version__ = "$Revision: 1.10 $"
__author__ = "S.Hilbert, K.Hilbert"
__license__ = "GPL"

#==============================================================
xdt_id_map = {
		#Turbomed fehlerhafte Feldkennungen :
		#sind nicht definiert nach BDT2/94, aber nach KVDT
		 '0215':'PLZ',
		 '0216':'Ort',
		 '3112':'PLZ',
		 '3113':'Ort',
		 '3673':'ICD??',
		 '6295':'??',
		 '6296':'??',
		 '6297':'??',
		 '6298':'??',
		 '6299':'??',
		#check for sending physician's id 
		 '9100':'Arztnummer des Absenders',
			
		 '9103':'Datum der Erstellung',

		 '9105':'Lfd.Nr. Datentraeger im Paket',
			
		 '9106':'Zeichencode',
		#--------------------------------------------------
		#data package header
		#--------------------------------------------------
		#ADT-version
		 '9210':'Version ADT-Satzbeschreibung',
		 '9213':'Version_BDT',
		#way data is archived
		#1 = storage as a whole
		#2 = storage arbitrary timeframe
		#3 = storage in quarters of a year
		 '9600':'Archivierungsart',
		#storage timeframe
		 '9601':'Zeitraum der Speicherung',
		#time of transfer start
		 '9602':'Beginn der Uebertragung',
		#--------------------------------------------------
		#data package header end
		#--------------------------------------------------
		#full length of data package 
		 '9202':'Gesamtlänge Datenpaket',
		#number of media for this data package     
		 '9203':'Anzahl Datenträger im Paket',
		#-------------------------------------------------
		#practice data
		#-------------------------------------------------
		#KBV-Pruefnummer 
		 '0101':'KBV-Pruefnummer',
		#responsible software vendor 
		 '0102':'Softwareverantwortlicher',
		#software package 
		 '0103':'Software',
		#PC hardware 
		 '0104':'Hardware',
		#Arztnummer 
		 '0201':'Arztnummer',
		#Praxistyp 
		 '0202':'Praxistyp',
		#Arztname
		 '0203':'Arztname',
		#Arztgruppe verbal 
		 '0204':'Arztgruppe verbal',
		#street
		 '0205':'Strasse',
		#postcode and city
		 '0206':'PLZ Ort',
		#Arzt und Leistungskennzeichen
		 '0207':'Arzt mit Leistungskennzeichen',
		#phone
		 '0208':'Telefonnummer',
		#fax
		 '0209':'Telefaxnmmer',
		#modem
		 '0210':'Modemnummer',
		#number of doctors
		 '0225':'Anzahl der Aerzte',
		#name of first free category
		 '0250':'Name erste freie Kategorie',
		#content of first free category
		 '0251':'Inhalt erste freie Kategorie',
		#-------------------------------------------------
		#medical treatment
		#-------------------------------------------------
		#Pattientennummer/Patientenkennung
		 '3000':'Patientennummer',
		#Namenszusatz/Vorsatzwort des Patienten
		 '3100':'Namenszusatz',
		#Name des Patienten
		 '3101':'Name des Patienten',
		#Vorname des Patienten
		 '3102':'Vorname des Patienten',
		#Geburstdatum des Patienten
		 '3103':'Geburstdatum des Patienten', 
		#Titel des Patienten 
		 '3104':'Tietel des Patienten',
		#Versichertennummer des Patienten
		 '3105':'Versichertennummer des Patienten',
		#Wohnort des Patienten
		 '3106':'Wohnort des Patienten',
		#Strasse des Patienten
		 '3107':'Strasse des Patienten',
		#Versichertenart M/F/R
		 '3108':'Versichertenart MFR',
		#Geschlecht des Patienten
		 '3110':'Geschlecht des Patienten',
		#Arbeitgeber -- nur bei header 0191 --
		 '3150':'Arbeitgeber',
		#Bezeichnung des Unfallversicherungstraegers -- nur bei header 0191 --
		 '3152':'Unfallversicherungstraeger',
		#Name des Hauptversicherten
		 '3201':'Name des Hauptversicherten',
		#Vorname des Hauptversicherten
		 '3202':'Vorname des Hauptversicherten',
		#Geburtsdatum des Hauptversicherten
		 '3203':'Geburtsdatum des Hauptversicherten',
		#Wohnort des Hauptversicherten
		 '3204':'Wohnort des Hauptversicherten',
		#Strasse des Hauptversicherten
		 '3205':'Strasse des Hauptversicherten',
		#Telefonnummer des Verletzten -- nur bei header 0191 -- 
		 '3208':'Telefonnummer des Verletzten',
		#Geschlecht des Hauptversicherten -- nur bei header 0190 --
		 '3210':'Geschlecht des Hauptversicherten',
		#Roentgennummer -- nur bei header 6100 --
		 '3601':'Roentgennummer',
		#Archivnummer -- nur bei header 6100 --
		 '3602':'Archivnummer',
		#BG-Nummer -- nur bei header 6100 --
		 '3603':'BG-Nummer',
		#Datum Patient seit -- nur bei header 6100 --
		 '3610':'Datum Patient seit',
		#Datum Versichertenbeginn bei Kassenwechsel -- nur bei header 6100 --
		 '3612':'Datum Versichertenbeginn bei Wechsel',
		#Beruf des Patienten -- nur bei header 6100 --
		 '3620':'Beruf des Patienten',
		#Groesse des Patienten -- nur bei header 6200 --
		 '3622':'Groesse des Patienten',
		#Gewicht des Patienten -- nur bei header 6200 --
		 '3623':'Gewicht des Patienten',
		#Arbeitgeber des Patienten -- nur bei header 6100 --
		 '3625':'Arbeitgeber des Patienten',
		#Telefonnummer des Patienten -- nur bei header 6100 --
		 '3626':'Telefonnummer des Patienten',
		#Nationalitaet des Patienten -- nur bei header 6100 --
		 '3627':'Nationalitaet des Patienten',
		#Muttersprache Patient -- nur bei header 6100 --
		 '3628':'Muttersprache des Patienten',
		#Arztnummer des Hausarztes -- nur bei header 6100 --
		 '3630':'Arztnummer des Hausarztes',
		#Entfernung Wohnung/Praxis-- nur bei header 6100 --
		 '3631':'Entfernung Wohnung-Praxis',
		#interne Zuordnung Arzt bei Gemeinschaftspraxen -- nur bei header 6100 --
		 '3635':'interne Zuordnung Arzt bei GP',
		#Rezeptkennung -- nur bei header 6100 --
		 '3637':'Rezeptkennung',
		#Dauerdiagnosen ab Datum -- nur bei header 6100 --
		 '3649':'Dauerdiagnosen ab Datum',
		#Dauerdiagnosen  -- nur bei header 6100 --
		 '3650':'Dauerdiagnosen',
		#Dauermedikamente ab Datum -- nur bei header 6100 --
		 '3651':'Dauermedikamente ab Datum',
		#Dauermedikamente -- nur bei header 6100 --
		 '3652':'Dauermedikamente',
		#Risikofaktoren -- nur bei header 6100 --
		 '3654':'Risikofaktoren',
		#Allergien -- nur bei header 6100 --
		 '3656':'Allergien',
		#Unfaelle -- nur bei header 6100 --
		 '3658':'Unfaelle',
		#Operationen -- nur bei header 6100 --
		 '3660':'Operationen',
		#Anamnese -- nur bei header 6100 --
		 '3662':'Anamnese',
		#Anzahl Geburten -- nur bei header 6100 --
		 '3664':'Anzahl Geburten',
		#Anzahl Kinder -- nur bei header 6100 --
		 '3666':'Anzahl Kinder',
		#Anzahl Schwangerschaften -- nur bei header 6100 --
		 '3668':'Anzahl Schwangerschaften',
		#Dauertherapie -- nur bei header 6100 --
		 '3670':'Dauertherapie',
		#Kontrolltermine -- nur bei header 6100 --
		 '3672':'Kontrolltermine',
		#Name erste freie Kategorie -- nur bei header 6100 --
		 '3700':'Name erste freie Kategorie',
		#Inhalt erste freie Kategorie -- nur bei header 6100 --
		 '3701':'Inhalt erste freie Kategorie',

		#3704-3719 freie Kategorien

		#Quartal
		 '4101':'Quartal',
		#Ausstellungsdatum
		 '4102':'Ausstellungsdatum',
		#Gueltigkeitsdatum
		 '4103':'Gueltigkeitsdatum',
		#VKNR- Vertragskassenarztnummer
		 '4104':'VKNR',
		#Geschaeftsstelle
		 '4105':'Geschaeftsstelle',
		#Kostentraegergruppe
		 '4106':'Kostentraegergruppe',
		#Abrechnungsart
		 '4107':'Abrechnungsart',
		#letzter Einlesetag der VK im Quartal TTMMJJ
		 '4109':'letzter Einlesetag der VK im Quartal',
		#Bis-Datum der Gueltigkeit MMJJ
		 '4110':'Bis-Datum der Gueltigigkeit',
		#Krankenkassennummer
		 '4111':'Krankenkassennummer',
		#Versichertenstatus VK
		 '4112':'Versichertenstatus VK',
		#Ost/West-Status VK
		 '4113':'Ost/West-Status VK',
		#Gebuehrenordnung
		 '4121':'Gebuehrenordnung',
		#Abrechnungsgebiet
		 '4122':'Abrechnungsgebiet',
		#Ursache des Leidens 
		 '4201':'Ursache des Leidens',
		#mutmasslicher Tag der Entbindung
		 '4206':'mutmasslicher Tag der Entbindung',
		#Diagnose/Verdacht -- nur bei header 0102 --
		 '4207':'Diagnose/Verdacht',
		#erlaeuternder Text zur Ueberweisung -- nur bei header 0102 --
		 '4209':'#erlaeuternder Text zur Ueberweisung',
		#Ankreuzfeld LSR  -- nur bei header 0102 --
		 '4210':'Ankreuzfeld LSR',
		#Ankreuzfeld HAH  -- nur bei header 0102 --
		 '4211':'Ankreuzfeld HAH',
		#Ankreuzfeld ABO.RH  -- nur bei header 0102 --
		 '4212':'Ankreuzfeld ABO.RH',
		#Ankreuzfeld AK  -- nur bei header 0102 --
		 '4213':'Ankreuzfeld AK',
		#Ueberweisung von Arztnummer  -- nur bei header 0102 --
		 '4218':'Ueberweisung von Arztnummer',
		#Ueberweisung an  -- nur bei header 0102 --
		 '4220':'Ueberweisung an',
		#stationaere Behandlung von bis -- nur bei header 0103/0190 --
		 '4233':'stationaere Behandlung von bis',
		#Klasse bei stationaerer Behandlung -- nur bei header 0190 --
		 '4236':'Klasse bei Behandlung',
		#Krankenhausname -- nur bei header 0190 --
		 '4237':'Krankenhausname',
		#Krankenhausaufenthalt -- nur bei header 0190 --
		 '4238':'Krankenhausaufenthalt',
		#Scheinuntergruppe
		 '4239':'Scheinuntergruppe',
		#weiterbehandelnder Arzt -- nur bei header 0104 --
		 '4243':'weiterbehandelnder Arzt',
		#Unfalltag -- nur bei header 0191 --
		 '4500':'Unfalltag',
		#Uhrzeit des Unfalls -- nur bei header 0191 --
		 '4501':'Uhrzeit des Unfalls',
		#Eingetroffen in Praxis am -- nur bei header 0191 --
		 '4502':'Eingetroffen in Praxis am',
		#Uhrzeit des Eintreffens -- nur bei header 0191 --
		 '4503':'Uhrzeit des Eintreffens',
		#Beginn Arbeitszeit -- nur bei header 0191 --
		 '4504':'Beginn der Arbeitszeit',
		#Unfallort -- nur bei header 0191 --
		 '4505':'Unfallort',
		#Beschaeftigung als -- nur bei header 0191 --
		 '4506':'Beschaeftigung als',
		#Beschaeftigung seit -- nur bei header 0191 --
		 '4507':'Beschaeftigung seit',
		#Staatsangehoerigkeit -- nur bei header 0191 --
		 '4508':'Staatsangehoerigkeit',
		#Unfallbetrieb -- nur bei header 0191 --
		 '4509':'Unfallbetrieb',
		#Unfallhergang -- nur bei header 0191 --
		 '4510':'Unfallhergang',
		#Verhalten des Verletzten nach dem Unfall -- nur bei header 0191 --
		 '4512':'Verhalten des Verletzten nach dem Unfall',
		#Erstmalige Behandlung -- nur bei header 0191 --
		 '4513':'Erstmalige_Behandlung',
		#Behandlung durch -- nur bei header 0191 --
		 '4514':'Behandlung_durch',
		#Art dieser ersten aerztlichen Behandlung -- nur bei header 0191 --
		 '4515':'Art dieser ersten aerztlichen Behandlung',
		#Alkoholeinfluss -- nur bei header 0191 --
		 '4520':'Alkoholeinfluss',
		#Anzeichen eines Alkoholeinflusses -- nur bei header 0191 --
		 '4521':'Anzeichen eines Alkoholeinflusses',
		#Blutentnahme -- nur bei header 0191 --
		 '4522':'Blutentnahme',
		#Befund -- nur bei header 0191 --
		 '4530':'Befund',
		#Roentgenergebniss -- nur bei header 0191 --
		 '4540':'Roentgenergebniss',
		#Art etwaiger Erstversorgung durch D-Arzt -- nur bei header 0191 --
		 '4550':'Art etwaiger Versorgung durch D-Arzt',
		#krankhafte Veraenderungen unabhaengig vom Unfall -- nur bei header 0191 --
		 '4551':'krankhafte Veraendrungen unabhaengig vom Unfall',
		#Bedenken gegen Angaben -- nur bei header 0191 --
		 '4552':'Bedenken gegen Angaben',
		#Art der Bedenken bei allegemeinen Bedenken-- nur bei header 0191 --
		 '4553':'Art der Bedenken gegen Angaben',
		#Bedenken gegen Vorliegen eines Arbeitsunfalls -- nur bei header 0191 --
		 '4554':'Bedenken gegen Arbeistunfall',
		#Art der Bedenken gegen Arbeitsunfall -- nur bei header 0191 --
		 '4555':'Art_Bedenken gegen Arbeitsunfall',
		#arbeitsfaehig -- nur bei header 0191 --
		 '4560':'arbeitsfaehig',
		#wieder arbeitsfaehig ab -- nur bei header 0191 --
		 '4561':'wieder arbeitsfaehig ab',
		#AU-Bescheinigung ausgestellt -- nur bei header 0191 --
		 '4562':'AU ausgestellt',
		#besondere Heilbehandlung erforderlich -- nur bei header 0191 --
		 '4570':'besondere Heilbehandlung erforderlich',
		#besondere Heilbehandlung durch -- nur bei header 0191 --
		 '4571':'bes_Heilbehandlung_durch',
		#Anschrift des behandelnden Arztes -- nur bei header 0191 --
		 '4572':'Anschrift behandelnder Arzt',
		#AU ab -- nur bei header 0191 --
		 '4573':'AU ab',
		#voraussichtliche Dauer der AU -- nur bei header 0191 --
		 '4574':'voraussichliche Dauer der AU',
		#Rechnungsart -- nur bei header 0190 --
		 '4580':'Rechnungsart',
		#allgemeine Heilbehandlung durch -- nur bei header 0191 --
		 '4581':'allgemeine Heilbehandlung durch',
		#AU ueber 3 Tage -- nur bei header 0191 --
		 '4582':'AU ueber 3 Tage',
		#AU bescheinigt als -- nur bei header 0191 --
		 '4583':'AU bescheinigt als',
		#Nachschau erforderlich -- nur bei header 0191 --
		 '4584':'Nachschau erforderlich',
		#Rechnungsnummer -- nur bei header 0190 --
		 '4601':'Rechnungsnummer',
		#Anschrift des Rechnungsadressaten (Empfaenger) -- nur bei header 0190 --
		 '4602':'Rechnungsanschrift',
		#ueberweisender Arzt -- nur bei header 0190 --
		 '4603':'ueberweisender Arzt',
		#Rechnungsdatum -- nur bei header 0190 --
		 '4604':'Rechnungsdatum',
		#Endsumme -- nur bei header 0190 --
		 '4605':'Endsumme',
		#Abdingungserklaerung vorhanden -- nur bei header 0190 --
		 '4608':'Abdingungserklaerung vorhanden',
		#Unterkonto Arzt -- nur bei header 0190 --
		 '4611':'Unterkonto Arzt',
		#Anlage erforderlich -- nur bei header 0190 --
		 '4613':'Anlage erforderlich',
		#Kopfzeile -- nur bei header 0190 --
		 '4615':'Kopfzeile',
		#Fusszeile -- nur bei header 0190 --
		 '4617':'Fusszeile',
		#Leistungstag
		 '5000':'Leistungstag',
		#Gebuehrennummer
		 '5001':'GNR',
		#Art der Untersuchung
		 '5002':'Art der Untersuchung',
		#Empfaenger des Briefes
		 '5003':'Empfaenger des Briefes',
		#Kilometer (nur bei GOA)
		 '5004':'Kilometer',
		#Multiplikator
		 '5005':'Multiplikator',
		#Um-Uhrzeit
		 '5006':'Um-Uhrzeit',
		#Bestellzeit-Ausfuehrungszeit
		 '5007':'Bestellzeit-Ausfuehrungszeit',
		#DKM=Doppelkilometer
		 '5008':'Doppel-KM',
		#freier Begruendungstext
		 '5009':'freie Begruendung',
		#Medikament als Begruendung -- nur bei header 0190 --
		 '5010':'Medikament als Begruendung',
		#Sachkosten-Bezeichnung
		 '5011':'Sachkosten-Bezeichnung',
		#Sachkosten/Materialkosten (Dpf)
		 '5012':'Sachkosten/Materialkosten',
		#Prozent der Leistung
		 '5013':'Prozent der Leistung',
		#Organ
		 '5015':'Organ',
		#Besuchsort bei Hausbesuchen
		 '5017':'Besuchsort bei Hausbesuchen',
		#Zone bei Besuchen
		 '5018':'Zone bei Besuchen',
		#Beschreibung der GNR -- nur bei header 0190 --
		 '5060':'Beschreibung der GNR',
		#Gebuehr -- nur bei header 0190 --
		 '5061':'Gebuehr',
		#Faktor -- nur bei header 0190 --
		 '5062':'Faktor',
		#Betrag -- nur bei header 0190 --
		 '5063':'Betrag',
		#Punktwert -- nur bei header 0191 --
		 '5065':'Punktwert',
		#Honorarbezeichnung -- nur bei header 0190 --
		 '5090':'Honorarbezeichnung',
		#Gutachten-Bezeichnung -- nur bei header 0190 --
		 '5091':'Gutachtenbezeichnung',
		#Abrechnungsdiagnosen -- nur bei header 0102 --
		 '6000':'Abrechnungsdiagnosen',
		#ICD-Schluessel
		 '6001':'ICD-Schluessel',
		#Tag der Speicherung von Behandlungsdaten -- nur bei header 6200 --
		 '6200':'gespeichert am',
		#aktuelle Diagnose -- nur bei header 6200 --
		 '6205':'aktuelle Diagnose',
		#Medikament verordnet auf Rezept -- nur bei header 6200 --
		 '6210':'Medikament verordnet auf Rezept',
		#ausserhalb Rezept verordnetes Medikament -- nur bei header 6200 --
		 '6211':'Medikament verordnet ausserhalb Rezept',
		#Aerztenummer -- nur bei header 6200 --
		 '6215':'Aerztenummer',
		#Befund -- nur bei header 6200 --
		 '6220':'Befund',
		#Fremdbefund -- nur bei header 6200 --
		 '6221':'Fremdbefund',
		#Laborbefund -- nur bei header 6200 --
		 '6222':'Laborbefund',
		#Roentgenbefund -- nur bei header 6200 --
		 '6225':'Roentgenbefund',
		#Blutdruck -- nur bei header 6200 --
		 '6230':'Blutdruck',
		#Symptome -- nur bei header 6200 --
		 '6240':'Symptome',
		#Therapie -- nur bei header 6200 --
		 '6260':'Therapie',
		#physikalische Therapie -- nur bei header 6200 --
		 '6265':'physikalische Therapie',
		#Ueberweisung Inhalt -- nur bei header 6200 --
		 '6280':'Ueberweisung Inhalt',
		#AU-Dauer -- nur bei header 6200 --
		 '6285':'AU Dauer',
		#AU-wegen -- nur bei header 6200 --
		 '6286':'AU wegen',
		#Krankenhauseinweisung,Krankenhaus -- nur bei header 6200 --
		 '6290':'Krankenhauseinweisung,Krankenhaus',
		#Krankenhauseinweisung -- nur bei header 6200 --
		 '6291':'Krankenhauseinweisung',
		#Bescheiningung -- nur bei header 6200 --
		 '6300':'Bescheinigung',
		#Inhalt der Bescheinigung -- nur bei header 6200 --
		 '6301':'Inhalt der Bescheinigung',
		#Attest -- nur bei header 6200 --
		 '6306':'Attest',
		#Inhalt des Attestes -- nur bei header 6200 --
		 '6307':'Inhalt des Attestes',
		#Name des Briefempfaengers -- nur bei header 6200 --
		 '6310':'Name des Briefempfaengers',
		#Anrede -- nur bei header 6200 --
		 '6311':'Anrede',
		#Strasse -- nur bei header 6200 --
		 '6312':'Strasse',
		#PLZ -- nur bei header 6200 --
		 '6313':'PLZ',
		#Wohnort -- nur bei header 6200 --
		 '6314':'Wohnort',
		#Schlussatz -- nur bei header 6200 --
		 '6315':'Schlusssatz',
		#Telefonnummer -- nur bei header 6200 --
		 '6316':'Telefonnummer',
		#Telefax -- nur bei header 6200 --
		 '6317':'Telefax',
		#Arztnummer/Arztident -- nur bei header 6200 --
		 '6319':'Arztnummer/Arztident',
		#Briefinhalt -- nur bei header 6200 --
		 '6320':'Briefinhalt',
		#Bild-Archivierungsnummer -- nur bei header 6200 --
		 '6325':'Bild-Archivierungsnummer',
		#Graphikformat -- nur bei header 6200 --
		 '6326':'Graphikformat',
		#Bildinhalt -- nur bei header 6200 --
		 '6327':'Bildinhalt',
		#Name der ersten freien Kategorie -- nur bei header 6200 --
		 '6330':'Name der ersten freien Kategorie',
		#Inhalt der ersten freien Kategorie -- nur bei header 6200 --
		 '6331':'Inhalt der ersten freien Kategorie',

		#--------------------------------------------------------
		# more free categories
		#Satzidentifikation
		 '8000':'Satzidentifikation >>===============',
		#Satzlaenge
		 '8100':'Satzlaenge',
		#Befundart -- nur bei header 6200 --
		 '8401':'Befundart',
		#Geraete- bzw. Verfahrensspezifisches Kennfeld -- nur bei header 6200 --
		 '8402':'Geraetespezifisches Kennfeld',
		#Test-Ident -- nur bei header 6200 --
		 '8410':'Test-Ident',
		#Testbezeichnung -- nur bei header 6200 --
		 '8411':'Testbezeichnung',
		#Teststatus -- nur bei header 6200 --
		 '8418':'Teststatus',
		#Ergebnis-Wert -- nur bei header 6200 --
		 '8420':'Ergebnis Wert',
		#Einheit -- nur bei header 6200 --
		 '8421':'Einheit',
		#Grenzwert Indikator -- nur bei header 6200 --
		 '8422':'Grenzwert Indikator',
		#Probematerial-Nummer -- nur bei header 6200 --
		 '8429':'Probenmaterial-Nummer',
		#Probenmaterial-Bezeichnung -- nur bei header 6200 --
		 '8430':'Probenmaterial-Bezeichnung',
		#Material-Spezifikation -- nur bei header 6200 --
		 '8431':'Material_Spezifikation',
		#Abnahme-Datum -- nur bei header 6200 --
		 '8432':'Abnahme-Datum',
		#Abnahme-Zeit -- nur bei header 6200 --
		 '8433':'Abnahme-Zeit',
		#Keim-Ident -- nur bei header 6200 --
		 '8440':'Keim-Ident',
		#Keim-Bezeichnung -- nur bei header 6200 --
		 '8441':'Keim-Bezeichnung',
		#Keim-Nummer -- nur bei header 6200 --
		 '8442':'Keim-Nummer',
		#Resistenz-Methode -- nur bei header 6200 --
		 '8443':'Resistenz-Methode',
		#Wirkstoff-Ident -- nur bei header 6200 --
		 '8444':'Wirkstoff-Ident',
		#Wirkstoff-Generic-Nummmer -- nur bei header 6200 --
		 '8445':'Wirkstoff-Generic-Nummer',
		#MHK/Breakpoint-Wert -- nur bei header 6200 --
		 '8446':'MHK',
		#Resistenz-Interpretation -- nur bei header 6200 --
		 '8447':'Resistenz-Interpretation',
		#Normalwert-Text -- nur bei header 6200 --
		 '8460':'Normalwert-Text',
		#Anmerkung -- nur bei header 6200 --
		 '8470':'Anmerkung',
		#Ergebnis-Text -- nur bei header 6200 --
		 '8480':'Ergebnis-Text',
		#Abschluss-Zeile -- nur bei header 6200 --
		 '8490':'Abschluss-Zeile',
		#Signatur -- nur bei header 6200 --
		 '8990':'Signatur',
	    }
#--------------------------------------------------------------

xdt_packet_type_map = {
	'0020': "========<< Anfang Datenträger >>========",
	'0021': "========<< Ende Datenträger >>========",
	'0022': "========<< Anfang Datenpaket >>========",
	'0023': "========<< Ende Datenpaket >>========",
	'0010': "========<< Praxisdaten >>========",
	'0101': "========<< Fall: Primärarzt >>========",
	'0102': "========<< Fall: Überweisung >>========",
	'0103': "========<< Fall: Belegarzt  >>========",
	'0104': "========<< Fall: Notfall/Dienst/Vertretung >>========",
	'0190': "========<< Fall: Privat >>========",
	'0191': "========<< Fall: BG >>========",
	'0199': "========<< Fall: unstrukturiert >>========",
	'6100': "========<< Patientenstamm >>========",
	'6200': "========<< Behandlungsdaten >>========"
}
#--------------------------------------------------------------
# XDT:
# dob: ddmmyyyy
# gender: 1 - male, 2 - female

# patient record fields
name_xdtID_map = {
	'last name': '3101',
	'first name': '3102',
	'date of birth': '3103',
	'gender': '3110'
}
#    'city': '3106',\
#    'street': '3107',\

# sort of GnuMed compatible
xdt_gmgender_map = {
	'1': 'm',
	'2': 'f',
	'm': 'm',
	'f': 'f'
}

# xDT character code mapping : 9106
xdt_character_code_map = {
	'1':'7-bit-Code ASCII',
	'2':'8-bit-Code ASCII'
}
# Archivierungsart : 9600
xdt_Archivierungsart_map = {
	'1':'Speicherung Gesamtbestand',
	'2':'Speicherung beliebiger Zeitraum',
	'3':'Speicherung eines Quartals'
}
# Praxistyp : 0202
xdt_Praxistyp_map = {
	'1':'Einzelpraxis',
	'2':'Gemeinschaftspraxis',
	'3':'Fachuebergreifende GP',
	'4':'Praxisgemeinschaft',
	'5':'Fachuebergreifende GP ohne Kennzeichen Leistung'
}
# Versichertenart MFR : 3108
xdt_Versichertenart_map = {
	'1':'Mitglied',
	'3':'Familienversicherter',
	'5':'Rentner',
}
# Kostentraegeruntergruppe : 4106
xdt_Kostentraegeruntergruppe_map = {
	'00':'default',
	'01':'SVA(Sozialversicherungsabkommen)',
	'02':'BVG(Bundesversorgungsgesetz)',
	'03':'BEG(Bundesentschaedigungsgesetz)',
	'04':'Grenzgaenger',
	'05':'Rheinschiffer',
	'06':'Sozialaemter',
	'07':'BVFG(Bundesvertriebenengesetz)'
}
# Abrechnungsart : 4107
xdt_Abrechnungsart_map = {
	'1':'PKA(Primaerkassen)',
	'2':'EKK(Ersatzkassen)',
	'3':'SKT(Sonstige Kostentraeger)',
}
# Ost/West-Status VK : 4113
xdt_Ost_West_Status_map = {
	'1':'West',
	'9':'Ost'
}
# Gebuehrenordnung : 4121
xdt_Gebuehrenordnung_map = {
	'1':'BMA',
	'2':'E-GO',
	'3':'GOA'
}
# Abrechnungsgebiet : 4122
xdt_Abrechnungsgebiet_map = {
	'00':'default',
	'01':'Dialyse-Arztkosten',
	'02':'Dialyse-Sachkosten',
	'03':'Methadon-Substitutionsbehandlung',
	'04':'Grosse Psychotherapie',
	'05':'Verhaltenstherapie',
	'06':'Fremde Zytologie'
}
# Ursache des Leidens : 4201
xdt_Ursache_des_Leidens_map = {
	'2':'Unfall, Unfallfolgen',
	'3':'Versorgungsleiden'
}
# Ankreuzfeld LSR, HAH, ABO.RH, AK
xdt_Ankreuzfeld_map = {
	'1':'angekreuzt'
}
# Scheinuntergruppe
xdt_Scheinuntergruppe_map = {
	'20':'Selbstaustellung',
	'21':'Zielauftrag (Defaultwert bei Einsendepraxen)',
	'22':'Rahmenauftrag',
	'23':'Konsillaruntersuchung',
	'24':'Mit/Weiterbehandlung (Defaultwert ausser bei Einsendepraxen)',
	'25':'Ueberweisung aus anderen Gruenden',
	'26':'Stat. Mitbehandlung, Verguetung nach amb. Grundsaetzen',
	'30':'Belegaerztliche Behandlung (Default bei SA 0103)',
	'31':'Belegaerztliche Mitbehandlung',
	'41':'aerztlicher Notfalldienst',
	'42':'Urlaubs-bzw. Krankheitsvertretung',
	'43':'Notfall',
	'44':'Notfalldienst bei Taxi',
	'45':'Notarzt-/Rettungswagen (Rettungsdienst)',
	'90':'default bei SA 0190',
	'91':'Konsillaruntersuchung',
	'92':'stat. Mitbehandlung Verguetung nach stat. Grundsaetzen',
	'93':'stat. Mitbehandlung Verguetung nach ambul. Grundsaetzen',
	'94':'belegaerztliche Behandlung im Krankenhaus'
}
# Gesetzlicher Abzug zur stationaeren Behandlung gemaess Paragraph 6a GOA
xdt_gesetzlicher_Abzug_map = {
	'1':'nein',
	'2':'ja'
}
# Klasse bei stationaerer Behandlung
xdt_Klasse_stationaere_Behandlung_map = {
	'1':'Einbettzimmer',
	'2':'Zweibettzimmer',
	'3':'Mehrbettzimmmer'
}
# Rechnungsart
xdt_Rechnungsart_map = {
	'01':'Privat',
	'20':'KVB',
	'21':'Bahn-Unfall',
	'30':'Post',
	'31':'Post-Unfall',
	'40':'Allgemeines Heilverfahren',
	'41':'Berufsgenossenschaft Heilverfahren',
	'50':'Bundesknappschaft',
	'70':'Justizvollzugsanstalt',
	'71':'Jugendarbeitsschutz',
	'72':'Landesversicherungsanstalt',
	'73':'Bundesversicherungsanstalt fuer Angestellte',
	'74':'Sozialamt',
	'75':'Sozialgericht',
	'80':'Studenten-Deutsche',
	'81':'Studenten-Auslaender'
}
# Abdingungserklaerung vorhanden
xdt_Abdingungserklaerung_map = {
	'1':'nein',
	'2':'ja'
}
# Anlage erforderlich
xdt_Anlage_erforderlich_map = {
	'1':'nein',
	'2':'ja'
}
#Alkoholeinfluss
xdt_Alkoholeinfluss_map = {
	'1':'nein',
	'2':'ja'
}
# Blutentnahme
xdt_Blutentnahme_map = {
	'1':'nein',
	'2':'ja'
}
# Bedenken gegen das Vorliegen eines Arbeitsunfalls
xdt_Arbeitsunfall_map = {
	'1':'nein',
	'2':'ja'
}
# arbeitsfaehig
xdt_arbeitsfaehig_map = {
	'1':'angekreuzt'
}
# Besondere Heilbehandlung erforderlich
xdt_Heilbehandlung_erforderlich_map = {
	'1':'ambulant',
	'2':'stationaer'
}
# Besondere Heilbehandlung durch
xdt_Besondere_Heilbehandlung_durch_map = {
	'1':'selbst',
	'2':'anderer Durchgangsarzt'
}
# Allgemeine Heilbehandlung durch
xdt_Allgemeine_Heilbehandlung_durch_map = {
	'1':'selbst',
	'2':'anderer Arzt'
}
# AU ueber 3 Tage
xdt_AU_3Tage_map = {
	'1':'angekreuzt'
}
# Befundart 
xdt_Befundart_map = {
	'E':'(kompletter) Endbefund',
	'T':'Teilbefund',
	'V':'(kompletter) Vorbefund',
	'A':'Archivbefund'
}
# Teststatus : 8418
xdt_Teststatus_map = {
	'B':'bereits berichtet',
	'K':'Korrigierter Wert oder fehlt'
}
# Resistenzmethode
xdt_Resistenzmethode_map = {
	'1':'Agardiffusion',
	'2':'Agardilution',
	'3':'MHK-Bestimmung',
	'4':'Breakpoint-Bestimmung'
}
# Resistenz-Interpretation
xdt_Resistenzinterpretation_map = {
	'0':'nicht getestet',
	'1':'sensibel/wirksam',
	'2':'maessig sensibel/schwach wirksam',
	'3':'resistent/unwirksam',
	'4':'wirksam in hohen Konzentrationen'
}
#--------------------------------------------------------------
xdt_map_of_content_maps = {
	'8000': xdt_packet_type_map,
	'9106': xdt_character_code_map,
	'9600': xdt_Archivierungsart_map,
	'0202': xdt_Praxistyp_map,
	'3108': xdt_Versichertenart_map,
	'3110': xdt_gmgender_map,
	'4106': xdt_Kostentraegeruntergruppe_map,
	'4107': xdt_Abrechnungsart_map,
	'4113': xdt_Ost_West_Status_map,
	'4121': xdt_Gebuehrenordnung_map,
	'4122': xdt_Abrechnungsgebiet_map,
	'4201': xdt_Ursache_des_Leidens_map,
	'4210': xdt_Ankreuzfeld_map,
	'4211': xdt_Ankreuzfeld_map,
	'4212': xdt_Ankreuzfeld_map,
	'4213': xdt_Ankreuzfeld_map,
	'4239': xdt_Scheinuntergruppe_map,
	'4230': xdt_gesetzlicher_Abzug_map,
	'4236': xdt_Klasse_stationaere_Behandlung_map,
	'4580': xdt_Rechnungsart_map,
	'4608': xdt_Abdingungserklaerung_map,
	'4613': xdt_Anlage_erforderlich_map,
	'4520': xdt_Alkoholeinfluss_map,
	'4522': xdt_Blutentnahme_map,
	'4554': xdt_Arbeitsunfall_map,
	'4560': xdt_arbeitsfaehig_map,
	'4570': xdt_Heilbehandlung_erforderlich_map,
	'4571': xdt_Besondere_Heilbehandlung_durch_map,
	'4581': xdt_Allgemeine_Heilbehandlung_durch_map,
	'4582': xdt_AU_3Tage_map,
	'8401': xdt_Befundart_map,
	'8418': xdt_Teststatus_map,
	'8443': xdt_Resistenzmethode_map,
	'8447': xdt_Resistenzinterpretation_map
}
#==============================================================
# $Log: gmXdtMappings.py,v $
# Revision 1.10  2003-02-19 15:57:57  ncq
# - better strings
#
# Revision 1.9  2003/02/19 15:23:44  ncq
# - a whole bunch of new mappings by Basti
#
# Revision 1.8  2003/02/19 12:27:42  ncq
# - map_of_maps -> map_of_content_maps
#
# Revision 1.7  2003/02/19 12:26:47  ncq
# - map of maps
#
# Revision 1.6  2003/02/17 23:31:02  ncq
# - added some patient related mappings
#
# Revision 1.5  2003/02/14 01:49:17  ncq
# - better strings
#
# Revision 1.4  2003/02/13 15:42:54  ncq
# - changed some strings
#
# Revision 1.3  2003/02/13 15:26:09  ncq
# - added mappings for content translation of Satzidentifikation
#
# Revision 1.2  2003/02/13 12:21:53  ncq
# - comment
#
# Revision 1.1  2003/02/13 12:21:26  ncq
# - first check in
#
