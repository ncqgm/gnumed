/***************************************************************************
                          homebusinessdoc.cpp  -  description
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

#include "homebusinessdoc.h"

HomeBusinessDoc::HomeBusinessDoc()
{
  modified = false;
}

HomeBusinessDoc::~HomeBusinessDoc()
{
}

void HomeBusinessDoc::newDoc()
{
}

bool HomeBusinessDoc::save()
{
  return true;
}

bool HomeBusinessDoc::saveAs(const QString &filename)
{
  return true;
}

bool HomeBusinessDoc::load(const QString &filename)
{
  emit documentChanged();
  return true;
}

bool HomeBusinessDoc::isModified() const
{
  return modified;
}
