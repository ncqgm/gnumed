#change the 2 environment variables base_struts, base_tomcat to point to the local locations.
base_struts=$HOME/downloads/jakarta-struts-1.1
base_tomcat=$HOME/downloads/jakarta-tomcat-5.0.28

cp -u $base_struts/lib/* WEB-INF/lib
cp -u $base_tomcat/common/lib/servlet-api.jar WEB-INF/lib
cp -u $base_struts/contrib/struts-el/lib/* WEB-INF/lib



