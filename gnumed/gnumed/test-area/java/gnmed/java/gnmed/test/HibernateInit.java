/*
 * HibernateInit.java
 *
 * Created on 23 July 2003, 10:31
 */

package gnmed.test;
import net.sf.hibernate.*;
import net.sf.hibernate.cfg.*;

import org.gnumed.gmIdentity.*;
import org.gnumed.gmGIS.*;
import org.gnumed.gmClinical.*;
import java.util.WeakHashMap;
import java.util.*;
/**
 *
 * @author  sjtan
 */
public class HibernateInit {
    private static SessionFactory sessions;
    private static Configuration ds;
    private static WeakHashMap oldSessions = new WeakHashMap();
    public static SessionFactory getSessions() {
        return sessions;
    }
    
    public static Session openSession() throws Exception {
        Session s =  sessions.openSession();
        oldSessions.put(s, new Integer(1) );
        return s;
    }
    
    public static  boolean cleanSessions() throws Exception {
        Iterator i = oldSessions.keySet().iterator();
        while (i.hasNext()) {
            Session s = (Session) i.next();
            if (s.isConnected()) {
                s.close();
            }
        }
        oldSessions.clear();
        return true;
    }
    
    public static Configuration getConfiguration() {
        return ds;
    }
    
    public static void initGmIdentityOnly() throws Exception {
        init();
        initGmIdentity();
        finalizeInit();
    }
    
    public static void init() throws Exception {
        
        // configure the Configuration
        
        ds = new Configuration();
        
    }
    
    public static void initGmIdentity() throws Exception {
        ds.addClass(identity.class)
        .addClass(Names.class).
        addClass(identities_addresses.class).
        addClass(address.class).
        addClass(street.class).
        addClass(state.class).
        addClass(urb.class).
        addClass(country.class).
        addClass(address_type.class);
    }
    
    //        ds.
    //        addClass(clin_health_issue.class).
    //        addClass(clin_issue_component.class).
    //
    //        addClass(clin_encounter.class).
    //        addClass(clin_root_item.class).
    //        addClass(clin_episode.class).
    //        addClass(enum_encounter_type.class).
    //        addClass(enum_allergy_type.class).
    //        addClass(enum_hx_source.class).
    //        addClass(enum_hx_type.class).
    //        addClass(enum_coding_systems.class).
    //        addClass(curr_encounter.class).
    //        addClass(script.class).
    //        addClass(code_ref.class).
    //        addClass(coding_systems.class)
    //        ;
    
    
    // build a SessionFactory
    
    public static void finalizeInit() throws Exception {
        sessions = ds.buildSessionFactory();
    }
    
    public static void exportDatabase() throws Exception {
//        new net.sf.hibernate.tool.hbm2ddl.SchemaExport(ds).create(true, true);
        String exported = TestProperties.properties.getProperty("exported");
        System.out.println("****    TestProperties.exported="+exported);
        if ( exported == null || exported.toLowerCase().equals("false")
        || exported.trim().length() == 0)
            new net.sf.hibernate.tool.hbm2ddl.SchemaExport(ds).create(true, true);
        //        if ( TestProperties.prop.getProperty("exported" ).equals(null) ||
        //        TestProperties.prop.getProperty("exported", "false").equals("false")) {
        //            new net.sf.hibernate.tool.hbm2ddl.SchemaExport(ds).drop(true, true);
        //            new net.sf.hibernate.tool.hbm2ddl.SchemaExport(ds).create(true, true);
        //            TestProperties.prop.setProperty("exported", "true");
        //            TestProperties.prop.save();
        //            return;
        //        }
        //        try {
        //        //    new net.sf.hibernate.tool.hbm2ddl.SchemaUpdate(ds).execute(true);
        //        } catch (Exception e) {
        //            e.printStackTrace();
        //        }
        //
        //
    }
    
    public static void setExported(boolean exported) {
        try {
            String val = exported ? "true" : "false";
            TestProperties.properties.setProperty("exported", "true");
            TestProperties.properties.save();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    /** Creates a new instance of HibernateInit */
    public HibernateInit() {
        
        
    }
    
    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) {
    }
    
}
