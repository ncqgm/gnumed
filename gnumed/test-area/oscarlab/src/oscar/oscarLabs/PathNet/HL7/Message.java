 
package oscar.oscarLabs.PathNet.HL7;
import java.sql.ResultSet;
import java.sql.SQLException;

import oscar.oscarLabs.PathNet.HL7.V2_3.MSH;
import oscar.oscarLabs.PathNet.HL7.V2_3.PID;
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
public class Message
{
    private static final String lineBreak = "\n",
		insert =
			"INSERT INTO hl7_message ( date_time ) VALUES ( '@date_time' );";
	private String now;
	private PID pid = null;
	private MSH msh = null;
	private Node current;
	public Message(String now)
	{
		this.now = now;
		this.current = null;
	}
	public void Parse(String data)
	{
		String[] lines = data.split(lineBreak);
		int count = lines.length;
		for (int i = 0; i < count; ++i)
		{
			if (lines[i].startsWith("MSH"))
			{
				this.msh = new MSH();
				current = this.msh.Parse(lines[i]);
			}
			else if (lines[i].startsWith("PID"))
			{
				this.pid = new PID();
				current = this.pid.Parse(lines[i]);
			}
			else if (lines[i].startsWith("NTE"))
			{
				if (current != null)
				{
					current.Parse(lines[i]);
				}
			} else if (lines[i].startsWith("PV1")) {
			    //don't choke , ignore
			}
			else if (this.pid != null)
			{
				current = this.pid.Parse(lines[i]);
			}
		}
	}
	public String toString()
	{
		return pid.toString();
	}
	
	public String getDumpString() 
	{
	    return pid.toString();
	}
	
	protected String getSql()
	{
		return insert.replaceAll("@date_time", this.now);
	}
	private String getLastInsertedIdSql()
	{
		return "SELECT LAST_INSERT_ID();";
	}
	public void ToDatabase(DBHandler db) throws SQLException
	{
		db.RunSQL(this.getSql());
		ResultSet result = db.GetSQL(this.getLastInsertedIdSql());
		int parent = 0;
		if (result.next())
		{
			parent = result.getInt(1);
		}
		if (parent == 0)
			throw new SQLException("Could not get last inserted id");
		msh.ToDatabase(db, parent);
		pid.ToDatabase(db, parent);
	}
	
	public PID getPID() {
	    
	    return pid;
	}
	
	public MSH getMSH() {
	    return msh;
	}
}
