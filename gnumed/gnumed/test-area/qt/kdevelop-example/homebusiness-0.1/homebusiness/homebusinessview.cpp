/***************************************************************************
                          homebusinessview.cpp  -  description
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

#include "homebusinessview.h"

HomeBusinessView::HomeBusinessView(QWidget *parent, HomeBusinessDoc *doc) : QWidget(parent)
{
  /** connect doc with the view*/
  connect(doc, SIGNAL(documentChanged()), this, SLOT(slotDocumentChanged()));
}

HomeBusinessView::~HomeBusinessView()
{
}

void HomeBusinessView::slotDocumentChanged()
{
  //TODO update the view

}
