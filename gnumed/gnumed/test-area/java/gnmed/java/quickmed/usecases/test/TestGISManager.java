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
import java.lang.reflect.*;
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
    
    public final static enum_telephone_role home = createOrFindEnumTelephone( Globals.bundle.getString("home"));
    public final static  enum_telephone_role work= createOrFindEnumTelephone( Globals.bundle.getString("work"));
    public final static enum_telephone_role mobile = createOrFindEnumTelephone( Globals.bundle.getString("mobile"));
    public final static enum_telephone_role nok = createOrFindEnumTelephone( Globals.bundle.getString("nok"));
    public final static address_type homeAddress = createOrFindAddressType(Globals.bundle.getString("home"));
    
    public final static enum_telephone_role pager  = createOrFindEnumTelephone(Globals.bundle.getString("pager"));
    public final static enum_telephone_role fax  = createOrFindEnumTelephone(Globals.bundle.getString("fax"));
    
    static address_type createOrFindAddressType( String type) {
        try {
            final  Method[] addrTypeSetter = new Method[] {
                address_type.class.getMethod("setName",  new Class[] { String.class})
            };
            
            return (address_type)  Utilities.createOrFindEntity(
            "from a in class address_type where a.name = ? ",
            new Object[] { type },
            new Type[] { Hibernate.STRING }  , address_type.class,
            addrTypeSetter );
        } catch (Exception e) {
            address_type a = new address_type();
            a.setName(type);
            return a;
        }
    }
    
    public static enum_telephone_role createOrFindEnumTelephone( String name) {
        try {
            Method[] setters = new Method[] { enum_telephone_role.class.getMethod("setRole", new Class[] { String.class }) };
            return (enum_telephone_role) Utilities.createOrFindEntity("from r in class org.gnumed.gmGIS.enum_telephone_role where r.role=?", new Object[] { name},
            new Type[] { Hibernate.STRING }, enum_telephone_role.class, setters);
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }
    
    public urb findByPostcode(String postcode) throws Exception {
        urb u = null;
        Session sess = null;
        logger.info(" using postcode = " + postcode.trim().toLowerCase());
        try {
            sess =  getSession();
            
            List l  =
            sess.find("select u from urb u where lower(u.postcode) like ?",
            postcode.trim().toLowerCase(), Hibernate.STRING);
            if (l.size() > 0)
                u = (urb) l.iterator().next();
        } catch (Exception e) {
            logger.info(e.getLocalizedMessage());
        } finally {
            getSession().disconnect();
        }
        logger.info("found u = " + (u != null ? u.getName() : null) );
        return u;
    }
    
    urb findUrbByNameAndState( String name, String stateName) throws Exception {
        urb u = null;
        Session sess = null;
        try {
            sess =  getSession();
            
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
            getSession().disconnect();
        }
        logger.info("found u = " + u);
        logger.info("u.name = " + u.getName());
        return u;
    }
    
    public street findStreetByStrings( String name, String urb, String state) throws Exception {
        street street = null;
        Session sess = null;
        try {
            sess =  getSession();
            
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
            sess.disconnect();
        }
        return street;
    }
    
    public street findStreetByNameAndUrb( String name, urb urb) throws Exception {
        street street = null;
        Session sess = null;
        try {
            sess =  getSession();
            
            
            
            List l  =
            sess.find("select s from street s where lower(s.name) like ? "+
            "and s.urb.id = ? ", new Object[] { name.trim().toLowerCase(), urb.getId() },
            new Type[] { Hibernate.STRING, Hibernate.INTEGER } );
            if (l.size() == 1)
                street = (street) l.iterator().next();
        } catch (Exception e) {
            logger.info(e.getLocalizedMessage());
        } finally {
            sess.disconnect();
        }
        return street;
    }
    
    public address findByNoAndStreet( String no, street street) throws Exception {
        Session sess = null;
        address  address = null;
        try {
            sess =  getSession();
            
            List l  =
            sess.find("select a from address a where lower(a.number) = ? and a.street.id = ? " +
            " and s.urb.id = ? ", new Object[] { no.trim().toLowerCase(), street.getId() },
            new Type[] { Hibernate.STRING, Hibernate.INTEGER } );
            if (l.size() == 1)
                address = ( address) l.iterator().next();
        } catch (Exception e) {
            logger.info(e.getLocalizedMessage());
        } finally {
            getSession().disconnect();
        }
        return address;
    }
    
    urb findUrbByName( String name)  throws Exception {
        Session sess = null;
        urb urb = null;
        try {
            sess =  getSession();
            
            Iterator i =
            sess.iterate("select u from  urb u where lower(u.name)= ?",
            name.trim().toLowerCase(), Hibernate.STRING );
            if (i.hasNext())
                urb = (urb) i.next();
        } catch (Exception e) {
            logger.info(e.getLocalizedMessage());
        } finally {
            getSession().disconnect();
        }
        return urb;
    }
    
    public boolean isPostcode( String code) throws Exception {
        Session sess = null;
        boolean found = false;
        try {
            sess =  getSession();
            
            found =
            sess.iterate("select u from  urb  u where lower(u.postcode)= ?",
            code.trim().toLowerCase(), Hibernate.STRING ).hasNext();
            
        } catch (Exception e) {
            logger.info(e.getLocalizedMessage());
        } finally {
            getSession().disconnect();
        }
        return found;
    }
    
    
    public address findExistingAddress( address a) {
        address a2 = null;
        Session sess = null;
        if (a.getStreet().getId() == null)
            return a;
        try {
            sess =  getSession();
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
                getSession().disconnect();
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
    
    
    /**
     * adds a default address of the type
     */
    public address addDefaultAddress( identity id ,address_type type) {
        address a = new address();
        a.setNumber("unknown address");
        updateAddress(id, type, a);
        return a;
    }
    
    
    /** finds an address by type, or null if no address of that type exists for this identity
     */
    public address findAddressByType(identity id, address_type type) {
        identities_addresses ida = null;
        Iterator j = id.getIdentities_addressess().iterator();
        if (!j.hasNext()) {
            return null;
        }
        while (j.hasNext()) {
            ida = (identities_addresses) j.next();
            if (ida.getAddress_type().equals(type))
                return ida.getAddress();
        }
        return null;
    }
    
    /**
     *find the telephone of the telephone role (home, fax, etc) for the address,
     *or null if none.
     */
    public telephone findTelephoneAt( address a, enum_telephone_role role) {
        Iterator j = a.getTelephones().iterator();
        while (j.hasNext()) {
            telephone t = (telephone) j.next();
            if (t.getEnum_telephone_role().equals(role))
                return t;
        }
        return null;
    }
    
    public telephone setTelephoneWithRoleAt( identity id, String number, enum_telephone_role role, address_type addressType) {
        
        // pre-condition
        if ( number == null || number.trim().length() == 0)
            return null;
        
        number = number.trim();
        
        
        address a =findAddressByType(id, addressType);
        if (a == null)
            a =  addDefaultAddress(id , addressType);
        telephone t = a.findTelephone(role);
        if ( t == null) {
            t = new telephone();
            t.setEnum_telephone_role(role);
            a.addTelephone(t);
        }
        t.setNumber(number);
        return t;
    }
    
    
    
    private SessionHolder sessionHolder = new SessionHolder();
    /** Getter for property session.
     * @return Value of property session.
     *
     */
    public Session getSession() {
        return getSessionHolder().getSession();
    }
    
    /** Setter for property session.
     * @param session New value of property session.
     *
     */
    public void setSession(Session session) {
        getSessionHolder().setSession(session);
    }
    
    /** Getter for property sessionHolder.
     * @return Value of property sessionHolder.
     *
     */
    public SessionHolder getSessionHolder() {
        return this.sessionHolder;
    }
    
    /** Setter for property sessionHolder.
     * @param sessionHolder New value of property sessionHolder.
     *
     */
    public void setSessionHolder(SessionHolder sessionHolder) {
        this.sessionHolder = sessionHolder;
    }
    
}
