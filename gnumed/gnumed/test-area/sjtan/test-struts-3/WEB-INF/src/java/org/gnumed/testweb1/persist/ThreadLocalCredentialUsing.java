/*
 * Created on 06-Feb-2005
 *
 */
package org.gnumed.testweb1.persist;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

/**
 * @author sjtan
 *
 */
public  class ThreadLocalCredentialUsing {
    InheritableThreadLocal threadLocalCredential= new InheritableThreadLocal();
    static Log log = LogFactory.getLog(ThreadLocalCredentialUsing.class);
    public void setCredential(Object o) {
        log.info(this + " SET with " + o);
        threadLocalCredential.set(o);
    }
    public Object getCredential() {
        log.info(this + " returning " + threadLocalCredential.get());
        return  threadLocalCredential.get();
    }
}