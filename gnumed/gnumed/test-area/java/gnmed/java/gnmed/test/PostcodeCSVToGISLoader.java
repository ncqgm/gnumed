/*
 * PostcodeCSVToGISLoader.java
 *
 * Created on 24 July 2003, 12:09
 */

package gnmed.test;

import java.io.*;
import java.util.*;

import net.sf.hibernate.*;
import net.sf.hibernate.type.Type;
import org.gnumed.gmGIS.*;
import java.util.logging.*;
/**
 *
 * @author  sjtan
 */
public class PostcodeCSVToGISLoader {
    
    /** Creates a new instance of PostcodeCSVToGISLoader */
    public PostcodeCSVToGISLoader()  throws Exception {
        checkLogging();
        if (HibernateInit.getSessions() == null)
            HibernateInit.initGmIdentityOnly();
    }
    
    
    
    public static String filename="postcodes.au.csv";
    static String PCODE = "Pcode";
    static String STATE="State";
    static String URB = "Locality";
    static String CAT="Category";
    static String SUB="Delivery Area";
    static String COUNTRY="Australia";
    
    static Map stateMap = new TreeMap();
    
    static {
        stateMap.put("WA",  "Western Australia");
        stateMap.put("VIC", "Victoria");
        stateMap.put("SA", "South Australia");
        stateMap.put("QLD", "Queensland");
        stateMap.put("TAS", "Tasmania");
        stateMap.put("NSW", "New South Wales");
        stateMap.put("NT", "Northern Territory");
        stateMap.put("ACT", "Australian Capital Territory");
    };
    int count = 0;
    int cycle = 10;
    
    Session session;
    country country;
    BufferedReader r;
    String[] headings;
    Map headMap = new HashMap();
    Map suburbCache = new HashMap();
    Map stateCache = new HashMap();
    void initFile() throws Exception {
        Properties p = new Properties();
        File f = new File(".");
        for (int i = 0; i < f.listFiles().length; ++i) {
            System.out.println(f.listFiles()[i]);
        }
        System.out.println(f.listFiles());
        p.load( new BufferedInputStream(new FileInputStream("gnmed-test.properties")));
        if (p.getProperty("postcode.csv.path", null) != null)
            filename = p.getProperty("postcode.csv.path");
        r = new BufferedReader( new FileReader(filename));
    }
    
    void readBatchFlushSize() throws Exception {
        cycle = Integer.parseInt( TestProperties.properties.getProperty("postcode.batch.flush.size"));
    }
    
    void readHeadings() throws Exception {
        headings = readLine();
        if (headings == null)
            throw new Exception("No headings found");
        
        for (int i = 0; i < headings.length; ++i) {
            headMap.put( headings[i].trim(), new Integer(i));
            
        }
    }
    
    public Map getHeadMap() {
        return headMap;
    }
    
    public boolean hasHeading(String key) {
        return headMap.containsKey(key);
        
    }
    
    public void showHeadings() {
        showList((String[])headMap.keySet().toArray( new String[0]));
    }
    
    /**
     *reads a comma separated line and splits it into tokens
     */
    String[] readRawLine() throws Exception {
        String line = r.readLine();
        if (line == null)
            return null;
        return line.split(",");
    }
    
    /**
     *reads a comma separated line, and returns unquoted tokens.
     */
    String[] readLine() throws Exception {
        String[] headings = readRawLine();
        if (headings == null)
            return headings;
        for (int i = 0; i < headings.length; ++i)
            headings[i]=removeSurroundingQuotes(headings[i]);
        
        
        return headings;
    }
    
    int getIndex( String heading) {
        // System.err.println("Looking for heading " + heading);
        return  ((Integer)headMap.get(heading)).intValue();
    }
    
    
    String removeSurroundingQuotes(String s) {
        if (s.indexOf('"') < 0)
            return s;
        return  s.substring(s.indexOf('"')+1, s.lastIndexOf('"'));
    }
    
    String[] readAndParseLine() throws Exception {
        String[] toks = readLine();
        Logger.global.info("read tokens " + showList(toks));
        if (toks == null)
            return null;
        String type = toks[getIndex(CAT)];
        if (!type.trim().equals(SUB)) {
            showList(toks);
            return readAndParseLine();
        }
        String pcodeStr = toks[ getIndex(PCODE) ];
        String urbStr = toks[getIndex(URB)];
        String stateStr = toks[getIndex(STATE)];
        String[] result= new String[] { pcodeStr, urbStr, stateStr };
        Logger.global.info("Using after parsing " + showList(result));
        return result;
    }
    
    String showList(String[] list) {
        if (list == null)
            return null;
        StringBuffer b = new StringBuffer();
        for (int i = 0; i < list.length; ++i) {
            b.append(list[i]);
            b.append("  ");
        }
        // System.out.println(b.toString());
        return b.toString();
    }
    
    urb findSuburb( String pcode, String urb ) throws Exception {
        urb u = (urb) suburbCache.get(pcode+urb);
        if (u != null)
            return u;
        Session s = HibernateInit.getSessions().openSession();
        List l = s .find("from u in class org.gnumed.gmGIS.urb where u.name = ? and u.postcode = ?",
        new String[] { urb, pcode }, new Type[] { Hibernate.STRING,Hibernate.STRING }) ;
        s.connection().commit();
        HibernateInit.closeSession(s);
        if (l.size() == 1) {
            suburbCache.put(pcode+urb, l.get(0));
            return (urb) l.get(0);
        }
        return null;
    }
    
    void initCountry() throws Exception {
        Session s = HibernateInit.openSession();
        List l = s.find("from c in class org.gnumed.gmGIS.country where c.name = ?", COUNTRY, Hibernate.STRING);
        if (l.size() != 0) {
            country = (country) l.get(0);
            return;
        }
        country = new country();
        country.setName(COUNTRY);
        s .save(country);
        s.flush();
        s.connection().commit();
        HibernateInit.closeSession(s);
    }
    
    state findState( String code) throws Exception {
        state state = (state) stateCache.get(code);
        if (state != null)
            return state;
        Session s = HibernateInit.openSession();
        List l  = s .find("from s in class org.gnumed.gmGIS.state where s.code = ?", code, Hibernate.STRING);
        s.connection().commit();
       HibernateInit.closeSession(s);
        state = l.size() > 0 ? (state) l.get(0) : null;
        stateCache.put( code, state);
        return state;
    }
    
    void initSession() throws Exception {
        HibernateInit.cleanSessions();
        session = HibernateInit.openSession();
        
    }
    void save(Object o) throws Exception {
        if (count % cycle == 0)
            initSession();
        session.save(o);
        if (++count % cycle == 0)
            endSession();
    }
    
    void endSession() throws Exception {
        session.flush();
        session.connection().commit();
        HibernateInit.closeSession(session);
    }
    
    void loadOrCreateStates() throws Exception {
        Session session = HibernateInit.openSession();
        Iterator i = stateMap.keySet().iterator();
        while (i.hasNext()) {
            String code = (String) i.next();
            if (findState( code) != null)
                continue;
            state s = new state();
            s.setCode(code);
            s.setName((String) stateMap.get(code));
            s.setCountry(country);
            session.save(s);
        }
        
        session.flush();
        session.connection().commit();
        HibernateInit.closeSession(session);
    }
    
    /**
     * preCondition: States loaded
     */
    urb createSuburbFromLine(String[] info) throws Exception {
        try {
            
            if (info == null)
                return null;
            Logger.global.info("Searching " + info[0] + " " + info[1]);
            urb u = findSuburb( info[0], info[1] );
            
            if (u != null) {
                Logger.global.info("Not SAVING: Found for object" + info[0] + " " + info[1]  );
                return u;
            }
            
            u = new urb();
            u.setName(info[1]);
            u.setPostcode(info[0]);
            state s = findState( info[2] );
            u.setState(s);
            Logger.global.info("** Trying to  save " + u.getName() + " " + u.getPostcode());
            save(u);
            
            return u;
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }
    
    void loopAndSaveObjects() throws Exception {
        String[] info;
        int k = 0;
        while ( (info=readAndParseLine()) != null) {
            urb u = createSuburbFromLine(info) ;
            
            if ( ++k % 100 == 0)
                System.out.println(".." + k);
            
        }
    }
    void checkLogging() {
        if (TestProperties.properties.getProperty("logger","").equals("off"))
            Logger.global.setLevel(Level.OFF);
        else
            Logger.global.setLevel(Level.ALL);
    }
    
    public void load() throws Exception {
        checkLogging();
        initFile();
        
        readHeadings();
        
        //        initSession();
        initCountry();
        //        endSession();
        
        //        initSession();
        loadOrCreateStates();
        //        endSession();
        
        //        initSession();
        readBatchFlushSize();
        loopAndSaveObjects();
        //        endSession();
        
        HibernateInit.setExported(true);
    }
    
    
    
    
    
}
