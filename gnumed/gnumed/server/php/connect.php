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
// Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
// or see online at http://www.gnu.org/licenses/gpl.html

// connect to the database, use fixed string for the moment
$conn = pg_connect ("dbname=gmdrugs user=foo");
// FUTURE CODE: this is the PHP magic for password protection
// this is cleartext, we need some way of insisting on SSL connection
// if (_SERVER['SERVER_PORT'] != '443')
//    {
//      echo 'Only HTTPS access is allowed';
//      exit;
//    ]
//  if (!isset($_SERVER['PHP_AUTH_USER'])) {
//    header('WWW-Authenticate: Basic realm="GNU Free Pharmacopoeia"');
//    header('HTTP/1.0 401 Unauthorized');
//    echo 'Access is prohibited without authentication. Please contact gnumed-devel at gnu dot org for an account';
//    exit;
//  } else {
//    $conn = pg_connect ("dbname=gmdrugs user={$_SERVER['PHP_AUTH_USER']} password={$_SERVER['PHP_AUTH_PW']}");
//    if ( ! $conn)
//      {
//        header ("HTTP/1.0 403 Forbidden");
//        echo "Wrong password";
//        exit;
//      }
//  }

// this ONLY works PHP >= 4.1
// this is only *needed* PHP >= 4.2! 
import_request_variables ('gp');

//function audit ($id)
     // function for providing an insert for audit data
//{
//  echo "<small><a href=\"audit.php?id=$id\">AUDIT</a></small>";
//}

?>
