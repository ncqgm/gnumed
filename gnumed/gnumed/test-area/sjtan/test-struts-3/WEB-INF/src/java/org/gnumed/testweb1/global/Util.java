/*
 * Util.java
 *
 * Created on June 21, 2004, 10:04 AM
 */

package org.gnumed.testweb1.global;

import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Iterator;
import java.util.Map;

import org.apache.commons.beanutils.BeanUtils;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.struts.config.ModuleConfig;
import org.apache.struts.config.PlugInConfig;
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
        log.info(bean + " has these properties" );
        Map map = BeanUtils.describe(bean);
        
        Iterator j = map.entrySet().iterator();
        
        while(j.hasNext()) {
            Map.Entry me = (Map.Entry) j.next();
            log.info( me.getKey() + ":" + me.getValue() );
        }
        
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
    
   

}