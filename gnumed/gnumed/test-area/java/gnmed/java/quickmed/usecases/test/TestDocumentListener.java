/*
 * TestDocumentListener.java
 *
 * Created on 13 April 2003, 23:56
 */

package quickmed.usecases.test;
import javax.swing.event.DocumentEvent;
import javax.swing.event.DocumentListener;
import java.util.logging.*;


/**
 *
 * @author  sjtan
 */
public class TestDocumentListener implements javax.swing.event.DocumentListener {
        private static Logger logger;
    static {
            logger = Logger.global;
        };
        void recordEvent(String from, DocumentEvent e) {
             try {
               logger.log(Level.INFO, from +" : "+ e.getDocument().getProperty(e.getDocument().TitleProperty) + ":"+e.getDocument().getText(0, e.getDocument().getLength() ));
            } catch (javax.swing.text.BadLocationException be) {
                 logger.log(Level.WARNING,  be.toString());
            }
        }
        /** Gives notification that an attribute or set of attributes changed.
         *
         * @param e the document event
         *
         */
        public void changedUpdate(DocumentEvent e) {
           recordEvent("change", e);
        }
        
        /** Gives notification that there was an insert into the document.  The
         * range given by the DocumentEvent bounds the freshly inserted region.
         *
         * @param e the document event
         *
         */
        public void insertUpdate(DocumentEvent e) {
              recordEvent("update", e);
        }
        
        /** Gives notification that a portion of the document has been
         * removed.  The range is given in terms of what the view last
         * saw (that is, before updating sticky positions).
         *
         * @param e the document event
         *
         */
        public void removeUpdate(DocumentEvent e) {
              recordEvent("remove", e);
        }
        
        /** Gives notification that an attribute or set of attributes changed.
         *
         * @param e the document event
         *
         */
}