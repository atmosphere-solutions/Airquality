<?php
  // If we are running this script from the command-line, set the _POST
  // variable (usually set from a HTTP request) from the arguments.
  // Pass the arguments as follows:
  //     php hist_database_conn.php 'val=1086&daily=true'
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
  $idtable = $_POST['time_period'] . '_Readings_' . $_POST['val'];

  $sql = "SELECT PM2_5Value, Lastseen FROM $idtable ORDER BY Lastseen";
  echo($sql);
  echo("\n");
  $result = $conn->query($sql);

  if ($result->num_rows > 0)
   {
    $monitor_array = array();

    while($row = $result->fetch_assoc())
    {
      $AC = $row["PM2_5Value"];
      $BC = $row["PM2_5Value"];
      $last = $row["Lastseen"];

      $date = date_create($last);
      $date_formatted = date_format($date, "U");

      $A_Channel = floatval($AC);
      $B_Channel = floatval($BC);
      $date_epoch = floatval($date_formatted) * 1000;
                    
      $monitor_array1[] = array($date_epoch, $A_Channel);
      $monitor_array2[] = array($date_epoch, $B_Channel);
    }

    $monitor_array[] = array($monitor_array1, $monitor_array2);

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

