<?php

include ('connect.php');

pg_query ("insert into info_reference (description, source_category) values ('$description', '$source_category')");

include ("references.php");

