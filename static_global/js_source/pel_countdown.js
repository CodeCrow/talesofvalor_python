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
