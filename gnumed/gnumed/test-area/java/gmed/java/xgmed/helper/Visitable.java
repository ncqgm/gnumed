/*
 * Visitable.java
 *
 * Created on 7 July 2003, 09:44
 */

package xgmed.helper;

/**
 *
 * @author  sjtan
 */
public interface Visitable {
     public void accept(Visitor v);
}
