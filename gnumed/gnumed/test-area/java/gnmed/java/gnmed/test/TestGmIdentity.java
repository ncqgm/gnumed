/*
 * TestGmIdentity.java
 *
 * Created on 23 July 2003, 10:25
 */

package gnmed.test;
import junit.framework.*;
import org.gnumed.gmIdentity.*;
import org.gnumed.gmGIS.*;

import net.sf.hibernate.Session;


/**
 *
 * @author  sjtan
 */
public class TestGmIdentity  extends TestCase {
    
    
    public static identity createTestIdentity() throws Exception {
        identity id = new identity();
        Names n = new Names();
        boolean male = NameProducer.getMale();
        String [] names = NameProducer.getFirstLastName(male);
        n.setFirstnames(names[0]);
        n.setLastnames(names[1]);
        id.setKaryotype(male ? "XY":"XX");
        id.setDob(NameProducer.getBirth());
        id.setPupic(NameProducer.getId()); 
        id.addNames(n);
        return id;
    }
    
   
    
    void saveOneTestIdentity() throws Exception {
        identity id = createTestIdentity();
        Session s = HibernateInit.getSessions().openSession();
        s.save(id);
        s.flush();
        s.connection().commit();
        s.close();
    }
    
    public void testIdentity() throws Exception {
        
        int n = 100;
        for (int i = 0; i < n; ++i) {
                saveOneTestIdentity();
        }
        
    }
    
    
    /** Creates a new instance of TestGmIdentity */
    public TestGmIdentity() {
    }
    
    public static void main(String[] args) throws Exception {
            HibernateInit.initGmIdentityOnly();
            HibernateInit.exportDatabase();
            TestSuite suite = new TestSuite();
            suite.addTestSuite(TestGmIdentity.class);
            junit.textui.TestRunner.run(suite);
      }
}
