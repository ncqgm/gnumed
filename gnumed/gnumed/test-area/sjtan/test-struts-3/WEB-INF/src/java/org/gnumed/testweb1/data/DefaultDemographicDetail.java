/*
 * DefaultDemographicDetails.java
 *
 * Created on June 19, 2004, 3:57 PM
 */

package org.gnumed.testweb1.data;

import java.beans.*;
import java.io.Serializable;
import java.util.Date;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import java.text.DateFormat;
import java.text.ParseException;
import java.util.Locale;
import org.gnumed.testweb1.global.Util;
/**
 * @author sjtan
 */
public class DefaultDemographicDetail implements Serializable, DemographicDetail {
    
    private Date birthdateValue;
    private String birthdate;
    private String email;
    private String fax;
    private String givenname;
    private String homePhone;
    private String mobile;
    private String postcode;
    private String privateHealthId;
    private String privateHealthProvider;
    private String publicHealthId;
    private String publicHealthIdExp;
    private String sex;
    private String state;
    private String street;
    private String streetno;
    private String surname;
    private String title;
    private String urb;
    private String veteransId;
    private String workPhone;
    private Long id;
    private String countryCode;
    
    private PropertyChangeSupport propertySupport;
    
    
    Log log = LogFactory.getFactory().getLog(this.getClass());
    
    
    
    public DefaultDemographicDetail() {
        propertySupport = new PropertyChangeSupport(this);
    }
    
    
    
    public void addPropertyChangeListener(PropertyChangeListener listener) {
        propertySupport.addPropertyChangeListener(listener);
    }
    
    public void removePropertyChangeListener(PropertyChangeListener listener) {
        propertySupport.removePropertyChangeListener(listener);
    }
    
    public String getBirthdate() {
        birthdate = DateFormat.
        getDateInstance(DateFormat.SHORT).format(getBirthdateValue());
        
        return birthdate;
        
    }
    
    public String getEmail() {
        return email;
    }
    
    public String getFax() {
        return fax;
    }
    
    public String getGivenname() {
        return givenname;
    }
    
    public String getHomePhone() {
        return homePhone;
    }
    
    public String getMobile() {
        return mobile;
        
    }
    
    public String getPostcode() {
        return postcode;
    }
    
    public String getPrivateHealthId() {
        return privateHealthId;
    }
    
    public String getPrivateHealthProvider() {
        return privateHealthProvider;
    }
    
    public String getPublicHealthId() {
        return publicHealthId;
    }
    
    public String getPublicHealthIdExp() {
        return publicHealthIdExp;
    }
    
    public String getSex() {
        return sex;
    }
    
    public String getState() {
        return state;
    }
    
    public String getStreet() {
        return street;
    }
    
    public String getStreetno() {
        return streetno;
    }
    
    public String getSurname() {
        return surname;
    }
    
    public String getTitle() {
        return title;
    }
    
    public String getUrb() {
        return urb;
    }
    
    public String getVeteransId() {
        return veteransId;
    }
    
    public String getWorkPhone() {
        return workPhone;
    }
    
    
    public void setEmail(String email) {
        this.email = email;
    }
    
    public void setFax(String fax) {
        this.fax = fax;
    }
    
    public void setGivenname(String givenname) {
        this.givenname = givenname;
    }
    
    public void setHomePhone(String homePhone) {
        this.homePhone = homePhone;
        
    }
    
    public void setMobile(String mobile) {
        this.mobile = mobile;
    }
    
    public void setPostcode(String postcode) {
        this.postcode = postcode;
    }
    
    public void setPrivateHealthId(String privateHealthId) {
        this.privateHealthId = privateHealthId;
    }
    
    public void setPrivateHealthProvider(String privateHealthProvider) {
        this.privateHealthProvider = privateHealthProvider;
    }
    
    public void setPublicHealthId(String publicHealthId) {
        this.publicHealthId = publicHealthId;
    }
    
    public void setPublicHealthIdExp(String publicHealthIdExp) {
        this.publicHealthIdExp = publicHealthIdExp;
    }
    
    public void setSex(String sex) {
        this.sex = sex;
        
    }
    
    public void setState(String state) {
        this.state = state;
        if (this.state != null)
            this.state = state.trim();
    }
    
    public void setStreet(String street) {
        this.street = street;
    }
    
    public void setStreetno(String streetno) {
        this.streetno = streetno;
        if ( this.streetno != null)
            this.streetno = this.streetno.trim();
    }
    
    public void setSurname(String surname) {
        this.surname = surname
        ;
    }
    
    public void setTitle(String title) {
        this.title = title;
    }
    
    public void setUrb(String urb) {
        this.urb = urb;
    }
    
    public void setVeteransId(String veteransId) {
        this.veteransId = veteransId;
    }
    
    public void setWorkPhone(String workPhone) {
        this.workPhone = workPhone;
    }
    
    public Long getId() {
        return id;
    }
    
    public void setId(Long id) {
        this.id = id;
    }
    
    public void setBirthdate(String birthdate) {
        
        if (birthdate==null)
            return;
        this.birthdate = birthdate.trim();
        if ("".equals(this.birthdate))
            return;
        
        try {
            
            Date date = (Date) Util.parseDate(birthdate);
            setBirthdateValue(date);
            
        } catch (Exception e2) {
            log.error("Tried last parse attempt: " ,e2);
        }
        
    }
    
    public java.util.Date getBirthdateValue() {
        return this.birthdateValue;
    }
    
    public void setBirthdateValue(java.util.Date birthdateValue) {
        this.birthdateValue = birthdateValue;
    }
    
    public String getCountryCode() {
        return countryCode;
    }
    
    public void setCountryCode(String countryCode) {
        this.countryCode = countryCode;
    }
    
    public String getPublicHealthIdWithExp() {
        return getPublicHealthId() + " (" + getPublicHealthIdExp()+")";
    }
    
    public void setPublicHealthIdWithExp(String publicHealthIdWithExp) {
        String[] parts = publicHealthIdWithExp.split("[\\(\\)]");
        if (parts == null) return;
        log.info(parts);
        if (parts.length > 0)
            setPublicHealthId(parts[0]);
        if (parts.length > 1)
            setPublicHealthIdExp(parts[1]);
    }
    
}

