/*
 * DomainPrinter.java
 *
 * Created on 25 July 2003, 00:33
 */

package gnmed.test;
import org.gnumed.gmGIS.*;
import org.gnumed.gmIdentity.*;
import java.util.*;
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
        ps.print("\nAddresses:");
        Iterator ai = id.getIdentities_addressess().iterator();
        while (ai.hasNext()) {
            printIdentityAddresses(ps,  (identities_addresses) ai.next());
            ps.println();
        }
        ps.println();
     }
    
    public  void printAddress(java.io.PrintStream ps, address a) {
        urb u = a.getStreet().getUrb();
        street s = a.getStreet();
        u.getName();
        s.getName();
        a.getNumber();
        System.out.println("urb = " + u.getName() + " state = " + u.getState());
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
