<?php

include ('connect.php');

pg_query ("insert into audit (action, why, table_name, table_row, source) values ('v', '$why', '$table', $id, $id_info)");

include ('comments.php');