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
    
    public static Session openSession() throws Exception {
        if (sessions == null) 
            initAll();
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
       
        
        
    }
    
    public static void initGmClinical() throws Exception {
        ds.
        addClass(clin_health_issue.class).
        addClass(enum_coding_systems.class).
        addClass(code_ref.class).
        addClass(coding_systems.class).
        addClass(clin_issue_component.class) .
        addClass(clin_encounter.class).
        addClass(clin_root_item.class).
        addClass(enum_encounter_type.class).
        addClass(curr_encounter.class).
  //      addClass(script.class).
        
        addClass(enum_allergy_type.class).
        addClass(enum_hx_source.class).
        addClass(enum_hx_type.class).
        addClass(clin_episode.class).
        
        addClass(script_drug.class).
        addClass(link_script_drug.class).
        addClass(script.class);
        
        ds.addClass(clin_attribute.class).
        addClass(category_type.class).
        addClass(category.class)
        
        
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
        
    }
    //
    
    
    
    
    
    
    //        ;
    
    
    // build a SessionFactory
    
    public static void finalizeInit() throws Exception {
        sessions = ds.buildSessionFactory();
    }
    
    public static void initAll() throws Exception {
        HibernateInit.init();
        HibernateInit.initGmIdentity();
        HibernateInit.initGmClinical();
        HibernateInit.finalizeInit();
        
        HibernateInit.exportDatabase();
    }
    
    private static void checkAccess() throws Exception {
        int result = javax.swing.JOptionPane.showConfirmDialog( null, "ARE YOU SURE YOU WISH TO RE_INIT THE DATABASE (AND LOSE ALL CURRENT DATA) ?" , "WARNING", javax.swing.JOptionPane.YES_NO_OPTION);
        if (result == javax.swing.JOptionPane.YES_OPTION) {
            checkAccess();
            return;
        }
        throw new Exception("DENIED RE-CREATION OF DATABASE");
        
            
    }
    
    public static void exportDatabase() throws Exception {
        //        new net.sf.hibernate.tool.hbm2ddl.SchemaExport(ds).create(true, true);
        String exported = TestProperties.properties.getProperty(SCHEMA_FLAG);
        System.out.println("****    TestProperties.exported="+exported);
        if ( exported == null ||  !exported.toLowerCase().equals("true") )
        {
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
        if (TestProperties.properties.getProperty("logger").equals("on"))
            Logger.global.setLevel(Level.ALL);
        else
            Logger.global.setLevel(Level.OFF);
    }
    
    
    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) {
    }
    
}
