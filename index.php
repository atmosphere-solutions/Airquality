<!DOCTYPE html>
<html class='a'>
    <!--<meta name='viewport' content='width=device-width, initial-scale=1.00, maximum-scale=1.00, minimum-scale=1.00, user-scalable=no'>-->
    <meta name="viewport" content="width=device-width">
    <head>
        <title>Map - Atmosphere Solutions</title>
        <style>
            @import url('CSS/global.css');
            #map_container
            {
                height: 100%;
                width: 100%;
            }

            #map 
            {
                height: 100%;
                width: 100%;
                position: absolute;
            }

            #logo-div /* Atmosphere Solutions Logo */
            {
                position: absolute;
                left: 50%;  /* Move Top/Left of Div to Center of screen. */
                top: 1%;
                transform: translate(-50%); /* Move Top/Left of Div to left by 50% of Div Width */
                background-color: #282928c0;
                border-radius: 10px;
            }
            .logo-img{
                height: 95%;
                width: 95%;
            }

            #purple-div
            {
                position: absolute;
                left: 1%;
                top: 1%;
                transform: translate(0%);
                background-color: #ffffffff;
                border-radius: 10px;
            }

            @media screen and (max-width: 600px) {
               #logo-div
               {
                   width: 40%
               }
               #purple-div
               {
                   width: 12%
               }
               #settings
               {
                   width: 12%
               }
            }
            @media screen and (min-width: 600px) {
               #logo-div
               {
                   width: 20%
               }
               #purple-div
               {
                   width: 20%
               }
               #settings
               {
                   width: 12%
               }
            }

            .purple-img{
                border-top: 5px;
                height: 90%;
                width: 90%;
            }

            #settings
            {
                display: block;
                position: absolute;
                text-align: center;
                left: 1%;
                bottom: 1%;
            }

            #correction_factor
            {
                margin: 2px;
            }

            #menu
            {
                position: fixed;
                height: 25px;
                width: 150px;
                font-size: 14px;
                bottom: 5px;
                left: 25px;
                border-radius: 10px;
            }

            .title
            {
                text-transform: uppercase;
                border: none;
                border-radius: 2px;
                color: white;
                text-align: center;
                display: inline-block;
                font-size: 26px;
                font-weight: 700;
                letter-spacing: 1px;
                margin: 0;
                margin-left: 15px;
                padding: 5px;
                width: 200px;
                text-align: left;
                word-wrap: break-word;
            }
            .menu
            {
                background-color: #282928c0;
                border-radius: 2px;
                color: white;
                text-align: left;
                font-size: 12px;
                margin: 1px;
                position: static;
                display: block;
                height: 115px;
                width: 285px;
                padding-left: 15px;
                padding-top: 5px;
                padding-bottom: 5px;
            }  
            .pm {
                border-radius: 5px;
                height: 50px;
                width: 270px;
                text-align: left;
            }

            .dropdown{
                width: 100px;
                height: 20px;
                font-size: 12px;
                background-color: #282928c0;
                color: white;
                border-color: white;
                border-radius: 2px;
                border: 1px;
            }
            
        </style>
        <script src ="Javascript/map_page_functions.js?2"></script>
        <script src="https://code.highcharts.com/stock/highstock.js"></script>
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/js-cookie@rc/dist/js.cookie.min.js"></script>
    </head>
    <body style = 'overflow: hidden;'>
        <div id = 'map_container' class="map_canvas">
            <div id = 'map'></div>
            <div id = 'logo-div' class="logo-div-class">
                <a class = 'logo-href' href="https://atmospheresolutions.ca">
                    <img class = 'logo-img' src = "Map_Icons/Atmospherelogo.png" />
                </a>
            </div>
            <div id = 'purple-div' class="purple-div-class">
                <a class = 'purple-href' href="https://purpleair.com">
                    <img class = 'purple-img' src = "Map_Icons/logo_purple_call.png" />
                </a>
            </div>
            <div id = 'settings' class="options">
                <p class = 'menu'>
                    <span>Correction Factor: </span>
                    <select id = 'correction_factor' class = 'dropdown'>
                        <option value = '0'>No Correction Factor</option>
                        <option value = '1'>AQ-SPEC</option>
                        <option value = '2'>LRAPA</option>
                        <option value = '3'>U of Utah</option>
                        <option value = '4' selected>UNBC</option>
                    <select><br>
                    <span>Location Zoom:</span> 
		    <select id = 'zoom_options' class = 'dropdown' style = 'margin-top: 5px;'> 
                        <option hidden disabled selected value></option>
                        <option value = '0' selected>Center on Gibsons</option>
                        <option value = '1'>Center on Location</option>
                    <select><br>
                    <!--
                    <span>Historical Averages: </span>
                    -->
                    <!--
                    <select id = 'avg_options' class = 'dropdown' style = 'margin-top: 5px;'>
                    -->
                        <!--
                        <option hidden disabled selected value></option>
                        <option value = '0'>Current Reading</option>
                        <option value = '1'>1 hr Average</option>
                        -->
                        <!-- <option value = '2'>3 hr Average</option>
                        <option value = '3'>6 hr Average</option>-->
                        <!--
                        <option value = '4'>24 hr Average</option>
                        -->
                    <!--
                    <select><br>
                    -->
                <img class = 'pm' src='Map_Icons/slider_custom_white.png'>
            </div>
        </div>
        <div id = 'container' style = 'width:400px; height:200px;'></div>
        <script>
            var map;
            var is_open = false;
            var open_0 = false;
            var open_1 = false;
            var open_2 = false;
            var master;
            var markers = [];
            var gibsons = {lat: 49.401154, lng: -123.5075};
            var rounded = new Array();
            var data_pass = new Array();
            var contentstring = new Array();
            var current_zoom;

            function initMap()
            {
                map = new google.maps.Map(document.getElementById('map'), {
                    center: gibsons,
                    zoom: 10,
                    mapTypeId: 'roadmap',
                    mapTypeControl: false,
                    streetViewControl: false,
                    fullscreenControl: false,
                    options: {
                        gestureHandling: 'greedy'
                    }
                });

                //Cookies.set('correction_factor', 0);
                //Cookies.set('average', 0);
                setMapzoom();
                ajaxRetrieve();

                // Update the markers at the specified interval.
                var marker_update_interval = 5 * 60 * 1000;
                setInterval(ajaxRetrieve, marker_update_interval);
            }
            
            $(document).ready(function() {
 
            //Triggers when a change occurs in the specified element
            $("#settings").on('change','#correction_factor', function() {

                var correction_type = $("#correction_factor").val();
                //Cookies.set('correction_factor', correction_type);
                ajaxRetrieve(correction_type);
                });
            
            //Triggers when a change occurs in the specified element
            $("#settings").on('change','#avg_options', function() {

                var averages = $("#avg_options").val();
                Cookies.set('average', averages);
                ajaxRetrieve();
                });

            //Triggers when a change occurs in the specified element
            $("#settings").on('change','#zoom_options', function() {

                var correction_type = $("#zoom_options").val();
                Cookies.set('location_zoom', correction_type);
                setMapzoom();
	    	});
	     });
        </script>
        <script async defer
            src = 'https://maps.googleapis.com/maps/api/js?key=AIzaSyA_nOosJgGoJYrYGQkXRgRbr7nKYzbgg34&callback=initMap'>
        </script>
    </body>
</html>
