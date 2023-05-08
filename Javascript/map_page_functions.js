//**************************************************************************************************
// Function: ajaxRetrieve
//**************************************************************************************************
function ajaxRetrieve(correction_factor)
{
$(document).ready(function() {
    // Variable to hold request
    var request;

    // Abort any pending request
    if (request) {
        request.abort();
    }

    console.log("Get data from php!")
    request = $.ajax({
        url: "/cur_database_conn_json.php",
        type: "get",
        dataType: "json"
    });
    console.log("request complete");

    request.done(function (response, textStatus, jqXHR){
        var correction = Cookies.get('correction_factor');
        var averages = Cookies.get('average');
        console.log(response[0]);
        console.log("setMarkers");


        setMarkers(response, correction_factor, averages);
        console.log(response);
        console.log("Hooray, it worked!");
    });

    request.fail(function (jqXHR, textStatus, errorThrown){
        console.error(
            "The following error occurred: " +
            textStatus, errorThrown
        );
    });
});
}


//**************************************************************************************************
// Function: deleteMarkers
//**************************************************************************************************
function deleteMarkers()
{
    for (let i = 0; i < markers.length; i++)
    {
        markers[i].setMap(null);
    }
    markers = [];
}


//**************************************************************************************************
// Function: setMarkers
//**************************************************************************************************
var infowindow;
function setMarkers(values, correctiontype, average)
{
    if (typeof infowindow == 'undefined'){
        infowindow_status = null;
    }
    else {
        infowindow_status = infowindow.getMap();
    }

    console.log(infowindow_status);
    if ((infowindow_status == null) || (typeof infowindow_status == 'undefined'))
    {
        var message;
        infowindow = new google.maps.InfoWindow();
        console.log("Updating Markers");

        deleteMarkers();

        master = values;

        var icon_10_outdoor = {
            url: "Map_Icons/Map_Icon_10_outdoor.png",
            scaledSize: new google.maps.Size(30, 30),
            origin: new google.maps.Point(0, 0),
            anchor: new google.maps.Point(15,15)
        };

        var icon_10_indoor = {
            url: "Map_Icons/Map_Icon_10_indoor.png",
            scaledSize: new google.maps.Size(30, 30),
            origin: new google.maps.Point(0, 0),
            anchor: new google.maps.Point(15,15)
        };


        var icon_20 = {
            url: "Map_Icons/Map_Icon_20.png",
            scaledSize: new google.maps.Size(30, 30),
            origin: new google.maps.Point(0, 0),
            anchor: new google.maps.Point(15,15)
        };

        var icon_30 = {
            url: "Map_Icons/Map_Icon_30.png",
            scaledSize: new google.maps.Size(30, 30),
            origin: new google.maps.Point(0, 0),
            anchor: new google.maps.Point(15,15)
        };

        var icon_40 = {
            url: "Map_Icons/Map_Icon_40.png",
            scaledSize: new google.maps.Size(30, 30),
            origin: new google.maps.Point(0, 0),
            anchor: new google.maps.Point(15,15)
        };

        var icon_50 = {
            url: "Map_Icons/Map_Icon_50.png",
            scaledSize: new google.maps.Size(30, 30),
            origin: new google.maps.Point(0, 0),
            anchor: new google.maps.Point(15,15)
        };

        var icon_60 = {
            url: "Map_Icons/Map_Icon_60.png",
            scaledSize: new google.maps.Size(30, 30),
            origin: new google.maps.Point(0, 0),
            anchor: new google.maps.Point(15,15)
        };

        var icon_70 = {
            url: "Map_Icons/Map_Icon_70.png",
            scaledSize: new google.maps.Size(30, 30),
            origin: new google.maps.Point(0, 0),
            anchor: new google.maps.Point(15,15)
        };

        var icon_80 = {
            url: "Map_Icons/Map_Icon_80.png",
            scaledSize: new google.maps.Size(30, 30),
            origin: new google.maps.Point(0, 0),
            anchor: new google.maps.Point(15,15)
        };

        var icon_90 = {
            url: "Map_Icons/Map_Icon_90.png",
            scaledSize: new google.maps.Size(30, 30),
            origin: new google.maps.Point(0, 0),
            anchor: new google.maps.Point(15,15)
        };

        var icon_100 = {
            url: "Map_Icons/Map_Icon_100.png",
            scaledSize: new google.maps.Size(30, 30),
            origin: new google.maps.Point(0, 0),
            anchor: new google.maps.Point(15,15)
        };

        var icon_100plus = {
            url: "Map_Icons/Map_Icon_100+.png",
            scaledSize: new google.maps.Size(30, 30),
            origin: new google.maps.Point(0, 0),
            anchor: new google.maps.Point(15,15)
        };

        var icon_NA = {
            url: "Map_Icons/Map_Icon_NA.png",
            scaledSize: new google.maps.Size(30, 30),
            origin: new google.maps.Point(0, 0),
            anchor: new google.maps.Point(15,15)
        };

        for (let i = 0; i < master.length; i++)
        {
            //Sets the Lat Lng and Air quality Value for each sensor
            var location = new google.maps.LatLng(master[i][4], master[i][5]);
            var sensor_reading = master[i][2]
            var humidity = master[i][6]
            var location_type = master[i][7]

            // I have hidden the average field (current, hour, 3-hour, 24-hour, etc.) for the map as we aren't storing data.
            if (average == 1)
            {
                // longer average - nothing stored in db right now so set to 2
                rounded[i] = String(Math.round(master[i][2] * 10) / 10);
            }
            else if (average == 2)
            {
                // longer average - nothing stored in db right now so set to 2
                rounded[i] = String(Math.round(master[i][2] * 10) / 10);
            }
            else if (average == 3)
            {
                // longer average - nothing stored in db right now so set to 2
                rounded[i] = String(Math.round(master[i][2] * 10) / 10);
            }
            else if (average == 4)
            {
                // longer average - nothing stored in db right now so set to 2
                rounded[i] = String(Math.round(master[i][2] * 10) / 10);
            }
            else
            {
                // default - current sensor reading
                rounded[i] = correctionFactor(sensor_reading, humidity, correctiontype);
            }

            var icon_type;
            var font_colour = 'white';
            var risk_colour = 'green';
            if ((rounded[i] > 100) && (rounded[i] < 1000))
            {
                rounded[i] = Math.round(rounded[i]);
                icon_type = icon_100plus;
                risk_colour = 'red';
                message = "<b style = 'color: red;'>Risk Level: Very High </b><br><b>At Risk Population:</b> Avoid strenuous activities outdoors. Children and the elderly should also avoid outdoor physical exertion.<br>" + 
                "<b>General Population:</b> Reduce or reschedule strenuous activities outdoors, especially if you experience symptoms such as coughing and throat irritiation.<br>";
            }
            else if ((rounded[i] < 100) && (rounded[i] >= 90))
            {
                rounded[i] = Math.round(rounded[i]);
                icon_type = icon_100;
                risk_colour = 'red';
                message = "<b style = 'color: red;'>Risk Level: High </b><br><b>At Risk Population:</b> Reduce or reschedule strenuous activities outdoors. Children and elderly should also take it easy.<br>" + 
                "<b>General Population:</b> Consider reducing or reschedulig strenuous activities outdoors if you are experiencing symptoms as coughing and throat irritation.<br>";
            }
            else if ((rounded[i] < 90) && (rounded[i] >= 80))
            {
                rounded[i] = Math.round(rounded[i]);
                icon_type = icon_90;
                risk_colour = 'red';
                message = "<b style = 'color: red;'>Risk Level: High </b><br><b>At Risk Population:</b> Reduce or reschedule strenuous activities outdoors. Children and elderly should also take it easy.<br>" + 
                "<b>General Population:</b> Consider reducing or reschedulig strenuous activities outdoors if you are experiencing symptoms as coughing and throat irritation.<br>";
            }
            else if ((rounded[i] < 80) && (rounded[i] >= 70))
            {
                rounded[i] = Math.round(rounded[i]);
                icon_type = icon_80;
                risk_colour = 'red';
                message = "<b style = 'color: red;'>Risk Level: High </b><br><b>At Risk Population:</b> Reduce or reschedule strenuous activities outdoors. Children and elderly should also take it easy.<br>" + 
                "<b>General Population:</b> Consider reducing or reschedulig strenuous activities outdoors if you are experiencing symptoms as coughing and throat irritation.<br>";
            }
            else if ((rounded[i] < 70) && (rounded[i] >= 60))
            {
                rounded[i] = Math.round(rounded[i]);
                icon_type = icon_70;
                risk_colour = 'red';
                message = "<b style = 'color: red;'>Risk Level: High </b><br><b>At Risk Population:</b> Reduce or reschedule strenuous activities outdoors. Children and elderly should also take it easy.<br>" + 
                "<b>General Population:</b> Consider reducing or reschedulig strenuous activities outdoors if you are experiencing symptoms as coughing and throat irritation.<br>";
            }
            else if ((rounded[i] < 60) && (rounded[i] >= 50))
            {
                icon_type = icon_60;
                font_colour = 'black';
                risk_colour = 'orange';
                message = "<b style = 'color: orange;'>Risk Level: Moderate </b><br><b>At Risk Population:</b> Consider reducing or reschedulig strenuous activities outdoors if you are experiencing symptoms.<br>" + 
                "<b>General Population:</b> No need to modify your usual outdoor activities unless you experience symptoms such as coughing and throat irritation.<br>";
            }
            else if ((rounded[i] < 50) && (rounded[i] >= 40))
            {
                rounded[i] = Math.round(rounded[i]);
                icon_type = icon_50;
                font_colour = 'black';
                risk_colour = 'orange';
                message = "<b style = 'color: orange;'>Risk Level: Moderate </b><br><b>At Risk Population:</b> Consider reducing or reschedulig strenuous activities outdoors if you are experiencing symptoms.<br>" + 
                "<b>General Population:</b> No need to modify your usual outdoor activities unless you experience symptoms such as coughing and throat irritation.<br>";
            }
            else if ((rounded[i] < 40) && (rounded[i] >= 30))
            {
                rounded[i] = Math.round(rounded[i]);
                icon_type = icon_40;
                font_colour = 'black';
                risk_colour = 'orange';
                message = "<b style = 'color: orange;'>Risk Level: Moderate </b><br><b>At Risk Population:</b> Consider reducing or reschedulig strenuous activities outdoors if you are experiencing symptoms.<br>" + 
                "<b>General Population:</b> No need to modify your usual outdoor activities unless you experience symptoms such as coughing and throat irritation.<br>";
            }
            else if ((rounded[i] < 30) && (rounded[i] >= 20))
            {
                rounded[i] = Math.round(rounded[i]);
                icon_type = icon_30;
                risk_colour = 'green';
                message = "<b style = 'color: green;'>Risk Level: Low </b><br><b>At Risk Population:</b> Enjoy your usual outdoor activities.<br> <b>General Population:</b> Ideal air quality for outdoor activities.<br>";
            }
            else if ((rounded[i] < 20) && (rounded[i] >= 10))
            {
                rounded[i] = Math.round(rounded[i]);
                icon_type = icon_20;
                risk_colour = 'green';
                message = "<b style = 'color: green;'>Risk Level: Low </b><br><b>At Risk Population:</b> Enjoy your usual outdoor activities.<br> <b>General Population:</b> Ideal air quality for outdoor activities.<br>";
            }
            else if ((rounded[i] < 10) && (rounded[i] >= 0))
            {
                if (location_type == 0)
                {
                    icon_type = icon_10_outdoor;
                }
                else
                {
                    icon_type = icon_10_indoor;
                }
                font_colour = 'black';
                risk_colour = 'green';
                message = "<b style = 'color: green;'>Risk Level: Low </b><br><b>At Risk Population:</b> Enjoy your usual outdoor activities.<br> <b>General Population:</b> Ideal air quality for outdoor activities.<br>";
            }
            else
            {
                icon_type = icon_NA
            }

            // Display the current sensor reading, humidity and corrected value.
            current_str = "<b style = 'color: " + risk_colour + ";'>Sensor Reading: " + sensor_reading.toString() + "&ensp;Humidity: " + humidity.toString() + "&ensp;Corrected Value: " + rounded[i].toString() + "</b><br><br>"
    
            data_pass[i] = {
                "ID": master[i][0], 
                "Name": master[i][1], 
                "Value": rounded[i],
                "Humidity": master[i][6],
                "Location": master[i][7],
            };
            console.log(data_pass[i]);

            contentstring[i] = "<div class = 'chart' id = 'sensor" + master[i][0] + "'> <h3 style = 'margin: 10px; font-size: 1.3em; font-family: 'serif';'>"
            + data_pass[i]["Name"] + " (" + data_pass[i]["ID"] + ")</h3>" + current_str + message + "<br><b>Chart Data Options: </b> &nbsp;" + "<select id = 'time_period'>" +
                "<option value = '_daily'>Daily</option>" +
                "<option value = '_hourly' selected>Hourly</option> " +
            "</select> &nbsp;" +
            "<select id = 'chart_correction'>" +
                "<option value = '0'>No Correction Factor</option>" +
                "<option value = '1'>AQ-SPEC</option>" +
                "<option value = '2'>LRAPA</option>" +
                "<option value = '3'>U of Utah</option>" +
                "<option value = '4' selected>UNBC</option>" +
            "</select>";
    
            //creates new markers
            var label_value = String(rounded[i]);
            var marker = new google.maps.Marker({
                    position: location, 
                    map: map,
                    label: { text: label_value, fontSize: '12px', color: font_colour },
                    icon: icon_type
            });
            markers.push(marker);
        
            //creates pop-ups
            google.maps.event.addListener(marker, 'click', (function (marker, i) {
            return function () {
                    infowindow.open(map, marker);
                    infowindow.setContent(contentstring[i] + "<div class = 'infowindow' id = 'container" + master[i][0] + "'></div></div>");
                    
                    var latlng = marker.getPosition();
                    map_recenter(latlng, 0, -200);
    
                    google.maps.event.addListener(infowindow, 'domready', function(){
                        // The following ensure the default values of the historical graph are set correctly.
                        // - to begin we select all data so we don't set the zoom
                        var sensor = data_pass[i]
                        var time = $("#time_period").val();
                        var correction = $("#chart_correction").val();
                        ajaxhistoricalRetrieve(sensor, time, correction);
                    });
                    waitForChange(data_pass[i]);
                }
            })(marker, i)); 
        }
    }
    else
    {
        console.log("Infowindow is open, skipping refresh.")
    }
}


//**************************************************************************************************
// Function: setMapZoom
//**************************************************************************************************
function setMapzoom()
{
var current_zoom = Cookies.get("location_zoom");
var gibsons = {lat: 49.401154, lng: -123.5075};

if (current_zoom == 1) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (position) {
            initialLocation = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
            map.setCenter(initialLocation);
            map.setZoom(10);
        });
    }
}
else
{
    map.setCenter(gibsons);
    map.setZoom(10);
}
}


//**************************************************************************************************
//  Function:  correctionFactor
//  Calculate the correction factor for the map display.
//  
//    "<option value = '0'>No Correction Factor</option>" +
//    "<option value = '1'>AQ-SPEC</option>" +
//    "<option value = '2'>LRAPA</option>" +
//    "<option value = '3'>U of Utah</option>" +
//    "<option value = '4'>UNBC</option>" +
//**************************************************************************************************
function correctionFactor(sensor_reading, humidity, type)
{
    var corrected = 0;

    if (type == 0)
    {
        //No Correction Factor
        corrected = sensor_reading;
    }
    else if (type == 1)
    {
        //AQ-SPEC: y = 0.624x + 2.728 (0-100 ug/m3)
        if (sensor_reading < 100)
        {
            corrected = Math.round(((0.624 * sensor_reading) + 2.728) * 10) / 10;
        }
        else
        {
            corrected = sensor_reading;
            console.log("Value: " + type  + "  did not meet requirements for correction factor")
        }
    }
    else if (type == 2)
    {
        //LRAPA y = 0.5x - 0.66 (0-60 ug/m3)
        if (sensor_reading < 60)
        {
            corrected = Math.round(((0.5 * sensor_reading) - 0.66) * 10) /10;
        }
        else
        {
            corrected = sensor_reading;
            console.log("Value: " + type  + "  did not meet requirements for correction factor")
        }
    
    }
    else if (type == 3)
    {
        //U of Utah: y = 0.778x + 2.65 (0-60 ug/m3)
        if (sensor_reading < 60)
        {
            corrected = Math.round(((0.778 * sensor_reading) + 2.65) * 10) / 10;
        }
        else
        {
            corrected = sensor_reading;
            console.log("Value: " + type  + "  did not meet requirements for correction factor")
        }
    }
    else
    { 
        // Old UNBC Correction Factor
        // - UNBC y = 0.68x + 1.91 (0-20 ug/m3)
        // - UNBC y = 0.87x - 6.62 (>20 ug/m3)
        // New UNBC Correction Factor:  Model 2 from the article "Development and evaluation of
        // correction models for a low-cost fine particulate matter monitor"
        // - UNBC Model 2 - y = pm25_cf1 / (1 + 0.24/(100/rh - 1))
        if ((humidity > 0) && (humidity < 100))
        {
            corrected = sensor_reading / (1 + 0.24 / (100 / humidity - 1));
            corrected = Math.round(corrected * 10) / 10;
            if (corrected > 100)
            {
                corrected = Math.round(corrected);
            }
        }
        else
        {
            corrected = sensor_reading;
        }
    }

    return corrected;
}


//**************************************************************************************************
// Function: ajaxhistoricalRetrieve
//**************************************************************************************************
function ajaxhistoricalRetrieve(sensor, time_period, cfactor, zoom)
{
    postarray = 'val=' + sensor["ID"] + '&time_period=' + time_period;
    element = "container" + sensor["ID"];

    console.log("Post: " + sensor["ID"]);
    console.log("Post Array: " + postarray);
    console.log("Element: " + element);
    console.log("Time Period: " + time_period);
    console.log("Zoom: " + zoom);
    console.log("Correction Factor: " + cfactor);

    $(document).ready(function(){
        var request;

        request = $.ajax({
            url: "/hist_database_conn.php",
            type: "post",
            dataType: "text",
            data: postarray
        });

        request.done(function (response){
            console.log("Request Complete")
            console.log("Response: ")
            console.log(response)

            var data = JSON.parse(response);
            console.log("Parsed Data: ")
            console.log(data)

            if ((cfactor !== null) && (typeof cfactor !== 'undefined'))
            {
                console.log("Correcting data with: " + cfactor);
                for (i in data)
                {
                    var sensor_value = data[i][1]
                    var humidity = data[i][2]
                    var corrected_sensor_value = correctionFactor(sensor_value, humidity, cfactor);
                    data[i][1] = corrected_sensor_value;
                }
            }
            else
            {
                console.log("Leaving data uncorrected!")
            }

            console.log("Corrected Data: ")
            console.log(data)
            drawChart(sensor, element, data, zoom);
            console.log("Done")
        });

        request.fail(function(jqXHR, textStatus, errorThrown){
            console.error("The following error occurred: " +
            textStatus, errorThrown
            );
        });
    });
}


//**************************************************************************************************
// Function: drawChart
//**************************************************************************************************
function drawChart(sensor, element, data, zoom)
{
    console.log('Placing chart at: ' + element);
    console.log('Data:' + data + '*****');
    //data_array = JSON.parse(data);
    data_array = data;
    console.log(data_array);
    console.log('Here 3')

     mychart = Highcharts.stockChart(element, {
        chart: {
            zoomType: 'x'
        },
        yAxis: {
            title: {
                    text: 'PM<sup>2.5</sup> (&#181g/m<sup>3</sup>)',//'Air Qualiy (&#181g/m<sup>-3</sup>)',
                    type: 'linear',
                    tickInterval: 1,
                    useHTML: true
                },
            opposite: false,
            plotBands: [{
                from: 0,
                to: 10,
                color: '#21c6f5'
            },
            {
                from: 10,
                to: 20,
                color: "#189aca"
            },
            {
                from: 20,
                to: 30,
                color: "#0d6797"
            },
            {
                from: 30,
                to: 40,
                color: "#fffd37"
            },
            {
                from: 40,
                to: 50,
                color: "#ffcc2e"
            },
            {
                from: 50,
                to: 60,
                color: "#fe9a3f"
            },
            {
                from: 60,
                to: 70,
                color: "#fd6769"
            },
            {
                from: 70,
                to: 80,
                color: "#ff3b3b"
            },
            {
                from: 80,
                to: 90,
                color: "#ff0101"
            },
            {
                from: 90,
                to: 100,
                color: "#cb0713"
            },
            {
                from: 100,
                to: 5000,
                color: "#650205"
            }]
        },
        xAxis: {
                type: 'datetime'
        },
        plotOptions: {
                series: {
                    turboThreshold: 0
                }
            },
        series: [{
            name: 'Mass Concentration',
            color: '#00FF00',
            data: data_array
        }],
        rangeSelector: {
            allButtonsEnabled: true,
            enabled: true
        },
        tooltip: {
            valueDecimals: 1,
            valueSuffix: ' &#181g m<sup>-3</sup>',
            useHTML: true
        }
        });

    if (typeof zoom !== 'undefined'){
        mychart.xAxis[0].setExtremes(zoom[0], zoom[1]);
    }
}
function map_recenter(latlng,offsetx,offsety) {
var point1 = map.getProjection().fromLatLngToPoint(
(latlng instanceof google.maps.LatLng) ? latlng : map.getCenter()
);
var point2 = new google.maps.Point(
( (typeof(offsetx) == 'number' ? offsetx : 0) / Math.pow(2, map.getZoom()) ) || 0,
( (typeof(offsety) == 'number' ? offsety : 0) / Math.pow(2, map.getZoom()) ) || 0
);  
map.setCenter(map.getProjection().fromPointToLatLng(new google.maps.Point(
point1.x - point2.x,
point1.y + point2.y
)));
}


//**************************************************************************************************
// Function waitForChange
//**************************************************************************************************
function waitForChange(sensor)
{
    $(document).ready(function() {
        //Triggers when a change occurs in the specified element
        div_id = "sensor" + sensor["ID"];

        // Triggers when a new time period is selected.
        $("#" + div_id).on('change','#time_period', function() {
            var time = $("#time_period").val();
            var correction = $("#chart_correction").val();
            ajaxhistoricalRetrieve(sensor, time, correction);
        });

        // Triggers when a new correction factor is selected.
        $("#" + div_id).on('change','#chart_correction', function() {
            var min, max;
            ({min, max} = mychart.axes[0].getExtremes()); 
            var zoom = [min, max];

            var time = $("#time_period").val();
            var correction = $("#chart_correction").val();
            console.log("Correction for sensor #" + sensor + " Has been changed to " + correction);
            ajaxhistoricalRetrieve(sensor, time, correction, zoom);
        });
    });
}
