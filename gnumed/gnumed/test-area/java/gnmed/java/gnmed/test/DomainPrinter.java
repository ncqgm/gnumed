/*
 * DomainPrinter.java
 *
 * Created on 25 July 2003, 00:33
 */

package gnmed.test;
import org.gnumed.gmGIS.*;
import org.gnumed.gmIdentity.*;
import java.util.*;
import org.gnumed.gmClinical.*;
import org.drugref.*;

/**
 *
 * @author  sjtan
 */
public class DomainPrinter {
    static SortedSet males;
    static DomainPrinter instance;
    static {
        males = new TreeSet(Arrays.asList( new String[] { "XXY", "XY", "XYY" }));
        instance = new DomainPrinter();
    };
    
    /** Creates a new instance of DomainPrinter */
    public DomainPrinter() {
    }
    
    
    public static DomainPrinter getInstance() {
        return instance;
    }
    
    public  void printNames( java.io.PrintStream ps, Names names) {
        ps.print(names.getFirstnames());
        ps.print(" ");
        ps.print(names.getLastnames());
    }
    
    public  void printIdentityAddresses( java.io.PrintStream ps, identities_addresses idAddr) {
        printAddrType(ps, idAddr.getAddress_type());
        ps.print(": ");
        printAddress(ps, idAddr.getAddress());
    }
    
    
    public  void printIdentity( java.io.PrintStream ps, identity id) {
        Iterator ni = id.getNamess().iterator();
        for (int i = 0; ni.hasNext(); ++i) {
            if (i > 0)
                ps.print("alias: ");
            printNames(ps, (Names)ni.next());
            ps.println();
        }
        
        ps.print("birthdate ");
        ps.print(id.getDob());
        ps.print(", ");
        ps.print("sex: ");
        ps.print( males.contains(id.getKaryotype().toUpperCase()) ? "male": "female");
        ps.print("\nAddresses:\n");
        Iterator ai = id.getIdentities_addressess().iterator();
        while (ai.hasNext()) {
            ps.print("\t");
            printIdentityAddresses(ps,  (identities_addresses) ai.next());
            
        }
        ps.println();
        if (id.getClin_health_issues().size() > 0) {
            ps.println("**** Health Issues *****");
            Iterator ci = id.getClin_health_issues().iterator();
            while (ci.hasNext()) {
                printClinHealthIssue(ps, (clin_health_issue) ci.next());
            }
            ps.println();
            ps.println();
        }
        
        if ( id.getClin_encounters().size() > 0) {
            ps.println("*******clinical encounters************");
            Iterator ei = id.getClin_encounters().iterator();
            while(ei.hasNext()) {
                clin_encounter encounter = (clin_encounter) ei.next();
                printClinEncounter( ps, encounter);
                ps.println();
            }
        }
        
        if(id.getScript_drugs().size() > 0)  {
            ps.println("***********MEDICATIONS***************");
            Iterator sdi = id.getScript_drugs().iterator();
            while ( sdi.hasNext()) {
                script_drug sd = (script_drug) sdi.next();
                printScriptDrug( ps, sd);
                ps.println();
            }
        }
    }
    
    public static void printScriptDrug( java.io.PrintStream ps, script_drug sd) {
        product p = sd.getProduct();
        drug_element de = p.getDrug_element();
        generic_drug_name name = (de.getGeneric_name().size() > 0) ?(generic_drug_name) de.getGeneric_name().iterator().next(): null;
        if (name != null )
            ps.print(name.getName());
        else
            if ( p != null && de != null && de.getAtcs().size() > 0) {
                atc atc = (atc) de.getAtcs().iterator().next();
                ps.print(atc.getText());
            } else {
                ps.print(p.getId() + ":drug with no ATC");
            }
        
        ps.print("\t");
        ps.print(sd.getDose_amount());
        drug_units units = p.getDrug_units();
        if ( units != null && !units.getUnit().equals("each"))
            ps.print(p.getDrug_units().getUnit());
        ps.print(" ");
        ps.print(sd.getProduct().getDrug_formulations().getDescription());
        if (p.getDrug_routes() != null) {
            ps.print(" taken ");
            ps.print(sd.getProduct().getDrug_routes().getDescription());
        }
        ps.print(" ");
        ps.print(sd.getFrequency());
        ps.print(" ");
        ps.print(sd.getDirections());
        ps.print("\t");
        if ( sd.getProduct().getPackage_sizes().size() > 0) {
            package_size sz = (package_size)sd.getProduct().getPackage_sizes().iterator().next();
            ps.print(  sz.getSize().intValue() );
            ps.print(" x ");
        }
        ps.print(sd.getProduct().getComment());
    }
    
    static class ClinRootItemComparator implements  Comparator {
        
        static Map map = new HashMap();
        static {
            map.put("clin_history", "a");
            map.put("allergy", "b");
            map.put("clin_physical", "c");
            map.put("clin_note", "d");
            map.put("script", "e");
        };
        
        static String getClassNameOnly( Object o) {
            String name = o.getClass().getName();
            return name.substring(name.lastIndexOf(".")+1);
        }
        
        static Comparable getOrdinal( Object o) {
            return (Comparable)  map.get(getClassNameOnly(o) );
        }
        
        public int compare(Object o1, Object o2) {
            return getOrdinal(o1).compareTo(getOrdinal(o2));
            
        }
        
    }
    
    TreeSet orderedRootItems = new TreeSet( new DomainPrinter.ClinRootItemComparator());
    
    void printClinEncounter( java.io.PrintStream ps, clin_encounter e) {
        //        clin_root_item dummy = new clin_root_item();
        //        e.addClin_root_item(dummy);
        //        e.removeClin_root_item(dummy);
        ps.print("Seen by ");
        printNames(ps, (Names)e.getProvider().getNamess().iterator().next());
        ps.print(" at ");
        printAddress(ps, e.getLocation());
        ps.print("PROBLEM: ");
        ps.println(e.getDescription());
        orderedRootItems.clear();
        orderedRootItems.addAll( e.getClin_root_items());
        Iterator i = orderedRootItems.iterator();
        while (i.hasNext()) {
            printClinRootItem( ps, (clin_root_item) i.next());
        }
    }
    
    void printClinRootItem( java.io.PrintStream ps, clin_root_item item) {
        ps.print(DomainPrinter.ClinRootItemComparator.getClassNameOnly(item));
        ps.println(":");
        ps.print(item.getNarrative());
        ps.println();
    }
    
    public  void printAddress(java.io.PrintStream ps, address a) {
        urb u = a.getStreet().getUrb();
        street s = a.getStreet();
        u.getName();
        s.getName();
        a.getNumber();
        //     System.out.println("urb = " + u.getName() + " state = " + u.getState());
        state sta = u.getState();
        sta.getName();
        ps.println("Address = " +  a.getNumber() + ", "+s.getName() + ", "+u.getName()+", "+sta.getName() + " "+u.getPostcode());
    }
    
    public  void printAddrTypes( java.io.PrintStream ps, java.util.List list) {
        for (int i  = 0; i < list.size(); ++i)  {
            printAddrType(  ps,  (address_type) list.get(i) );
            ps.print("  ");
        }
    }
    
    public  void printAddrType( java.io.PrintStream ps, address_type type) {
        ps.print(type.getName());
    }
    
    public void printClinHealthIssue(  java.io.PrintStream ps,  clin_health_issue issue) {
        ps.println(issue.getDescription());
        
        Iterator i = issue.getClin_issue_components().iterator();
        while (i.hasNext()) {
            clin_issue_component comp = (clin_issue_component) i.next();
            if (comp instanceof clin_diagnosis) {
                ps.print("\t");
                printClinDiagnosis(ps, (clin_diagnosis)comp);
                ps.println();
            }
        }
    }
    
    public void printClinDiagnosis(java.io.PrintStream ps, clin_diagnosis diagnosis) {
        ps.print(diagnosis.getApprox_start());
        ps.print("  ");
        code_ref cref = diagnosis.getCode_ref();
        disease_code dcode = cref.getDisease_code();
        ps.print(dcode.
        getDescription());
    }
    
    public static  String getStringList(String[] list) {
        if (list == null)
            return null;
        StringBuffer b = new StringBuffer();
        for (int i = 0; i < list.length; ++i) {
            b.append(list[i]);
            b.append("  ");
        }
        // System.out.println(b.toString());
        return b.toString();
    }
}
