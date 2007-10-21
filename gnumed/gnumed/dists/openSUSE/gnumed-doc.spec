#
# spec file for package gnumed-doc (Version 0.2.7.1)
#
# Copyright (c) 2007 Sebastian Hilbert, Leipzig, Germany
# This file and all modifications and additions to the pristine
# package are under the same license as the package itself.
#
# Please submit bugfixes or comments via http://savannah.gnu.org/bugs/?group=gnumed&func=additem
#

# norootforbuild

Name:           gnumed-doc
Summary:        An electronic medical record and patient record archive
License:        GPL
Version:        0.2.7.1
Release:        0.0
Group:          Productivity/Publishing/Other
Source:         http://www.gnumed.de/downloads/client/0.2/GNUmed-client.%{version}.tgz
#Patch0:         
#Patch1:         
#Patch2:         
Requires:  	file
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

########################################################################################

mkdir -p $RPM_BUILD_ROOT/usr/share/doc/gnumed/user-manual
#/usr/share/doc/gnumed-doc/README.Debian
#/usr/share/doc/gnumed-doc/changelog.Debian.gz
#/usr/share/doc/gnumed-doc/copyright
cp -r client/doc/user-manual/AddDocuments.html $RPM_BUILD_ROOT/usr/share/doc/gnumed/user-manual
cp -r client/doc/user-manual/AppointmentHandling.html $RPM_BUILD_ROOT/usr/share/doc/gnumed/user-manual
cp -r client/doc/user-manual/BasicEmrConcept.html $RPM_BUILD_ROOT/usr/share/doc/gnumed/user-manual
cp -r client/doc/user-manual/BasicEmrStructuring.html $RPM_BUILD_ROOT/usr/share/doc/gnumed/user-manual
cp -r client/doc/user-manual/BasicPatientHandling.html $RPM_BUILD_ROOT/usr/share/doc/gnumed/user-manual
cp -r client/doc/user-manual/BasicProgressNotes.html $RPM_BUILD_ROOT/usr/share/doc/gnumed/user-manual
cp -r client/doc/user-manual/ConfigFiles.html $RPM_BUILD_ROOT/usr/share/doc/gnumed/user-manual
cp -r client/doc/user-manual/ConfigPatientSearch.html $RPM_BUILD_ROOT/usr/share/doc/gnumed/user-manual
cp -r client/doc/user-manual/CustomizingClientStartup.html $RPM_BUILD_ROOT/usr/share/doc/gnumed/user-manual
cp -r client/doc/user-manual/DocumentManagementConcepts.html $RPM_BUILD_ROOT/usr/share/doc/gnumed/user-manual
cp -r client/doc/user-manual/DocumentManagementConfiguration.html $RPM_BUILD_ROOT/usr/share/doc/gnumed/user-manual
cp -r client/doc/user-manual/ExternalPatientImport.html $RPM_BUILD_ROOT/usr/share/doc/gnumed/user-manual
cp -r client/doc/user-manual/GnumedGuiElements.html $RPM_BUILD_ROOT/usr/share/doc/gnumed/user-manual
cp -r client/doc/user-manual/GnumedManual.html $RPM_BUILD_ROOT/usr/share/doc/gnumed/user-manual
cp -r client/doc/user-manual/GnumedReportGenerator.html $RPM_BUILD_ROOT/usr/share/doc/gnumed/user-manual
cp -r client/doc/user-manual/GnumedUserInterface.html $RPM_BUILD_ROOT/usr/share/doc/gnumed/user-manual
cp -r client/doc/user-manual/HooksFramework.html $RPM_BUILD_ROOT/usr/share/doc/gnumed/user-manual
cp -r client/doc/user-manual/LegacyAppAPW.html $RPM_BUILD_ROOT/usr/share/doc/gnumed/user-manual
cp -r client/doc/user-manual/LegacyAppConfiguration.html $RPM_BUILD_ROOT/usr/share/doc/gnumed/user-manual
cp -r client/doc/user-manual/LegacyAppDocConcept.html $RPM_BUILD_ROOT/usr/share/doc/gnumed/user-manual
cp -r client/doc/user-manual/LegacyAppTerminiko.html $RPM_BUILD_ROOT/usr/share/doc/gnumed/user-manual
cp -r client/doc/user-manual/ManagingUsers.html $RPM_BUILD_ROOT/usr/share/doc/gnumed/user-manual
cp -r client/doc/user-manual/PatientPhotographs.html $RPM_BUILD_ROOT/usr/share/doc/gnumed/user-manual
cp -r client/doc/user-manual/ReleaseStatus.html $RPM_BUILD_ROOT/usr/share/doc/gnumed/user-manual
cp -r client/doc/user-manual/StartingGnumed.html $RPM_BUILD_ROOT/usr/share/doc/gnumed/user-manual
cp -r client/doc/user-manual/ViewingDocuments.html $RPM_BUILD_ROOT/usr/share/doc/gnumed/user-manual
cp -r client/doc/user-manual/XmlRpcApi.html $RPM_BUILD_ROOT/usr/share/doc/gnumed/user-manual
#cp -r client/doc/user-manual/index.html $RPM_BUILD_ROOT/usr/share/doc/gnumed/user-manual
cp -r client/doc/user-manual/GnumedManual.html $RPM_BUILD_ROOT/usr/share/doc/gnumed/user-manual/index.html

find -P $RPM_BUILD_ROOT -type f | sed s#$RPM_BUILD_ROOT##g > INSTALLED_FILES 

#cp -p COPYING INSTALL PKG-INFO TODO README $RPM_BUILD_ROOT/%{_defaultdocdir}/%{name}/
#cp -pr examples doc  $RPM_BUILD_ROOT/%{_defaultdocdir}/%{name}/


%clean
[ -n "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != / ] && rm -rf "$RPM_BUILD_ROOT"


%files -f INSTALLED_FILES
#%defattr(-,root,root)


#%doc %{_defaultdocdir}/%{name}

%changelog -n gnumed-doc
* Sun Oct 21 2007 - sebastian.hilbert@gmx.net
- usable version, some weird hacks removed

* Sun Jun 03 2007 - sebastian.hilbert@gmx.net
- Initial creation of package gnumed-doc (GNUmed).
