/*
 * Util.java
 *
 * Created on June 21, 2004, 10:04 AM
 */

package org.gnumed.testweb1.global;

import org.apache.commons.logging.LogFactory;
import org.apache.commons.lang.exception.ExceptionUtils;
import org.apache.commons.logging.Log;
import org.apache.commons.beanutils.BeanUtils;
import java.util.Iterator;
import java.util.Map;

import org.apache.struts.config.PlugInConfig;
import org.apache.struts.config.ModuleConfig;
import java.util.Map;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.text.ParseException;

import org.apache.struts.action.ActionMapping;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpSession;
/**
 *
 * @author  sjtan
 */
public class Util {
    static DateFormat[] dateFormats = null;
   
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
            dateFormats = new DateFormat[3];
            dateFormats[0] = DateFormat.getDateInstance(DateFormat.SHORT);
            dateFormats[1] = DateFormat.getDateInstance(DateFormat.MEDIUM);
            dateFormats[2] =  new SimpleDateFormat("yyyy-MM-dd hh:mm:ss.S");
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
    
    public static  void setScopedMappingAttribute(HttpServletRequest request, ActionMapping mapping,   Object form) {
         if ( "session".equals(mapping.getScope() )) {
            request.getSession().setAttribute(mapping.getAttribute(), form);
            log.info("SESSION FORM ATTRIBUTE KEY"+ mapping.getAttribute());
        } else {
            request.setAttribute(mapping.getAttribute(), form);
             log.info("REQUEST FORM ATTRIBUTE KEY"+ mapping.getAttribute());
       
        }
    }
    
    public static String getStaceTraceN(final java.lang.Throwable exception, final int n) {
        Throwable e = ExceptionUtils.getRootCause(exception);
        String[] frames = ExceptionUtils.getStackFrames(e);
        StringBuffer buf = new StringBuffer();
        for (int i=0;i< n && i < frames.length; ++i) {
            buf.append(frames[i]);
            buf.append("\n");
        }
        return buf.toString();
    }
    
    public static String getShortNowString(boolean withTime) {
        if (!withTime)
            return DateFormat.getDateInstance(DateFormat.SHORT).format(new java.util.Date());
        
        return DateFormat.getDateTimeInstance(DateFormat.SHORT, DateFormat.SHORT).format(new java.util.Date());
    }
    
}