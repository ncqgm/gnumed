/*
 * TestGmGIS.java
 *
 * Created on 25 July 2003, 00:11
 */

package gnmed.test;

import junit.framework.*;
import org.gnumed.gmIdentity.*;
import org.gnumed.gmGIS.*;
import net.sf.hibernate.*;
import java.util.*;
import java.util.logging.*;

/**
 *
 * @author  sjtan
 */
public class TestGmGIS extends TestCase {
    
    /** Creates a new instance of TestGmGIS */
    public TestGmGIS() {
    }
    
    static List urbs;
    
    static List getUrbs() throws Exception {
       
       if (urbs == null) {
            Session s = HibernateInit.openSession();
            urbs = s.find("from u in class org.gnumed.gmGIS.urb");
            s.flush();
            s.connection().commit();
       }
       return urbs;
    }
       
    
    public static urb getRandomUrb() throws Exception {
            Random r  = new Random();
            List urbs = getUrbs();
            if (urbs.size() == 0) {
                urb u = new urb();
                u.setName("NO_URB_FOUND");
                return u;
            }
           urb u =  (urb) urbs.get( r.nextInt((int)urbs.size()) );
           return u;
    }
        
    public static address createRandomAddress() throws Exception {
        String street = NameProducer.getStreet();
        String[] parts = street.split(",");
        Logger.global.info("Random address parts = " +  DomainPrinter.getStringList( parts) );
        address a = new address();
        a.setNumber(parts[0]);
        street s2 = new street();
        urb u = getRandomUrb();
        s2.setName(parts[1]);
        s2.setUrb(u);
        s2.setPostcode(u.getPostcode());
        a.setStreet(s2);
        return a;
    }
    
    public void testAddress() throws Exception {
        
        int n = 100;
        for (int i = 0; i < n; ++i) {
            address a = createRandomAddress();
            Session s = HibernateInit.openSession();
            s.save(a);
            s.flush();
            s.connection().commit();
            s.close();
        }
        
        Session s = HibernateInit.openSession();
        List l = s.find("from a in class org.gnumed.gmGIS.address");
        for (int j = 0; j < l.size(); ++j) {
           DomainPrinter.getInstance().printAddress(System.out,  (address)l.get(j));
        }
        s.connection().rollback();
        s.close();
    }
    
    public static void main(String[] args) throws Exception {
            HibernateInit.initGmIdentityOnly();
//            HibernateInit.exportDatabase();
            TestSuite suite = new TestSuite();
            suite.addTestSuite(TestGmGIS.class);
            junit.textui.TestRunner.run(suite);
      }
}
