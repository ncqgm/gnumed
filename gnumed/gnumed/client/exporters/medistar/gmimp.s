; =============================================================================
; Medistar-Formular zum Import von MD-Daten aus GNUmed
; 
; Dieses Formular ermöglich den Import von Karteieinträgen aus
; GNUmed in die medizinischen Daten (MD) von Medistar.
;
; Installation:
; - diese Datei nach LW:\medistar\forms\ kopieren
; - in Medistar Formularassembler aufrufen
; - einen freien Formularplatz wählen, z.B. 95
; - als Quelldatei "MS3.GMIMP-S" eingeben
; - "Formularcode einlesen" auswählen
; - Erfolgsmeldung sollte erscheinen
;
; Nutzung:
; - in GNUmed Patienten anlegen oder aufrufen
; - in Verlaufsnotizen Konsultationsdaten eingeben und speichern
; - im Menü "Karteikarte" den Punkt "Medistar-Export" aufrufen
; - die Exportdatei nach LW:\medistar\inst\soap.txt verschieben
; - in Medistar den Patienten anlegen oder aufrufen
; - bei Direktbefehl "FA95" eingeben (95 je nach Installation)
; - den Dateinamen (soap.txt) bestätigen
; - Erfolgsmeldung sollte erscheinen
; - in den MD sollten die GNUmed-Daten erscheinen
;
; Format der Export-/Importdatei:
; - zeilenorientiert
; - maximale Zeilenlänge 65 Zeichen
; - CRLF als Zeilenende (DOS-Konvention)
; - Zeichensatz "IBM PC" (unter Linux: "recode latin1/CR..IBM-PC/CRLF")
; - Markierungs- und Datenzeilen
; - Markierungszeilen: "*MD?*" wobei ? in A, B, D, T
; - Datenezeilen: beliebiger Text
; - alle Datenzeilen werden dem Zeilentyp der zuletzt gelesenen
;   Markierungszeile zugeordnet
; - Datenzeilen vor der ersten Markierungszeile erhalten den Typ "H"
;
; =============================================================================
; $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/exporters/medistar/gmimp.s,v $ 
; $Id: gmimp.s,v 1.2 2005-05-12 15:10:17 ncq Exp $
; Version: $Revision: 1.2 $
; Autor  : "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
; Lizenz : "GPL (details at http://www.gnu.org)"

; =============================================================================
FORM	"GNUmed-Import"
f1		05, 03, 08		; aktuelles Datum
f2		06, 03, 65		; Name Importdatei, nicht änderbar

FORMINPUT
	lr 1, "soap.txt"
	sr 1, f2

	; -- Layout -----------------------------------------
	print "Import medizinische Daten GNUmed => MD", 2, 2
	print p17, 3, 3		; Name Patient
	print p18, 4, 3		; Geburtstdatum Patient
	pdintd f1
	print f2
	; -- Layout -----------------------------------------

	input f2			; wirklich nötig ?

	recdate f1			; setze MD-Datum für Zuordnung
	sqopni "soap.txt"	; Importdatei, fest definiert, im Verzeichnis \medistar\inst\

	; -- Import -----------------------------------------
	print "=> importiere ...", 8, 3
	lr3, "H"			; Default-Zeilentyp "H" (Hinweis, Kommentar)
nxtline:
	sqread s1, 0		; lies ganze Zeile
	jmp nz, eof			; falls EOF

	; Anamnese ?
	lr 2, "*MDA*"		; Markierungszeile
	cr 1, 2				; gefunden ?
	iff z
		lr 3, "A"		; setze Zeilentyp "A"
		jmp nxtline		; nächste Zeile verarbeiten
	endif

	; Befund ?
	lr 2, "*MDB*"
	cr 1, 2
	iff z
		lr 3, "B"
		jmp nxtline
	endif

	; Diagnose ?
	lr 2, "*MDD*"
	cr 1, 2
	iff z
		lr 3, "D"
		jmp nxtline
	endif

	; Therapie ?
	lr 2, "*MDT*"
	cr 1, 2
	iff z
		lr 3, "T"
		jmp nxtline
	endif

	srmd 1, 3			; ansonsten Datenzeile, also in MD speichern
	jmp, nxtline
eof:
	SQCLS				; Datei schließen
	print "fertig", 8, 21
	STOP				; Programm beenden

FORMPRINT
FORMSAVE
FORMEND

; =============================================================================
; $Log: gmimp.s,v $
; Revision 1.2  2005-05-12 15:10:17  ncq
; - improved docs
;
; Revision 1.1  2005/05/12 10:02:34  ncq
; - Medistar import form for GNUmed progress notes
;
