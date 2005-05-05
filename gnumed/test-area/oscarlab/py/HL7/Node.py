 
"""
below is the copyright of the original code.

package oscar.oscarLabs.PathNet.HL7
Class Node

/* 
 *
 * 
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
 """
import string, sys
class  Node:
	def accept(self, visitor):
		pass
	
	def getProperties(self):
		return []
	

	def __init__(self):
		self.__data = {}
		
	def get(self, key, defaultValue ):
		return self._prepareString( self.__data.get(key, defaultValue) )

	def Parse( self, line, propertiesIndex = -1, fieldsIndex  = -1):
		if propertiesIndex == -1 and fieldsIndex == -1:
			return self

		fields = line.split("|")
		properties = self.getProperties()
		for i in xrange(0, len(fields) - fieldsIndex):
			try:
				
				self.__data[properties[propertiesIndex + i]] = fields[fieldsIndex+i]
			except:
				print "ERROR IN SETTING DATA"
				print "i=", i, "propertiesIndex=", propertiesIndex, "fieldsIndex=", fieldsIndex
				print "properties =", properties
				print "fields = ", fields
				import traceback
				traceback.print_tb(sys.exc_info()[2])

			
		return self

	def _prepareString(self,s):
		if not s:
			s=""
		s = string.replace(s, "\\\\", "\\\\\\\\")
		s= string.replace(s, "\\\'", "\\\\\'")
		s =string .replace(s, "\\^", " ")
		return s
	
	


    	""" translated from
	protected Hashtable data;
	private static final String last_insert_id = "SELECT LAST_INSERT_ID();";
	protected abstract String[] getProperties();
	public abstract void ToDatabase(DBHandler db, int parent)
		throws SQLException;
	public abstract Node Parse(String line);
	protected abstract String getInsertSql(int parent);
	protected int getLastInsertedId(DBHandler db) throws SQLException
	{
		ResultSet result = db.GetSQL(last_insert_id);
		int parent = 0;
		if (result.next())
		{
			parent = result.getInt(1);
		}
		if (parent == 0)
			throw new SQLException("Could not get last inserted id");
		return parent;
	}
	
	public String get(String key, String defaultValue)
	{
		return this.prepareString(
			this.data.containsKey(key)
				? (String) this.data.get(key)
				: defaultValue);
	}
	protected Node Parse(String line, int propertiesIndex, int fieldsIndex)
	{
		String[] fields = line.split("\\|");
		this.data = new Hashtable(fields.length);
		String[] properties = this.getProperties();
		int count = fields.length;
		for (int i = 0;(fieldsIndex + i) < count; i++)
		{
			this.data.put(
				properties[propertiesIndex + i],
				fields[fieldsIndex + i]);
		}
		return this;
	}
	private String prepareString(String str)
	{
		return str
			.replaceAll("\\\\", "\\\\\\\\")
			.replaceAll("\\\'", "\\\\\'")
			.replaceAll("\\^", " ");
	}
	protected void getInsertFieldsAndValues(String fields, String values)
	{
		String[] properties = this.getProperties();
		for (int i = 0; i < properties.length; ++i)
		{
			fields += ", " + properties[i];
			values += ", '" + this.get(properties[i], "") + "'";
		}
	}
	"""
