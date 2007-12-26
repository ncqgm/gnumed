#
# spec file for package gnumed-common (Version 0.2.7.1)
#
# Copyright (c) 2007 Sebastian Hilbert, Leipzig, Germany
# This file and all modifications and additions to the pristine
# package are under the same license as the package itself.
#
# Please submit bugfixes or comments via http://savannah.gnu.org/bugs/?group=gnumed&func=additem
#

# norootforbuild

Name:           gnumed-common
Summary:        An electronic medical record and patient record archive
License:        GPL
Version:        0.2.7.1
Release:        0.0
Group:          Productivity/Publishing/Other
Source:         http://www.gnumed.de/downloads/client/0.2/GNUmed-client.%{version}.tgz
#Patch0:         
#Patch1:         
#Patch2:         
Requires:  	python >= 2.3 python-devel python-psycopg2 python-egenix-mx-base
PreReq:         filesystem /usr/bin/touch
Provides:       gnumed-common
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
URL:            http://wiki.gnumed.de/

%description
This is the GNUmed Electronic Medical Record. Its purpose is to enable doctors to keep a medically sound record on their patients' health. Currently it is not fully featured. The features provided are, however, tested, in use, and considered stable. This package does NOT yet provide functionality for billing and stock keeping.

While the GNUmed team has taken the utmost care to make sure the medical records are safe at all times you still need to make sure you are taking appropriate steps to backup the medical data to a safe place at appropriate intervals. Do test your backup and desaster recovery procedures, too !

Protect your data! GNUmed itself comes without any warranty whatsoever. You have been warned.

Homepage: http://gnumed.org/

This package contains the wxpython client. 

Authors:
--------
    Sebastian Hilbert <sebastian.hilbert@gmx.net>
    Karsten Hilbert <karsten.hilbert@gmx.net>
    GNUmed team


%debug_package

%prep
%setup -n GNUmed-%{version}

%build

%install
[ -n "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != / ] && rm -rf "$RPM_BUILD_ROOT"
mkdir -p "$RPM_BUILD_ROOT"

#python setup.py install --optimize=2 --record-rpm=INSTALLED_FILES \
#      --root="$RPM_BUILD_ROOT"

mkdir -p $RPM_BUILD_ROOT%{_defaultdocdir}/%{name}


mkdir -p $RPM_BUILD_ROOT/usr/lib/python/site-packages/Gnumed/pycommon
#/usr/share/doc/gnumed-common/README.Debian
#/usr/share/doc/gnumed-common/changelog.Debian.gz
#/usr/share/doc/gnumed-common/copyright
#/usr/share/python-support/gnumed-common/.version
cp -r client/__init__.py $RPM_BUILD_ROOT/usr/lib/python/site-packages/Gnumed
cp -r client/pycommon/__init__.py $RPM_BUILD_ROOT/usr/lib/python/site-packages/Gnumed/pycommon
cp -r client/pycommon/gmBackendListener.py $RPM_BUILD_ROOT/usr/lib/python/site-packages/Gnumed/pycommon
cp -r client/pycommon/gmCfg.py $RPM_BUILD_ROOT/usr/lib/python/site-packages/Gnumed/pycommon
cp -r client/pycommon/gmCfg2.py $RPM_BUILD_ROOT/usr/lib/python/site-packages/Gnumed/pycommon
cp -r client/pycommon/gmDispatcher.py $RPM_BUILD_ROOT/usr/lib/python/site-packages/Gnumed/pycommon
cp -r client/pycommon/gmExceptions.py $RPM_BUILD_ROOT/usr/lib/python/site-packages/Gnumed/pycommon
cp -r client/pycommon/gmI18N.py $RPM_BUILD_ROOT/usr/lib/python/site-packages/Gnumed/pycommon
cp -r client/pycommon/gmLog.py $RPM_BUILD_ROOT/usr/lib/python/site-packages/Gnumed/pycommon
cp -r client/pycommon/gmLog2.py $RPM_BUILD_ROOT/usr/lib/python/site-packages/Gnumed/pycommon
cp -r client/pycommon/gmLoginInfo.py $RPM_BUILD_ROOT/usr/lib/python/site-packages/Gnumed/pycommon
cp -r client/pycommon/gmNull.py $RPM_BUILD_ROOT/usr/lib/python/site-packages/Gnumed/pycommon
    

find -P $RPM_BUILD_ROOT -type f | sed s#$RPM_BUILD_ROOT##g > INSTALLED_FILES 

#cp -p COPYING INSTALL PKG-INFO TODO README $RPM_BUILD_ROOT/%{_defaultdocdir}/%{name}/
#cp -pr examples doc  $RPM_BUILD_ROOT/%{_defaultdocdir}/%{name}/


%clean
[ -n "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != / ] && rm -rf "$RPM_BUILD_ROOT"


%files -f INSTALLED_FILES
%defattr(-,root,root)


%doc %{_defaultdocdir}/%{name}

%changelog -n gnumed-common
* Sun Oct 21 2007 - sebastian.hilbert@gmx.net
- usable version, some weird hacks removed

* Sun Jun 03 2007 - sebastian.hilbert@gmx.net
- Initial creation of package gnumed-common (GNUmed).