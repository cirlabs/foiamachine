(function() {
	
	var strServerRoot = 'http://birddogit.herokuapp.com';
	var trackingTimer;
	
	var jQuery;

	/******** Load jQuery if not present *********/
	if (window.jQuery === undefined || window.jQuery.fn.jquery !== '1.7.1') {
		var script_tag = document.createElement('script');
		script_tag.setAttribute("type","text/javascript");
		script_tag.setAttribute("src",
			"http://media.apps.cironline.org/shared/bootstrap/js/jquery.js");
		if (script_tag.readyState) {
		  script_tag.onreadystatechange = function () { // For old versions of IE
			  if (this.readyState == 'complete' || this.readyState == 'loaded') {
				  scriptLoadHandler();
			  }
		  };
		} else { // Other browsers
		  script_tag.onload = scriptLoadHandler;
		}
		// Try to find the head, otherwise default to the documentElement
		(document.getElementsByTagName("head")[0] || document.documentElement).appendChild(script_tag);
	} else {
		// The jQuery version on the window is the one we want to use
		jQuery = window.jQuery;
		main();
	}
	
	/******** Called once jQuery has loaded ******/
	function scriptLoadHandler() {
		// Restore jQuery and window.jQuery to their previous values and store the
		// new jQuery in our local jQuery variable
		jQuery = window.jQuery.noConflict(true);
		$ = window.jQuery;
		// Call our main function
		main(); 
	}
	
	/******** Our main function ********/
	function main() { 

		var arrCSSLinks = [];
		arrCSSLinks.push("http://media.apps.cironline.org/birddog/site_media/css/widget.css");
		arrCSSLinks.push("http://media.apps.cironline.org/shared/bootstrap/css/bootstrap.css");
		arrCSSLinks.push("http://media.apps.cironline.org/shared/bootstrap/css/bootstrap-responsive.css");
		arrCSSLinks.push("http://media.apps.cironline.org/shared/cawatch-responsive/cawatch-bootstrap-reset.css");
		
		/******* Load CSS *******/
        jQuery.each(arrCSSLinks, function (numKey, objItem) {
			var css_link = jQuery("<link>", { 
				rel: "stylesheet", 
				type: "text/css", 
				href: objItem
			});
			css_link.appendTo('head');
        });
                        
		/******* Load HTML *******/
		jQuery(document).ready(function(jQuery) { 
			
			var boolHed = true;
			var boolDescription = true;
			if (typeof widget_exclude === 'undefined') {
				boolHed = true;
				boolDescription = true;
			} else {
				if (jQuery.inArray('headline',widget_exclude) != -1) {
					boolHed = false;
				}
				if (jQuery.inArray('description',widget_exclude) != -1) {
					boolDescription = false;
				}
			}
				
			if (boolHed) {
				jQuery('#birddog-widget-container').append('<h2 id="widget-hed"><strong>Bird Dog.it: The Widget</strong></h2>');
			}
			
			if (boolDescription) {
				jQuery('#birddog-widget-container').append('<p id="widget-intro">I support a Bird-Dog.it request. YOUR AGENCY HERE is now XXXX days overdue in fulfilling this public records request.</p>');
			}
			
			jQuery('#birddog-widget-container').append('<p>It\'s hard to tell you this, but you have been</p>');
			
			jQuery('#birddog-widget-container').append('<div id="shamed">SHAMED!!!!</div>');
			
			jQuery('#birddog-widget-container').append('<div id="widget-logo">Produced by <a href="http://birddogit.herokuapp.com/" target="_blank"><img src="http://media.apps.cironline.org/birddog/site_media/img/logo-cirFooter.png" width="172" height="42" border="0"/></a></div>');
			
			doGATracking();
		});
	}
		
	function doGATracking() {
		//check if analytics running
		if (!window._gat) {
			var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
			
			var script = document.createElement( 'script' );
			script.type = 'text/javascript';
			script.src = gaJsHost + "google-analytics.com/ga.js";
			document.getElementById('birddog-widget-container').appendChild(script);
			
		}
		
		tryTracking();
		
	}
		
	function addCommas(nStr) {
		nStr += '';
		x = nStr.split('.');
		x1 = x[0];
		x2 = x.length > 1 ? '.' + x[1] : '';
		var rgx = /(\d+)(\d{3})/;
		while (rgx.test(x1)) {
			x1 = x1.replace(rgx, '$1' + ',' + '$2');
		}
		return x1 + x2;
	}
})();

var widgetTracker;

function tryTracking() {
	try {
	   widgetTracker = _gat._getTracker("UA-2147301-15"); // CIR news apps account
	   widgetTracker._trackEvent('Widgets', 'bird dog widget load', location.href);
	   
	   clearTimeout(trackingTimer);
	   
	} catch(err){
		trackingTimer = setTimeout('tryTracking()',500);	
	}
}
