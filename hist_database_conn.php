<?php
  // If we are running this script from the command-line, set the _POST
  // variable (usually set from a HTTP request) from the arguments.
  // Pass the arguments as follows:
  //     php hist_database_conn.php 'val=1086&time_period=_hourly'
  if (!isset($_SERVER["HTTP_HOST"])) 
  {
    parse_str($argv[1], $_POST);
  }

  // SQL Database Login Information
  $servername = "localhost";
  $username = "airdata";
  $password = "AESl0uis!";
  $dbname = "airdata";

  // Create Database Connection
  $conn = new mysqli($servername, $username, $password, $dbname);
  // Check connection
  if ($conn->connect_error)
  {
    die("Connection failed: " . $conn->connect_error);
  }

  # Select the daily or hourly table.
  $table_name = "Daily";
  $time_period = $_POST["time_period"];
  //echo($time_period . "\n");
  if (strcmp($time_period,"_hourly") == 0)
  {
    $table_name = "Hourly";
  }
  $idtable = $table_name . '_Readings_' . $_POST['val'];

  $sql = "SELECT PM2_5Value, Humidity, Lastseen FROM $idtable ORDER BY Lastseen";
  //echo($sql . "\n");

  $result = $conn->query($sql);

  if ($result->num_rows > 0)
   {
    $monitor_array = array();

    while($row = $result->fetch_assoc())
    {
      $pm_value = $row["PM2_5Value"];
      $humidity = $row["Humidity"];
      $last = $row["Lastseen"];

      $date = date_create($last);
      $date_formatted = date_format($date, "U");

      $pm_value_float = floatval($pm_value);
      $humidity_float = floatval($humidity);
      $date_epoch = floatval($date_formatted) * 1000;
                    
      $monitor_array[] = array($date_epoch, $pm_value_float, $humidity_float);
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

