/*
 * IdentityManager.java
 *
 * Created on 5 August 2003, 11:02
 */

package quickmed.usecases.test;
import java.util.*;
import java.util.logging.*;

import net.sf.hibernate.*;
import net.sf.hibernate.type.*;
import junit.framework.*;


import org.drugref.*;
import org.gnumed.gmIdentity.*;
import org.gnumed.gmClinical.*;
/**
 *
 * @author  sjtan
 */
public class IdentityManager {
    static IdentityManager manager;
    static {
        manager = new IdentityManager();
    }
    
    public static IdentityManager instance() {
        return manager;
    }
    
    /** Creates a new instance of IdentityManager */
     IdentityManager() {
    }
    
    public void save(identity identity) {
        try {
           Session sess =  gnmed.test.HibernateInit.openSession();
           if (identity.getId() == null)
             sess.save(identity);
           else
               sess.saveOrUpdate(identity);
           sess.flush();
           sess.connection().commit();
           sess.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    public List findIdentityByNames( String lastnames, String firstnames) throws Exception {
         Session sess =  gnmed.test.HibernateInit.openSession();
         List l = sess.find("select i from identity i inner join identity.Namess n " +
                            "where lower(n.lastnames) like ? and lower(n.firstnames) like ?" , 
            new Object[] { lastnames.toLowerCase()+"%", firstnames.toLowerCase() +"%" },
            new Type[] { Hibernate.STRING , Hibernate.STRING } );
            
        sess.close();
        return l;
    }
    
}
