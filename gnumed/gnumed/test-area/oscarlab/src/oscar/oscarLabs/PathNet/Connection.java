 
package oscar.oscarLabs.PathNet;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;

import org.apache.commons.httpclient.HttpException;
import org.w3c.dom.Document;
import org.xml.sax.SAXException;

import oscar.Properties;
import oscar.oscarLabs.PathNet.Communication.HTTP;
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
public class Connection
{
	private boolean secure;
	private String url;
	private static final String LoginQuery =
		"Page=Login&Mode=Silent&UserID=@username&Password=@password",
		RequestNewQuery = "Page=HL7&Query=NewRequests",
		RequestNewPendingQuery = "Page=HL7&Query=NewRequests&Pending=Yes",
		PositiveAckQuery = "Page=HL7&ACK=Positive",
		NegativeAckQuery = "Page=HL7&ACK=Negative",
		LogoutQuery = "Logout=Yes";
	private HTTP http;
	public Connection()
	{
		this.url = Properties.getProperty(Properties.PathNetUrl);
		this.http = new HTTP(this.url);
	}
	public boolean Open(String username, String password)
	{
		boolean success = true;
		try
		{
			String response =
				this.CreateString(
					LoginQuery.replaceAll("@username", username).replaceAll(
						"@password",
						password));
			success = (response.toUpperCase().indexOf("ACCESSGRANTED") > -1);
		}
		catch (Exception ex)
		{
			System.err.println(
				"Error - oscar.PathNet.Connection.Open - Message: "
					+ ex.getMessage());
			success = false;
		}
		return success;
	}
	public void Close()
	{
		try
		{
			this.CreateInputStream(LogoutQuery).close();
		}
		catch (Exception ex)
		{
			System.err.println(
				"Error - oscar.PathNet.Connection.Close - Message: "
					+ ex.getMessage());
		}
	}
	public ArrayList Retrieve()
	{
		ArrayList messages = null;
		try
		{
			System.err.println("retrieving");
			Document document =
				this.CreateDocument(this.CreateInputStream(RequestNewQuery));
			if (document
				.getDocumentElement()
				.getAttribute("MessageFormat")
				.toUpperCase()
				.equals("ORUR01")
				&& document
					.getDocumentElement()
					.getAttribute("Version")
					.toUpperCase()
					.equals(
					"2.3"))
			{
				if (document
					.getDocumentElement()
					.getAttribute("MessageCount")
					.equals(
						String.valueOf(
							document
								.getDocumentElement()
								.getChildNodes()
								.getLength())))
				{
					messages =
						new ArrayList(
							document
								.getDocumentElement()
								.getChildNodes()
								.getLength());
					for (int i = 0;
						i
							< document
								.getDocumentElement()
								.getChildNodes()
								.getLength();
						i++)
					{
						System.err.println("messages : " + i);
						messages.add(
							document
								.getDocumentElement()
								.getChildNodes()
								.item(i)
								.getFirstChild()
								.getNodeValue());
					}
				}
				else
				{
					this.Acknowledge(false);
				}
			}
		}
		catch (Exception ex)
		{
			System.err.println(
				"Error - oscar.PathNet.Connection.Retrieve - Message: "
					+ ex.getMessage());
		}
		return messages;
	}
	public void Acknowledge(boolean success)
	{
		try
		{
			this
				.CreateInputStream(
					(success ? PositiveAckQuery : NegativeAckQuery))
				.close();
		}
		catch (Exception ex)
		{
			System.err.println(
				"Error - oscar.PathNet.Connection.Acknowledge - Message: "
					+ ex.getMessage());
		}
	}
	private Document CreateDocument(InputStream input)
		throws SAXException, IOException, ParserConfigurationException
	{
		DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
		DocumentBuilder builder = factory.newDocumentBuilder();
		return builder.parse(input);
	}
	private InputStream CreateInputStream(String queryString)
		throws HttpException, IOException
	{
		return this.http.Get(queryString);
	}
	private String CreateString(String queryString)
		throws HttpException, IOException
	{
		return this.http.GetString(queryString);
	}
}
