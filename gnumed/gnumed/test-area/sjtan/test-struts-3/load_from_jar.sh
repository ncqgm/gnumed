cp META-INF/context.xml META-INF/backup-context.xml
cp WEB-INF/web.xml WEB-INF/backup-web.xml
rm ../update-webclient.jar
bunzip2 ../update-webclient.jar.bz2
jar -xvf ../update-webclient.jar

echo "WEB-INF/web.xml have been saved to backup-web.xml"
echo "META-INF/context.xml has also been saved"

