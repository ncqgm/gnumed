/*
 * TestBasicScriptPrintableFactory.java
 *
 * Created on 29 August 2003, 14:47
 */

package quickmed.usecases.test;
import org.drugref.*;
import org.gnumed.gmClinical.*;
import org.gnumed.gmIdentity.*;
import org.gnumed.gmGIS.*;
import java.util.GregorianCalendar;
import java.util.*;
import java.awt.print.*;
import javax.swing.*;
import java.awt.event.*;
import java.util.logging.*;
/**
 *
 * @author  syan
 */
public class TestBasicScriptPrintable {
    private BasicScriptPrintable printable;
    
    /** Creates a new instance of TestBasicScriptPrintableFactory */
    public TestBasicScriptPrintable() {
        try {
            test();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    /** Setter for property basicScriptPrintable.
     */
    public void setBasicScriptPrintable( BasicScriptPrintable printable) {
        this.printable = printable;
    }
    
    /** Getter for property basicScriptPrintable.
     * @return Value of property basicScriptPrintable.
     *
     */
    public BasicScriptPrintable getBasicScriptPrintable() {
        return printable;
    }
    
    
    /** minimal provider information for script */
    identity createProvider() {
        identity provider = createIdentity("John", "Smith", "Dr", "3193", "Newman st", "34", "work" );
        
        social_identity sid = new social_identity();
        sid.setEnum_social_id(IdentityManager.prescriberNo);
        sid.setNumber("222444");
        provider.addSocial_identity(sid);
        
        social_identity provider_no = new social_identity();
        provider_no.setEnum_social_id(IdentityManager.providerNo);
        provider_no.setNumber("2224444XX");
        provider.addSocial_identity(provider_no);
        
        telephone t = new telephone();
        t.setNumber("5555 3333");
        t.setEnum_telephone_role(TestGISManager.instance().work);
        provider.findIdentityAddressByAddressType(TestGISManager.workAddress).getAddress().addTelephone(t);
        return provider;
    }
    
    /** minimal patient information for script */
    identity createPatient() {
        identity patient = createIdentity("David", "Doe", "Mr.", "3192", "Harold st", "33", "home");
        social_identity sid = new social_identity();
        sid.setEnum_social_id(IdentityManager.medicare);
        sid.setNumber("111144445555");
        sid.setExpiry(new GregorianCalendar(2005, 12, 1).getTime());
        patient.addSocial_identity(sid);
        return patient;
    }
    
    
    identity createIdentity( String firstName, String lastName, String title,
    String postcode, String streetName, String houseNumber,
    String addressType ) {
        
        identity provider = new identity();
        Names names = new Names();
        names.setFirstnames(firstName);
        names.setLastnames(lastName);
        names.setTitle(title);
        provider.addNames(names);
        
        urb urb = new urb();
        urb.setName("FALLTHROUGH URB");
        street street = new street();
        street.setUrb(urb);
        
        try {
            urb = TestGISManager.instance().findUrbByPostcode(postcode);
        } catch (Exception e) {
            e.printStackTrace();
        }
        try {
            
            street = TestGISManager.instance().createOrFindStreet(streetName, urb);
            
            
        } catch (Exception e) {
            e.printStackTrace();
        }
        
        address address = TestGISManager.instance().createOrFindAddress(houseNumber, street);
        
        identities_addresses ia = new identities_addresses();
        
        if ( addressType.toLowerCase().trim().equals("work"))
            ia.setAddress_type(TestGISManager.instance().workAddress);
        
        if ( addressType.toLowerCase().trim().equals("home"))
            ia.setAddress_type(TestGISManager.instance().homeAddress);
        
        ia.setAddress(address);
        provider.addIdentities_addresses(ia);
        return provider;
    }
    
    link_script_drug createLinkScriptDrug(String drugName, String instructions, Double qty, Integer repeats ) throws Exception {
        link_script_drug lsd = new link_script_drug();
        script_drug sd = new script_drug();
        List packages = TestScriptDrugManager.instance().findPackagedProductByDrugName(drugName);
        displaySubsidized(packages);
        package_size pz = null;
        if (packages.size() > 0) {
            pz = (package_size) packages.get(0);
        }
        sd.setPackage_size(pz);
        sd.setDirections(instructions);
        sd.setQty(qty);
        lsd.setRepeats(repeats);
        lsd.setScript_drug(sd);
        return lsd;
    }
    
    void displaySubsidized(List packages) {
        for (int i = 0; i < packages.size(); ++i) {
            package_size pz = (package_size) packages.get(i);
            Logger.global.info(pz.getProduct().getComment() +   "subsidized count ="+ Integer.toString(pz.getProduct().getSubsidized_productss().size()) );
        }
    }
    
    link_script_drug[] getTestScriptDrugs() {
        String [] drugNames = { "salbutamol", "fluticasone", "prednisolone", "orlistat" };
        String [] instructions = { "2 puffs 4/24 prn", "2 puffs bd", "1 daily for 3 days", "1 tds" };
        double [] qtys = { (double) 2.0 , (double) 1.0, (double) 30 , (double) 30 };
        int[] repeats = { 5, 5, 0, 5 };
        link_script_drug[] lsds = new link_script_drug[drugNames.length];
        for (int i = 0; i < drugNames.length; ++i) {
            try {
                lsds[i] = createLinkScriptDrug(drugNames[i], instructions[i],
                new Double(qtys[i]), new Integer( repeats[i] )  );
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
        return lsds;
    }
    
    
    public void test() throws Exception {
        BasicScriptPrintable printable = new MedicareBasicScriptPrintable();
        printable.setPrescriber(createProvider());
        printable.setPatient(createPatient());
        printable.setScriptDate(new Date());
        printable.setScriptItems( Arrays.asList(getTestScriptDrugs()) );
        setBasicScriptPrintable(printable);
        
        //        Pageable pageable = printable.getPageable();
        //        JFrame f = new JFrame("Test Prescription Graphics");
        //
        //        f.getContentPane().setSize(1000, 800);
        //        f.setVisible(true);
        //        List images = new ArrayList();
        //        for (  int i = 0; i < pageable.getNumberOfPages(); ++i) {
        //
        //            final Printable p  = pageable.getPrintable(i);
        //            final java.awt.Graphics g = f.getContentPane().getGraphics();
        //
        //            g.setClip(0,0, 1000, 800);
        //            final int j = i;
        //            f.addWindowStateListener( new WindowStateListener() {
        //                public void windowStateChanged(WindowEvent we) {
        //
        //
        //
        //            SwingUtilities.invokeLater( new Runnable() {
        //                public void run() {
        //                    try {
        //                        p.print(g, new PageFormat(), j);
        //                    } catch (Exception e) {
        //                        e.printStackTrace();
        //                    }
        //                }
        //            } );
        //                }
        //            } );
        //        }
    }
    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) throws Exception {
        TestBasicScriptPrintable test = new TestBasicScriptPrintable();
        test.test();
        if (args == null || args.length == 0)  {
            //            test.setBasicScriptPrintable( new MedicareBasicScriptPrintable() ) ;
        } else {
        }
        
    }
    
    
}
