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
    
    
    
    static Logger logger;
    static ResourceBundle bundle = ResourceBundle.getBundle("SummaryTerms");
    
    
    private static Method[] socialIdSetters = null;
    private static Method[] addrTypeSetter =null;
    static {
        logger = Logger.getLogger("DemographicIdentityModel");
        logger.setLevel(Level.ALL);
        //        logger.addHandler(new ConsoleHandler());
        try {
            socialIdSetters = new Method[] { enum_social_id.class.getMethod("setName", new Class[] { String.class}),
            enum_social_id.class.getMethod("setId", new Class[]{ Integer.class}) };
            
            addrTypeSetter = new Method[] {
                address_type.class.getMethod("setName",  new Class[] { String.class})
            };
            logger.info("CREATED socialIdSetters and AddrTypeSetter");
        } catch (Exception e) {
            e.printStackTrace();
            System.exit(-1);
        }
    }
    static DateFormat shortestformat = new SimpleDateFormat("MM/yy");
    
    
    
    static enum_telephone_role home = createOrFindEnumTelephone( bundle.getString("home"));
    static  enum_telephone_role work= createOrFindEnumTelephone( bundle.getString("work"));
    static enum_telephone_role mobile = createOrFindEnumTelephone( bundle.getString("mobile"));
    static enum_telephone_role nok = createOrFindEnumTelephone( bundle.getString("nok"));
    static enum_social_id pension = createOrFindEnumSocialId(bundle.getString("pension") , 2);
    static enum_social_id medicare =createOrFindEnumSocialId(bundle.getString("medicare"), 1);
    static enum_social_id recordNo = createOrFindEnumSocialId(bundle.getString("record_no"), 3);
    static address_type homeAddress = createOrFindAddressType(bundle.getString("home"));
    
    static Map mapMarital ;
    static category_type maritalStatus = createOrFindCategoryType( bundle.getString("marital_status") );
    static category married = createOrFindCategory( bundle.getString("married"), maritalStatus);
    static  category unmarried = createOrFindCategory( bundle.getString("unmarried"), maritalStatus);
    static    category divorced = createOrFindCategory( bundle.getString("divorced"), maritalStatus);
    static   category widowed = createOrFindCategory( bundle.getString("widowed"), maritalStatus);
    static category unknown = createOrFindCategory( bundle.getString("unknown"), maritalStatus);
    static category [] maritalList = new category[] { married, unmarried, divorced, widowed };
    
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
            logger.info("CREATED mapMarital");
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
    public static Map createMap( Method keyGetter, List list) {
        Map map = new HashMap();
        for (int i = 0; i < list.size(); ++i) {
            try {
                map.put( keyGetter.invoke(list.get(0), new Object[0]), list.get(0));
            } catch (Exception e) {
                logger.info(e.getMessage());
            }
        }
        return map;
    }
    
    /** finds an entity with a particular attribute, or creates it
     */
    public static Object createOrFindEntity( String query,final  Object[] params, Type[] types,
    Class targetClass, Method[] paramSetters) throws Exception  {
        Object newObject = null;
        Session s = null;
        try {
            s=  HibernateInit.openSession();
            newObject = s.iterate(query, params, types).next();
            if (newObject != null) {
                return newObject;
            }
            throw new  Exception("No object found");
        } catch (Exception e) {
            try {
                logger.info("Unable to find a " + targetClass.getName() + " with specified parameters . CREATING NEW ONE");
                newObject = targetClass.newInstance();
                for (int i = 0; i < paramSetters.length; ++i) {
                    paramSetters[i].invoke(newObject, new Object[] { params[i] } );
                }
                s.save(newObject);
                s.flush();
                s.connection().commit();
                logger.info("SUCCESSFULLY CREATED a " +  targetClass.getName() );
                return newObject;
            } catch ( Exception e2) {
                s.disconnect();
                s.close();
                throw e2;
            }
        } finally {
            logger.info("DISCONNECTING AND CLOSING " + s.toString());
            //  s.disconnect();
            s.close();
            
        }
        //        return newObject;
    }
    
    static category_type createOrFindCategoryType( String type) {
        try {
            return (category_type) createOrFindEntity(
            "from org.gnumed.gmClinical.category_type as t where t.name= ?",
            new Object[] { type  },
            new Type[] { Hibernate.STRING },
            category_type.class,
            new Method[] { category_type.class.getMethod("setName", new Class[] { String.class } ) }
            );
            
        } catch (Exception e) {
            e.printStackTrace();
            category_type t = new category_type();
            t.setName(type);
            return t;
        }
    }
    
    static category createOrFindCategory( String type, category_type superType ) {
        try {
            category t = (category) createOrFindEntity(
            "from org.gnumed.gmClinical.category  as t where t.name= ? and t.category_type.name = ?",
            new Object[] { type , superType.getName() },
            new Type[] { Hibernate.STRING, Hibernate.STRING},
            category.class ,
            new Method[] { category.class.getMethod("setName", new Class[] { String.class } ) }
            );
            t.setCategory_type(superType);
            Session sess = HibernateInit.openSession();
            sess.update(t);
            sess.flush();
            sess.connection().commit();
            sess.close();
            return t;
        } catch (Exception e) {
            e.printStackTrace();
            category  t = new category();
            t.setName(type);
            t.setCategory_type(superType);
            return t;
        }
    }
    
    static address_type createOrFindAddressType( String type) {
        try {
            return (address_type) createOrFindEntity(
            "from org.gnumed.gmGIS.address_type as t where t.name = ?",
            new Object[] { type  },
            new Type[] { Hibernate.STRING },
            address_type.class,
            addrTypeSetter  );
        } catch (Exception e) {
            e.printStackTrace();
            address_type atype = new address_type();
            atype.setName(type);
            return atype;
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
        logger.info("CREATED STREET " + st.getName() + " in urb " + st.getUrb());
        logger.info("urb name ="+ st.getUrb().getName());
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
    
    
    public static boolean isStateString(String state) {
        try {
            Session s = HibernateInit.openSession();
            String v = state.toUpperCase().trim() ;
            logger.info("SEEING IF " + v + " is a STATE STRING .");
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
                sess.close();
                return createStreet( street, u);
            }
            
            
            street s = (street) it.next() ;
            sess.close();
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
        if ( role == mobile) {
            telephone t = new telephone();
            t.setEnum_telephone_role(role);
            t.setNumber(telephone);
            identity.setMobile(t);
            logger.info("identity mobile set to " + t.getNumber());
            return;
        }
        // THIS DEPENDS ON AN ADDRESS EXISTING FOR THE PATIENT. MAY NEED DEFAULT ADDRESS.
        
        Iterator i = getIdentity().getIdentities_addressess().iterator();
        while (i.hasNext()) {
            identities_addresses ia = (identities_addresses) i.next();
            address  a = ia.getAddress();
            if ( a.getTelephones().size() == 0)
                a.addTelephone(new telephone());
            telephone t = (telephone) a.getTelephones().iterator().next();
            t.setNumber(telephone);
            t.setEnum_telephone_role(role);
        }
        
    }
    
    Date parseDate( Object val) {
        String s = (String) val;
        try {
            return (Date)shortestformat.parse(s.trim());
        } catch (Exception e) {
            logger.info("UNABLE TO PARSE into DATE: " + s);
            
        }
        return new Date();
    }
    
    void setSocialIdentityAttr( social_identity si, Object val, boolean expiry) {
        if (expiry)
            si.setExpiry((Date) parseDate(val));
        else
            si.setNumber((String)val);
        logger.info(si.toString() + " set with " + val.toString() + "is expiry = " + new Boolean(expiry).toString());
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
            gnmed.test.DomainPrinter.getInstance().printAddress( getPrintStream(),  ia.getAddress());
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
        return getIdentity().findNames(0).getFirstnames();
    }
    
    public String getHomeTelephone() {
        return getIdentity().findTelephoneByRole(home).getNumber();
    }
    
    public String getLastNames() {
        return getIdentity().findNames(0).getLastnames();
    }
    
    public String getMedicare() {
        return "medicare";
    }
    
    public String getMedicareExpiry() {
        return "MedicareExp";
    }
    
    public String getMobilePhone() {
        return  getIdentity().findTelephoneByRole(mobile).getNumber();
    }
    
    public String getNokPhone() {
        return "nok phone";
    }
    
    public String getPensioner() {
        return "pensioner";
    }
    
    public String getPensionerExpiry() {
        return "pension exp";
        
    }
    
    public String getPostcode() {
        return "postcode";
    }
    
    public String getRecordNo() {
        return "recordno";
    }
    
    public String getSex() {
        return getIdentity().getKaryotype().equals("XY") ? "male":"female";
    }
    
    public String getWorkTelephone() {
        return  getIdentity().findTelephoneByRole(work).getNumber();
    }
    
    static Pattern addressPattern =
    Pattern.compile("\\s*(\\d+|\\d+\\w?|\\d+\\W+\\d+)[,|\\s]+([\\w|\\s]+)[,|\\s]+(\\D+)[,|\\s]*(\\d+)?");
    
    /** Holds value of property lastAddressString. */
    private String lastAddressString;
    
    /** Holds value of property lastAddress. */
    private address lastAddress;
    
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
            return  TestGISManager.instance().findByPostcode(postcode);
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
            return  TestGISManager.instance().findUrbByNameAndState(name, state);
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
            street s = TestGISManager.instance().findStreetByNameAndUrb(street, urb );
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
        TestGISManager.instance().updateAddress(getIdentity(), homeAddress, a);
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
    
    
    public Object getMaritalStatus() {
        category_attribute a = getIdentity().findCategoryAttribute(maritalStatus);
        if ( a == null)
            return bundle.getString("unknown");
        return a.getCategory().getName();
    }
    
    public void setMaritalStatus(Object maritalStatus) {
        category c = (category ) maritalStatus;
        if (c == null)
            c = unmarried;
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
    
    
    public void setHomeTelephone(String homeTelephone) {
        setTelephone(homeTelephone, home);
    }
    
    public void setLastNames(String lastNames) {
        getNames().setLastnames(lastNames);
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
    
}
