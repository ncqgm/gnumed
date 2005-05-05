 
package oscar.oscarLabs.PathNet.HL7.V2_3;

import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

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
public class PID extends oscar.oscarLabs.PathNet.HL7.Node
{
	private ArrayList
		containers;
		
	private ArrayList
		note;
		
	private int
		message_id;
		
	public List getContainers() {
	    return containers;
	}
	public List getNotes() {
	    return note;
	}
	
	public PID()
	{
		this.containers = new ArrayList();
		this.note = new ArrayList();
	}

	public Node Parse(String line)
	{
		if(line.startsWith("PID"))
		{
			return super.Parse(line, 0, 1);
		}
		if(line.startsWith("ORC"))
		{
			PIDContainer container = new PIDContainer();
			this.containers.add(container);
			return container.Parse(line);
		}
		else if(line.startsWith("OBR"))
		{
			if(this.containers.isEmpty() || ((PIDContainer)this.containers.get(this.containers.size() -1)).HasOBR())
			{
				PIDContainer container = new PIDContainer();
				this.containers.add(container);
				return container.Parse(line);
			}
			else
			{
				return ((PIDContainer)this.containers.get(this.containers.size() -1)).Parse(line);
			}
		}
		else if(line.startsWith("NTE"))
		{
			NTE nte = new NTE();
			this.note.add(nte.Parse(line));
		}
		else
		{
			return ((PIDContainer)this.containers.get(this.containers.size() -1)).Parse(line);
		}
		System.err.println("Error During Parsing, Unknown Line - oscar.PathNet.HL7.V2_3.PID - Message: " + line);
		return null;
	}
	
	public String getNote()
	{
		String notes = "";
		int size = note.size();
		for(int i = 0; i < size; ++i )
		{
			notes += ((NTE)note.get(i)).get("comment", "");
		}
		return notes;
	}
	
	public void ToDatabase(DBHandler db, int parent) throws SQLException
	{
		db.RunSQL(this.getInsertSql(parent));
		int lastInsert = super.getLastInsertedId(db);
		int size = this.containers.size();
		for(int i = 0; i < size; ++i)
		{
			((PIDContainer)this.containers.get(i)).ToDatabase(db, lastInsert);
		}
	}
	
	protected String getInsertSql(int parent)
	{
		String fields = "INSERT INTO hl7_pid ( message_id";
		String values = "VALUES ('" + String.valueOf(parent) + "'";
		String[] properties = this.getProperties();
		for(int i = 0; i < properties.length; ++i)
		{
			fields += ", " + properties[i];
			values += ", '" + this.get(properties[i], "") + "'";
		}
		fields += ", note";
		values += ", '" + getNote() + "'";
		return fields + ") " + values + ");";
	}
	
	protected String[] getProperties()
	{
		return new String[]{
			"set_id",
			"external_id",
			"internal_id",
			"alternate_id",
			"patient_name",
			"mother_maiden_name",
			"date_of_birth",
			"sex",
			"patient_alias",
			"race",
			"patient_address",
			"country_code",
			"home_number",
			"work_number",
			"language",
			"marital_status",
			"religion",
			"patient_account_number",
			"ssn_number",
			"driver_license",
			"mother_identifier",
			"ethnic_group",
			"birth_place",
			"multiple_birth_indicator",
			"birth_order",
			"citizenship",
			"veteran_military_status",
			"nationality",
			"patient_death_date_time",
			"patient_death_indicator"
		};
	}
    /* (non-Javadoc)
     * @see oscar.oscarLabs.PathNet.HL7.Node#accept(oscar.oscarLabs.PathNet.HL7.NodeVisitor)
     */
    public void accept(NodeVisitor visitor) {
        // TODO Auto-generated method stub
        visitor.visitPID(this);
    }
}
