/*
 * Created on 05-Mar-2005
 *
 * TODO To change the template for this generated file go to
 * Window - Preferences - Java - Code Style - Code Templates
 */

package test;

import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStreamReader;
import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Iterator;
import java.util.List;

import oscar.oscarLabs.PathNet.HL7.DebugNodeVisitor;
import oscar.oscarLabs.PathNet.HL7.DocumentUtil;
import oscar.oscarLabs.PathNet.HL7.Message;
import oscar.oscarLabs.PathNet.HL7.NodeVisitor;

/**
 * @author sjtan
 * 
 * TODO To change the template for this generated type comment go to Window -
 * Preferences - Java - Code Style - Code Templates
 */
public class TestDriver {
    static String FILENAME = "2001-09-21 17-56.HL7";

    public static void main(String[] args) throws IOException {
        if (args.length > 0) {
            FILENAME = args[0];
          
        } 
        TestDriver driver = new TestDriver();
        if (FILENAME.endsWith("xml") ) {
       
            List messages = new DocumentUtil().parseXML(new FileInputStream(FILENAME));
            Iterator i = messages.iterator();
            while (i.hasNext()) {
                String msg = (String) i.next();
                List m = Arrays.asList(msg.split("\n"));
                driver.printMessages(driver.getMessages(m));
            }
                
            
        } else {
            driver.run();
        }
    }

    public void run() throws IOException {
        List l = new ArrayList();
        FileInputStream fileInputStream = new FileInputStream(FILENAME);
        BufferedReader reader = new BufferedReader(new InputStreamReader(
                fileInputStream));
        String line = reader.readLine();
        ArrayList lines = new ArrayList();
        while (line != null) {
             lines.add(line);
            line = reader.readLine();
        }
        
        ArrayList messages = getMessages(lines);

        printMessages(messages);

    }

    /**
     * @param lines
     * @return
     */
    private ArrayList getMessages(List lines) {
        StringBuffer sb = new StringBuffer();
        ArrayList messages = new ArrayList();

        Iterator i = lines.iterator();
        while (i.hasNext()) {
            String aline = (String) i.next();
            if (aline.startsWith("MSH")) {
                Message m = new Message(new Timestamp(System
                        .currentTimeMillis()).toLocaleString());
                String messageString = sb.toString();
                m.Parse(messageString);

                messages.add(m);
                sb = new StringBuffer();
            }
            sb.append(aline);
            
            sb.append("\n");
        }

        Message m = new Message(new Timestamp(System.currentTimeMillis())
                .toLocaleString());

        System.err.println("read data \n" + sb.toString());
        m.Parse(sb.toString());
        messages.add(m);
        return messages;
    }

    /**
     * @param messages
     */
    public void printMessages(List messages) {
        NodeVisitor visitor = new DebugNodeVisitor();
        Iterator i = messages.iterator();
        while (i.hasNext()) {
            Message message = (Message) i.next();
            if (message.getMSH() != null)
                message.getMSH().accept(visitor);
            if (message.getPID() != null)
                message.getPID().accept(visitor);
            System.err.println("---------------------");
        }
    }
}
