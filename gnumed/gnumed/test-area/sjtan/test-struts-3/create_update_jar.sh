jar -cvf ../update-webclient.jar *.sh *.txt  `find pages -name "*.jsp"` pages/*.css  pages/*.html  WEB-INF/*.xml `find WEB-INF -name "*.properties"` `find WEB-INF -name "*.java"`
rm ../update-webclient.jar.bz2
bzip2 ../update-webclient.jar
scp ../update-webclient.jar.bz2 sjtan@salaam.homeunix.com:./
