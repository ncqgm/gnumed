/*
 * TestIdentityAddress.java
 *
 * Created on 25 July 2003, 09:59
 */

package gnmed.test;
import junit.framework.*;
import org.gnumed.gmIdentity.*;
import org.gnumed.gmGIS.*;
import java.util.*;

import net.sf.hibernate.*;
/**
 *
 * @author  sjtan
 */
public class TestIdentityAddress extends TestCase {
    String[] addressTypes = {"home", "work", "school", "holiday house" };
    
    /** Creates a new instance of TestIdentityAddress */
    public TestIdentityAddress() throws Exception  {
        create_address_types();
    }
    
    public void setUp() throws Exception {
        
    }
    
    void create_address_types() throws Exception {
        Session sess = HibernateInit.openSession();
        for (int i = 0; i < addressTypes.length; ++i) {
            List l = sess.find("from addrType in class org.gnumed.gmGIS.address_type where addrType.name=?",
            addressTypes[i], Hibernate.STRING);
            if (l.size() > 0)
                continue;
            address_type t = new address_type();
            t.setName(addressTypes[i]);
            sess.save(t);
        }
        sess.flush();
        sess.connection().commit();
         HibernateInit.closeSession(sess);
    }
    
    List getAddressTypes() throws Exception {
        Session sess = HibernateInit.openSession();
        List l = sess.find("from addrType in class org.gnumed.gmGIS.address_type");
        sess.flush();
         HibernateInit.closeSession(sess);
        return l;
    }
    identities_addresses create_identities_addresses( address address, address_type t) {
        identities_addresses ia = new identities_addresses();
        ia.setAddress(address);
        ia.setAddress_type(t);
        return ia;
    }
    
    public identity createPersonWithAddresses(int n) throws Exception {
        List typeList = getAddressTypes();
        //        System.out.println("Printing address types");
        //        DomainPrinter.printAddrTypes( System.out, typeList);
        identity id = TestGmIdentity.createTestIdentity();
        for (int i = 0; i < n; ++i) {
            id.addIdentities_addresses(create_identities_addresses(TestGmGIS.createRandomAddress(), (address_type)typeList.get(i) ) );
        }
        return id;
    }
    
    public void createManyPersonsWithManyAddresses() throws Exception {
        Random r = new Random();
        
        Session sess = HibernateInit.openSession();
        for (int i = 0; i < TestProperties.properties.getIntProperty("test.identity.addresses.number"); ++i) {
            identity id = createPersonWithAddresses( r.nextInt(4));
            sess.save(id);
            
        }
        sess.flush();
        sess.connection().commit();
         HibernateInit.closeSession(sess);
    }
    
    public List findPersonsWithMultipleAddresses() throws Exception {
        Session s = HibernateInit.openSession();
        List l = s.find("from p in class org.gnumed.gmIdentity.identity where p.identities_addressess.size > 0");
        return l;  // note whether session is /is not closed at this point for debugging.
    }
    
    void printPersons(java.io.PrintStream ps, List list) {
        Iterator i = list.iterator();
        while (i.hasNext()) {
            identity id = (identity) i.next();
            DomainPrinter.getInstance().printIdentity(ps, id);
        }
    }
    
    public void testIdentityAddress() throws Exception {
        createManyPersonsWithManyAddresses();
        List list = findPersonsWithMultipleAddresses();
        assertTrue(list.size() > 0);
        printPersons(System.out, list);
    }
    
    public static void main(String[] args) throws Exception {
        HibernateInit.initAll();
        TestSuite suite = new TestSuite();
        suite.addTestSuite(TestIdentityAddress.class);
        junit.textui.TestRunner.run(suite);
    }
}
