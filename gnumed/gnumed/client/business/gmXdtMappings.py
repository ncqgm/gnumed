"""GnuMed XDT mapping data.

This maps XDT field IDs to verbose names.
"""
#==============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmXdtMappings.py,v $
# $Id: gmXdtMappings.py,v 1.1 2003-02-13 12:21:26 ncq Exp $
__version__ = "$Revision: 1.1 $"
__author__ = "S.Hilbert"
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

		 '9105':'Ordnungsnummer des Datentraegers dieses Datenpakets',
			
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
		 '9202':'Gesamtlaenge des Datenpakets',
		#number of media for this data package     
		 '9203':'Anzahl Datentraeger des Datenpakets',
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
		 '0250':'Name der ersten freien Kategorie',
		#content of first free category
		 '0251':'Inhalt der ersten frien Kategorie',
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
		 '3635':'interne Zuordnung Arzt bei Gemeinschaftspraxen',
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
		 '3668':'Anzahl Schwangerschafen',
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
		 '6200':'Tag der Speicherung von Behandlungsdaten',
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
		 '8000':'Satzidentifikation',
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
#==============================================================
# $Log: gmXdtMappings.py,v $
# Revision 1.1  2003-02-13 12:21:26  ncq
# - first check in
#
