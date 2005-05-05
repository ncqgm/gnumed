


"""replaces this code:
	
/*
 * Created on 08-Mar-2005
 *
 * TODO To change the template for this generated file go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
package oscar.oscarLabs.PathNet.HL7;

import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;

import org.w3c.dom.Document;
import org.xml.sax.SAXException;

/**
 * @author sjtan
 *
 * TODO To change the template for this generated type comment go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
public class DocumentUtil {
    private Document CreateDocument(InputStream input)
	throws SAXException, IOException, ParserConfigurationException
{
	DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
	DocumentBuilder builder = factory.newDocumentBuilder();
	return builder.parse(input);
}
    public List   parseXML(InputStream is) {
	ArrayList messages = null;
	try
	{
		System.err.println("retrieving");
		Document document =
			this.CreateDocument(is);
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
				throw new Exception("Message Count differs.");
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
}
"""

from xml.dom.minidom import parse
import sys

def parseXML(filename):
	dom = parse(filename)
	l = [node.firstChild.nodeValue for node in dom.documentElement.childNodes]
	return l	

if __name__== "__main__":
	l = parseXML(sys.argv[1])
	for x in l:
		print x
		print "-"* 100
