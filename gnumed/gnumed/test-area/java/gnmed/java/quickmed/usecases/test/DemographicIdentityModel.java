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
    
    /** Holds value of property identity. */
    private identity identity;
    /** Holds value of property uiModel. */
    private DemographicModel uiModel;
    
    /** Holds value of property lastAddressString. */
    private String lastAddressString;
    
    /** Holds value of property lastAddress. */
    private address lastAddress;
    
    private street undefinedStreet;
    
    private address addressEdited;
    
    /** Holds value of property managerReference. */
    private ManagerReference managerReference;
    
    private AddressValidator addressValidator;
    
    
    final static Logger logger = Logger.global;
    
    
    
    final static DateFormat shortestformat = new SimpleDateFormat("MM/yy");
   
    
    /** Holds value of property byteStream. */
    private ByteArrayOutputStream byteStream = new ByteArrayOutputStream();
    
    /** Holds value of property printStream. */
    private PrintStream printStream = new PrintStream(byteStream, true);
    
    
    
    /** Creates a new instance of DemographicIdentityModel */
    public DemographicIdentityModel() {
    }
    
    Names getNames() {
        if(  getIdentity().getNamess().size() == 0)
            getIdentity().addNames(new Names());
        return  (Names) getIdentity().getNamess().iterator().next();
    }
    
    
    public void setTelephone( String telephone, enum_telephone_role role) {
        if (telephone == null || role==null || telephone.trim().equals(""))
            return;
        
        if ( role.equals(TestGISManager.mobile) ) {
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
        getManagerReference().getGISManager().setTelephoneWithRoleAt(getIdentity(), telephone, role, TestGISManager.homeAddress);
        
        
        
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
        configureAddressValidator() ;
        
    }
    
    void configureAddressValidator() {
        
        addressValidator = new AddressValidator();
        if ( getManagerReference() != null)
        addressValidator.setGisManager(getManagerReference().getGISManager());
    }
    
    
    public String getAddress()  {
        identities_addresses ia = getIdentity().findIdentityAddressByAddressType(TestGISManager.homeAddress);
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
//////        logger.info("****** identity ****** birthdate = " + getIdentity().getDob());
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
        //        logger.info("*** LOOKING FOR  Telephone type = " + home.getRole());
        return getTelephone(TestGISManager.home);
    }
    
    public String getLastNames() {
        return getNames().getLastnames();
    }
    
    public String getMedicare() {
        return findSocialIdentity(IdentityManager.medicare).getNumber();
    }
    
    public String getMedicareExpiry() {
        return formatDate(findSocialIdentity(IdentityManager. medicare).getExpiry());
    }
    
    public String getMobilePhone() {
        if ( getIdentity().getMobile() == null)
            return "";
        return  getIdentity().getMobile().getNumber();
    }
    
    public String getNokPhone() {
        return  getTelephone(TestGISManager.nok);
    }
    
    public String getPensioner() {
        return findSocialIdentity( IdentityManager.pension).getNumber();
    }
    
    public String getPensionerExpiry() {
        return  formatDate(findSocialIdentity(IdentityManager.pension).getExpiry());
        
    }
    
    public String getPostcode() {
        return "postcode";
    }
    
    public String getRecordNo() {
        return findSocialIdentity(IdentityManager.recordNo).getNumber();
    }
    
    public String getSex() {
        if (getIdentity().getKaryotype() == null)
            return "";
        return getIdentity().getKaryotype().equals("XY") ? Globals.bundle.getString("male"): Globals.bundle.getString("female");
    }
    
    public String getWorkTelephone() {
        return  getTelephone(TestGISManager.work);
    }
    
    
    public String getTelephone( enum_telephone_role role) {
        try {
            return  getIdentity().findTelephoneByRole(role).getNumber();
        } catch (Exception e) {
            logger.fine(e.toString());
        }
        return "";
    }
    
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
    
  
    
    
    public void setAddress(String addressStr) {
        getManagerReference().getGISManager().updateAddress(getIdentity(),
        TestGISManager.homeAddress, addressValidator.getAddress(addressStr));
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
        setTelephone(homeTelephone, TestGISManager.home);
    }
    
    public void setLastNames(String lastNames) {
        getNames().setLastnames(lastNames.trim());
    }
    
    public void setMedicare(String _medicare) {
        setSocialIdentity(_medicare, IdentityManager.medicare, false);
    }
    
    public void setMedicareExpiry(String medicareExpiry) {
        setSocialIdentity( medicareExpiry, IdentityManager.medicare,  true);
    }
    
    public void setMobilePhone(String mobilePhone) {
        setTelephone(mobilePhone, TestGISManager.mobile);
    }
    
    public void setNokPhone(String nokPhone) {
        
        setTelephone(nokPhone, TestGISManager.nok);
    }
    
    public void setPensioner(String pensioner) {
        setSocialIdentity( pensioner, IdentityManager.pension, false);
    }
    
    public void setPensionerExpiry(String pensionerExpiry) {
        setSocialIdentity(pensionerExpiry, IdentityManager.pension, true);
    }
    
    public void setPostcode(String postcode) {
    }
    
    public void setRecordNo(String recordNoStr) {
        setSocialIdentity(recordNoStr,IdentityManager. recordNo, false);
    }
    
    public void setSex(String sex) {
        if (sex.equals(Globals.bundle.getString("male"))) {
            identity.setKaryotype("XY");
            return;
        }
        identity.setKaryotype("XX");
    }
    
    public void setWorkTelephone(String workTelephone) {
        setTelephone(workTelephone, TestGISManager.work);
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
        return IdentityManager.maritalList;
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
        return findAttribute( IdentityManager.maritalStatus);
        
    }
    
    public void setMaritalStatus(Object marital) {
        setAttribute(marital  );
    }
    
    
    public Object getAbo() {
        return findAttribute(IdentityManager.ABO);
    }
    
    public void setAbo(Object abo) {
        setAttribute(abo );
    }
    
    public Object getRhesus() {
        return findAttribute(IdentityManager.rhesus);
    }
    
    public void setRhesus(Object rh) {
        setAttribute(rh );
    }
    
    public Object[] getABOList() {
        return IdentityManager.ABOList;
    }
    
    
    
    public Object[] getRhesusList() {
        return IdentityManager.rhesusList;
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
            return Globals.bundle.getString("unknown");
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
