#change the 2 environment variables base_struts, base_tomcat to point to the local locations.

if ! -d $HOME ;then HOME=/home/$USER; fi
base_struts=`find $HOME -type d -name "jakarta-struts-1.2*" | head -n1`
base_tomcat=`find $HOME -maxdepth 3 -type d -name "jakarta-tomcat-5.*" | head -n1`

echo base_struts is $base_struts
echo base_tomcat is $base_tomcat
#commons_lang=$HOME/downloads/jakarta-commons/lang/commons-lang-2.0/commons-lang-2.0.jar

cp -u $base_struts/lib/* WEB-INF/lib
cp -u $base_struts/LICENSE LICENSE-STRUTS
cp -u $base_struts/NOTICE  NOTICE-STRUTS

cp -u $base_tomcat/common/lib/servlet-api.jar WEB-INF/lib
cp -u $base_struts/contrib/struts-el/lib/* WEB-INF/lib
cp -u $base_struts/contrib/struts-el/README.txt README-STRUTS-EL.txt




