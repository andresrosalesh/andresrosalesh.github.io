// Time value definitions
let seconds = 0;
let display_secs = 0;
let minutes = 0;
let display_mins = 0;
let hours = 0;
let display_hours = 0;

// Start stop status
let status = 0;
let windowinterval = null;

let startDate = null;
let startTime = null;
let stopDate = null;
let stopTime = null;
let reset_ = true;

function timer() {
    // Increment time variables
    seconds++;
    if (seconds / 60 === 1) {
        seconds = 0;
        minutes++;

        if (minutes / 60 === 1) {
            minutes = 0;
            hours++;
        }
    }

    // Leading zeros
    if (seconds < 10) {
        display_secs = "0" + seconds.toString();
    } else {
        display_secs = seconds;
    }

    if (minutes < 10) {
        display_mins = "0" + minutes.toString();
    } else {
        display_mins = minutes;
    }

    if (hours < 10) {
        display_hours = "0" + hours.toString();
    } else {
        display_hours = hours;
    }

    // Display time
    document.getElementById("timer").innerHTML = display_hours + ":" + display_mins + ":" + display_secs;
}


function start() {
    if (status === 0) {
        // Start timing
        windowinterval = window.setInterval(timer, 1000);
        document.getElementById("start_stop").innerHTML = "Stop";
        status = 1;

        // Record start time and date
        if (reset_) {
            let today = new Date();
            startDate = [today.getFullYear(), today.getMonth() + 1, today.getDate()];
            startTime = [today.getHours(), today.getMinutes(), today.getSeconds()];
            reset_ = false;
        }

    } else {
        // Stop timing
        window.clearInterval(windowinterval);
        document.getElementById("start_stop").innerHTML = "Start";
        status = 0;

        // Record stop time and date
        let today = new Date();
        stopDate = [today.getFullYear(), today.getMonth() + 1, today.getDate()];
        stopTime = [today.getHours(), today.getMinutes(), today.getSeconds()];
    }
}

function reset() {
    // If timing is running, stop it
    if (status === 1) {
        start();
    }

    // Set all vars to 0
    status = 0;
    seconds = 0;
    minutes = 0;
    hours = 0;
    reset_ = true;
    document.getElementById("timer").innerHTML = "00:00:00";
}

$(document).ready(function submit(){
    $('#submit').click(function() {
        // Ensure timing has stopped and start and end times are captured
        if (status === 0) {

            // Check deep work and shallow work booleans
            let dwb;
            if (document.getElementById("dw").checked) {
                if (document.getElementById("sw").checked) {
                    dwb = 2; // 2 is signal to back end that user cannot select both deep and shallow work
                } else {
                    dwb = 1; // 1 = deep work
                }
            } else if (document.getElementById("sw").checked) {
                dwb = 0; // 0 = shallow work
            } else {
                dwb = 3; // 3 is signal to back end that no classification was selected
            }

            // Arrange timing data and html form elements in dict
            timingData = {'hours': hours, "minutes": minutes, "seconds": seconds, "startTime": startTime, "stopTime": stopTime, "startDate": startDate, "stopDate": stopDate,
                            "task": document.getElementById("task").value, "deepworkBool": dwb}

            // Send to index page as JSON data
            $.ajax({
                type: "POST",
                contentType: "application/json;",
                url: "/",
                data: JSON.stringify(timingData),
                dataType: "json",
                success: function(response) {
                    if (response.redirect) {
                        window.location.href = response.redirect;
                    }
                }
            });
        }
    });
});