Quick-Start FAQ
===============

What's Struts Blank?

- It's an "empty" application provided to help you get started on your own project. Just copy the struts-blank.war to a new WAR file using the name for your application. Place it in your container's "webapp" folder (or equivalent), and let your container auto-deploy the application. Edit the skeleton configuration files as needed, restart your container, and you are on your way! (You can find the application.properties file with this message in the /WEB-INF/src/java/resources folder.)

Where do I put my own code?

- The build file is setup so that you can place your own packages anywhere under the WEB-INF/src directory. 

What are the references to /javasoft/lib in the build.xml about?

- Most Struts applications use some common JAR files. This is one common location for these on a development computer, but another may be used

What targets does the build file accept?

- "clean" to delete the old class, resource, and configuration files. 

- "compile" to rebuild the Java class files and copy over the resource and configuration files. 

- "project" to also generate the Javadoc.

- "dist" to create a binary distribution.

- "all" for a clean rebuild the project and binary distributions.

Where are the binary distributions placed?

- By default, under /projects/lib on your default drive. You can change these through the "distpath.project" variable in the build file.

Where's the Application Resources?

- It's named application.properties. The original is under WEB-INF/src/java/resources. The resource bundle is copied under classes during a build.

Why did the changes to my application.properties or other resource file disappear?

- The original configuration files are under WEB-INF/src/java and copied under classes during a build. Change the WEB-INF/src/java versions and rebuild before deploying.

###