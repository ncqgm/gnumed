#!/bin/sh
#JDBC_DRIVER=/opt/pgsql/lib/postgresql-jdbc3-7.3.jar
JDBC_DRIVER=/usr/share/pgsql/pg73jdbc2.jar
apath=".";for f in `ls lib/*.jar` ;do apath=$apath:$f ; done; echo $apath
java -cp ./src:$JDBC_DRIVER:hibernate2.jar:$apath net.sf.hibernate.eg.NetworkDemo
