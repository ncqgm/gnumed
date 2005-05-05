package oscar.oscarLabs.PathNet;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;

import oscar.Properties;
import oscar.oscarLabs.PathNet.HL7.Message;
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
public class Controller implements Runnable
{
	private oscar.oscarLabs.PathNet.Connection connection;
	private static boolean run;
	public Controller()
	{
		run = Boolean.getBoolean(Properties.getProperty(Properties.PathNetRun, "false"));
		connection = new oscar.oscarLabs.PathNet.Connection();
		System.err.println("Information - oscar.PathNet.Controller - Message: Thread Running " + run);
	}
	public void run()
	{
		while (run)
		{
			String username =
				Properties.getProperty(Properties.PathNetUsername);
			String password =
				Properties.getProperty(Properties.PathNetPassword);
			if (connection.Open(username, password))
			{
				ArrayList messages = connection.Retrieve();
				if (messages != null)
				{
					boolean success = true;
					try
					{
						int size = messages.size();
						DBHandler db = new DBHandler();
						String now =
							new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(
								new Date());
						for (int i = 0; i < size; i++)
						{
							Message message = new Message(now);
							message.Parse((String) messages.get(i));
							message.ToDatabase(db);
						}
						db.CloseConn();
					}
					catch (Exception ex)
					{
						//success = false; //<- for future when transactional
						System.err.println(
							"Error - oscar.PathNet.Contorller - Message: "
								+ ex.getMessage()
								+ " = "
								+ ex.toString());
					}
					connection.Acknowledge(success);
				}
				connection.Close();
			}
			long sleep =
				Long.parseLong(Properties.getProperty(Properties.PathNetSleep))
					* 60000;
			try
			{
				Thread.sleep(sleep);
			}
			catch (Exception ex)
			{
				System.err.println(
					"Thread has failed to sleep. Thread will end until error corrected and restarted - oscar.PathNet.Controller - Message: "
						+ ex.getMessage());
				run = false;
			}
		}
	}
	public static void setRun(boolean keepRunning)
	{
		run = keepRunning;
	}
}
