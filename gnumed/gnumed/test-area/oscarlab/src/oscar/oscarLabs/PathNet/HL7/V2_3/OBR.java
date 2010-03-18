 
package oscar.oscarLabs.PathNet.HL7.V2_3;

import java.sql.ResultSet;
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
public class OBR extends oscar.oscarLabs.PathNet.HL7.Node
{
	
	private static final String
		select = "SELECT hl7_obr.obr_id FROM hl7_obr WHERE hl7_obr.filler_order_number='@filler_no'";

	private ArrayList 
		obxs,
		note;
	
	public List getOBXS() {
	    return obxs;
	    
	}
	
	public List getNotes() {
	    return note;
	}

	public OBR()
	{
		super();
		this.obxs = new ArrayList();
		this.note = new ArrayList();
	}

	public Node Parse(String line)
	{
		if(line.startsWith("OBR"))
		{
			return super.Parse(line, 0, 1);
		}
		else if(line.startsWith("OBX"))
		{
			OBX obx = new OBX();
			this.obxs.add(obx);
			obx.Parse(line);
			return this;
		}
		else if(line.startsWith("NTE"))
		{
			NTE nte = new NTE();
			this.note.add(nte);
			nte.Parse(line);
			return this;
		}
		System.err.println("Error During Parsing, Unknown Line - oscar.PathNet.HL7.V2_3.OBR - Message: " + line);
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
	
	public void ToDatabase(DBHandler db, int parent)throws SQLException
	{
		if(this.get("result_status", "").equalsIgnoreCase("A") || this.get("result_status", "").equalsIgnoreCase("F"))
		{
			int index = getLastUpdated(db, this.get("filler_order_number", ""));
			if(index != 0)
			{
				db.RunSQL(this.getUpdateSql(this.get("filler_order_number", "")));
			}
			else
			{
				db.RunSQL(this.getInsertSql(parent));
				index = super.getLastInsertedId(db);
			}
			int size = this.obxs.size();
			for(int i = 0; i < size; ++i)
			{
				((OBX)obxs.get(i)).ToDatabase(db, index);
			}
		}
		else if(this.get("result_status", "").equalsIgnoreCase("I"))
		{
			db.RunSQL(this.getInsertSql(parent));
			int lastInsert = super.getLastInsertedId(db);
			int size = this.obxs.size();
			for(int i = 0; i < size; ++i)
			{
				((OBX)obxs.get(i)).ToDatabase(db, lastInsert);
			}
		}
		else if(this.get("result_status", "").equalsIgnoreCase("C"))
		{
			db.RunSQL(this.getUpdateSql(this.get("filler_order_number", "")));
			int lastUpdate = this.getLastUpdated(db, this.get("filler_order_number", ""));
			int size = this.obxs.size();
			for(int i = 0; i < size; ++i)
			{
				((OBX)obxs.get(i)).setUpdate(true);
				((OBX)obxs.get(i)).ToDatabase(db, lastUpdate);
			}
		}
	}
	
	protected int getLastUpdated(DBHandler db, String id)throws SQLException
	{
		ResultSet result = db.GetSQL("SELECT obr_id FROM hl7_obr WHERE filler_order_number='" + id +"'");
		int parent = 0;
		if(result.next())
		{
			parent = result.getInt(1);
		}
		return parent;
	}
	
	protected String getInsertSql(int parent)
	{
		String fields = "INSERT INTO hl7_obr ( pid_id";
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

	protected String getUpdateSql(String id)
	{
		String sql = "UPDATE hl7_obr SET" ;
		String[] properties = this.getProperties();
		for(int i = 0; i < properties.length; ++i)
		{
			sql += " " + properties[i] + "='" + get(properties[i], "") + "',";
		}
		sql += "note='" + getNote() + "' WHERE filler_order_number='" + id + "'";
		return sql;
	}

	protected String[] getProperties()
	{
		return new String[] {
			"set_id",
			"placer_order_number",
			"filler_order_number",
			"universal_service_id",
			"priority",
			"requested_date_time",
			"observation_date_time",
			"observation_end_date_time",
			"collection_volume",
			"collector_identifier",
			"specimen_action_code",
			"danger_code",
			"relevant_clinical_info",
			"specimen_received_date_time",
			"specimen_source",
			"ordering_provider",
			"order_callback_phone_number",
			"placers_field1",
			"palcers_field2",
			"filler_field1",
			"filler_field2",
			"results_report_status_change",
			"charge_to_practice",
			"diagnostic_service_sect_id",
			"result_status",
			"parent_result",
			"quantity_timing",
			"result_copies_to",
			"parent_number",
			"transportation_mode",
			"reason_for_study",
			"principal_result_interpreter",
			"assistant_result_interpreter",
			"technician",
			"transcriptionist",
			"scheduled_date_time",
			"number_of_sample_containers",
			"transport_logistics_of_collected_sample",
			"collector_comment",
			"transport_arrangement_responsibility",
			"transport_arranged",
			"escort_required",
			"planned_patient_transport_comment" };
	}

    /* (non-Javadoc)
     * @see oscar.oscarLabs.PathNet.HL7.Node#accept(oscar.oscarLabs.PathNet.HL7.NodeVisitor)
     */
    public void accept(NodeVisitor visitor) {
        // TODO Auto-generated method stub
        visitor.visitOBR(this);
    }
}
