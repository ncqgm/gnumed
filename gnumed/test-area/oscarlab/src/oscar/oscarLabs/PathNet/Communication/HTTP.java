 
package oscar.oscarLabs.PathNet.Communication;
import java.io.IOException;
import java.io.InputStream;

import org.apache.commons.httpclient.HttpClient;
import org.apache.commons.httpclient.HttpException;
import org.apache.commons.httpclient.methods.GetMethod;
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
public class HTTP
{
	private String url;
	private HttpClient client;
	public HTTP(String url)
	{
		this.url = url;
		this.client = new HttpClient();
	}
	public InputStream Get(String queryString)
		throws IOException, HttpException
	{
		GetMethod method = new GetMethod(url);
		method.setQueryString(queryString);
		System.err.println(this.client.executeMethod(method));
		method.getResponseBodyAsString();
		InputStream response = method.getResponseBodyAsStream();
		method.releaseConnection();
		return response;
	}
	public String GetString(String queryString)
		throws IOException, HttpException
	{
		GetMethod method = new GetMethod(url);
		method.setQueryString(queryString);
		this.client.executeMethod(method);
		String response = method.getResponseBodyAsString();
		method.releaseConnection();
		return response;
	}
}
