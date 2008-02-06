%define name    gnumed-server
%define oname  GNUmed-server
%define summary The GNUmed backend server
%define version v8

%define pg_hba   /var/lib/pgsql/data/pg_hba.conf
%define pg_ident /var/lib/pgsql/data/pg_ident.conf

Summary: 	%summary
Name:		%name
Version:	%version
Release:	%mkrel 1
License:	GPL
Group:		System/Servers
Source:		http://www.gnumed.de/downloads/server/v8/%{oname}.%{version}.tgz
Patch0:		bootstrap-latest.sh.patch
Patch1:		bootstrap_gm_db_system.py.patch
BuildRoot:	%_tmppath/%name-%version-buildroot
URL:		http://wiki.gnumed.de/

Requires:	sudo
Requires:	python
Requires:	python-psycopg2
Requires:	postgresql8.2-plpython
Requires:	postgresql8.2-plpgsql

%description
The GNUmed project builds an open source Electronic Medical Record. It is developed by a handful of medical doctors and programmers from all over the world. It can be useful to anyone documenting the health of patients, including but not limited to doctors, physical therapists, occupational therapists, ...

%prep
%setup -q -n GNUmed-%{version}
%patch0 -p1
%patch1 -p1

%install
%{__mkdir_p} %buildroot/%{_libdir}/%{oname}
pushd server
    %{__mkdir_p} %buildroot/%{_libdir}/%{oname}/server
    cp -r * %buildroot/%{_libdir}/%{oname}/server
    echo "%{version}" > %buildroot/%{_libdir}/%{oname}/server/version.txt
popd	

%clean
test "x$RPM_BUILD_ROOT" != "x/" && rm -rf $RPM_BUILD_ROOT

%post
if [ $1 = 1 ]; then
    # initial install, let's make sure that postgresql is running
    /sbin/chkconfig postgresql on
    service postgresql restart &> /dev/null ||:
    
    # configure the pg_hba.conf file for postgresql Host Based Authentication
    grep -qP 'local\s+template1\s+postgres\s+ident\s+postgres-alikes' %pg_hba
    if [ $? -eq 1  ]; then
        echo "local template1 postgres ident postgres-alikes" >> %pg_hba
    fi
    grep -qP 'local\s+gnumed_v7\s+postgres\s+ident\s+postgres-alikes' %pg_hba
    if [ $? -eq 1  ]; then
        echo "local gnumed_v7 postgres ident postgres-alikes" >> %pg_hba
    fi
    grep -qP 'local\s+gnumed_v8\s+postgres\s+ident\s+postgres-alikes' %pg_hba
    if [ $? -eq 1  ]; then
        echo "local gnumed_v8 postgres ident postgres-alikes" >> %pg_hba
    fi
    grep -qP 'local\s+all\s+postgres\s+ident\s+sameuser' %pg_hba
    if [ $? -eq 1  ]; then
        echo "local all postgres ident sameuser" >> %pg_hba
    fi
    grep -qP 'local\s+template1\s+gm-dbo\s+ident\s+gm-dbo-alikes' %pg_hba
    if [ $? -eq 1  ]; then
        echo "local template1 gm-dbo ident gm-dbo-alikes" >> %pg_hba
    fi
    grep -qP 'local\s+samegroup\s+\+gm-logins\s+md5' %pg_hba
    if [ $? -eq 1  ]; then
        echo "local samegroup +gm-logins md5" >> %pg_hba
    fi
    
    #configure the pg_ident.conf file
    grep -qP 'gm-dbo-alikes\s+gmadm\s+gm-dbo' %pg_ident
    if [ $? -eq 1  ]; then
        echo "gm-dbo-alikes gmadm gm-dbo" >> %pg_ident
    fi
    grep -qP 'postgres-alikes\s+postgres\s+postgres' %pg_ident
    if [ $? -eq 1  ]; then
        echo "postgres-alikes postgres postgres" >> %pg_ident
    fi
    grep -qP 'postgres-alikes\s+gmadm\s+postgres' %pg_ident
    if [ $? -eq 1  ]; then
        echo "postgres-alikes gmadm postgres" >> %pg_ident
    fi
    
    # signal postgres that configuration has changed
    sudo -u postgres pg_ctl -D `dirname %pg_ident` reload &> /dev/null ||:
    
    # now let's bootstrap the database
    cd %{_libdir}/%{oname}/server/bootstrap
    export PYTHONPATH=%{_libdir}/%{oname}
    ./bootstrap-latest.sh &> /dev/null ||:
fi
if [ $1 = 2 ]; then
    # upgrade
    # figure out which version is installed by reading %{_libdir}/%{oname}/version.txt and save this in $prev
    # do the following 
    #       upgrade-db.sh $prev $prev+1
    # until $prev+1 equals $version
    echo "Upgrading is not implemented yet (nothing to upgrade to), yet somehow when you ran this - you just lost all of your data!"
fi

%postun
%{__rm} -rf %{_libdir}/%{oname}

%files
%defattr(-,root,root,-)
%{_libdir}/%{oname}

%changelog
* Tue Feb 04 2008 Doktor5000 <rpm@mandrivauser.de> v8-1mud2008.0
- initial package for mud-free testing

* Sat Jan 26 2007 Paul Grinberg <gri6507@yahoo.com> v8-2pclos2007
- initial version for PCLinuxOS 2007
