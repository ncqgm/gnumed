/*
 * TestGisManager.java
 *
 * Created on 9 August 2003, 09:48
 */

package quickmed.usecases.test;
import org.gnumed.gmGIS.*;
import org.gnumed.gmIdentity.identity;

import gnmed.test.HibernateInit;

import net.sf.hibernate.*;
import net.sf.hibernate.type.*;
import junit.framework.*;
import java.util.*;
import java.util.logging.*;
/**
 *
 * @author  sjtan
 */
public class TestGISManager {
    static Logger logger = Logger.global;
    /** Creates a new instance of TestGisManager */
    
    static TestGISManager instance = new TestGISManager();
    
    public static TestGISManager instance() {
        return instance;
    }
    
    public TestGISManager() {
    }
    
    public urb findByPostcode(String postcode) throws Exception {
        urb u = null;
        Session sess = null;
        logger.info(" using postcode = " + postcode.trim().toLowerCase());
        try {
            sess =  HibernateInit.openSession();
            List l  =
            sess.find("select u from urb u where lower(u.postcode) like ?",
            postcode.trim().toLowerCase(), Hibernate.STRING);
            if (l.size() > 0)
                u = (urb) l.iterator().next();
        } catch (Exception e) {
             logger.info(e.getLocalizedMessage());
        } finally {
            sess.close();
        }
        logger.info("found u = " + (u != null ? u.getName() : null) );
        return u;
    }
    
    urb findUrbByNameAndState( String name, String stateName) throws Exception {
         urb u = null;
        Session sess = null;
        try {
            sess =  HibernateInit.openSession();
            List l  =
            sess.find("select u from urb u where lower(u.name) like ? and ( lower( u.state.name) like ? "+
           " or lower(u.state.code) like ? )",
           new Object[] { name.toLowerCase().trim(), stateName.toLowerCase().trim(),  stateName.toLowerCase().trim() },
           new Type[] { Hibernate.STRING, Hibernate.STRING, Hibernate.STRING } );
            if (l.size() >  0)
                u = (urb) l.iterator().next();
        } catch (Exception e) {
             logger.info(e.getLocalizedMessage());
        } finally {
            sess.close();
        }
        logger.info("found u = " + u);
        logger.info("u.name = " + u.getName());
        return u;
    }
    
    public street findStreetByStrings( String name, String urb, String state) throws Exception {
        street street = null;
         Session sess = null;
        try {
            sess =  HibernateInit.openSession();
            List l  =
            sess.find("select s from street s where lower(s.name) like ? "+
            "and lower(urb) like ? and (lower(s.state.name) like ? or lower(s.state.code) like ? ",
            new Object[] { name.trim().toLowerCase(), urb.trim().toLowerCase(), state.trim().toLowerCase() },
            new Type[] { Hibernate.STRING, Hibernate.STRING, Hibernate.STRING } );
            if (l.size() == 1)
               street = (street) l.iterator().next();
        } catch (Exception e) {
             logger.info(e.getLocalizedMessage());
        } finally {
            sess.close();
        }
        return street;
    }
    
    public street findStreetByNameAndUrb( String name, urb urb) throws Exception {
     street street = null;
         Session sess = null;
        try {
            sess =  HibernateInit.openSession();
            List l  =
            sess.find("select s from street s where lower(s.name) like ? "+
            "and s.urb.id = ? ", new Object[] { name.trim().toLowerCase(), urb.getId() },
            new Type[] { Hibernate.STRING, Hibernate.INTEGER } );
            if (l.size() == 1)
               street = (street) l.iterator().next();
        } catch (Exception e) {
            logger.info(e.getLocalizedMessage());
        } finally {
            sess.close();
        }
        return street;
    }
    
    public address findByNoAndStreet( String no, street street) throws Exception {
         Session sess = null;
         address  address = null;
        try {
            sess =  HibernateInit.openSession();
            List l  =
            sess.find("select a from address a where lower(a.number) = ? and a.street.id = ? " +
            " and s.urb.id = ? ", new Object[] { no.trim().toLowerCase(), street.getId() },
            new Type[] { Hibernate.STRING, Hibernate.INTEGER } );
            if (l.size() == 1)
                address = ( address) l.iterator().next();
        } catch (Exception e) {
            logger.info(e.getLocalizedMessage());
        } finally {
            sess.close();
        }
        return address;
    }
    
    urb findUrbByName( String name)  throws Exception {
         Session sess = null;
       urb urb = null;
        try {
            sess =  HibernateInit.openSession();
            Iterator i = 
            sess.iterate("select u from  urb u where lower(u.name)= ?",
                        name.trim().toLowerCase(), Hibernate.STRING );
            if (i.hasNext())
                urb = (urb) i.next();
        } catch (Exception e) {
            logger.info(e.getLocalizedMessage());
        } finally {
            sess.close();
        }
        return urb;
    }
    
    public boolean isPostcode( String code) throws Exception {
         Session sess = null;
        boolean found = false;
        try {
            sess =  HibernateInit.openSession();
            found = 
            sess.iterate("select u from  urb  u where lower(u.postcode)= ?",
                        code.trim().toLowerCase(), Hibernate.STRING ).hasNext();
            
        } catch (Exception e) {
            logger.info(e.getLocalizedMessage());
        } finally {
            sess.close();
        }
        return found;
    }
    
   
    public address findExistingAddress( address a) {
        address a2 = null;
        Session sess = null;
        if (a.getStreet().getId() == null)
            return a;
        try {
             sess =  HibernateInit.openSession();
              Iterator j = sess.iterate( "select a from address a where a.number like ? "+
                              "a.street.id = ? ", new Object[] { a.getNumber(), a.getStreet().getId() },
                                                  new Type[] { Hibernate.STRING, Hibernate.LONG } );
              
              if (j.hasNext())  
                   a2 = (address)j.next();
            
        } catch (Exception e) {
            e.printStackTrace();
        }
        finally {
            try {
            sess.close();
            } catch (Exception e2) {
                e2.printStackTrace();
            }
        }
        return a2 != null ? a2: a;
    }
    
    address substituteExistingAddress( address a) {
        address a2 = findExistingAddress(a);
        if (a2 != null)
            return a2;
        return a;
    }
    
    /**
     *  updates the address of the identity for a particular type.
     *  currently, just clears old address references, but might
     *have an active flag on identities_address instead to remember
     *old addresses. This version doesn't update the db straight away.
     */
    public identity updateAddress( identity id, address_type type, address newAddress) {
        address address = substituteExistingAddress( newAddress);
        Iterator j = id.getIdentities_addressess().iterator();
        while (j.hasNext()) {
            identities_addresses ia = (identities_addresses) j.next();
            if ( ia.getAddress_type().equals(type)) {
                ia.setAddress(address);
                return id;
            }
        }
        identities_addresses ia2 = new identities_addresses();
        ia2.setAddress_type(type);
        ia2.setAddress(address);
        id.addIdentities_addresses(ia2);
        return id;
    }
                
        
//        Session sess = null;
//        identities_addresses ia = null;
//        try {
//              sess =  HibernateInit.openSession();
//              Iterator j = sess.iterate( "select ia from identity i inner join i.identities_addressess ia where "+
//              "i.id = ? and ia.address_type.name like ?",
//              new Object[] { id.getId(), type.getName() },
//              new Type[] { Hibernate.INTEGER, Hibernate.STRING } );
//              if (j.hasNext()) {
//                  ia = (identities_addresses) j.next();
////                  sess.delete( ia.getAddress());
////                  
////                  ia.setAddress(null);
////                  sess.flush();
//                 
//                  sess.evict(ia.getAddress());
//                  ia.setAddress(newAddress);
//                   sess.update(ia);
//                  
//                  // the logic can be changed to just delete the old address
//                  // and then call id.setIdentityAddress
//                  
//              } else 
//                  id.setIdentityAddress(type, newAddress);
//              // the default operation is to forget the old addresses 
//              while (j.hasNext()) {
//                sess.delete(j.next());
//              }
//             
//               sess.flush();
//               sess.connection().commit();
////              ia = new identities_addresses();
////              ia.setAddress(newAddress);
////              ia.setAddress_type(type);
////              id.addIdentities_addresses(ia);
//////              sess.save(ia);
////              sess.flush();
////              sess.update(id);
////              sess.flush();
////              sess.connection().commit();
//        } catch (Exception e) {
//            e.printStackTrace();
//        } finally {
//            try {
//            sess.close();
//            } catch (Exception e2) {
//                e2.printStackTrace();
//            }
//        }
//        return id;
//        
//    }
}
