#change the 2 environment variables base_struts, base_tomcat to point to the local locations.
base_struts=$HOME/downloads/jakarta-struts-1.2.4
base_tomcat=$HOME/jakarta-tomcat-5.0.19
#commons_lang=$HOME/downloads/jakarta-commons/lang/commons-lang-2.0/commons-lang-2.0.jar

cp -u $base_struts/lib/* WEB-INF/lib
cp -u $base_struts/LICENSE LICENSE-STRUTS
cp -u $base_struts/NOTICE  NOTICE-STRUTS

cp -u $base_tomcat/common/lib/servlet-api.jar WEB-INF/lib
cp -u $base_struts/contrib/struts-el/lib/* WEB-INF/lib
cp -u $base_struts/contrib/struts-el/README.txt README-STRUTS-EL.txt




