<?php

// PHP interface to gnumed drug database
// Copyright (C) 2002 Ian Haywood 

// This program is free software; you can redistribute it and/or
// modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.

// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA
// or see online at http://www.gnu.org/licenses/gpl.html

# page to recieve new warning 

include ('connect.php');
pg_query ("insert into drug_information (id_info_reference, id_topic) values ($id_info_reference, $id_topic)"); 
pg_query ("insert into link_drug_information values ($id, currval ('drug_information_id_seq'))");
$result = pg_fetch_row (pg_query ("select currval ('drug_information_id_seq')"));
$id_info = $result[0];
include ('edit_info.php');
?>