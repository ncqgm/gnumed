cat README
HTTPLIB=lib/commons-httpclient-2.0.2.jar
javac -d classes -classpath $HTTPLIB -sourcepath src `find src/oscar/oscarLabs/PathNet/HL7 -name "*.java"` src/test/*.java src/oscar/oscarDB/*.java
java -cp classes test.TestDriver $1 2> out
less out

