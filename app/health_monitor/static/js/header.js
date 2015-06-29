$(document).ready(function() {

    var displayCurWeather = function() {
		$.getJSON('/meteo/getloc', function(data) {
			$('#curweather').html("<h4>");
			$('#icweather').html("");

    		$('#curweather').append(data.time + "</br>");

			if (data.loc) {
				$('#curweather').append(data.location + "</br>");
    			displayBusy($('#icweather'), true);
				$.getJSON('/meteo/currentweather', function(data) {
					displayBusy($('#icweather'), false);
		    		if (data.meteo) {
		    			var temperature = Math.round((data.temperature - 273.15) * 100) / 100;
		    			$('#curweather').append(temperature + "°C, " + data.humidity + "% humidity</br>");
		    			$('#icweather').html("<img src=\"" + data.icon + "\" width=\"50px\"/>");
		    		}
			    });
			}
			
	    	$('#curweather').append("</h4>");
		});

    }

    var displayBusy = function(element, enable) {
    	if(enable) {
    		element.attr("style", "position:absolute; right:245px; top:37px;");

		    $.getScript("static/js/jquery.activity-indicator-1.0.0.js", function() {
		    	element.activity({length: 5});
			});
    	} else {
		    $.getScript("static/js/jquery.activity-indicator-1.0.0.js", function() {
	    		element.activity(false);
			});
			
    		element.attr("style", "position:absolute; right:220px; top:15px;");
    	}
	}


    displayCurWeather();
});
