/*
 * DrugRefAccessImpl1.java
 *
 * Created on October 10, 2004, 4:35 PM
 */

package org.gnumed.testweb1.persist.scripted.gnumed1;
import java.sql.*;
import java.util.*;
import org.gnumed.testweb1.data.DrugRefConstructed;
import org.gnumed.testweb1.data.DrugRef;
import org.apache.commons.logging.*;
//import org.gnumed.testweb1.global.GrantSetupDialog;

/**
 *
 * @author  sjtan
 */
public class DrugRefAccessImpl1 implements DrugRefAccess {
    javax.sql.DataSource dataSource;
    org.gnumed.testweb1.data.DataObjectFactory factory;
    java.sql.Connection superConn=null;
    static Log log = LogFactory.getLog(DrugRefAccessImpl1.class);
    
    /** Creates a new instance of DrugRefAccessImpl1 */
    public DrugRefAccessImpl1()  {
        
    }
    
    public org.gnumed.testweb1.data.DrugRef[] findDrugRef(String name) throws java.sql.SQLException {
        if (name == null )
            return new org.gnumed.testweb1.data.DrugRef[0];
        
        name = name.trim();
        
        if ("".equals(name))
            return  new org.gnumed.testweb1.data.DrugRef[0];
        
        String s2 =  SELECT_DRUGREF + " where position ( lower( ? ) in lower("+
        BRAND_NAME + ") ) > 0 or position ( lower( ? ) in lower(" +  ATC_NAME + ") ) > 0";
        Connection conn = getDataSource().getConnection();
        PreparedStatement stmt = conn.prepareStatement(s2);
        stmt.setString(1, name);
        stmt.setString(2, name);
        stmt.execute();
        
        ResultSet rs = stmt.getResultSet();
        List l = new ArrayList();
        while(rs.next()) {
            DrugRefConstructed drugRef = getDataObjectFactory().createDrugRefConstructed();
            drugRef.setAttributes(
            new Integer(rs.getInt(ID_PRODUCT)),
            rs.getString(BRAND_NAME),
            rs.getString(ATC_NAME),
            rs.getString(ATC_CODE),
            rs.getString(DRUG_SHORT_DESCRIPTION),
            rs.getInt( SUBSIDIZIED_QTY),
            rs.getInt(MAX_RPT),
            rs.getInt(PKG_SIZE),
            rs.getString(SUBSIDY_SCHEME),
            rs.getString(DRUG_FORMULATION),
            rs.getString(AMOUNT_UNIT)
            );
            l.add(drugRef);
            
        }
        return (DrugRef[]) l.toArray(new DrugRef[0]);
        
    }
    
    public org.gnumed.testweb1.data.DataObjectFactory getDataObjectFactory() {
        return factory;
    }
    
    public javax.sql.DataSource getDataSource() {
        return dataSource;
    }
    
    public void load() throws java.sql.SQLException {
        
//        Connection conn = getDataSource().getConnection();
//        
//        Statement stmt = conn.createStatement();
//        
//        conn.rollback();
////        for (int k = 0; k < 3; ++k ) {
//            boolean denied = false;
//            try {
//                stmt.executeUpdate(CREATE_VIEW_DRUGS);
//                conn.commit();
//            } catch (Exception e){
//                if (e.toString().indexOf("permission denied") >= 0)
//                    denied = true;
//            }
//            try {
//                stmt.execute( "select * from " +VIEW_NAME +" limit 1");
//                conn.commit();
////                break;
//            } catch(Exception e) {
//                log.info("got " + e + " when SELECT FROM" + VIEW_NAME);
//                if (e.toString().indexOf("permission denied") >= 0)
//                    denied = true;
//           }
//            if (denied) {
//                GrantSetupDialog dialog = new GrantSetupDialog(new java.awt.Frame(), true);
//                dialog.setLogin(this);
//                dialog.show();
//                if (dialog.isActive()) {
//                    dialog.setVisible(false);
//                    dialog.dispose();
//                }
//            }
            
            
//            if (superConn != null) {
//                Statement stmt2 = superConn.createStatement();
//                
//                for (int i = 0; i < TABLES.length; ++i) {
//                    String s = "grant select, references on "+ TABLES[i] + " to \""+conn.getMetaData().getUserName()+"\"";
//                    try{
//                        
//                        stmt2.execute(s);
//                        superConn.commit();
//                    } catch( Exception e) {
//                        log.info("FAILED TO do "+s + " : err="+e );
//                        superConn.rollback();
//                        stmt2.close();
//                        stmt2=superConn.createStatement();
//                    }
//                    stmt2.execute("grant all on " + VIEW_NAME + " to " + conn.getMetaData().getUserName());
//                    superConn.commit();
//                    stmt2.close();
//                    superConn.close();
//                }
//            }
//            
//        }
//        stmt.close();
//        conn.close();
//        
    }
    
    
    
    public void setDataObjectFactory(org.gnumed.testweb1.data.DataObjectFactory dataObjectFactory) {
        this.factory = dataObjectFactory;
    }
    
    public void setDataSource(javax.sql.DataSource ds) {
        this.dataSource = ds;
    }
/*    
    public void doLogin(String userName, char[] password) {
        synchronized(this) {
        StringBuffer sb  = new StringBuffer(password.length);
        sb.insert(0, password);
        Arrays.fill(password, ' ');
        try {
            log.info(" Using username=" + userName + " password "+sb.toString());
            DriverManager.registerDriver((Driver)Class.forName("org.postgresql.Driver").newInstance());
            superConn = DriverManager.getConnection("jdbc:localhost:postgresql:drugref", userName,  sb.toString());
            sb.delete(0, sb.length());
        } catch (Exception e) {
            superConn = null;
            log.error("UNABLE TO LOGIN AS " + userName + "reason " + e);
        }
        }
    }
 */  
}
