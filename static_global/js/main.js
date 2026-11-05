(function(){function r(e,n,t){function o(i,f){if(!n[i]){if(!e[i]){var c="function"==typeof require&&require;if(!f&&c)return c(i,!0);if(u)return u(i,!0);var a=new Error("Cannot find module '"+i+"'");throw a.code="MODULE_NOT_FOUND",a}var p=n[i]={exports:{}};e[i][0].call(p.exports,function(r){var n=e[i][1][r];return o(n||r)},p,p.exports,r,e,n,t)}return n[i].exports}for(var u="function"==typeof require&&require,i=0;i<t.length;i++)o(t[i]);return o}return r})()({1:[function(require,module,exports){
// the semi-colon before function invocation is a safety net against concatenated
// scripts and/or other plugins which may not be closed properly.
;( function( $, window, document, undefined ) {

	"use strict";

		// undefined is used here as the undefined global variable in ECMAScript 3 is
		// mutable (ie. it can be changed by someone else). undefined isn't really being
		// passed in so we can ensure the value of it is truly undefined. In ES5, undefined
		// can no longer be modified.

		// window and document are passed through as local variables rather than global
		// as this (slightly) quickens the resolution process and can be more efficiently
		// minified (especially when both are regularly referenced in your plugin).

		// Create the defaults once
		var pluginName = "selectionSave",
			defaults = {
				selectionEndPoint: "/",
				valueSelector: "id"
			};

		// The actual plugin constructor
		function SelectionSave ( element, options ) {
			this.element = element;
			this.$element = $(this.element);

			// jQuery has an extend method which merges the contents of two or
			// more objects, storing the result in the first object. The first object
			// is generally empty as we don't want to alter the default options for
			// future instances of the plugin
			this.settings = $.extend( {}, defaults, options );
			this._defaults = defaults;
			this._name = pluginName;
			this.init();
		}

		// Avoid Plugin.prototype conflicts
		$.extend( SelectionSave.prototype, {
			init: function() {

				// Place initialization logic here
				// You already have access to the DOM element and
				// the options via the instance, e.g. this.element
				// and this.settings
				// you can add more functions like the one below and
				// call them like the example below
				this.$element.on('click', (e) => {
					// get the datum identifier
					var selectionId = parseInt($(e.currentTarget).data('id')) * ($(e.currentTarget).is(':checked') ? 1 : -1);
					// send the identifier to the endpoint.
					var jqxhr = $.post( this.settings.selectionEndPoint, {id: selectionId} )
					.fail((e) => {
    					alert( "error" );
  					});
				})
			},
		} );

		// A really lightweight plugin wrapper around the constructor,
		// preventing against multiple instantiations
		$.fn[ pluginName ] = function( options ) {
			return this.each( function() {
				if ( !$.data( this, "plugin_" + pluginName ) ) {
					$.data( this, "plugin_" +
						pluginName, new SelectionSave( this, options ) );
				}
			} );
		};


} )( jQuery, window, document );
},{}],2:[function(require,module,exports){
/*
 * Counts down to the PEL deadline shown in the page header.
 *
 * The server decides whether there is anything to count: it only renders
 * the element when this player still owes a PEL for an event that has
 * finished and is not yet overdue.  This just ticks it, and takes the box
 * away if the deadline passes while the page is sitting open.
 */
;(function ($) {
    "use strict";

    var SECOND = 1000;
    var MINUTE = 60 * SECOND;
    var HOUR = 60 * MINUTE;
    var DAY = 24 * HOUR;

    function pad(value) {
        return (value < 10 ? "0" : "") + value;
    }

    function describe(remaining) {
        var days = Math.floor(remaining / DAY);
        var hours = Math.floor((remaining % DAY) / HOUR);
        var minutes = Math.floor((remaining % HOUR) / MINUTE);
        var seconds = Math.floor((remaining % MINUTE) / SECOND);
        // days are only worth saying when there are any.
        var clock = pad(hours) + ":" + pad(minutes) + ":" + pad(seconds);
        if (days > 0) {
            return days + (days === 1 ? " day " : " days ") + clock;
        }
        return clock;
    }

    $(function () {
        var box = $(".pel-countdown");
        if (!box.length) {
            return;
        }
        var deadline = new Date(box.data("pel-deadline")).getTime();
        if (isNaN(deadline)) {
            // nothing sensible to count to, so do not leave a half drawn box.
            box.remove();
            return;
        }
        var clock = box.find(".pel-countdown-clock");

        function tick() {
            var remaining = deadline - Date.now();
            if (remaining <= 0) {
                // the deadline went by while the page was open.
                box.remove();
                window.clearInterval(timer);
                return;
            }
            clock.text(describe(remaining));
        }

        var timer = window.setInterval(tick, SECOND);
        tick();
    });
}(jQuery));

},{}],3:[function(require,module,exports){
/*
 * This is the main file from which all the other things
 * are installed.
 * 
 * They can be installed using npm if they arn't included directly through the HTML
 */

/* 
Setup for using the csrf token
*/
// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

// UI niceties . . .
$(".alert").click((e) => {
    console.log("cliky the alert");
    $(e.currentTarget).hide(500);
});

window.showError = function(title, message) {
    $('#error_modal_label').html(title);
    $('#error_modal_body').html(message);
    $('#error_modal').modal('show');
}


require('./jquery.selection_save.js');
require('./pel_countdown.js');

},{"./jquery.selection_save.js":1,"./pel_countdown.js":2}]},{},[3]);
