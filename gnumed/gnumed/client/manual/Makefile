# Makefile for GNUMed docs

imagefiles = $(wildcard *.jpg)
dist_files = Makefile $(imagefiles) manual.sgml

all: index.html manual.pdf

index.html: gnumed.sgml
	db2html manual.sgml
	cp -R manual/* .
	rm -Rf manual/
	mv book1.html index.html

gnumed.pdf: gnumed.sgml $(imagefiles)
	db2pdf gnumed.sgml

	
clean:
	rm -Rf gnumed/
	rm -f gnumed.pdf
	rm -f *.tex *.aux *.log *.out
	rm -Rf DB* # temp dirs created by db2html
	rm *.html
	rm *.css


