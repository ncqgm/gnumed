


create table node
(
	id mediumint auto_increment primary key,
	title varchar (128) unique,
	author varchar (64),
	contents mediumtext,
	up mediumint unsigned references node (id),
	prev mediumint unsigned references node (id)
);

create table images
(
	id mediumint auto_increment primary key,
	name varchar (128) unique,
	contents longblob,
	mime varchar (128),
	approved tinyint default 0
);