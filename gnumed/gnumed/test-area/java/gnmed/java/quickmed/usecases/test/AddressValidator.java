/*
 * AddressVaidator.java
 *
 * Created on 21 August 2003, 12:10
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
 * @author  syan
 */
public class AddressValidator {
    
    final static Logger logger = Logger.global;
    
    final static String defaultWord = Globals.bundle.getString("default");
    final static String defaultStreetWord = Globals.bundle.getString("street");
    final static String defaultUrbWord = Globals.bundle.getString("urb");
    
    
    final static String alphaPhraseOnly = "([a-zA-Z\\s]+)?";
    final static String alphaPhrasePossesive = "([a-zA-Z\\s]++)?";
    final static String buildingPat = "([a-zA-Z|\\s]+[0-9]*)??"; // relunctant unless sep by comma,
    // so 'unit' 'flat' phrase captured by number field.
    final static String numberPat = "(\\d+|\\d+\\w?|\\d+\\W+\\d+|\\w+\\s+\\d+\\W*\\d*)?";
    final static String streetPat = alphaPhrasePossesive;
    final static String urbPat = alphaPhraseOnly;
    final static String statePat= alphaPhraseOnly ;
    final static String pcodePat = "(\\d+)?";
    final static String sepPat = "[,|\\s]+";
    final static String sepPatOpt = "[,|\\s]*";
    final static String addressParseRegex = new StringBuffer()
    .append(buildingPat).append(sepPatOpt)
    .append(numberPat).append(sepPat)
    .append(streetPat).append(sepPat).
    append(urbPat).append(sepPat).
    append(statePat).append(sepPatOpt).
    append(pcodePat).toString();
    
    final static int buildPos = 1; // null if not present
    final static int noPos = 2; // null if not present
    final static int streetPos = 3; // if street is not given but urb is, then will shift urb into street
    // so if urb is null but street isn't check that street is not an urb.
    final static int urbPos = 4;
    final static int statePos = 5;  // null if not present
    final static int pcodePos = 6;
    /** this regex Pattern will produce null for any empty indexes; urb and state should
     * preferably be comma separated
     */
    final static Pattern addressPattern = Pattern.compile(addressParseRegex);
    
    /** Holds value of property gisManager. */
    private TestGISManager gisManager;
    
    
    /** Creates a new instance of AddressVaidator */
    public AddressValidator() {
    }
    
    
    public address getAddress(  String addressStr) {
        logger.info("trying to parse " + addressStr);
        Matcher m = addressPattern.matcher(new StringBuffer( addressStr.trim()));
        if(!m.find()) {
            logger.info("not parseable = " + addressStr);
            return null;
        }
        String building = m.group(buildPos);
        String number = m.group(noPos);
        String streetS = m.group(streetPos);
        String urbS = m.group(urbPos);
        String state = m.group(statePos);
        String postcode = m.group(pcodePos);
        logger.info( " number = " + number + " street = " + streetS + " urbOrState = " + urbS + " postcode = " + postcode);
        
        
        
        street street = null;
        urb urb = null;
        address address = null;
        state stateObj = null;
        
        if (state != null)
            stateObj = getGisManager().findState(state);
        if (stateObj == null && postcode != null)
            stateObj = getGisManager().findStateByPostcode(postcode);
        
       
        // find by name first, some urbs share the same postcode
        if (urb == null && urbS != null)
            urb = findUrb(urbS, state);
        
        
         if (urb == null && postcode != null)
            urb = findUrb(postcode);
        
        if (urb == null)
            urb = getDefaultUrbFor(stateObj);
        
        if (streetS != null)
            street = findStreet(streetS, urb);
        
        if ( street == null)
            street = getDefaultStreetFor(urb);
        
        return getAddressFor( building, number, street);
        
        
    }
    
    public urb findUrb(String postcode) {
        try {
            return getGisManager().findUrbByPostcode(postcode);
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }
    
    
    public urb findUrb(String urbStr, String stateStr) {
        try {
            return getGisManager().findUrbByNameAndState(urbStr, stateStr);
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }
    
    public urb getDefaultUrbFor(state state) {
        return getGisManager().createOrFindNamedUrb( defaultWord + " " + defaultUrbWord, state );
        
    }
    
    public street findStreet(String street,urb  urb) {
        street s= null;
        if (street == null )
            return s;
        try {
            s = getGisManager().findStreetByNameAndUrb(street, urb);
            if (s == null)
                s = getGisManager().createStreet(street, urb);
            if (s == null)
                throw new Exception("UNABLE TO CREATE street" + street + "urb" + urb);
        } catch (Exception e) {
            e.printStackTrace();
        }
        return s;
    }
    
    public street getDefaultStreetFor(urb  urb) {
        return  findStreet( defaultWord + " " + defaultStreetWord, urb) ;
        
    }
    
    public static String getCombinedBuildingNumberString(String building, String number) {
        StringBuffer sb = new StringBuffer();
        
        if (building != null)
            sb.append(building);
        if ( number != null) {
            if (building != null)
                sb.append(", ");
            
            sb.append(number);
        }
        return sb.toString();
    }
    
    public address getAddressFor(  String building, String number, street street) {
        
        String noStr = getCombinedBuildingNumberString(building, number);
        address a = null;
        logger.info("using info " + noStr + " street = " + street);
        logger.info("street info = " + street.getName() + street.getUrb());
        
        try {
           a = getGisManager().createOrFindAddress( noStr, street);
        } catch (Exception e) {
            e.printStackTrace();
        }
        return a;
        
    }
    
    /** Getter for property gisManager.
     * @return Value of property gisManager.
     *
     */
    public TestGISManager getGisManager() {
        return this.gisManager;
    }
    
    /** Setter for property gisManager.
     * @param gisManager New value of property gisManager.
     *
     */
    public void setGisManager(TestGISManager gisManager) {
        this.gisManager = gisManager;
    }
    
}
