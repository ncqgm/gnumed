create sequence action_id_seq;
create sequence unit_id_seq;
create sequence clin_id_seq;

create table action ( 
	action_id integer primary key default nextval('action_id_seq'),
			external_id varchar(40),
			name varchar(40) ) inherits audit;

create table test inherits ( action);

create table unit ( unit_id integer primary key default nextval('unit_id_seq'),
			 name varchar( 20)  not null ) ;

create table qty_test ( unit_id integer ) inherits ( test );

create table treatment inherits(action);
create table examination inherits(action);



create table clin_record ( clin_id integer primary key default nextval('clin_id_seq'),
				time date, place_id integer, source_id integer );

create table informal_record ( note text ) inherits (clin_record);

create table result (action_id integer ) inherits (clin_record);

create table measurement ( amt numeric ( 8, 3) ) inherits (result);

create  table clin_order ( action_id integer,  clin_id_completed integer) inherits ( clin_record);
create table qty_result ( qty_test integer, clin_order integer ) inherits (clin_record)   ;


