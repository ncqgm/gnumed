#change the 2 environment variables base_struts, base_tomcat to point to the local locations.
base_struts=$HOME/downloads/jakarta-struts-1.2.4
base_tomcat=$HOME/downloads/jakarta-tomcat-5.0.28
commons_lang=$HOME/downloads/jakarta-commons/lang/commons-lang-2.0/commons-lang-2.0.jar

cp -u $base_struts/lib/* WEB-INF/lib
cp -u $base_tomcat/common/lib/servlet-api.jar WEB-INF/lib
cp -u $base_struts/contrib/struts-el/lib/* WEB-INF/lib
cp -u $commons_lang WEB-INF/lib



