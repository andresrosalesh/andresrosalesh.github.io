
// Display line graph as soon as page loads
window.onload = function () {

	// dw_graph_week returns x and y data for line graph
	let formattedTimeData = dw_graph_week(timings, shallow);
	let daysOfWeek = formattedTimeData[0]; // x, format: YYYY-MM-DD (Weekday)
	let deepWorkHours = formattedTimeData[1]; // y, format: hours
	let shallowWorkHours = formattedTimeData[2]; // y, format: hours
	let noWorkHours = formattedTimeData[3];

	// Customize axes depending on user selection of week or month view
	let graph_title, graph_xlabel, graph_scale_height;
	if (type_of_trend === 'month') {
		graph_title = "Last Month of Deep Work";
		graph_xlabel = "Last Month";
		graph_scale_height = 100;
	} else {
		graph_title = "Last Week of Deep Work";
		graph_xlabel = "Last Week";
		graph_scale_height = 60;
	}


	// Draw line graph
	let date_label;
	new Chart(document.getElementById("line-chart"), {
		type: 'line',
		  data: {
		    labels: daysOfWeek,
		    datasets: [{
		        data: deepWorkHours,
		        label: "Deep",
		        borderColor: "#3e95cd",
		        fill: true
		      }, {
		        data: shallowWorkHours,
		        label: "Shallow",
		        borderColor: "#8e5ea2",
		        fill: false
		      },
		      {
		        data: noWorkHours,
		        label: "No Work",
		        borderColor: "#FFA500",
		        fill: false
		      }]
		  },
		  options: {
		    title: {
		      display: true,
		      text: graph_title,
		      fontSize : 30
		    },
		    scales: {
                xAxes: [{
                	afterFit: function(scale) {
		               scale.height = graph_scale_height
		            },
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: graph_xlabel,
                        fontSize: 20
                    },
                    ticks: {
						callback: function(label) {
					        return label.slice(5); // Chop year off ticks
					    }
                    }
                }],
                yAxes: [{
                	afterFit: function(scale) {
		               scale.width = 60
		            },
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Working Hours',
                        fontSize: 20
                    },
					ticks: {
						max : 8,
                        beginAtZero: true
					}
                }]
            },
            // Customize bubble when user hovers over data point
            tooltips: {
		      callbacks: {
			        title: function(tooltipItem, data) {
			          date_label = data['labels'][tooltipItem[0]['index']].slice(0,10);
			          return data['labels'][tooltipItem[0]['index']].slice(5); // Chop year off hover labels
			        },
			        afterLabel: function(tooltipItem, data) {
			          // Display sleep, mood, and energy statistics when user hovers over data
			          let date_no_dash = date_label.slice(0, 4) + date_label.slice(5,7) + date_label.slice(8);
			          for (let k = 0; k < wbdata.length; k++) {
			          	if (date_no_dash === wbdata[k]['date']) {
			          		return "Sleep: " + wbdata[k]['sleepq'] + '/10, ' + wbdata[k]['sleeph'] + "h" + wbdata[k]['sleepm'] + "m |" + " Mood: " + wbdata[k]['mood'] + '/10 |' + " Energy: " + wbdata[k]['energy'] + '/10';
			          	}
			          }
			        }
	    	  },
		    },
		  }
		});

	// Custom graph fonts and fontsizes
	Chart.defaults.global.defaultFontColor='white';
	Chart.defaults.global.defaultFontSize = 14;

	// Compute and display Analytics

	// Get all time data
	let formattedAllTimeData = dw_graph_week(all_timings, all_shallow);
	let allDaysOfWeek = formattedAllTimeData[0];
	let allDeepWorkHours = formattedAllTimeData[1];
	let allShallowWorkHours = formattedAllTimeData[2];
	let allNoWorkHours = formattedAllTimeData[3];

	// Match with well being data
	let alltime_data = [];
	for (let i = 0; i < allDaysOfWeek.length; i++) {
		let day = allDaysOfWeek[i].slice(0, 4) + allDaysOfWeek[i].slice(5,7) + allDaysOfWeek[i].slice(8,10);
		let k = 0;
		let found = false;
		while (k < all_wbdata.length && !found) {
			// If date is found
			if (day === all_wbdata[k]['date']) {
				alltime_data.push([day, allDeepWorkHours[i], allShallowWorkHours[i], allNoWorkHours[i], all_wbdata[k]['sleepq'], all_wbdata[k]['sleeph'] + (all_wbdata[k]['sleepm']/60), all_wbdata[k]['mood'], all_wbdata[k]['energy'], all_wbdata[k]['prod']]);
				found = true;
			}
			k++;
		}
	}

	// Sleep slope
	let sleep_slope = (getMax(alltime_data, 1) - getMin(alltime_data, 1)) / (getMax(alltime_data, 5) - getMin(alltime_data, 5));
	document.getElementById("sleep-analytics").innerHTML = "Each extra hour of sleep you've gotten has been tied to " + sleep_slope + " more hours of deep work.";

	// Mood slope
	let mood_slope = (getMax(alltime_data, 6) - getMin(alltime_data, 6)) / (getMax(alltime_data, 1) - getMin(alltime_data, 1));
	document.getElementById("mood-analytics").innerHTML = "Each extra hour of deep work you've accomplished has been tied to a" + ((mood_slope > 0) ? "n increase of " : "decrease of ") + mood_slope + " points in your mood rating.";

	// Energy slope
	let energy_slope = (getMax(alltime_data, 7) - getMin(alltime_data, 7)) / (getMax(alltime_data, 1) - getMin(alltime_data, 1));
	document.getElementById("energy-analytics").innerHTML = "Each extra hour of deep work you've accomplished has been tied to a" + ((energy_slope > 0) ? "n increase of " : "decrease of ") + energy_slope + " points in your energy levels.";

	// Affects on feelings of productivity, TODO at some point
}

// Helper functions

function getMax(arr, pos) {
	let max = Math.max.apply(Math, arr.map(function(i) {
	    return i[pos];
	}));
	return max;
}

function getMin(arr, pos) {
	let min = Math.min.apply(Math, arr.map(function(i) {
	    return i[pos];
	}));
	return min;
}


// Returns day of the week from a YYYYMMDD date format
function getDayOfWeek(date) {
  const dayOfWeek = new Date(date).getDay();
  return isNaN(dayOfWeek) ? null :
    ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][dayOfWeek];
}

// Turns YYYYMMDD format to YYYY-MM-DD (Day of Week)
function dateEntry(date) {
	// Expected date format: YYYYMMDD
	let dateDashed = date.slice(0, 4) + "-" + date.slice(4,6) + "-" + date.slice(6);
	day = getDayOfWeek(dateDashed);
	dayofweek = (day === 'Tuesday' || day === 'Thursday' || day === 'Saturday' || day === 'Sunday') ? day.substring(0,2) : day[0]
	return dateDashed + " (" + dayofweek + ")";
}

// Takes user's logged timings and remaining shallow work times
// Returns three arrays matching day of week to deepwork hours and shallow work hours
function dw_graph_week(timings, shallow) {

	// Arrays to be filled and returned
	let daysofweek = [];
	let deepWorkHours = [];
	let shallowWorkHours = [];
	let noWorkHours = [];

	// Appends days of week and time logs to arrays
	function append(i, j) {
		date_entry = dateEntry(timings[i]['start_date']);
		daysofweek.push(date_entry)

		// k used to iterate from i to j
		let dw = 0;
		let sw = 0;
		let nw = 0;
		for (let k = i; k < j; k++) {
			if (timings[k]['dw'] === 1) {
				dw += timings[k]['hours'] + (timings[k]['minutes'] / 60) + (timings[k]['seconds'] / 3600);
			} else {
				sw += timings[k]['hours'] + (timings[k]['minutes'] / 60) + (timings[k]['seconds'] / 3600);
			}
		}

		// Append accumulated deepwork time
		deepWorkHours.push(dw);
		shallowWorkHours.push(sw);

		// Add shallow work hours that user did not explicitly log
		// n refers to the nth shallow work entry and is updated after each new day is reached in the while loop below
		if (n < shallow.length) {
			// sw += shallow[n]['hours'] + (shallow[n]['minutes'] / 60) + (shallow[n]['seconds'] / 3600);
			nw += shallow[n]['hours'] + (shallow[n]['minutes'] / 60) + (shallow[n]['seconds'] / 3600);
		}

		// Append accumulated no work time
		// shallowWorkHours.push(sw);
		noWorkHours.push(nw);
	}

	// Two pointer operation to traverse array
	// i stops at a new date while j takes one step in each operation checking if the next day is a new date
	// When j finds a new date, entries i to j-1 are appended to arrays
	// i is then updated to where j is
	let i = 0;
	let j = 0;
	let n = 0; // number of unique days encountered, for use in getting time from shallowwork data
	while (i < timings.length && j < timings.length) {
		// If new date
		if (timings[i]['start_date'] !== timings[j]['start_date']) {

			// Append entries by dealing with i to j - 1 entries
			append(i, j);

			i = j;
			j++;
			n++;

		} else if (timings[i]['start_date'] === timings[j]['start_date']) {
			j++; // Otherwise look at next date
		}

		// If j past array length
		if (j === timings.length) {
			append(i, j);
		}
	}

	// Return filled arrays
	return [daysofweek, deepWorkHours, shallowWorkHours, noWorkHours];
}
