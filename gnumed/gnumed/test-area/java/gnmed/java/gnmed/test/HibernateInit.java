/*
 * HibernateInit.java
 *
 * Created on 23 July 2003, 10:31
 */

package gnmed.test;
import net.sf.hibernate.*;
import net.sf.hibernate.cfg.*;
import java.util.WeakHashMap;
import java.util.*;
import java.util.logging.*;

import org.gnumed.gmIdentity.*;
import org.gnumed.gmGIS.*;
import org.gnumed.gmClinical.*;
import org.drugref.*;



/**
 *
 * @author  sjtan
 */
public class HibernateInit {
    static Object lock = new Object();
    static final String SCHEMA_FLAG = "schema.has.been.exported";
    private static SessionFactory sessions;
    private static Configuration ds;
    private static WeakHashMap oldSessions = new WeakHashMap();
    
    public static SessionFactory getSessions() {
        return sessions;
    }
    
    static {
        try {
            initLogger();
        } catch (Exception e) {
            e.printStackTrace();
        }
    };
    
    static boolean preserveSession = false;
    
    public static Session openSession() throws Exception {
        if (sessions == null)
            initAll();
        
        if (preserveSession && getOneSession() != null) {
            getOneSession().reconnect();
            return getOneSession();
        }
        
        
        
        Session s =  sessions.openSession();
        
        
        
        oldSessions.put(s, new Integer(1) );
        return s;
    }
    
    public static void closeSession(Session s) throws Exception {
        if (preserveSession) {
            setOneSession(s);
            s.disconnect();
            return;
        }
        s.close();
    }
    
    public static  boolean cleanSessions() throws Exception {
        Iterator i = oldSessions.keySet().iterator();
        while (i.hasNext()) {
            Session s = (Session) i.next();
            try {
                s.close();
            } catch (Exception e) {
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
        
        
        setPreserveSession();
        
    }
    
    static void setPreserveSession() {
      preserveSession = TestProperties.properties.getProperty("session.preserved", "false").equals("true");
        
    }
    
    public static void initGmIdentity() throws Exception {
        ds.addClass(identity.class)
        .addClass(Names.class);
        
        ds.addClass( enum_social_id.class);
        ds.addClass(social_identity.class);
        
        ds.addClass(identities_addresses.class).
        addClass(address.class).
        addClass(street.class).
        addClass(state.class).
        addClass(urb.class).
        addClass(country.class).
        addClass(address_type.class);
        ds.addClass(telephone.class);
        
        ds.addClass(enum_telephone_role.class);
        
        ds.addClass(identity_role.class);
         ds.addClass(identity_role_info.class);
         
         ds.addClass(search_identity.class);
        
        
    }
    
    public static void initGmClinical() throws Exception {
        ds.        addClass(clin_health_issue.class);
        ds. addClass(enum_coding_systems.class);
        ds.   addClass(code_ref.class);
        ds.  addClass(coding_systems.class);
        ds.  addClass(clin_issue_component.class);
        ds.  addClass(clin_encounter.class);
        ds. addClass(clin_root_item.class);
        ds. addClass(enum_encounter_type.class);
        ds. addClass(curr_encounter.class);
        //      addClass(script.class).
        
        ds.  addClass(enum_allergy_type.class);
        ds. addClass(enum_hx_source.class);
        ds. addClass(enum_hx_type.class);
        ds.  addClass(clin_episode.class);
        
        ds.  addClass(script_drug.class);
        ds.  addClass(link_script_drug.class);
        ds.  addClass(script.class);
        
        ds.addClass(clin_attribute.class);
        ds. addClass(category_type.class);
        ds. addClass(category.class);
        
        
        ;
        
        ds.addClass( disease_code.class);
        ds.addClass( product.class);
        ds.addClass(drug_routes.class);
        ds.addClass(drug_element.class);
        ds.addClass(drug_units.class);
        ds.addClass(atc.class);
        ds.addClass(drug_formulations.class);
        ds.addClass(drug_warning_categories.class);
        ds.addClass(link_compound_generics.class);
        ds.addClass(package_size.class);
        ds.addClass(generic_drug_name.class);
        
        
        ds.addClass(subsidized_products.class);
        ds.addClass(subsidies.class);
    }
    //
    
    
    
    
    
    
    //        ;
    
    
    // build a SessionFactory
    
    public static void finalizeInit() throws Exception {
        sessions = ds.buildSessionFactory();
    }
    
    public static void initAll() throws Exception {
        synchronized (lock) {
            if (sessions != null)
                return;
            HibernateInit.init();
            HibernateInit.initGmIdentity();
            HibernateInit.initGmClinical();
            HibernateInit.finalizeInit();
            
            HibernateInit.exportDatabase();
        }
    }
    
    static int checkCount = 0;
    
    /** Holds value of property oneSession. */
    private static Session oneSession;
    
    private static void checkAccess() throws Exception {
        int result = javax.swing.JOptionPane.showConfirmDialog( new javax.swing.JFrame(), "ARE YOU SURE YOU WISH TO RE_INIT THE DATABASE (AND LOSE ALL CURRENT DATA) ?" , "WARNING", javax.swing.JOptionPane.YES_NO_OPTION);
        if (result == javax.swing.JOptionPane.YES_OPTION) {
            if (++checkCount < 2)
                checkAccess();
            checkCount = 0;
            return;
        }
        throw new Exception("DENIED RE-CREATION OF DATABASE");
        
        
    }
    
    public static void exportDatabase() throws Exception {
        
        //        new net.sf.hibernate.tool.hbm2ddl.SchemaExport(ds).create(true, true);
        String exported = TestProperties.properties.getProperty(SCHEMA_FLAG);
        System.out.println("****    TestProperties.exported="+exported);
        if ( exported == null ||  !exported.toLowerCase().equals("true") ) {
            checkAccess();
            
            
            // additional setup for name space problem
            
            try {
                java.sql.Connection c = sessions.openSession().connection();
                c.createStatement().execute("set session search_path = public, pg_catalog");
                c.commit();
                // c.close();
            } catch ( Exception e) {
                e.printStackTrace();
            }
            
            new net.sf.hibernate.tool.hbm2ddl.SchemaExport(ds).create(true, true);
            
            // additional setup to fit drugref database in.
            java.sql.Connection c = sessions.openSession().connection();
            c.createStatement().execute("alter table link_drug_atc add column audit_id integer");
            c.commit();
            c.close();
            return;
        }
        //        new net.sf.hibernate.tool.hbm2ddl.SchemaUpdate(ds).execute(true);
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
            TestProperties.properties.setProperty(SCHEMA_FLAG, "true");
            TestProperties.properties.save();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    /** Creates a new instance of HibernateInit */
    public HibernateInit() {
        
        
    }
    
    
    
    public static void initLogger() throws Exception {
        Map logLevels = new HashMap();
        
        logLevels.put("fine", Level.FINE);
        logLevels.put("finer", Level.FINER);
        logLevels.put("finest", Level.FINEST);
        logLevels.put("warning", Level.WARNING);
        logLevels.put("info", Level.INFO);
        logLevels.put("all", Level.ALL);
        logLevels.put("off", Level.OFF);
        if (TestProperties.properties.getProperty("logger").equals("on")) {
            System.out.println(TestProperties.properties.getProperty("logger.level"));
            System.out.println("levelMap = " + logLevels);
            Level level = (Level) logLevels.get(TestProperties.properties.getProperty("logger.level").toLowerCase());
            if (level == null)
                level = Level.ALL;
            
            Logger.global.setLevel(level);
            Handler[] h = Logger.global.getHandlers();
            
            for (int i = 0 ; i < h.length; ++i) {
                if (h[i] instanceof ConsoleHandler) {
                    System.out.println("FOUND A CONSOLE HANDLER SETTING TO LEVEL=" + level.getName());
                    h[i].setLevel(level);
                }
            }
            
            System.out.println("LOGGING SET TO " + level.getName());
            
        }    else           Logger.global.setLevel(Level.OFF);
    }
    
    
    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) {
    }
 
    /** Getter for property oneSession.
     * @return Value of property oneSession.
     *
     */
   static Session getOneSession() {
        return oneSession;
    }
    
    /** Setter for property oneSession.
     * @param oneSession New value of property oneSession.
     *
     */
    static void setOneSession(Session _oneSession) {
       oneSession = _oneSession;
    }
    
}