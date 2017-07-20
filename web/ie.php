<?php
$data = split('&', $_SERVER['QUERY_STRING'], 3);
$ie = split('=',$data[0],2); $ie = $ie[1];
$url = split('=',$data[1],2); $url = $url[1];
$page = file_get_contents($url);
echo preg_replace(
  '/<head>/i',
  '<head>'.
    '<meta http-equiv="X-UA-Compatible" content="IE='.$ie.'" />'.
    '<base href="'.$url.'" />',
  $page
);
?>