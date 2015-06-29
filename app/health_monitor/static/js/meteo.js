$(document).ready(function() {

	var displayAll = function() {
		$.getJSON('/meteo/weather', function(data) {
	        var node = document.getElementById("weather");
	    	node.innerHTML = "";

	    	if (data.geo) {
	    		displayLocation(node, data);
	    		displayWeather(node, data);
	    	}
	    });
    }

	var displayLocation = function(node, data) {
		var inputloc = document.getElementById('location');
		inputloc.setAttribute("value", data.location);

		var loc = document.createElement('div'); 
		loc.innerHTML = "<h4>Weather at <b>" + data.location + "</b></h4>";
        node.appendChild(loc);
	}

	var displayWeather = function(node, data) {
		var prev = document.createElement('div');
	    if (data.meteo) {
			var actual = document.createElement('div');
			var date = data.weather[0].timestamp.split("#");
			var temperature = Math.round((data.weather[0].weather.measured.temperature - 273.15) * 100) / 100; 
			actual.innerHTML = "<h4>We are <b>" + date[0] + ", " + date[1]
				+ "</b><br/><br/>Temperature : <b>" + temperature + "°C</b><br/>"
				+ "Humidity : <b>" + data.weather[0].weather.measured.humidity + "%</b>"
				+ "<br/><img src=\"" + data.weather[0].icon + "\" width=\"100px\"/><br/></h4><h3>Forecasts</h3>";
			node.appendChild(actual);

			var table = document.createElement('table');
			var tbody = document.createElement('tbody');
			var line = document.createElement('tr');
			line.innerHTML = "<td>Date</td>"
				+ "<td>Time</td>"
				+ "<td>Weather</td>"
				+ "<td>Température</td>"
				+ "<td>Humidity</td>"
				+ "<td>Wind speed</td>"
				+ "<td>Wind direction</td>";
			line.setAttribute("style", "font-weight: bold;");
			tbody.appendChild(line)

			for(var i = 1; i < data.weather.length; i++)
			{
				var tmpLine = document.createElement('tr');
			    var weather = data.weather[i].weather;
			    var ktemp = parseInt(weather.measured.temperature);
			    var temperature = Math.round((ktemp - 273.15) * 100) / 100;
			    var date = data.weather[i].timestamp.split("#");

			    tmpLine.innerHTML = "<td>" + date[0]
			    	+ "</td><td>" + date[1]
			    	+ "</td><td><img src=\"" + data.weather[i].icon + "\" width=\"50px\"/></td><td>"
			    	+  temperature + "°C</td><td>"
			    	+  weather.measured.humidity + "%</td><td>"
			    	+  weather.measured.wind_speed + " km/h</td><td>"
			    	+  weather.measured.wind_direction + "°</td>";
			    tbody.appendChild(tmpLine);
			}
			table.appendChild(tbody);
			table.setAttribute("class", "table table-striped");
			table.setAttribute("style", "width: 1000px");

			prev.appendChild(table);
        } else {
            prev.innerHTML = "<h4>Weather data cannot be retrieved.</h4>"
        }
        node.appendChild(prev);
	}

    var waitMode = function(enable) {
    	if(enable) {
	    	$("#location").attr("readonly", "true");
	    	$("#update").attr("disabled", "disabled");
    		$.getScript("static/js/jquery.activity-indicator-1.0.0.js", function() {
				$('#busy').activity({align: 'left'});
			});
    	} else {
	    	$("#location").removeAttr("readonly");
	    	$("#update").removeAttr("disabled");
    		$.getScript("static/js/jquery.activity-indicator-1.0.0.js", function() {
				$('#busy').activity(false);
			});
    	}		
    }

    $('#update-location').ajaxForm({
        dataType:  'json',
        beforeSubmit:  waitMode(true),
        success : function(data){
        	var node = document.getElementById("weather");
	    	node.innerHTML = "";

	    	if (data.ok) {
	    		$.getScript("static/js/header.js", function() {
	    			displayCurWeather();
	    		});
	    		displayAll();
	    	} else {
	    		node.innerHTML = "<h4>The specified address cannot be geolocalized.</h4>";
	    	}
	    	waitMode(false);
        }
    });

	waitMode(true);
    displayAll();
	waitMode(false);
});
