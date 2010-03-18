"""
/*
 * Created on Mar 18, 2004
 *
 * To change the template for this generated file go to
 * Window&gt;Preferences&gt;Java&gt;Code Generation&gt;Code and Comments
 */
package oscar.oscarLabs.PathNet.HL7.V2_3;

import java.sql.SQLException;

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
public class PIDContainer extends Node
{
	private ORC
		orc;
		
	private OBR
		obr;
		
	public OBR getOBR() {
	    return obr;
	}
	public ORC getORC() {
	    return orc;
	}
	
	public PIDContainer()
	{
		this.obr = null;
		this.orc = null;
	}
		
	public Node Parse(String line)
	{
		if(line.startsWith("ORC"))
		{
			this.orc = new ORC();
			return this.orc.Parse(line);
		}
		else if(line.startsWith("OBR"))
		{
			this.obr = new OBR();
			return this.obr.Parse(line);
		}
		else if(this.obr != null)
		{
			return this.obr.Parse(line);
		}
		System.err.println("Error During Parsing, Unknown Line - oscar.PathNet.HL7.V2_3.PIDContainer - Message: " + line);
		return null;
	}
	
	public void ToDatabase(DBHandler db, int parent)throws SQLException
	{
		if(this.orc != null)
		{
			this.orc.ToDatabase(db, parent);
		}
		this.obr.ToDatabase(db, parent);
	}
	
	public boolean HasOBR()
	{
		return (this.obr != null);	
	}
	
	protected String getInsertSql(int parent)
	{
		return "";
	}
	
	protected String[] getProperties()
	{
		return new String[0];
	}
    /* (non-Javadoc)
     * @see oscar.oscarLabs.PathNet.HL7.Node#accept(oscar.oscarLabs.PathNet.HL7.NodeVisitor)
     */
    public void accept(NodeVisitor visitor) {
        // TODO Auto-generated method stub
        visitor.visitPIDContainer(this);
    }

}

"""


from HL7.Node import Node
from HL7.V2_3.OBR import OBR
from HL7.V2_3.ORC import ORC


class PIDContainer(Node):

	def __init__(self):
		Node.__init__(self)
		self.__obr = None
		self.__orc = None
	
	def getOBR(self):
		return self.__obr
	def getORC(self):
		return self.__orc
		
	def getContainers(self):
		return self.__containers

	def getNotes(self):
		return self.__notes

	def accept(self, visitor):
		visitor.visitPIDContainer(self)

	def Parse(self, l):	

		if not l or len(l) < 3:
			return self
				
		prefix = l[0:3]
		if prefix == "ORC":
			self.__orc = ORC()
			return self.__orc.Parse(l)
		elif prefix =="OBR":
			self.__obr = OBR()
			return self.__obr.Parse(l)
	
		elif self.__obr <> None:
			return self.__obr.Parse(l)

		else:
			print 	"Error During Parsing, Unknown Line - oscar.PathNet.HL7.V2_3.PIDContainer - Message: " + l
		return None

	def hasOBR(self):
		return self.__obr <> None

	
	def getProperties(self):
		return []
