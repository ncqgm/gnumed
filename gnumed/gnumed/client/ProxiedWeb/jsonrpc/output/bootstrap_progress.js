// this is almost directly taken from Google's GWT which is now open source

var __PYGWT_JS_INCLUDED;

if (!__PYGWT_JS_INCLUDED) {
  __PYGWT_JS_INCLUDED = true;

var __pygwt_retryWaitMs = 50;
var __pygwt_moduleNames = [];
var __pygwt_isHostPageLoaded = false;
var __pygwt_isInitialized = false;
var __pygwt_onLoadError = function (exception, name) {
   var exc_name = exception.__name__;
   var msg = exception.message;

   if (typeof exc_name == 'undefined') {
     exc_name = exception.name;
   }
   if (typeof msg == 'undefined' || msg == '' || msg == exc_name) {
     if (    exception.args
         && exception.args.__array
         && exception.args.__array.length > 0) {
        msg = exception.args.__array.join(", ");
     } else {
        msg = exception.toString();
     }
   }
   alert( name + " " + exc_name + ': '  + msg );

};

function __pygwt_initProgressBar() {
  var delay = 100;
  var displayStartAt = 10;
  var displayAtEvery = 20;
  var displayCounter = 0;
  var displayed = false;
  var pct = 0;
  var div = document.createElement("div")
  var outertable = document.createElement("table");
  var table = document.createElement("table");
  var tr, td;

  // Progress bar
  td = document.createElement("td");
  td.style.backgroundColor = 'AA00AA';
  td.width = "100%";
  td.height = "10";
  tr = document.createElement("tr");
  tr.appendChild(td)
  table.appendChild(tr);
  table.style.width = '0';

  // Outer table
  td = document.createElement("td");
  td.innerHTML = "Loading..."
  tr = document.createElement("tr");
  tr.appendChild(td);
  tr.style.verticalAlign = "bottom";
  outertable.appendChild(tr);

  td = document.createElement("td");
  td.appendChild(table)
  tr = document.createElement("tr");
  tr.appendChild(td);
  tr.style.verticalAlign = "top";
  outertable.appendChild(tr);
  outertable.style.width = '100%';
  outertable.style.height = '100%';

  // Container
  div.appendChild(outertable);
  div.style.zIndex=10000;
  div.style.position='absolute';
  div.style.left='0px';
  div.style.top='0px';
  div.style.width='100%';
  div.style.height='100%';
  div.style.backgroundColor = 'FFFFFF';

  var progress = function() {
  if (!__pygwt_isInitialized) {
    displayCounter++;
    if (displayed == false && displayCounter >= displayStartAt) {
      document.body.appendChild(div);
      displayed = true;
    }
    if (displayCounter > displayAtEvery) {
      displayCounter = 0;
      if (pct <= 95) {
        pct += 5;
        table.style.width = pct + "%";
      }
    }
    window.setTimeout(progress, delay);
  } else {
    if (displayed) {
      document.body.removeChild(div);
    }
  }
};
  window.setTimeout(progress, delay);
}

function __pygwt_processMetas() {
  var metas = document.getElementsByTagName("meta");
  for (var i = 0, n = metas.length; i < n; ++i) {
    var meta = metas[i];
    var name = meta.getAttribute("name");
    if (name) {
      if (name == "pygwt:module") {
        var content = meta.getAttribute("content");
        if (content) {
          __pygwt_moduleNames = __pygwt_moduleNames.concat(content);
        }
      }
    }
  }
}


function __pygwt_forEachModule(lambda) {
  for (var i = 0; i < __pygwt_moduleNames.length; ++i) {
    lambda(__pygwt_moduleNames[i]);
  }
}


// When nested IFRAMEs load, they reach up into the parent page to announce that
// they are ready to run. Because IFRAMEs load asynchronously relative to the 
// host page, one of two things can happen when they reach up:
// (1) The host page's onload handler has not yet been called, in which case we 
//     retry until it has been called.
// (2) The host page's onload handler has already been called, in which case the
//     nested IFRAME should be initialized immediately.
//
function __pygwt_webModeFrameOnLoad(iframeWindow, name) {
  var moduleInitFn = iframeWindow.pygwtOnLoad;
  if (__pygwt_isHostPageLoaded && moduleInitFn) {
    var old = window.status;
    window.status = "Initializing module '" + name + "'";
    try {
        moduleInitFn(__pygwt_onLoadError, name);
    } finally {
        window.status = old;
        __pygwt_isInitialized = true;
    }
  } else {
    setTimeout(function() { __pygwt_webModeFrameOnLoad(iframeWindow, name); }, __pygwt_retryWaitMs);
  }
}


function __pygwt_hookOnLoad() {
  var oldHandler = window.onload;
  window.onload = function() {
    __pygwt_isHostPageLoaded = true;
    if (oldHandler) {
      oldHandler();
    }
  };
}


// Returns an array that splits the module name from the meta content into
// [0] the prefix url, if any, guaranteed to end with a slash
// [1] the dotted module name
//
function __pygwt_splitModuleNameRef(moduleName) {
   var parts = ['', moduleName];
   var i = moduleName.lastIndexOf("=");
   if (i != -1) {
      parts[0] = moduleName.substring(0, i) + '/';
      parts[1] = moduleName.substring(i+1);
   }
   return parts;
}


//////////////////////////////////////////////////////////////////
// Called directly from compiled code
//
function __pygwt_initHandlers(resize, beforeunload, unload) {
   var oldOnResize = window.onresize;
   window.onresize = function() {
      resize();
      if (oldOnResize)
         oldOnResize();
   };

   var oldOnBeforeUnload = window.onbeforeunload;
   window.onbeforeunload = function() {
      var ret = beforeunload();

      var oldRet;
      if (oldOnBeforeUnload)
        oldRet = oldOnBeforeUnload();

      if (ret !== null)
        return ret;
      return oldRet;
   };

   var oldOnUnload = window.onunload;
   window.onunload = function() {
      unload();
      if (oldOnUnload)
         oldOnUnload();
   };
    var errordialog=function(msg, url, linenumber) {
        var dialog=document.createElement("div");
            dialog.className='errordialog';
            dialog.innerHTML='&nbsp;<b style="color:red">JavaScript Error: </b>' + msg +' at line number ' + linenumber +'. Please inform webmaster.';
            document.body.appendChild(dialog);
            return true;
    }

    window.onerror=function(msg, url, linenumber){
        return errordialog(msg, url, linenumber);
    }
}


//////////////////////////////////////////////////////////////////
// Web Mode
//
function __pygwt_injectWebModeFrame(name) {
   if (document.body) {
      var parts = __pygwt_splitModuleNameRef(name);
   
      // Insert an IFRAME
      var iframe = document.createElement("iframe");
      var selectorURL = parts[0] + parts[1] + ".nocache.html";
      iframe.src = selectorURL;
      iframe.style.border = '0px';
      iframe.style.width = '0px';
      iframe.style.height = '0px';
      if (document.body.firstChild) {
         document.body.insertBefore(iframe, document.body.firstChild);
      } else {
         document.body.appendChild(iframe);
      }
   } else {
      // Try again in a moment.
      //
      window.setTimeout(function() { __pygwt_injectWebModeFrame(name); }, __pygwt_retryWaitMs);
   }
}


//////////////////////////////////////////////////////////////////
// Set it up
//
__pygwt_initProgressBar();
__pygwt_processMetas();
__pygwt_hookOnLoad();
__pygwt_forEachModule(__pygwt_injectWebModeFrame);


} // __PYGWT_JS_INCLUDED
