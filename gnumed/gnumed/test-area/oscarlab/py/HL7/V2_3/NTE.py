""" 
package oscar.oscarLabs.PathNet.HL7.V2_3;

import oscar.oscarLabs.PathNet.HL7.Node;
import oscar.oscarLabs.PathNet.HL7.NodeVisitor;
import oscar.oscarDB.DBHandler;
/*
 * Copyright (c) 2001-2002. Andromedia. All Rights Reserved. *
 * This software is published under the GPL GNU General Public License. 
 * This program is free software; you can redistribute it and/or 
 * modify it under the terms of the GNU General Public License 
 * as published by the Free Software Foundation; either version 2 
 * of the License, or (at your option) any later version. * 
 * This program is distributed in the hope that it will be useful, 
 * but WITHOUT ANY WARRANTY; without even the implied warranty of 
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
 * GNU General Public License for more details. * * You should have received a copy of the GNU General Public License 
 * along with this program; if not, write to the Free Software 
 * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA. * 
 * 
 * <OSCAR TEAM>
 * 
 * This software was written for 
 * Andromedia, to be provided as
 * part of the OSCAR McMaster
 * EMR System
 * 
 * @author Jesse Bank
 * For The Oscar McMaster Project
 * Developed By Andromedia
 * www.andromedia.ca
 */
public class NTE extends oscar.oscarLabs.PathNet.HL7.Node
{
    
	public Node Parse(String line)
	{
		return super.Parse(line, 0, 1);
	}
	
	public void ToDatabase(DBHandler db, int parent)
	{}
	
	protected String getInsertSql(int parent)
	{
		return "";
	}
	
	protected String[] getProperties()
	{
		return new String[]{
			"set_id",
			"comment_source",
			"comment" };
	}

    /* (non-Javadoc)
     * @see oscar.oscarLabs.PathNet.HL7.Node#accept(oscar.oscarLabs.PathNet.HL7.NodeVisitor)
     */
    public void accept(NodeVisitor visitor) {
        // TODO Auto-generated method stub
        visitor.visit(this);
    }
}
"""
from HL7.Node import Node

class NTE(Node):
	def __init__(self):
		Node.__init__(self)
		
	def Parse(self, l):
		return Node.Parse(self, l)
		
	def getProperties(self):
		return [
			"set_id",
			"comment_source",
			"comment"
			]
	
	def accept(self, visitor):
		visitor.visit(self)		
