/*
 * Util.java
 *
 * Created on June 21, 2004, 10:04 AM
 */

package org.gnumed.testweb1.global;

import java.beans.PropertyDescriptor;
import java.io.UnsupportedEncodingException;
import java.security.Principal;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.sql.Statement;
import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.Iterator;
import java.util.Map;

import javax.servlet.http.HttpServletRequest;

import org.apache.commons.beanutils.BeanUtils;
import org.apache.commons.beanutils.PropertyUtils;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.struts.config.ModuleConfig;
import org.apache.struts.config.PlugInConfig;
import org.gnumed.testweb1.persist.CredentialUsing;
import org.gnumed.testweb1.persist.DemographicDataAccess;
import org.gnumed.testweb1.persist.LoginInfoUsing;
/**
 *
 * @author  sjtan
 */
public class Util {
    static DateFormat[] dateFormats = null;
    static DateFormat outputDateTimeFormat = null;
    static DateFormat outputDateFormat = null;
    static {
        outputDateFormat= SimpleDateFormat.getDateInstance(SimpleDateFormat.SHORT);
        outputDateTimeFormat = SimpleDateFormat.getDateTimeInstance(SimpleDateFormat.SHORT, SimpleDateFormat.SHORT);
        
    };
    
    static Log log = null;
    
    /** Creates a new instance of Util */
    public Util() {
    }
    
    public static Log getLog( ) {
        if (log == null)
            log = LogFactory.getLog(Util.class);
        return log;
    }
    
    private static DateFormat[] getDateFormats() {
        if ( dateFormats == null) {
            dateFormats = new DateFormat[] {
                DateFormat.getDateInstance(DateFormat.SHORT),
                DateFormat.getDateInstance(DateFormat.MEDIUM),
                new SimpleDateFormat("yyyy-MM-dd hh:mm:ss.S"),
                new SimpleDateFormat("dd-MM-yyyy"),
                new SimpleDateFormat("dd-MM-yyyy hh:mm"),
                new SimpleDateFormat("MMM/yyyy"),
                new SimpleDateFormat("MM/yyyy"),
                new SimpleDateFormat("MMM-yyyy"),
                new SimpleDateFormat("MMM yyyy"),
                new SimpleDateFormat("MM-yyyy"),
                new SimpleDateFormat("yyyy")
            };
        }
        return dateFormats;
    }
    
    public static PlugInConfig findPluginConfig(
    ModuleConfig moduleConfig,
    Class pluginClass ) {
        
        PlugInConfig[] configs = moduleConfig.findPlugInConfigs();
        PlugInConfig c;
        for (int i=0; i < configs.length; ++i) {
            c = configs[i];
            Log log = getLog();
            log.info( "Checking  config " + c.getClassName() + " against " + pluginClass.getName() );
            if (c.getClassName().equals(pluginClass.getName() )  ) {
                log.info("FOUND CONFIG");
                return c;
            } else
            { log.info("Config no match"); }
        }
        return null;
    }
    
    public static String getDateString(java.util.Date date) {
        return outputDateFormat.format(date);
    }
    
    public static String getDateTimeString(java.util.Date date) {
        return outputDateTimeFormat.format(date);
    }
    
    public static String getShortestDateTimeString(java.util.Date date) {
        try {
            if ( date.getTime() == outputDateFormat.parse(outputDateFormat.format(date)).getTime() ) {
                java.util.Calendar cal = java.util.Calendar.getInstance();
                cal.setTime(date);
                if ( cal.get(Calendar.DAY_OF_MONTH) == cal.getMinimum(Calendar.DAY_OF_MONTH) ){
                    if  (cal.get(Calendar.MONTH) == cal.getMinimum(Calendar.MONTH) ) {
                        return new SimpleDateFormat("yyyy").format(date);
                    }
                    return new  SimpleDateFormat("MMM yyyy").format(date);
                }
                return outputDateFormat.format(date);
            }
        } catch (Exception e) {
            log.error(e);
        }
        return outputDateTimeFormat.format(date);
    }
    
    public static void tranferFromResultSet(java.lang.Object target,
    final java.lang.String csvTargetFields,
    java.sql.ResultSet resultSet,
    final java.lang.String csvSourceFields)
    throws IllegalAccessException,
    java.lang.reflect.InvocationTargetException ,
    java.sql.SQLException{
        
        String[] targetFields = csvTargetFields.split("\\w*,\\w*");
        String[] sourceFields = csvSourceFields.split("\\w*,\\w*");
        
        
        for (int i = 0; i < resultSet.getMetaData().getColumnCount() ; i++) {
            
        }
    }
    
    public static void logBean(Log log, Object bean) throws Exception {
        if (bean == null) {
            log.error("PASSED A NULL LOG BEAN");
            return;
        }
        PropertyDescriptor[] props = PropertyUtils.getPropertyDescriptors(bean);
        for (int i =0; i < props.length;++i) {
        	try {
        		String val = BeanUtils.getProperty(bean, props[i].getName()); 
        		log.info(bean + " has property " 
        				+ props[i].getName() + " , val =" + val);
        	}catch (Exception e) {
				// TODO: handle exception
        		log.error("error getting property "+ props[i].getName()+" "+ e.getMessage());
			}
        }
        /*log.info(bean + " has these properties" );
        
        Map map = BeanUtils.describe(bean);
        
        Iterator j = map.entrySet().iterator();
        
        while(j.hasNext()) {
            Map.Entry me = (Map.Entry) j.next();
            log.info( me.getKey() + ":" + me.getValue() );
        }*/
        
    }
    
    
    
    
    public static java.util.Date parseDate( String s) throws ParseException {
        ParseException pe = null;
        DateFormat[] dateFormats = getDateFormats();
        for (int i = 0; i < dateFormats.length ; ++i) {
            try {
                return dateFormats[i].parse(s);
            } catch (ParseException e) {
                pe=e;
            }
        }
        throw pe;
    }
    
    
    /*public static String getStaceTraceN(final java.lang.Throwable exception, final int n) {
        Throwable e = ExceptionUtils.getRootCause(exception);
        String[] frames = ExceptionUtils.getStackFrames(e);
        StringBuffer buf = new StringBuffer();
        for (int i=0;i< n && i < frames.length; ++i) {
            buf.append(frames[i]);
            buf.append("\n");
        }
        return buf.toString();
    }*/
    
    public static String getShortNowString(boolean withTime) {
        if (!withTime)
            return DateFormat.getDateInstance(DateFormat.SHORT).format(new java.util.Date());
        
        return DateFormat.getDateTimeInstance(DateFormat.SHORT, DateFormat.SHORT).format(new java.util.Date());
    }
    
    public static String nullIsBlank( String s) {
    	if ( s== null) 
    		s = "";
    	return s.trim();
    }
    
   public static Date getRelativeDate( int years, int month, int daysAhead ) {
       Calendar c = Calendar.getInstance();
       c.set(Calendar.YEAR, c.get(Calendar.YEAR) + years);
       c.set(Calendar.MONTH, c.get( Calendar.MONTH)+month);
       c.set(Calendar.DATE, c.get(Calendar.DATE) + daysAhead);
       return c.getTime();
   }
   /**
    * @param e
    * @return
    */
   public static StringBuffer getStringStackTrace(Exception e) {
       StringBuffer sb = new StringBuffer();
       for (int i = 0; i < e.getStackTrace().length; ++i) {
       sb.append(
       "\t"
              + e.getStackTrace()[i].getClassName() + "."  
       		
              +e.getStackTrace()[0].getMethodName() +":"
       
              + String.valueOf(e.getStackTrace()[0].getLineNumber())
          ); 
       }
       return sb;
   }

   
   private static String defaultEncoding = "UTF-8";
   private static String defaultEncodingPostgres = "LATIN1";
   public static void setEncoding( String encoding) {
       synchronized( Util.class) {
           defaultEncoding = encoding;
       }
   }
   
   
   
   public static String encode(String str) throws UnsupportedEncodingException {
       if (str == null)
           return str;
        String newStr = new String( str.getBytes(), defaultEncoding );
        log.info("ENCODING STRING " + str + " to " + newStr);
        
        return newStr;
   }
   

   
	/**
    * @param conn
    */
   public static void setDefaultClientEncoding(Connection conn) throws SQLException {
       // TODO Auto-generated method stub
       Statement stmt = conn.createStatement();
       stmt.execute("set client_encoding to '" + defaultEncodingPostgres +"'");
   }

   public static void setSessionAuthentication(Connection conn, Principal principal) throws SQLException {
       PreparedStatement stmt = conn.prepareStatement("set  session authorization ?");
       String name = principal.getName();
       
       if (name.equals("tomcat") )
           name = "any-doc";
       stmt.setString( 1, name );
       
       stmt.execute();
   }   
   
   /**
    * @param request
    * @param dataAccess
    */
   public static void setUserCredential(HttpServletRequest request, CredentialUsing using) {
           log.info("SETTING CREDENTIAL = " + request.getUserPrincipal() + " on " + using);
           using.setCredential(request.getUserPrincipal());
      
   }

   
}