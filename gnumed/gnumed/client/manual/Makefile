# Makefile for GNUMed docs

imagefiles = $(wildcard *.jpg)
dist_files = Makefile $(imagefiles) manual.sgml

all: index.html manual.pdf

index.html: manual.sgml
	db2html manual.sgml
	cp -R manual/* .
	rm -Rf manual/
	mv book1.html index.html

manual.pdf: manual.sgml $(imagefiles)
	db2pdf manual.sgml

	
clean:
	rm -Rf manual/
	rm -f manual.pdf
	rm -f manual.tex manual.aux manual.log manual.out
	rm -Rf DB* # temp dirs created by db2html
	rm *.html
	rm *.css


