<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>
<html>
<head><title>JSP Page</title></head>
<body>

    <%-- <jsp:useBean id="beanInstanceName" scope="session" class="beanPackage.BeanClassName" /> --%>
    <%-- <jsp:getProperty name="beanInstanceName"  property="propertyName" /> --%>

    <h3>Development Notes</h3>
    <h4> Struts Background </h4>
    <ol>
    <li><h5>Java</h5> This is the language for Struts. The main java concepts
    are JavaBeans, and Collections. The libraries used include :-
    <ul>
    <li>
        java.util.* ( Date, Calendar, Map, HashMap/HashTable, List, ArrayList/Vector, Collections, Arrays,  ResourceBundle, PropertyResourceBundle Set, HashSet, TreeSet  ), 
    </li>
    <li>
        java.text.* ( DateFormat, SimpleDateFormat)
    </li>
    <li> java.sql.* (Driver, Connection, Statement, PreparedStatement, ResultSet, MetaResultSet)
    </li>
    </ul></li>
    <li><h5>apache.commons</h5> These are more libraries that Apache came up with
    that Struts uses. The main user ones would be
    <ul>
        <li>org.apache.commons.logging. ( Log, LogFactory)</li>
        <li>org.apache.lang.exceptions ( ExceptionUtils) </li>
        <li> org.apache.beanutils. ( BeanUtil, PropertyUtil) </li>
    </ul>
    Tomcat also uses org.apache.commons.dbcp  (db=database, cp=connection pooling)
    Connection pooling saves on the time to create a connection on behalf of a client request, 
    which is reported to take a few seconds.
    </li>
    <li><h5>tomcat</h5> is a java web server, that implements java server pages (jsp), 
    taglibs, java servlet specification.  A java servlet is like an application server
    within a tomcat http/https server, that does application specific responses to requests.
    Struts provides a java servlet, and on the application programming side provides a
    framework for building java web applications.
    <ol>
    <li><h6>java servlets</h6>Not much needed to know, other than it usually has
        one method that receives enough parameter objects to do most things. This method
        should probably be stateless, and only set state through the parameter objects. 
        In struts, the method is an Action's execute method, <a href='#struts-action-execute'>description</a>
        which receives a request, mapping,
        form , and response attribute. The request attribute commonly 
    </li>
    <li><h6>running a web app in tomcat </h6>
        <ol>
        <li>
            tomcat should run fairly easily after downloading a binary, as long
            as java sdk is present and its bin directory accessible via PATH environment variable.
            change to bin directory, and do ./catalina.sh start , or ./catalina.sh debug, followed by run.
            When in ./catalina.debug, exit will exit the debugging and stop tomcat.
            
        </li>
        <li>
            drop a webapp.war file, e.g. struts-example.war into the tomcat-home/webapps directory,
            and tomcat should start it up.
        </li>
        <li>
            edit tomcat-home/conf/tomcat-users.xml file, to set a user with a password who has
            the role admin, and manager. This allows one to login  from the tomcat home page
            to admin, or manager. manager app allows a webapp to be manually stopped, or removed, or restarted.
            
        </li>
        <li>
            there is one easily available java ide that provides a apache tomcat server that will run web apps from any
           project directory . It also provides a management interface for the tomcat server.
           
        </li>
        </ol>
    </ol>
    
     </li>
    
    <li> <h6>Struts</h6> is a web application framework. It defines a fairly regid way of
    organising a web app , so that a person can move from one Struts application to another
    and quickly get an idea how it works.
    <ol>
    <li><a name='struts-action-execute'/>
    In struts, the method is an Action's execute method, <a href="#struts-action-execute">description</a>
    which receives parameters : 
        <ul>
        <li> request </li>
        <li> mapping</li>
        <li>form</li> and 
        <li>response</li>
        </ul> . 
    <p>The <b>request</b> attribute commonly is used to read or write variables to the client.</p>
    <p>request represents a request scope context, and request.getSession() represents a session context.</p>
    <p> request.getSession().getSessionContext() isn't very interesting, but request.getSession().getServletContext() 
    can be useful:  for instance,  there is a getAttribute(String name) method on
    all of the request, session, and servletContext objects, so a request attribute pertains to
    a current user action, a session attribute pertains to a specific user, and a servlet context attribute
    is one for the whole application instance for all users. Typically, database sources, internationalization
    resources, business object factories and business object persistent services might be in the servlet context,
    user attributes might be in the session context ( user session stuff ? location , time , personal server
    upload/download directory ) , and things like current form data, current record id (often in request.getParameter("an_id_name") ), in the request scope.
    </p>
    <p> The <b> form </b> object usually holds the updateable data. Readonly data to be displayed can also be passed
    via the request.setAttribute( ) method.
    </p>
    <p> the <b> mapping </b> attribute. Accesses the struts-config information. Mostly used to find
    the next web page configured, via <b>mapping.getInputForward()</b> for re-input, and <b>mapping.findForward(forwardName)</b> 
    for success and other next pages.
    </p>
    <p> the <b> response </b> attribute. Haven't had much use for this parameter yet.
    </p>
    <p> <b> other struts.Action class  methods and attributes </b> which are useful, are 
    <b>saveErrors(request, actionErrors)</b> for passing error messages back after inputForward re-displays the form. 
    </p>
   
    </li>
    <li><h5>Struts Layout</h5>
    <ol><li><h6>Directories</h6>
    <ul><li><b>WEB-INF</b> :All tomcat applications have this directory. It contains
    usually all the configuration files,  often all java compiled class files in <em>WEB-INF/classes</em>  ,
    and library jar files in <em>WEB-INF/lib</em> . There also may be fixed configuration files like
    taglib .tld files , as well in struts, validation-rules.xml, which holds template javascript validation
    snippets. </li> 
    <li><b>META-INF</b> In tomcat 5, <b>context.xml</b> page can be used to specify a named datasource with a connection pooling
    implementation.  It also can specify an alternate directory for the application,  by dropping in 
    the tomcat-home/conf/Catalina directory the context.xml file containing the absolute path name
    for the application. It also can specify application logging  </li>
    <li> Web Pages can be stored in a specific page directory . The configuration files, 
    should give a path to the page relative to the applications base directory e.g. /pages/apage.jsp
    </li>
          
        </ul>
    </li>
        
    
    <li><h6>configuration files</h6>Usually all in WEB-INF. 
    They are <b> web.xml, struts-config.xml, tiles-def.xml, validation.xml </b>.
    <ul>
    <li> <b>web.xml</b> specifies 
        <ol>
        <li>welcome page, initial page location</li>
        <li>servlet class implementation (struts actionservlet) , and
        servlet class configuration files : i.e. struts-config.xml, but can
        be followed by other xml files that specify "module" divisions of the application,
    </li>
    <li>datasource resource name, as specified in context xml
    </li>
    </ol>
    </li>
    <li> <b>struts-config.xml</b>
        specifies 
    <ol>
        <li><b>form bean mappings</b>, either to config file specified "dyna" forms,
            or to user java subclassed ActionForm classes, which behave more dynamically and
            deal with non-simple form properties ( collections etc).
        </li>
        <li>
        <p>
            <b>action mappings</b> which define the path of success/failure between pages; 
            usually there will be a mapping for page setup (e.g. xxxEditAction),
            and one for page processing (e.g. xxSaveAction).
            </p>
            <p> action mapping also specifies which Action user subclass handles the action
            </p>
            <p> there is also a 'name' or 'attribute' attribute which specifies a 
            form named in the form configuration above. At the moment, what seems to work
            is to use 'attribute' for enty actions (before form construction), 
            and 'name' for exit actions (after the form is submitted).</p>
            <p>action mappings may have an internal forward mapping, which can specify
             a path for the next web page, or a tiles definition which constructs the
             next web page ( see  tiles-def.xml below).</p>
             <p>
             <code>
             <p>
            &lt;action </p>
            <p>
                path="/DemographicEdit"
             </p>
             <p>
                type="org.gnumed.testweb1.actions.DemographicEditAction"
             </p>
             <p>
                attribute="demographicForm"
                </p>
             <p>
                scope="request"
             &gt;  </p>
                <p>
                &lt;forward name="successLoadForEdit" path="demoentry"/ &gt;
                </p>
             <p>&lt;/action&gt;</p>
       
             </code>
             </p>
        </li>
        <li>
            <b>resource mapping </b> for internationalizable property files,
         </li>
        <li> <b>plugin mappings </b> for specifying PlugIn subclasses, which will 
    have there own configuration parameters, and will be loaded for the application as application services
    e.g. persistence, object implementation factories, validation, login .
        </li>
         <li> other configuration items include  <b>global forwards</b> and <b> global exceptions</b>
        for defining common pages and error pages.
        </li>
    </ol>
    </li>
    <li> <b>tiles-config.xml </b> <a name='#tiles-def'/>
    Tiles , along with css, can provide a uniform look. A template tile definition is created :
    to create a template tile, first create a web page, which has a table which defines the layout.
    In some of the table cells, put a tiles:insert tag  , using the tiles taglib include
    (see pages/main.jsp). Then in the tiles-def.xml file define a definition that has a page
    attribute pointing this template page. Then define further definitions , that extend the first
    definition, only there are "put" elements which have a name attribute of a named tiles:insert tag within
    the template page, and a value attribute of a instance page. 
    these "concrete" definitions have names, which will be accessible as 
    path attribute values inside forward elements in the action elements definitions of
    the struts-config files. See pages/main.jsp , tiles-def.xml and the action-mappings
    inside struts-config.xml
    </li>
    </ul>
    </li>
    
      
    </ol>
    </li>
    </ol>
    
    
      
    <h2>Learning notes</h2>     
        
    
   
    <h3>bug notes</h3>
    <ol>
    <li>Struts Forms
    <ol>
    <li>DynaActionForms need to handle a date field. ? how  ? javascript</li>
    <li>Use a readonly html:property field for id, instead of disabled, otherwise
    the disabled field won't be returned when the form is processed by
    the struts action following submit </li>
    <li><h6> ClinicalUpdateForm </h6>
    <ul>
        
        <li> 
        <em>vaccination update fields</em> or
        <b>howto get vaccination update to work, or more generally , 
        <em>HOWTO create more dynamic jsp forms that update object array attributes in a form.</em>
    
        </b> <p> <b> What is found in the Struts documentation / FAQ , explains
        how to display indexed properties, but doesn't specify the following update
        quirk </b>
        </p> 
        <em>WHY CAN THE JSP FORM FIND VACCINATIONS WITH DEFAULT DATES, BUT WON"T 
        RETURN FILLED OUT VACCINATIONS?</em><p> 
        The ClinicalUpdateForm class must have a method  :-
        <p> <center><code>Vaccination getVaccination(int index)</code></center></p></p>
        for struts to properly update a contained vaccination object.
        <p> The following methods in ClinicalUpdateForm will seem to work:
        <p><center><code>Vaccination[] getVaccination(int index); </code></center> </p> 
    
        <p><center><code> List getVaccination(int index);  </code></center> </p>
        <p>but only will be usable as  <em>readonly</em> methods : they won't return the updated vaccinations in the form, whereas
        the first will.
        </p>
        </li>
        <li><p> The following is not essential: </p>
            <small>
            <p>a form is  passed back as the form parameter in the action execute method,
            that handles form posting. e.g. in actions/xxxSaveForm.java
            </p>
            A Form bean is  also passed to and from a jsp page under the struts-config form mapping
            name, as a request scoped attribute. (eg.<code>request.getAtrribute('clinUpdateForm';</code>  )
            <p> (See &lt;form-beans&gt; , &lt;form-bean&gt; in WEB-INF/struts-config.xml ).</p> <p> i.e. it will exist in
            some scope under the struts-config defined name e.g. ClinicalUpdateForm maps to clinUpdateForm,
            according to this application's struts-config.xml .</p>
        </small>
        </li>
    </ul>
    </li>
 
    </ol
    </li>
    <li>Action Configuration
    <ol>
        <il><h5>Correct handling of validation error</h5> 
        <cite>
            &lt;action<br/>  
            path="/SaveDemographic"<br/>
            type="org.gnumed.testweb1.actions.DemographicEntryAction"<br/>
            name="demographicForm"<br/>
            scope="request"<br/>
            input="demographicEntry"<br/>
            &gt;<br/>
            &lt;forward name="demographicEntry" path="demoentry"/&gt;
            <br/>
            &lt;/action&gt;<br/>
        </cite>
        the internal forward definition "demographicEntry" is needed in
        order for the demoentry page to re-display data failing validation. Directly
        naming demoentry as the input attribute value doesn't work.
        </li>
    </ol>
    <li> <h5>Getting a custom dyna validator form config to work, after examining struts-example </h5>
    The steps for <b>configuring a validating dyna form are</b>:
    <ol><li> Have a form created. This can be in struts-config.xml as a DynaValidatorForm or a specific
        ActionForm java class. </li>
        <li>In the jsp file using the form within a &lt html:form / &gt tag , have a onsubmit attribute in html:form start-tag i.e. 
        <p><code> &lt html:form formName="myForm" onsubmit="return validateMyForm(this);" </code></p>
        <p> The validateMyForm is usually for validated forms, and will be generated by DynaValidatorForm definitions,
        from a form validation definition  in validation.xml.
         </p>
        </li>
        <li> In validation.xml , create a default formset ( no language or country start-tag attribute). Add the form entry
        for the created form. The entry should list an entry for every field that is validated.
        The details for creating the validation entry is discussed in dev_validation.html struts developer
        guide. Also look at the validation for struts-example for each of the fields for logon. </li>

        <li> In resources.properties , ensure that the default validation error messages are in the default resources. 
        If creating from a blank struts.war , then they should be there. </li>

        <li> In the jsp file again, at the top or the end,  create a &lt html:javascript &gt tag element naming the form e.g.
        <p> form="myForm" with dynamicJavascript="true" and staticJavascript="false".</p>
        If the staticJavascript is allowed to be true, then the generated javaScript will be loaded
        as html text.
        This is required because the javaScript will be loaded as text otherwise ( some sort of browser bug).
        Then have a script element pointing to a page staticJavascript
        <p><code> &lt script&gt language='Javascript1.1' src='./staticJavascript.jsp'/&lt script&gt'</code></p></li>
        <li> The page staticJavascript first declares the content type to be x-Javascript, 
        then has a html:javascript element which turns dynamicJavascript off and staticJavascript on.
        This reversal makes this page include the generated javascript, and this page is the source
        for the script element</li>
        <li> The goal is to get the javascript generated by validation.xml to be included as javascript
        in the page, so looking at the page source in a browser when testing , helps. </li>
        <li> if everything looks ok, the javascript code is in the output page, consider the script
            tag attributes. If there is a <code>&lt script type='text/javascript' language='Javascript1.1' &gt</code>
            then perhaps there is a problem with accepting the language, so remove the language attribute
            from the jsp page's &lt script &gt  declaration and see if it works. 
        </li>
    </ol>
</li>
    </ol>
</body>
</html>
