<?php
  $servername = "localhost";
  $username = "airdata";
  $password = "AESl0uis!";
  $dbname = "airdata";

  // Create connection
  $conn = new mysqli($servername, $username, $password, $dbname);
  // Check connection
  if ($conn->connect_error)
  {
    die("Connection failed: " . $conn->connect_error);
  }

  $sql = "SELECT ID, Name, Humidity, PM2_5Value, Lat, Lon, DateCreated, Location FROM Current_Readings_For_Map";
  $result = $conn->query($sql);

  if ($result->num_rows > 0)
  {
    $monitor_array = array();

    while($row = $result->fetch_assoc())
    {
      $id = $row["ID"];
      $label = $row["Name"];
      $value = $row["PM2_5Value"];
      $last = $row["lastModified"];
      $lat = $row["Lat"];
      $lng = $row["Lon"]; 
      $humidity = $row["Humidity"]; 
      $location = $row["Location"]; 
                    
      $monitor_array[] = array($id, $label, $value, $last, $lat, $lng, $humidity, $location);
    }

    //converts PHP array into a format javascript can interpret
    $javascriptarray = json_encode($monitor_array);

    echo($javascriptarray);
  }
  else
  {
    echo "0 results";
  }
  $conn->close();
?>

