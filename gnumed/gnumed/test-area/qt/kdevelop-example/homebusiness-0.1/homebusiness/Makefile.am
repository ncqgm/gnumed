####### kdevelop will overwrite this part!!! (begin)##########
bin_PROGRAMS = homebusiness

## INCLUDES were found outside kdevelop specific part

homebusiness_SOURCES = mergecustomerdialog.ui mergeproductdialog.ui productdialog.ui discountdialog.ui productoffer.ui ordermain.ui ordermainadapter.cpp orderdetail.ui Customer.cpp Containers.cpp application1.cpp homebusinessview.cpp homebusinessdoc.cpp homebusiness.cpp main.cpp 
SOURCES = ordermainadapter.cpp Customer.cpp Containers.cpp application1.cpp homebusinessview.cpp homebusinessdoc.cpp homebusiness.cpp main.cpp 
INTERFACES = mergecustomerdialog.ui mergeproductdialog.ui productdialog.ui discountdialog.ui productoffer.ui ordermain.ui orderdetail.ui 
TRANSLATIONS = 
KDE_OPTIONS = qtonly
homebusiness_LDADD   = $(LIB_QPE)  -lpq -lkdecore $(LIB_QT) $(LIBSOCKET)


EXTRA_DIST = main.cpp homebusiness.cpp homebusiness.h homebusinessdoc.cpp homebusinessdoc.h homebusinessview.cpp homebusinessview.h lo32-app-homebusiness.png lo16-app-homebusiness.png filenew.xpm filesave.xpm fileopen.xpm application1.cpp application1.h Containers.cpp Containers.h Customer.cpp Customer.h orderdetail.ui ordermainadapter.cpp ordermainadapter.h ordermain.ui productoffer.ui discountdialog.ui productdialog.ui mergeproductdialog.ui mergecustomerdialog.ui datadef.sql 

####### kdevelop will overwrite this part!!! (end)############


# set the include path for X, qt and KDE
INCLUDES= $(all_includes)

homebusiness_METASOURCES = AUTO

# the library search path. 
homebusiness_LDFLAGS = $(all_libraries) 

# them while "make clean", use CLEANFILES
DISTCLEANFILES = $(homebusiness_METASOURCES)

