/*
 * DemographicIdentityModel.java
 *
 * Created on 1 August 2003, 21:25
 */

package quickmed.usecases.test;

import org.gnumed.gmIdentity.*;
import org.gnumed.gmGIS.*;
//import org.gnumed.gmClinical.category_type;
//import org.gnumed.gmClinical.category;
import org.gnumed.gmClinical.*;
import gnmed.test.*;

import java.util.logging.*;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.lang.reflect.*;
import java.util.*;
import java.util.regex.*;

import net.sf.hibernate.*;
import net.sf.hibernate.type.Type;
import java.io.*;
/**
 *
 * @author  sjtan
 */
public class DemographicIdentityModel implements  DemographicModel {
    
    street undefinedStreet;
    address addressEdited;
    
    
    
    
    
    /** Holds value of property identity. */
    private identity identity;
    /** Holds value of property uiModel. */
    private DemographicModel uiModel;
    
    
    
    final static Logger logger;
    final static ResourceBundle bundle = ResourceBundle.getBundle("SummaryTerms");
    
    
    private  static Method[] socialIdSetters = null;
    private  static Method[] addrTypeSetter =null;
    static {
//        logger = Logger.getLogger("DemographicIdentityModel");
        logger = Logger.global;
//        logger.setLevel(logger.global.getLevel());
        //        logger.addHandler(new ConsoleHandler());
        try {
            socialIdSetters = new Method[] { enum_social_id.class.getMethod("setName", new Class[] { String.class}),
            enum_social_id.class.getMethod("setId", new Class[]{ Integer.class}) };
            
            addrTypeSetter = new Method[] {
                address_type.class.getMethod("setName",  new Class[] { String.class})
            };
            logger.fine("CREATED socialIdSetters and AddrTypeSetter");
        } catch (Exception e) {
            e.printStackTrace();
            System.exit(-1);
        }
    }
    final static DateFormat shortestformat = new SimpleDateFormat("MM/yy");
    
    
    
    final static enum_telephone_role home = createOrFindEnumTelephone( bundle.getString("home"));
    final static  enum_telephone_role work= createOrFindEnumTelephone( bundle.getString("work"));
    final static enum_telephone_role mobile = createOrFindEnumTelephone( bundle.getString("mobile"));
    final static enum_telephone_role nok = createOrFindEnumTelephone( bundle.getString("nok"));
    final static enum_social_id pension = createOrFindEnumSocialId(bundle.getString("pension") , 2);
    final static enum_social_id medicare =createOrFindEnumSocialId(bundle.getString("medicare"), 1);
    final static enum_social_id recordNo = createOrFindEnumSocialId(bundle.getString("record_no"), 3);
    final static address_type homeAddress = createOrFindAddressType(bundle.getString("home"));
    
    static Map mapMarital ;
      static category_type maritalStatus = createOrFindCategoryType( bundle.getString("marital_status") );
    
      static category_type ABO = createOrFindCategoryType( bundle.getString("ABO") );
    
    
      static category_type rhesus = createOrFindCategoryType( bundle.getString("rhesus") );
    
    
    
    final static category married = createOrFindCategory( bundle.getString("married"), maritalStatus);
    final static  category unmarried = createOrFindCategory( bundle.getString("unmarried"), maritalStatus);
    final static    category divorced = createOrFindCategory( bundle.getString("divorced"), maritalStatus);
    final static   category widowed = createOrFindCategory( bundle.getString("widowed"), maritalStatus);
    final static category unknown = createOrFindCategory( bundle.getString("unknown"), maritalStatus);
    final static category [] maritalList = new category[] { married, unmarried, divorced, widowed };
    
    
    final static category A = createOrFindCategory( bundle.getString("A"), ABO);
    final static  category B = createOrFindCategory( bundle.getString("B"), ABO);
    final static    category AB = createOrFindCategory( bundle.getString("AB"), ABO);
    final static   category O = createOrFindCategory( bundle.getString("O"), ABO);
    final static category rhPos = createOrFindCategory( bundle.getString("positive"), rhesus);
    final static category rhNeg = createOrFindCategory( bundle.getString("negative"), rhesus);
    final static category [] ABOList = new category[] {A, B, AB, O };
    final static category [] rhesusList = new category[] {rhPos, rhNeg };
    
    /** Holds value of property byteStream. */
    private ByteArrayOutputStream byteStream = new ByteArrayOutputStream();
    
    /** Holds value of property printStream. */
    private PrintStream printStream = new PrintStream(byteStream, true);
    
    static {
        
        try {
            mapMarital=  createMap(
            category.class.getMethod("getName", new Class[0]),
            Arrays.asList(new Object[] {widowed, unmarried, married, divorced })
            );
            logger.fine("CREATED mapMarital");
        } catch (Exception e) {
            logger.severe(e.getMessage());
            mapMarital.put("married", married);
            mapMarital.put("unmarried", unmarried);
        }
    };
    
    /** Creates a new instance of DemographicIdentityModel */
    public DemographicIdentityModel() {
    }
    
    Names getNames() {
        if(  getIdentity().getNamess().size() == 0)
            getIdentity().addNames(new Names());
        return  (Names) getIdentity().getNamess().iterator().next();
    }
    
    
    
    /**
     * creates a map out of a list of attributes given a getter method for a particular attribute.
     *  Precondition: objects must be the same class or inherit from the same class as the class from
     *  which the getter method comes from.
     */
    public  static Map createMap( Method keyGetter, List list) {
        Map map = new HashMap();
        for (int i = 0; i < list.size(); ++i) {
            try {
                map.put( keyGetter.invoke(list.get(0), new Object[0]), list.get(0));
            } catch (Exception e) {
                e.printStackTrace();
                logger.info(e.getMessage());
            }
        }
        return map;
    }
    
    /** finds an entity with a particular attribute, or creates it
     */
    public static  Object createOrFindEntity( String query,final  Object[] params, Type[] types,
    Class targetClass, Method[] paramSetters) throws Exception  {
        Object newObject = null;
        Session s = null;
        try {
            s= HibernateInit.openSession();
            newObject = s.iterate(query, params, types).next();
            if (newObject != null) {
                return newObject;
            }
            throw new  Exception("No object found");
        } catch (Exception e) {
            try {
                logger.fine("Unable to find a " + targetClass.getName() + " with specified parameters . CREATING NEW ONE");
                newObject = targetClass.newInstance();
                for (int i = 0; i < paramSetters.length; ++i) {
                    paramSetters[i].invoke(newObject, new Object[] { params[i] } );
                }
                s.save(newObject);
                s.flush();
                s.connection().commit();
                logger.fine("SUCCESSFULLY CREATED a " +  targetClass.getName() );
                return newObject;
            } catch ( Exception e2) {
                
                HibernateInit.closeSession(s);
                throw e2;
            }
        } finally {
            logger.fine("DISCONNECTING AND CLOSING " + s.toString());
            //  s.disconnect();
            HibernateInit.closeSession(s);
            
        }
        //        return newObject;
    }
    
    
    static category_type createAndSaveCategoryType  (Session sess, String type) throws Exception {
        category_type c = new category_type();
        c.setName(type);
        sess.save(c);
        sess.flush();
        sess.connection().commit();
        logger.fine("SAVED CATEGORY_TYPE = " + c.getId() + " " +c.getName());
        return c;
    }
    
    static category_type createOrFindCategoryType( String type) {
        category_type c = null;
        Session sess = null;
        try {
            sess =  HibernateInit.openSession();
            List l = sess.find("select ct from category_type ct where ct.name like ?",
            type,  Hibernate.STRING
            );
            
            if (l.size() == 0 )
                c = createAndSaveCategoryType(sess,   type);
            else
                c = (category_type) l.get(0);
        } catch (Exception e) {
            
            e.printStackTrace();
            
        }finally {
            try {
                 HibernateInit.closeSession(sess);
            }
            catch (Exception e2) {
                e2.printStackTrace();
            }
        }
        return c;
    }
    
    static category createAndSaveCategory( Session sess, String type, category_type superType )throws Exception {
        category c = new category();
        c.setName(type);
        c.setCategory_type(superType);
        sess.save(c);
        sess.flush();
        
        sess.connection().commit();
        return c;
    }
    
    static category createOrFindCategory( String type, category_type superType ) {
        category c = null;
        Session sess = null;
        try {
            sess =  HibernateInit.openSession();
            List l = sess.find("select c from category c where c.name like ? and c.category_type.id = ?",
            new Object[] { type, superType.getId() } ,
            new Type[] { Hibernate.STRING, Hibernate.LONG }
            );
            
            if (l.size() == 0 )
                c = createAndSaveCategory(sess,   type, superType);
            else
                c = (category) l.get(0);
        } catch (Exception e) {
            
            e.printStackTrace();
            
        }finally {
            try {
               HibernateInit.closeSession(sess);
            }
            catch (Exception e2) {
                e2.printStackTrace();
            }
        }
        return c;
    }
    
    static address_type createOrFindAddressType( String type) {
        try {
        return (address_type) createOrFindEntity(
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
    
    
    static enum_social_id createOrFindEnumSocialId( String name, int id) {
        try {
            return (enum_social_id) createOrFindEntity(
            "from e in class org.gnumed.gmIdentity.enum_social_id where e.name = ? and  e.id = ?",
            new Object[] { name, new Integer(id) },
            new Type[] { Hibernate.STRING, Hibernate.INTEGER },
            enum_social_id.class, socialIdSetters
            
            );
        } catch (Exception e ) {
            e.printStackTrace();
        }
        enum_social_id eid = new enum_social_id();
        eid.setName(name);
        eid.setId(new Integer(id));
        return eid;
    }
    
    
    static enum_telephone_role createOrFindEnumTelephone( String name) {
        try {
            Method[] setters = new Method[] { enum_telephone_role.class.getMethod("setRole", new Class[] { String.class }) };
            return (enum_telephone_role) createOrFindEntity("from r in class org.gnumed.gmGIS.enum_telephone_role where r.role=?", new Object[] { name},
            new Type[] { Hibernate.STRING }, enum_telephone_role.class, setters);
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
        //        enum_telephone_role role = null;
        //        Session s;
        //        try {
        //            s=  HibernateInit.openSession();
        //            role = (enum_telephone_role) s.iterate("from r in class org.gnumed.orgGIS.enum_telephone_role where r.role=?",
        //            name , Hibernate.STRING).next();
        //            return role;
        //        }catch(Exception e) {
        //            logger.info("Could not find telephone role = " + name);
        //            role = new enum_telephone_role();
        //            role.setRole(name);
        //            try {
        //                s.save(role);
        //                s.flush();
        //                s.connection().commit();
        //            } catch (Exception e2) {
        //                e2.printStackTrace();
        //            }
        //        }
        //        finally {
        //            s.close();
        //        }
        //        return role;
    }
    
    street createStreet(String street,  urb urb) throws Exception {
        Session s=  HibernateInit.openSession();
        street st = new street();
        st.setName(street);
        st.setUrb(urb);
        s.save(st);
        s.flush();
        s.connection().commit();
        s.close();
        logger.fine("CREATED STREET " + st.getName() + " in urb " + st.getUrb());
        logger.fine("urb name ="+ st.getUrb().getName());
        return st;
    }
    //
    //    urb findUrb( String urb, String state) throws Exception {
    //        urb u = null;
    //        Session sess = HibernateInit.openSession();
    //        u = (urb) sess.iterate("from org.gnumed.gmGIS.urb as urb"+
    //        " where urb.name like ? and "+
    //        " (urb.state.code = ? or urb.state.name like ?)",
    //        new Object[] { urb.toUpperCase() + "%" , state.toUpperCase() , state.toUpperCase() + "%" },
    //        new Type[] { Hibernate.STRING, Hibernate.STRING ,Hibernate.STRING }).next();
    //        return u;
    //
    //    }
    
    
    public  static boolean isStateString(String state) {
        try {
            Session s = HibernateInit.openSession();
            String v = state.toUpperCase().trim() ;
            logger.fine("SEEING IF " + v + " is a STATE STRING .");
            List l = s.find("select s from state s where upper(s.name) like ? or s.code like ?",
            new Object[] {v ,v } , new Type[] { Hibernate.STRING , Hibernate.STRING });
            s.connection().commit();
            s.disconnect();
            
            if (l.size() == 1) {
                logger.info(v + " is a state string");
                return true;
            }
            logger.info(v + " isn't a state string");
        } catch (Exception e) {
            e.printStackTrace();
        }
        return false;
    }
    
    /**
     * this function will need to search for a match street
     */
    street findStreet( String street, String urb, String state) {
        try {
            street = street.trim();
            urb = urb.trim();
            if ( street.length() == 0 || urb.length() == 0)
                return undefinedStreet;
            
            urb u = findUrb(urb, state);
            logger.info("Using urb = "+ u.toString() + " name = " + u.getName() + "state = " + u.getState());
            Session sess = HibernateInit.openSession();
            Iterator it  = sess.iterate("from s in class org.gnumed.gmGIS.street "+
            " where s.name like ? and s.urb.id = ?",
            new Object[] { street + "%", u.getId()},
            new Type[] { Hibernate.STRING, Hibernate.INTEGER });
            if( ! it.hasNext())  {
                HibernateInit.closeSession(sess);
                return createStreet( street, u);
            }
            
            
            street s = (street) it.next() ;
             HibernateInit.closeSession(sess);
            if (s == null)
                return undefinedStreet;
            return s;
        } catch (Exception e) {
            logger.severe( e.toString());
            return undefinedStreet;
        }
        
    }
    
    /**
     * searches identity.identities_addresses for address of same type
     */
    void setAddressAttr(address a , address_type type) {
        identities_addresses ia = getIdentity().findIdentityAddressByAddressType(type);
        if (ia == null)
            ia = new identities_addresses();
        ia.setAddress_type(type);
        ia.setAddress(a);
        getIdentity().addIdentities_addresses(ia);
        logger.info("CREATED new identity_address of type " + type + ".  identities_addresses.size = " + Integer.toString(getIdentity().getIdentities_addressess().size()));
        setAddressEdited(a);
    }
    
    void setTelephone( String telephone, enum_telephone_role role) {
        
        if ( role.equals(mobile) ) {
            telephone t = new telephone();
            t.setEnum_telephone_role(role);
            t.setNumber(telephone);
            identity.setMobile(t);
            logger.finer(" *** identity mobile set to " + t.getNumber());
            return;
        }
        // THIS DEPENDS ON AN ADDRESS EXISTING FOR THE PATIENT. MAY NEED DEFAULT ADDRESS.
      
        /* SETS THE HOME TELEPHONE AT THE HOME ADDRESS. */
         logger.info(" *** SETTING " + telephone + " for  " + role.getRole() + " telephone");
         getManagerReference().getGISManager().setTelephoneWithRoleAt(getIdentity(), telephone, role, homeAddress);
         
        
        
    }
    
    Date parseDate( Object val) {
        String s = (String) val;
        try {
            return (Date)shortestformat.parse(s.trim());
        } catch (Exception e) {
            logger.fine("UNABLE TO PARSE into DATE: " + s);
            
        }
        return new Date();
    }
    
    String formatDate(Date d) {
             return  shortestformat.format(d);
       
    }
    
    
    void setSocialIdentityAttr( social_identity si, Object val, boolean expiry) {
        if (expiry)
            si.setExpiry((Date) parseDate(val));
        else
            si.setNumber((String)val);
        logger.fine(si.toString() + " set with " + val.toString() + "is expiry = " + new Boolean(expiry).toString());
    }
    
    social_identity findSocialIdentity( enum_social_id type ) {
         social_identity sid = null;
        identity id = getIdentity();
        Collection c = id.getSocial_identitys();
        Iterator j = c.iterator();
        logger.fine("THERE WERE " + c.size() + " Social Identities found. Looking for " + type.getId() + " "+type.getName());
        while (j.hasNext()) {
             sid = (social_identity) j.next();
             try {
            logger.finer("LOOKING AT SID "+ sid.getNumber() + sid.getEnum_social_id().getName() ); 
             } catch (Exception e) {
              logger.info("UNABLE to print " + sid);   
             }
            logger.fine("checking at sid with type " + sid.getEnum_social_id());
            if (sid.getEnum_social_id().equals(type)) {
                logger.finer("RETURNING " + sid.getNumber() + sid.getEnum_social_id().getName());
                return sid;
            }
        }
        sid = new social_identity();
        return sid;
    }
    
   
    
    void setSocialIdentity( Object val, enum_social_id type, boolean expiry) {
        Iterator i = getIdentity().getSocial_identitys().iterator();
        while (i.hasNext()) {
            social_identity si = (social_identity) i.next();
            if (si == null)
                logger.severe("****** Social identity is null in iterator ***");
            if (si.getEnum_social_id().equals(type) ) {
                setSocialIdentityAttr(si, val, expiry);
                return;
            }
        }
        social_identity si2 = new social_identity();
        si2.setEnum_social_id(type);
        setSocialIdentityAttr(si2, val, expiry);
        
        getIdentity().addSocial_identity(si2);
    }
    
    
    /** Getter for property identity.
     * @return Value of property identity.
     *
     */
    public identity getIdentity() {
        return this.identity;
    }
    
    /** Setter for property identity.
     * @param identity New value of property identity.
     *
     */
    public void setIdentity(identity identity) {
        this.identity = identity;
    }
    
    
    
    public String getAddress()  {
        identities_addresses ia = getIdentity().findIdentityAddressByAddressType(homeAddress);
        if (ia != null && ia.getAddress() != null) {
            getByteStream().reset();
            gnmed.test.DomainPrinter.getInstance().printAddress( getPrintStream(),  ia.getAddress(), true);
            setLastAddressString( getByteStream().toString());
            setLastAddress(ia.getAddress());
            return  getByteStream().toString();
        }
        setLastAddress(null);
        return  "";
    }
    
    public Object getBirthdate() {
        logger.info("****** identity ****** birthdate = " + getIdentity().getDob());
        return getIdentity().getDob();
    }
    
    public Object getCommenced() {
        return new Date();
    }
    
    public String getCountryOfBirth() {
        return "AU";
    }
    
    public String getFirstNames() {
        return getNames().getFirstnames();
    }
    
    public String getHomeTelephone() {
        logger.info("*** LOOKING FOR  Telephone type = " + home.getRole());
        return getIdentity().findTelephoneByRole(home).getNumber();
    }
    
    public String getLastNames() {
        return getNames().getLastnames();
    }
    
    public String getMedicare() {
        return findSocialIdentity (medicare).getNumber();
    }
    
    public String getMedicareExpiry() {
        return formatDate(findSocialIdentity ( medicare).getExpiry());
    }
    
    public String getMobilePhone() {
        return  getIdentity().getMobile().getNumber();
    }
    
    public String getNokPhone() {
        return  getIdentity().findTelephoneByRole(nok).getNumber();
    }
    
    public String getPensioner() {
        return findSocialIdentity( pension).getNumber();
    }
    
    public String getPensionerExpiry() {
        return  formatDate(findSocialIdentity (pension).getExpiry());
        
    }
    
    public String getPostcode() {
        return "postcode";
    }
    
    public String getRecordNo() {
        return findSocialIdentity(recordNo).getNumber();
    }
    
    public String getSex() {
        return getIdentity().getKaryotype().equals("XY") ? "male":"female";
    }
    
    public String getWorkTelephone() {
        return  getIdentity().findTelephoneByRole(work).getNumber();
    }
    
    final static Pattern addressPattern =
    Pattern.compile("\\s*(\\d+|\\d+\\w?|\\d+\\W+\\d+)[,|\\s]+([\\w|\\s]+)[,|\\s]+(\\D+)[,|\\s]*(\\d+)?");
    
    /** Holds value of property lastAddressString. */
    private String lastAddressString;
    
    /** Holds value of property lastAddress. */
    private address lastAddress;
    
    /** Holds value of property managerReference. */
    private ManagerReference managerReference;
    
    String[] getTwoParts( String s) {
        String[] parts = s.split("[,|\\s]+");
        StringBuffer partOneBuffer = new StringBuffer();
        for (int i = 0; i < parts.length -1; ++i) {
            partOneBuffer.append(parts[i]).append(" ");
        }
        return new String[] { partOneBuffer.toString(), parts[parts.length -1] };
    }
    
    boolean isValidPostcode(String code) {
        try {
            return TestGISManager.instance().isPostcode(code);
        } catch (Exception e) {
            logger.info(e.toString());
        }
        return false;
    }
    
    boolean streetContainsUrb( String street) {
        try {
            urb u = TestGISManager.instance().findUrbByName(getTwoParts(street)[1]);
            return u != null;
        } catch (Exception e) {
            e.printStackTrace();
        }
        return false;
    }
    
    String getStreetPartOnly( String street) {
        return getTwoParts(street)[0];
    }
    
    String getUrbPartOnly( String street) {
        return getTwoParts(street)[1];
    }
    
    address findIdentityAddress( address_type type) {
        identities_addresses  ia = getIdentity().findIdentityAddressByAddressType(type);
        if (ia == null)
            return null;
        return ia.getAddress();
    }
    
    street findStreet( String street, String postcode) {
        try {
            street s = TestGISManager.instance().findStreetByNameAndUrb(street,
            findUrb(postcode) );
            return s;
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }
    
    urb findUrb( String postcode) {
        try {
            return  getManagerReference().getGISManager().findByPostcode(postcode);
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }
    urb findUrb( String name, String state) {
        if (state == null)
            state = "%";
        logger.info("urb name = " + name + " : state name = " + state);
        try {
            return  getManagerReference().getGISManager().findUrbByNameAndState(name, state);
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }
    
    address getAddressWithNumber( String number) {
        address a = findIdentityAddress( homeAddress);
        if (a == null)
            a = new address();
        a.setNumber(number);
        return a;
    }
    
    street getStreetByName( String street, urb urb) {
        try {
            street s = getManagerReference().getGISManager().findStreetByNameAndUrb(street, urb );
            if ( s == null) {
                s = new street();
                logger.info("street created");
            }
            else logger.info("street found ");
            s.setUrb( urb );
            s.setName(street);
            logger.info( "street="  + s.getUrb().getName() + " : " + s.getName());
            return s;
            
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }
    
    void setAddressObject( String number, String street, String postcode) {
        logger.info("Setting by number, street, postcode ");
        setAddressObject(number, getStreetByName( street, findUrb(postcode) ));
    }
    
    void setAddressObject( String number, String street, String urb, String state ) {
        setAddressObject( number, getStreetByName( street, findUrb(urb, state)));
    }
    
    void setAddressObject( String number, street street) {
        
        address a = getAddressWithNumber(number);
        a.setStreet(street);
        //        getIdentity().setIdentityAddress(homeAddress, a);
        getManagerReference().getGISManager().updateAddress(getIdentity(), homeAddress, a);
        //    getUiModel().setAddress(getAddress());
    }
    
    
    
    public void setAddress(String address) {
        logger.info("trying to parse " + address);
        Matcher m = addressPattern.matcher(new StringBuffer( address.trim()));
        if(!m.find()) {
            logger.info("not parseable = " + address);
            return;
        }
        String number = m.group(1);
        String streetS = m.group(2);
        String urbOrState = m.group(3);
        String postcode = m.group(4);
        logger.info( " number = " + number + " street = " + streetS + " urbOrState = " + urbOrState + " postcode = " + postcode);
        String urbS = null;
        String stateS = null;
        String[]  parts ;
        
        if ( number != null && postcode!=null && isValidPostcode(postcode) ) {
            setAddressObject( number, isStateString(urbOrState) ? getStreetPartOnly(streetS) : streetS , postcode);
            return;
        }
        if ( number != null && urbOrState != null && streetContainsUrb(streetS) &&
        isStateString(urbOrState) ) {
            setAddressObject( number,  getStreetPartOnly(streetS), getUrbPartOnly(streetS), urbOrState);
            return;
        }
        if ( number != null && streetContainsUrb( streetS) && urbOrState == null) {
            setAddressObject( number, getStreetPartOnly(streetS), getUrbPartOnly(streetS), null);
            return;
        }
        if ( isStateString(getTwoParts(urbOrState)[1]) ) {
            setAddressObject( number, streetS, getTwoParts(urbOrState)[0], getTwoParts(urbOrState)[1]);
            return;
        }
        
    }
    
    public void setBirthdate(Object birthdate) {
        Date d = (Date) birthdate;
        getIdentity().setDob(d);
    }
    
    public void setCommenced(Object commenced) {
        
    }
    
    public void setCountryOfBirth(String countryOfBirth) {
    }
    
    
    public void setFirstNames(String firstNames) {
        getNames().setFirstnames(firstNames.trim());
    }
    
    
    
    
    public void setHomeTelephone(String homeTelephone) {
        logger.fine("***  ");
        setTelephone(homeTelephone, home);
    }
    
    public void setLastNames(String lastNames) {
        getNames().setLastnames(lastNames.trim());
    }
    
    public void setMedicare(String _medicare) {
        setSocialIdentity(_medicare, medicare, false);
    }
    
    public void setMedicareExpiry(String medicareExpiry) {
        setSocialIdentity( medicareExpiry, medicare,  true);
    }
    
    public void setMobilePhone(String mobilePhone) {
        setTelephone(mobilePhone, mobile);
    }
    
    public void setNokPhone(String nokPhone) {
        setTelephone(nokPhone, nok);
    }
    
    public void setPensioner(String pensioner) {
        setSocialIdentity( pensioner, pension, false);
    }
    
    public void setPensionerExpiry(String pensionerExpiry) {
        setSocialIdentity(pensionerExpiry, pension, true);
    }
    
    public void setPostcode(String postcode) {
    }
    
    public void setRecordNo(String recordNoStr) {
        setSocialIdentity(recordNoStr, recordNo, false);
    }
    
    public void setSex(String sex) {
        if (sex.equals(bundle.getString("male"))) {
            identity.setKaryotype("XY");
            return;
        }
        identity.setKaryotype("XX");
    }
    
    public void setWorkTelephone(String workTelephone) {
        setTelephone(workTelephone, work);
    }
    
    /** Getter for property addressEdited.
     * @return Value of property addressEdited.
     *
     */
    public address getAddressEdited() {
        return this.addressEdited;
    }
    
    /** Setter for property addressEdited.
     * @param addressEdited New value of property addressEdited.
     *
     */
    public void setAddressEdited(address addressEdited) {
        this.addressEdited = addressEdited;
    }
    
    /** Getter for property uiModel.
     * @return Value of property uiModel.
     *
     */
    public DemographicModel getUiModel() {
        return this.uiModel;
    }
    
    /** Setter for property uiModel.
     * @param uiModel New value of property uiModel.
     *
     */
    public void setUiModel(DemographicModel uiModel) {
        this.uiModel = uiModel;
    }
    
    /** Getter for property getMaritalStatus.
     * @return Value of property getMaritalStatus.
     *
     */
    public Object[] getMaritalList() {
        return maritalList;
    }
    
    /** Getter for property byteStream.
     * @return Value of property byteStream.
     *
     */
    public ByteArrayOutputStream getByteStream() {
        return this.byteStream;
    }
    
    /** Getter for property printStream.
     * @return Value of property printStream.
     *
     */
    public PrintStream getPrintStream() {
        return this.printStream;
    }
    
    /** Setter for property printStream.
     * @param printStream New value of property printStream.
     *
     */
    public void setPrintStream(PrintStream printStream) {
        this.printStream = printStream;
    }
    
    /** Setter for property byteStream.
     * @param byteStream New value of property byteStream.
     *
     */
    public void setByteStream(ByteArrayOutputStream byteStream) {
    }
    
    /** Getter for property lastAddressString.
     * @return Value of property lastAddressString.
     *
     */
    public String getLastAddressString() {
        return this.lastAddressString;
    }
    
    /** Setter for property lastAddressString.
     * @param lastAddressString New value of property lastAddressString.
     *
     */
    public void setLastAddressString(String lastAddressString) {
    }
    
    /** Getter for property lastAddress.
     * @return Value of property lastAddress.
     *
     */
    public address getLastAddress() {
        return this.lastAddress;
    }
    
    /** Setter for property lastAddress.
     * @param lastAddress New value of property lastAddress.
     *
     */
    public void setLastAddress(address lastAddress) {
        this.lastAddress = lastAddress;
    }
    
    
    public Object getMaritalStatus() {
        return findAttribute( maritalStatus);
        
    }
    
    public void setMaritalStatus(Object marital) {
        setAttribute(marital  );
    }
    
    
    public Object getAbo() {
        return findAttribute(ABO);
    }
    
    public void setAbo(Object abo) {
        setAttribute(abo );
    }
    
    public Object getRhesus() {
        return findAttribute(rhesus);
    }
    
    public void setRhesus(Object rh) {
        setAttribute(rh );
    }
    
    public Object[] getABOList() {
        return ABOList;
    }
    
    
    
    public Object[] getRhesusList() {
        return rhesusList;
    }
    
    
    /**
     * sets a category on the identity
     */
    void setAttribute( Object attribute) {
        
        category c = null;
        if (attribute instanceof category)
            c= (category ) attribute;
        if (c == null)
            return;
        
        logger.info(" category  returned " + c);
        if (getIdentity() == null)
            throw new RuntimeException("IDENTITY SHOULD EXIST");
        if (getIdentity().findCategoryAttribute(c.getCategory_type() ) == null) {
            category_attribute a = new category_attribute();
            a.setCategory(c);
            getIdentity().addClin_attribute(a);
            return;
        }
        getIdentity().findCategoryAttribute(c.getCategory_type()).setCategory(c);
    }
    
    Object findAttribute( category_type type) {
        category_attribute a = getIdentity().findCategoryAttribute(type);
        if ( a == null)
            return bundle.getString("unknown");
        return a.getCategory();
    }
    
    /** Getter for property managerReference.
     * @return Value of property managerReference.
     *
     */
    public ManagerReference getManagerReference() {
      return (ManagerReference) getIdentity().getPersister();
    }
    
    
    
}
