/*
 * BasicLetterGenerationCapable.java
 *
 * Created on 26 August 2003, 18:10
 */

package quickmed.usecases.test;
import java.io.*;
import org.gnumed.gmIdentity.identity;

/**
 *
 * @author  syan
 */
public interface BasicLetterGenerationCapable {
    public String getLetter();
    public void setClient( identity client);
    public void setProvider( identity provider);
    public void printTo(PrintStream ps);
     public void printTo(PrintWriter pw);
    public void execute() throws Exception;
}
