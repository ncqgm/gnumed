apt-get install python2.2-psycopg
apt-get -t unstable install libwxgtk2.3-python
apt-get -t unstable install python-pgsql
dpkg -i gnumed-snapshot-client
#should work well now.... prev comment: # above statement will fail, but the below statement will install some the required dependencies
apt-get -f install
# ok, now i'll forget about the gnumed client for a while.. cause i wont be able to install anything else after it without doing a 'apt-get -f' (which would remove the client!).. so we do everything else and dpkg -i --force-depends and install libwxgtk2.3-python and gnumed-client later on!
apt-get install postgresql=*
echo "get the most master working with -d /var/lib/postgres/data (default) and then create user 'knoppix' and 'guest' and root"

echo "now dpkg all the gnumed stuff"
echo "then change country in /etc/gnumed/server.conf"
ln -s /etc/init.d/apache /etc/rc5.d/S20apache
cp debian-med /etc/init.d/debian-med
ln -s /etc/init.d/debian-med /etc/rc5.d/S19debian-med
apt-get install med-dent
#apt-get install resmed-doc med-bio med-common med-common-dev med-dent med-doc med-imaging med-imaging-dev med-tools med-bio-contrib
#not req dpkg --ignore-depends=python -i libwxgtk2.3-python_2.3.3.2_i386.deb

dpkg -i gnumed-client-snapshot

echo "vi /etc/postgresql/pg_hba.conf to allow access to all (change to trust)" 
