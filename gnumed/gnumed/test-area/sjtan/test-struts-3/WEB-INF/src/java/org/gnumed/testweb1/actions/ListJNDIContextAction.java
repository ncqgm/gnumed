/*
 * ListJNDIContextAction.java
 *
 * Created on June 19, 2004, 11:45 PM
 */

package org.gnumed.testweb1.actions;

import org.apache.struts.action.Action;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpSession;
import javax.servlet.http.HttpServletResponse;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.struts.action.Action;
import org.apache.struts.action.ActionError;
import org.apache.struts.action.ActionErrors;
import org.apache.struts.action.ActionForm;
import org.apache.struts.action.ActionForward;
import org.apache.struts.action.ActionMapping;
import org.apache.struts.util.ModuleException;
import org.apache.struts.util.MessageResources;
import org.apache.commons.beanutils.PropertyUtils;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpSession;
import javax.servlet.http.HttpServletResponse;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.struts.action.Action;
import org.apache.struts.action.ActionError;
import org.apache.struts.action.ActionErrors;
import org.apache.struts.action.ActionForm;
import org.apache.struts.action.ActionForward;
import org.apache.struts.action.ActionMapping;
import org.apache.struts.action.ActionMessages;
import org.apache.struts.action.ActionMessage;
import org.apache.struts.util.ModuleException;
import org.apache.struts.util.MessageResources;
import org.apache.commons.beanutils.PropertyUtils;
import org.apache.commons.beanutils.BeanUtils;

import org.gnumed.testweb1.global.Constants;


import javax.naming.Context;
import javax.naming.InitialContext;
import javax.naming.NameClassPair;
import javax.naming.NamingEnumeration;
import javax.naming.Binding;
import javax.naming.Referenceable;
import java.util.Enumeration;
import javax.sql.DataSource;
import java.sql.*;
/**
 *
 *
 * @author  sjtan
 */
public class ListJNDIContextAction extends Action {
    
    /** Creates a new instance of ListJNDIContextAction */
    public ListJNDIContextAction() {
    }
    Log log = LogFactory.getFactory().getLog(ListJNDIContextAction.class);
    
    public void listNamingContext(Context context) throws javax.naming.NamingException{
        
        NamingEnumeration ne = context.listBindings("");
        while (ne.hasMore()) {
            Binding binding = (Binding)  ne.next();
            log.info( ne +"->" +binding.getName() + ": " + binding.getClassName());
            if (binding.getClassName().endsWith("Context")) {
                log.info("Checking" + binding.getName());
                listNamingContext((Context) binding.getObject()  );
                
            } else {
                if ( binding.getClassName().endsWith("ResourceRef")
                || binding.getClassName().endsWith("DataSource")) {
                    log.info("checking " + binding.getClassName());
                    javax.naming.Reference ref =
                    (javax.naming.Reference) binding.getObject();
                    Enumeration en = ref.getAll();
                    while(en.hasMoreElements()) {
                        Object o = en.nextElement();
                        log.info("found o " + o + " at " + ref.getClassName());
                    }
                }
            }
        }
    }
    
    public ActionForward execute(ActionMapping mapping,
    ActionForm form,
    HttpServletRequest request,
    HttpServletResponse response) {
        
        ActionErrors errors = new ActionErrors();
        
        try {
            DataSource src =(DataSource) servlet.getServletContext().getAttribute(Constants.POOLED_DATASOURCE);
            
            if (src == null) {
                
                InitialContext context = new InitialContext();
                
                Context c1 = (Context) context.lookup(Constants.JNDI_ROOT);
                listNamingContext(c1);
                
                src = (DataSource) c1.lookup(Constants.JNDI_REF_POOLED_CONNECTIONS);
                log.info("got datasource "+ src);
                
                servlet.getServletContext().setAttribute(Constants.POOLED_DATASOURCE, src);
                
            }
            Connection con = src.getConnection();
            Statement stmt = con.createStatement();
            
            stmt.execute("select lastnames, firstnames from names");
            ResultSet rs = stmt.getResultSet();
            java.io.PrintWriter w = response.getWriter();
            w.print("<body>");
            w.print("<ol>");
            while (rs.next()) {
                log.info( rs.getString(1) + ", "+rs.getString(2) );
                w.print("<li>");
                w.print(rs.getString(1));
                w.print(", ");
                w.print(rs.getString(2));
                w.print("</li>");
                
            }
            w.print("</ol></body>");
            w.flush();
            log.info("finished with connection");
            
            con.close();
            
            return null;
            
      /*   catch (UpdateDemographicException ude) {
            log.error(ude);
             errors.add(errors.GLOBAL_MESSAGE, new  ActionError("errors.create.demo"));
        } catch (CreateDemographicException cde) {
            log.error(cde);
            errors.add( errors.GLOBAL_MESSAGE, new ActionError("errors.create.demo"));
        } catch (IllegalAccessException iae) {
            log.error(iae);
            errors.add(errors.GLOBAL_MESSAGE, new ActionError("errors.app", iae));
        } catch(InvocationTargetException ite ) {
            log.error(ite);
            errors.add(errors.GLOBAL_MESSAGE, new ActionMessage("errors.app", ite));
        } catch ( NoSuchMethodException nsme) {
            log.error(nsme);
            errors.add(errors.GLOBAL_MESSAGE, new ActionError("errors.app", nsme));
        } catch (NullPointerException npe) {
            npe.printStackTrace();
            log.error(npe);
        }
       
       */
            
        } catch (Exception e)  {
            log.debug("error in " + this.toString() , e);
        }
        finally {
            
            
        }
        
        saveErrors(request, errors);
        //   return  mapping.getInputForward();
        return mapping.getInputForward();
    }
    
    
    
}
