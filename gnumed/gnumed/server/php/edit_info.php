<!--
PHP interface to gnumed drug database
Copyright (C) 2002 Ian Haywood 

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
or see online at http://www.gnu.org/licenses/gpl.html
!>


<?php

# page to edit drug information 

if (! $conn)
     include ('connect.php');
$result = pg_fetch_array (pg_query ("select information_topic.title as title, get_drug_name (id_drug) as name, info, id_drug from drug_information, link_drug_information, information_topic where drug_information.id = $id_info and link_drug_information.id_info = drug_information.id and id_topic = information_topic.id"));
?>

<html>
<title>Information <?= $result['name'] ?> - <?= $result['title'] ?></title>
<body>

<form method="post" action="update_info.php">
<textarea name="info" cols="70" rows="40">
<?= $result['info'] ?>
</textarea>
<input type="hidden" name="id_info" value="<?= $id_info ?>">
<input type="hidden" name="id_drug" value="<?= $result['id_drug'] ?>">
<input type="submit" value="submit">
</form></body></html>