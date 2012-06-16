# Makefile to build several kinds of output for GNUmed user documentation

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/doc/developer-manual/Makefile,v $
# $Revision: 1.1 $
# license: GPL v2 or later
# author: Andreas Tille <tille@debian.org>

## linuxdoc does not work for this DTD
# SGMLTOOL=linuxdoc -c latin --language=en
# OPTHTML=-s 2 --backend=html
# OPTONEHTML=-s 0 --backend=html
# OPTPDF=--backend=latex -t 2 -p a4 --output=pdf
# OPTDVI=--backend=latex -t 2 -p a4 --output=dvi
# OPTPS=--backend=latex -t 2 -p a4 --output=ps

SGMLTOOL=sgmltools
OPTHTML=--backend=html
OPTONEHTML=--backend=onehtml
# output options check and info are not available for sgmltools-light
OPTDVI=--backend=dvi
OPTPS=--backend=ps

# Choose appropriate commands for your output format
HTML=$(SGMLTOOL) $(OPTHTML)
HTM=$(SGMLTOOL) $(OPTONEHTML)
# CHECK=$(SGMLTOOL) --backend=check
# INFO=$(SGMLTOOL) --backend=info
TXT=$(SGMLTOOL) --backend=txt
# PDF=$(SGMLTOOL) $(OPTPDF)
DVI=$(SGMLTOOL) $(OPTDVI)
PS=$(SGMLTOOL) $(OPTPS)

# .SUFFIXES: .sgml .html .htm .check .info .txt .pdf .dvi .ps
.SUFFIXES: .sgml .html .htm .txt .pdf .dvi .ps

.sgml.html:
	$(HTML) $^

.sgml.htm:
	$(HTM) $^

#.sgml.check:
#	$(CHECK) $^ &> $@

.sgml.info:
	echo "Sorry. INFO format does not build yet.
	# $(INFO) $^

.sgml.txt:
	$(TXT) $^

#.sgml.pdf:
#	$(PDF) $^
.pdf.ps:
	ps2pdf $^

.sgml.dvi:
	$(DVI) $^

.sgml.ps:
	$(PS) $^

all: developer-manual.html
	# Browseable HTML

developer-manual.html: developer-manual.sgml
developer-manual.htm: developer-manual.sgml
# developer-manual.check: developer-manual.sgml
developer-manual.info: developer-manual.sgml

browsable: developer-manual.html
unsplitted: developer-manual.htm
# check: developer-manual.check
# info: developer-manual.info
txt: developer-manual.txt
pdf: developer-manual.pdf
dvi: developer-manual.dvi
ps: developer-manual.ps

clean:
#	rm -f *-manual.html *-[0-9]*.html *-manual.log *-manual.htm *-manual.check *-manual.ps
	rm -rf developer-manual

distclean:
	make clean
#	rm -f *-manual.txt *-manual.dvi *-manual.pdf

#==================================================================
# $Log: Makefile,v $
# Revision 1.1  2002-11-20 13:26:54  ncq
# - Makefiles kindly contributed by Andreas of Debian-Med fame
#
