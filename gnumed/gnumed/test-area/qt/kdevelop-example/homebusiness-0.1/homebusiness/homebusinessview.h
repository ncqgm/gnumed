/***************************************************************************
                          homebusinessview.h  -  description
                             -------------------
    begin                : Wed Apr 21 17:35:34 EST 2004
    copyright            : (C) 2004 by s j tan
    email                : 
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/

#ifndef HOMEBUSINESSVIEW_H
#define HOMEBUSINESSVIEW_H

// include files for QT
#include <qwidget.h>

// application specific includes
#include "homebusinessdoc.h"

/**
 * This class provides an incomplete base for your application view. 
 */

class HomeBusinessView : public QWidget
{
  Q_OBJECT
  public:
    HomeBusinessView(QWidget *parent=0, HomeBusinessDoc* doc=0);
    ~HomeBusinessView();
  
  protected slots:
    void slotDocumentChanged();
  
};

#endif
