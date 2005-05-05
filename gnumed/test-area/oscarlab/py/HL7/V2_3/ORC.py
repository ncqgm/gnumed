""" 
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
public class ORC extends oscar.oscarLabs.PathNet.HL7.Node
{	
	public Node Parse(String line)
	{
		if(line.startsWith("ORC"))
		{
			return super.Parse(line, 0, 1);
		}
		System.err.println("Error During Parsing, Unknown Line - oscar.PathNet.HL7.V2_3.ORC - Message: " + line);
		return null;
	}
	
	public void ToDatabase(DBHandler db, int parent)throws SQLException
	{
		db.RunSQL(this.getInsertSql(parent));
	}
	
	protected String getInsertSql(int parent)
	{
		String fields = "INSERT INTO hl7_orc ( pid_id";
		String values = "VALUES ('" + String.valueOf(parent) + "'";
		String[] properties = this.getProperties();
		for(int i = 0; i < properties.length; ++i)
		{
			fields += ", " + properties[i];
			values += ", '" + this.get(properties[i], "") + "'";
		}
		return fields + ") " + values + ");";
	}
	
	protected String[] getProperties()
	{
		return new String[]{
			"order_control",
			"placer_order_number1",
			"filler_order_number",
			"placer_order_number2",
			"order_status",
			"response_flag",
			"quantity_timing",
			"parent",
			"date_time_of_transaction",
			"entered_by",
			"verified_by",
			"ordering_provider",
			"enterer_location",
			"callback_phone_number",
			"order_effective_date_time",
			"order_control_code_reason",
			"entering_organization",
			"entering_device",
			"action_by"
		};
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


class ORC(Node):

	def __init__(self):
		Node.__init__(self)
		
		
	def accept(self, visitor):
		visitor.visit(self)

	def Parse(self, l):	

		if not l or len(l) < 3:
			return self
				
		prefix = l[0:3]
		if prefix == "ORC":
			return Node.Parse(self, l,0 , 1)
		else:
			print 	"Error During Parsing, Unknown Line - oscar.PathNet.HL7.V2_3.PIDContainer - Message: " + l
		return None

	def getProperties(self):
		return [
			"order_control",
			"placer_order_number1",
			"filler_order_number",
			"placer_order_number2",
			"order_status",
			"response_flag",
			"quantity_timing",
			"parent",
			"date_time_of_transaction",
			"entered_by",
			"verified_by",
			"ordering_provider",
			"enterer_location",
			"callback_phone_number",
			"order_effective_date_time",
			"order_control_code_reason",
			"entering_organization",
			"entering_device",
			"action_by"

			]
